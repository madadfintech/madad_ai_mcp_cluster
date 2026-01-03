"""Custom exceptions for the MCP system"""

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

class MCPValidationError(MCPException):
    """Parameter validation failed"""
    pass

class MCPTimeoutError(MCPException):
    """Request timed out"""
    pass

class OrchestratorError(MCPException):
    """Orchestrator-level error"""
    pass