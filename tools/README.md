# API Wrapper Tools

This folder contains API wrapper tools that the MCP exposes as available tools.

## Structure

- `base.py` - Base classes and interfaces for creating tools
- `api_wrappers/` - Specific API wrapper implementations
- `api_wrappers/read/non_transactional/` - Read tools for non-transactional endpoints
- `api_wrappers/write/transactional/` - Write tools for transactional endpoints
- `api_wrappers/external/external_vendor/` - External vendor flow endpoints
- `api_wrappers/common/` - Shared clients and utilities

## Creating a New Tool

1. Create a new file in `api_wrappers/` for the API wrapper
2. Inherit from `BaseTool` in `base.py`
3. Implement the `execute()` method with the API logic
4. Override `get_schema()` to define input parameters if needed
5. Register the tool in the orchestrator or agent host

### Example Tool

```python
from tools.base import BaseTool
from typing import Any, Dict

class MyAPITool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_api_tool",
            description="Description of what this tool does"
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Implement api call logic here
        return {"result": "success"}
    
    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["inputSchema"]["properties"] = {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter"}
        }
        schema["inputSchema"]["required"] = ["param1"]
        return schema
```

## Usage

Tools in this folder are consumed by the MCP servers and agent host to provide capabilities to LLM clients.
