import openai
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from agent_host.mcp_client import MCPClientManager
from shared.logging_config import get_logger
from shared.exceptions import *
from shared.config import settings

logger = get_logger(__name__)

class AIAgentOrchestrator:
    """Production-ready AI Agent Orchestrator - ALL ISSUES FIXED"""
    
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.AsyncOpenAI(api_key=openai_api_key, timeout=settings.OPENAI_TIMEOUT)
        self.mcp_manager = MCPClientManager()
        self.logger = get_logger("AIAgentOrchestrator")
        self.request_counter = 0
        self.initialized = False
        
        # Use accessible model
        self.model = settings.OPENAI_MODEL if settings.OPENAI_MODEL != "gpt-4" else "gpt-4o-mini"
        self.logger.info(f"Initialized with model: {self.model}")
        
    async def initialize_servers(self) -> Dict[str, bool]:
        """Initialize connections to all MCP servers"""
        self.logger.info("Initializing MCP servers")
        
        servers = [
            ("query_server", settings.QUERY_SERVER_URL),
            ("transactional_server", settings.TRANSACTIONAL_SERVER_URL),
            ("external_api_server", settings.EXTERNAL_API_SERVER_URL),
        ]
        
        results = {}
        for name, url in servers:
            try:
                success = await self.mcp_manager.add_server(name, url)
                results[name] = success
                
                if success:
                    self.logger.info("Connected to MCP server", server_name=name)
                else:
                    self.logger.warning("Failed to connect to MCP server", server_name=name)
                    
            except Exception as e:
                self.logger.error("Exception connecting to MCP server",
                                server_name=name,
                                error=str(e))
                results[name] = False
        
        self.initialized = any(results.values())
        
        if not self.initialized:
            raise OrchestratorError("Failed to connect to any MCP servers")
        
        self.logger.info("MCP server initialization completed", results=results)
        return results
    
    def _prepare_message_for_api(self, message: Any) -> Dict[str, Any]:
        """
        Prepare a message for OpenAI API
        CRITICAL FIX: Handle None content properly
        """
        message_dict = {"role": message.role}
        
        # CRITICAL: Only include content if it's not None
        # OpenAI API doesn't like None content
        if message.content is not None:
            message_dict["content"] = message.content
        
        # Add tool calls if present
        if hasattr(message, 'tool_calls') and message.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        
        return message_dict
    
    async def _call_llm(self, messages: List[Dict], tools: List[Dict]) -> Any:
        """
        Call LLM with proper error handling
        NO RETRY DECORATOR - handle errors explicitly
        """
        try:
            self.logger.debug(f"Calling OpenAI API", 
                            model=self.model, 
                            messages_count=len(messages),
                            tools_count=len(tools))
            
            # Make the API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,  # Don't send empty tools list
                tool_choice="auto" if tools else None,
                temperature=0.7
            )
            
            self.logger.debug("OpenAI API call successful")
            return response
            
        except openai.BadRequestError as e:
            # Extract detailed error info
            error_msg = str(e)
            error_details = {
                "model": self.model,
                "messages_count": len(messages),
                "tools_count": len(tools)
            }
            
            if hasattr(e, 'body'):
                error_details["body"] = e.body
            
            self.logger.error("OpenAI BadRequestError", 
                            error=error_msg,
                            details=error_details)
            
            # Provide helpful error message
            if "model" in error_msg.lower():
                raise OrchestratorError(
                    f"Model '{self.model}' not available. Set OPENAI_MODEL in .env to: gpt-4o-mini, gpt-4o, or gpt-3.5-turbo"
                )
            elif "tool" in error_msg.lower():
                raise OrchestratorError(
                    f"Tool format error. Check MCP tool definitions. Error: {error_msg}"
                )
            else:
                raise OrchestratorError(f"OpenAI API error: {error_msg}")
                
        except openai.AuthenticationError as e:
            self.logger.error("OpenAI authentication failed")
            raise OrchestratorError("Invalid OpenAI API key")
            
        except openai.RateLimitError as e:
            self.logger.error("OpenAI rate limit exceeded")
            raise OrchestratorError("Rate limit exceeded. Try again later.")
            
        except openai.APITimeoutError as e:
            self.logger.error("OpenAI request timed out")
            raise MCPTimeoutError("OpenAI request timed out")
            
        except Exception as e:
            self.logger.error("Unexpected error calling OpenAI",
                            error=str(e),
                            error_type=type(e).__name__)
            raise OrchestratorError(f"Unexpected error: {type(e).__name__}: {str(e)}")
    
    async def process_query(self, user_query: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Process a user query using available MCP tools"""
        if not self.initialized:
            raise OrchestratorError("Orchestrator not initialized")
        
        self.request_counter += 1
        request_id = f"req_{self.request_counter}_{datetime.now().timestamp()}"
        
        self.logger.info("Processing query",
                        request_id=request_id,
                        query=user_query[:100],  # Truncate for logging
                        model=self.model)
        
        start_time = datetime.now()
        tools_used = []
        iterations = 0
        
        try:
            # Get available tools
            tools = self.mcp_manager.get_tools_for_llm()
            
            self.logger.info(f"Loaded {len(tools)} tools from MCP servers")
            
            # System message
            system_message = {
                "role": "system",
                "content": """You are an AI assistant with access to multiple specialized servers through MCP tools:

1. query_server: Read-only data (users, products, analytics, knowledge, status)
2. transactional_server: State changes (orders, inventory)
3. external_api_server: External services (search, weather, translation)

Use tools to gather information, then provide clear, helpful responses."""
            }
            
            messages = [
                system_message,
                {"role": "user", "content": user_query}
            ]
            
            # Orchestration loop
            while iterations < max_iterations:
                iterations += 1
                
                self.logger.debug(f"Iteration {iterations}/{max_iterations}")
                
                # Call LLM
                try:
                    response = await self._call_llm(messages, tools)
                except OrchestratorError as e:
                    # Return error immediately
                    self.logger.error("LLM call failed", error=str(e))
                    return {
                        "request_id": request_id,
                        "response": str(e),
                        "success": False,
                        "metadata": {
                            "error": str(e),
                            "iterations": iterations,
                            "model_used": self.model
                        }
                    }
                
                message = response.choices[0].message
                
                # CRITICAL FIX: Properly format message for next iteration
                message_dict = self._prepare_message_for_api(message)
                messages.append(message_dict)
                
                # Check if LLM wants to use tools
                if message.tool_calls:
                    self.logger.info(f"LLM requesting {len(message.tool_calls)} tool calls")
                    
                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        
                        try:
                            tool_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as e:
                            self.logger.error("Invalid tool arguments",
                                            tool_name=tool_name,
                                            error=str(e))
                            
                            # Add error result
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": "Invalid arguments format"})
                            })
                            continue
                        
                        try:
                            # Execute tool via MCP
                            self.logger.debug(f"Calling tool: {tool_name}")
                            result = await self.mcp_manager.call_tool(tool_name, tool_args)
                            
                            tools_used.append({
                                "tool": tool_name,
                                "parameters": tool_args,
                                "success": result.success,
                                "execution_time_ms": result.execution_time_ms
                            })
                            
                            # Add tool result to messages
                            tool_content = json.dumps(result.result if result.success else {"error": result.error})
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_content
                            })
                            
                            self.logger.debug(f"Tool {tool_name} completed", success=result.success)
                            
                        except MCPException as e:
                            self.logger.error("MCP tool error",
                                            tool_name=tool_name,
                                            error=str(e))
                            
                            # Add error result
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": f"Tool failed: {str(e)}"})
                            })
                            
                            tools_used.append({
                                "tool": tool_name,
                                "parameters": tool_args,
                                "success": False,
                                "error": str(e)
                            })
                    
                    # Continue loop to get final response
                    continue
                    
                else:
                    # LLM provided final response
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    self.logger.info("Query completed",
                                   request_id=request_id,
                                   iterations=iterations,
                                   tools_used=len(tools_used),
                                   execution_time=execution_time)
                    
                    return {
                        "request_id": request_id,
                        "response": message.content or "No response generated",
                        "success": True,
                        "metadata": {
                            "iterations": iterations,
                            "tools_used": tools_used,
                            "execution_time_seconds": execution_time,
                            "model_used": self.model,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
            
            # Max iterations reached
            self.logger.warning("Max iterations reached", request_id=request_id)
            
            return {
                "request_id": request_id,
                "response": "Maximum iterations reached. Please try rephrasing your query.",
                "success": False,
                "metadata": {
                    "error": "max_iterations_reached",
                    "iterations": iterations,
                    "tools_used": tools_used,
                    "model_used": self.model
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error("Query processing failed",
                            request_id=request_id,
                            error=str(e),
                            error_type=type(e).__name__)
            
            return {
                "request_id": request_id,
                "response": f"Error: {type(e).__name__}: {str(e)}",
                "success": False,
                "metadata": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "iterations": iterations,
                    "tools_used": tools_used,
                    "execution_time_seconds": execution_time,
                    "model_used": self.model
                }
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_status = await self.mcp_manager.health_check_all()
        stats = self.mcp_manager.get_statistics()
        
        return {
            "initialized": self.initialized,
            "health_status": health_status,
            "statistics": stats,
            "total_requests_processed": self.request_counter,
            "openai_model": self.model,
            "timestamp": datetime.now().isoformat()
        }