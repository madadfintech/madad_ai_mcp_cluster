# ============================================================================
# FILE: shared/fastmcp.py - FIXED VERSION
# ============================================================================
"""
Enhanced FastMCP Library with production-ready features
"""
from typing import Dict, List, Any, Optional, Callable, Type
from fastapi import FastAPI, Request, HTTPException
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
import inspect
import json
import re
from enum import Enum
import httpx
import time
import os

# Import with fallback
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    print("Warning: tenacity not installed, retries disabled")

# Lazy imports to avoid circular dependencies
_logger = None
_settings = None

def get_logger_instance(name: str):
    """Lazy logger import"""
    global _logger
    if _logger is None:
        try:
            from shared.logging_config import get_logger
            _logger = get_logger
        except ImportError:
            import logging
            return logging.getLogger(name)
    return _logger(name)

def get_settings():
    """Lazy settings import"""
    global _settings
    if _settings is None:
        try:
            from shared.config import settings
            _settings = settings
        except ImportError:
            # Create a minimal settings object
            class MinimalSettings:
                MCP_CLIENT_TIMEOUT = int(os.getenv("MCP_CLIENT_TIMEOUT", "30"))
                MCP_CLIENT_MAX_RETRIES = int(os.getenv("MCP_CLIENT_MAX_RETRIES", "3"))
                MCP_CLIENT_RETRY_DELAY = float(os.getenv("MCP_CLIENT_RETRY_DELAY", "1.0"))
            _settings = MinimalSettings()
    return _settings

# Custom exceptions (inline to avoid import issues)
class MCPException(Exception):
    """Base exception for MCP system"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class MCPConnectionError(MCPException):
    """Failed to connect to MCP server"""
    pass

class MCPToolNotFoundError(MCPException):
    """Requested tool not found"""
    pass

class MCPToolExecutionError(MCPException):
    """Tool execution failed"""
    pass

class MCPToolType(str, Enum):
    FUNCTION = "function"

class MCPParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"

class MCPParameter(BaseModel):
    type: MCPParameterType
    description: Optional[str] = None
    required: bool = False

class MCPTool(BaseModel):
    name: str
    description: str
    type: MCPToolType = MCPToolType.FUNCTION
    parameters: Dict[str, MCPParameter] = {}
    required_params: List[str] = []

class MCPToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class MCPToolResult(BaseModel):
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

class MCPServerInfo(BaseModel):
    name: str
    version: str
    tools: List[MCPTool]
    status: str = "operational"

class FastMCPServer:
    """Production-ready FastMCP Server with auto-discovery"""
    
    def __init__(self, app: FastAPI, name: str = "FastMCP Server", version: str = "1.0.0"):
        self.app = app
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.route_handlers: Dict[str, Callable] = {}
        self.logger = get_logger_instance(f"FastMCPServer.{name}")
        
        # Add MCP endpoint
        self.app.add_api_route("/mcp", self.mcp_endpoint, methods=["GET", "POST"])
        self.app.add_api_route("/health", self.health_check, methods=["GET"])
        
        # Auto-discover existing routes
        self._discover_tools()
        
        self.logger.info(f"FastMCP Server initialized: {name}, tools: {len(self.tools)}")
    
    def _discover_tools(self):
        """Automatically discover and register tools from existing FastAPI routes"""
        for route in self.app.routes:
            if isinstance(route, APIRoute) and route.path not in ["/mcp", "/health"]:
                try:
                    self._register_route_as_tool(route)
                except Exception as e:
                    self.logger.warning(f"Failed to register route {route.path}: {e}")

    def _tool_name_for_route(self, method: str, path: str) -> str:
        """Create an OpenAI/MCP-safe tool name from a FastAPI route."""
        raw_name = f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_name)
        safe_name = re.sub(r"_+", "_", safe_name).strip("_")
        return safe_name or f"{method.lower()}_root"

    def _register_pydantic_model_parameters(
        self,
        model_class: Type[BaseModel],
        parameters: Dict[str, MCPParameter],
        required_params: List[str],
    ):
        """Flatten a Pydantic request body model into MCP tool parameters."""
        if hasattr(model_class, "model_fields"):
            fields = model_class.model_fields
            for field_name, field_info in fields.items():
                annotation = field_info.annotation
                required = field_info.is_required()
                description = getattr(field_info, "description", None)
                parameters[field_name] = MCPParameter(
                    type=self._mcp_type_from_annotation(annotation),
                    description=description or f"Parameter {field_name}",
                    required=required,
                )
                if required:
                    required_params.append(field_name)
            return

        fields = getattr(model_class, "__fields__", {})
        for field_name, field_info in fields.items():
            annotation = getattr(field_info, "outer_type_", str)
            required = getattr(field_info, "required", False)
            description = getattr(field_info.field_info, "description", None)
            parameters[field_name] = MCPParameter(
                type=self._mcp_type_from_annotation(annotation),
                description=description or f"Parameter {field_name}",
                required=required,
            )
            if required:
                required_params.append(field_name)

    def _mcp_type_from_annotation(self, annotation: Any) -> MCPParameterType:
        """Map Python/Pydantic annotations to MCP parameter types."""
        origin = getattr(annotation, "__origin__", None)
        if annotation == int:
            return MCPParameterType.INTEGER
        if annotation == bool:
            return MCPParameterType.BOOLEAN
        if annotation == dict or origin == dict:
            return MCPParameterType.OBJECT
        if annotation == list or origin == list:
            return MCPParameterType.ARRAY
        return MCPParameterType.STRING
    
    def _register_route_as_tool(self, route: APIRoute):
        """Convert a FastAPI route to an MCP tool"""
        method = list(route.methods)[0] if route.methods else "GET"
        tool_name = self._tool_name_for_route(method, route.path)
        handler = route.endpoint
        
        # Extract parameters
        sig = inspect.signature(handler)
        parameters = {}
        required_params = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['request', 'self']:
                continue

            if inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel):
                self._register_pydantic_model_parameters(
                    param.annotation,
                    parameters,
                    required_params,
                )
                continue

            param_type = self._mcp_type_from_annotation(param.annotation)
            
            parameters[param_name] = MCPParameter(
                type=param_type,
                description=f"Parameter {param_name} for {route.path}",
                required=param.default == inspect.Parameter.empty
            )
            
            if param.default == inspect.Parameter.empty:
                required_params.append(param_name)
        
        tool = MCPTool(
            name=tool_name,
            description=f"{method} {route.path} - {handler.__doc__ or 'No description'}",
            parameters=parameters,
            required_params=required_params
        )
        
        self.tools[tool_name] = tool
        self.route_handlers[tool_name] = (route, method)
    
    async def mcp_endpoint(self, request: Request):
        """MCP endpoint handler"""
        if request.method == "GET":
            return MCPServerInfo(
                name=self.name,
                version=self.version,
                tools=list(self.tools.values())
            )
        
        elif request.method == "POST":
            start_time = time.time()
            
            try:
                body = await request.json()
                tool_call = MCPToolCall(**body)
                result = await self._execute_tool(tool_call, request)
                execution_time = (time.time() - start_time) * 1000
                
                return MCPToolResult(
                    success=True, 
                    result=result,
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                self.logger.error(f"Tool execution failed: {e}")
                
                return MCPToolResult(
                    success=False, 
                    error=str(e),
                    execution_time_ms=execution_time
                )
    
    async def _execute_tool(self, tool_call: MCPToolCall, original_request: Request):
        """Execute a tool call"""
        if tool_call.tool_name not in self.tools:
            raise MCPToolNotFoundError(
                f"Tool '{tool_call.tool_name}' not found",
                {"available_tools": list(self.tools.keys())}
            )
        
        route, method = self.route_handlers[tool_call.tool_name]
        settings = get_settings()
        
        async with httpx.AsyncClient(timeout=settings.MCP_CLIENT_TIMEOUT) as client:
            base_url = f"http://localhost:{original_request.url.port}"
            url = f"{base_url}{route.path}"
            
            if method.upper() in ["GET", "DELETE"]:
                response = await client.request(method, url, params=tool_call.parameters)
            else:
                response = await client.request(method, url, json=tool_call.parameters)
            
            if response.status_code >= 400:
                raise MCPToolExecutionError(
                    f"Tool execution failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
            
            return response.json()
    
    async def health_check(self):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "server_name": self.name,
            "version": self.version,
            "total_tools": len(self.tools)
        }

class FastMCPClient:
    """Production-ready MCP Client"""
    
    def __init__(self, base_url: str, name: str = "unnamed"):
        self.base_url = base_url.rstrip('/')
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
        self.logger = get_logger_instance(f"FastMCPClient.{name}")
        self.is_connected = False
    
    async def connect(self):
        """Connect to MCP server and discover tools"""
        settings = get_settings()
        max_retries = settings.MCP_CLIENT_MAX_RETRIES if HAS_TENACITY else 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Connecting to MCP server: {self.base_url} (attempt {attempt + 1})")
                
                async with httpx.AsyncClient(timeout=settings.MCP_CLIENT_TIMEOUT) as client:
                    response = await client.get(f"{self.base_url}/mcp")
                    response.raise_for_status()
                    
                    server_info = MCPServerInfo(**response.json())
                    self.tools = {tool.name: tool for tool in server_info.tools}
                    self.is_connected = True
                    
                    self.logger.info(f"Connected to MCP server: {self.base_url}, tools: {len(self.tools)}")
                    return server_info
                    
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(settings.MCP_CLIENT_RETRY_DELAY * (2 ** attempt))
                else:
                    raise MCPConnectionError(
                        f"Failed to connect to MCP server at {self.base_url}",
                        {"error": str(e)}
                    )
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool call"""
        if not self.is_connected:
            raise MCPConnectionError("Client is not connected to MCP server")
        
        if tool_name not in self.tools:
            raise MCPToolNotFoundError(
                f"Tool '{tool_name}' not available",
                {"available_tools": list(self.tools.keys())}
            )
        
        settings = get_settings()
        tool_call = MCPToolCall(tool_name=tool_name, parameters=parameters)
        
        try:
            async with httpx.AsyncClient(timeout=settings.MCP_CLIENT_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=tool_call.dict()
                )
                response.raise_for_status()
                return MCPToolResult(**response.json())
                
        except httpx.HTTPError as e:
            self.logger.error(f"Tool call failed: {tool_name}, error: {e}")
            raise MCPToolExecutionError(
                f"Failed to execute tool '{tool_name}'",
                {"error": str(e)}
            )
    
    async def health_check(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False
