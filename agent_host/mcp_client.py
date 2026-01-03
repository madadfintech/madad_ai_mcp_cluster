from typing import Dict, List, Any, Optional
from shared.fastmcp import FastMCPClient, MCPTool, MCPToolResult
from shared.logging_config import get_logger
from shared.exceptions import *
import asyncio

logger = get_logger(__name__)

class MCPClientManager:
    """Manages multiple MCP client connections - FIXED tool extraction"""
    
    def __init__(self):
        self.clients: Dict[str, FastMCPClient] = {}
        self.all_tools: Dict[str, tuple[str, MCPTool]] = {}
        self.health_status: Dict[str, bool] = {}
        self.logger = get_logger("MCPClientManager")
    
    async def add_server(self, name: str, base_url: str) -> bool:
        """Add and connect to an MCP server"""
        try:
            self.logger.info("Adding MCP server", server_name=name, base_url=base_url)
            
            client = FastMCPClient(base_url, name=name)
            await client.connect()
            
            self.clients[name] = client
            self.health_status[name] = True
            
            # Register all tools with server prefix
            for tool_name, tool in client.tools.items():
                full_tool_name = f"{name}_{tool_name}"
                self.all_tools[full_tool_name] = (name, tool)
            
            self.logger.info("MCP server added successfully",
                           server_name=name,
                           tools_count=len(client.tools))
            return True
            
        except MCPException as e:
            self.logger.error("Failed to add MCP server",
                            server_name=name,
                            error=str(e),
                            details=e.details)
            self.health_status[name] = False
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool call on the appropriate server"""
        if tool_name not in self.all_tools:
            available_tools = list(self.all_tools.keys())
            self.logger.error("Tool not found",
                            tool_name=tool_name,
                            available_tools=available_tools[:10])
            
            raise MCPToolNotFoundError(
                f"Tool '{tool_name}' not found",
                {"available_tools": available_tools}
            )
        
        server_name, tool = self.all_tools[tool_name]
        client = self.clients[server_name]
        
        # CRITICAL FIX: Use the original tool name stored in the MCPTool object
        # This correctly handles server names with underscores like "query_server"
        actual_tool_name = tool.name
        
        try:
            self.logger.info("Executing tool",
                           tool_name=tool_name,
                           server_name=server_name,
                           actual_tool_name=actual_tool_name,
                           parameters=parameters)
            
            result = await client.call_tool(actual_tool_name, parameters)
            
            self.logger.info("Tool execution completed",
                           tool_name=tool_name,
                           success=result.success,
                           execution_time_ms=result.execution_time_ms)
            
            return result
            
        except MCPException as e:
            self.logger.error("Tool execution failed",
                            tool_name=tool_name,
                            server_name=server_name,
                            error=str(e))
            raise
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all connected servers"""
        self.logger.info("Running health check on all servers")
        
        tasks = []
        for name, client in self.clients.items():
            tasks.append(self._check_server_health(name, client))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, name in enumerate(self.clients.keys()):
            is_healthy = results[i] if isinstance(results[i], bool) else False
            self.health_status[name] = is_healthy
        
        self.logger.info("Health check completed", status=self.health_status)
        return self.health_status
    
    async def _check_server_health(self, name: str, client: FastMCPClient) -> bool:
        """Check health of a single server"""
        try:
            is_healthy = await client.health_check()
            self.logger.debug("Server health check",
                            server_name=name,
                            healthy=is_healthy)
            return is_healthy
        except Exception as e:
            self.logger.warning("Server health check failed",
                              server_name=name,
                              error=str(e))
            return False
    
    def get_available_tools(self) -> Dict[str, MCPTool]:
        """Get all available tools across all servers"""
        return {name: tool for name, (_, tool) in self.all_tools.items()}
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Format tools for LLM consumption (OpenAI function calling format)
        CRITICAL FIX: Proper parameter formatting for OpenAI API
        """
        tools = []
        
        for tool_name, (server_name, tool) in self.all_tools.items():
            properties = {}
            required = []
            
            # Build properties dict
            for param_name, param in tool.parameters.items():
                prop_def = {
                    "type": param.type.value
                }
                
                # Add description if available
                if param.description:
                    prop_def["description"] = param.description
                
                properties[param_name] = prop_def
                
                # Track required parameters
                if param.required:
                    required.append(param_name)
            
            # CRITICAL FIX: Always include parameters object
            # Even if empty, OpenAI expects this structure
            parameters_obj = {
                "type": "object",
                "properties": properties if properties else {},
            }
            
            # Only add required if there are required params
            if required:
                parameters_obj["required"] = required
            
            # Build tool definition
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool.description or f"Tool: {tool_name}",
                    "parameters": parameters_obj
                }
            }
            
            tools.append(tool_def)
        
        self.logger.debug(f"Formatted {len(tools)} tools for LLM")
        return tools
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            "total_servers": len(self.clients),
            "healthy_servers": sum(1 for h in self.health_status.values() if h),
            "total_tools": len(self.all_tools),
            "servers": {
                name: {
                    "healthy": self.health_status.get(name, False),
                    "tools_count": len(client.tools)
                }
                for name, client in self.clients.items()
            }
        }