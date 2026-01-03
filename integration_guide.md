# MCP Multi-Agent System - Integration Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Adding New MCP Servers](#adding-new-mcp-servers)
7. [Adding Routes and Tools](#adding-routes-and-tools)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## System Overview

The MCP Multi-Agent System is a production-ready orchestrator that enables AI agents to interact with multiple domain-specific services through a unified interface. The system automatically discovers FastAPI routes and converts them into tools that can be called by LLMs.

### Key Features

- **Auto-Discovery**: FastAPI routes are automatically converted to MCP tools
- **Multi-Server Architecture**: Separate servers for different domains (query, transactional, external APIs)
- **OpenAI Integration**: Tools formatted for OpenAI function calling
- **Health Monitoring**: Built-in health checks for all services
- **Comprehensive Logging**: Structured logging throughout the system
- **Error Handling**: Robust exception handling with detailed error messages

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Request                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Host (Port 8000)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AIAgentOrchestrator                        │  │
│  │  - Processes queries with OpenAI                     │  │
│  │  - Manages tool execution workflow                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           MCPClientManager                           │  │
│  │  - Aggregates tools from all servers                 │  │
│  │  - Executes tool calls                               │  │
│  │  - Formats tools for OpenAI                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Query Server    │ │ Transactional    │ │ External API     │
│  (Port 8001)     │ │ Server           │ │ Server           │
│                  │ │ (Port 8002)      │ │ (Port 8003)      │
│  - Read-only ops │ │ - State changes  │ │ - External APIs  │
│  - Data queries  │ │ - CRUD ops       │ │ - 3rd party      │
│  - Analytics     │ │ - Transactions   │ │   services       │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         │                   │                     │
         └───────────────────┴─────────────────────┘
                              │
                  ┌───────────▼───────────┐
                  │   FastMCP Library     │
                  │  - Auto-discovery     │
                  │  - Route conversion   │
                  └───────────────────────┘
```

---

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- OpenAI API key
- Basic understanding of FastAPI and async Python

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd mcp_server_cluster
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.25.0
openai>=1.0.0
python-dotenv>=1.0.0
structlog>=23.1.0
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Server URLs
QUERY_SERVER_URL=http://localhost:8001
TRANSACTIONAL_SERVER_URL=http://localhost:8002
EXTERNAL_API_SERVER_URL=http://localhost:8003

# Agent Host
AGENT_HOST_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=console
```

---

## Quick Start

### Start All Servers

You'll need 4 terminal windows:

**Terminal 1 - Query Server:**
```bash
cd servers/query_server
python main.py
```

**Terminal 2 - Transactional Server:**
```bash
cd servers/transactional_server
python main.py
```

**Terminal 3 - External API Server:**
```bash
cd servers/external_api_server
python main.py
```

**Terminal 4 - Agent Host:**
```bash
cd agent_host
python main.py
```

### Verify Installation

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "servers": {
    "query_server": true,
    "transactional_server": true,
    "external_api_server": true
  }
}
```

### Test with a Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all users in the system"
  }'
```

---

## Adding New MCP Servers

### Step 1: Create Server Directory

```bash
mkdir servers/your_server_name
cd servers/your_server_name
```

### Step 2: Create Server Structure

```
your_server_name/
├── __init__.py
├── main.py
├── routes.py
└── models.py
```

### Step 3: Implement Main Entry Point

**main.py:**
```python
from fastapi import FastAPI
from .routes import router
from shared.fastmcp import FastMCPServer
from shared.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Your Server Name",
    description="Description of your server",
    version="1.0.0"
)

# Include your routes
app.include_router(router, prefix="/v1")

# Initialize FastMCP - this auto-discovers all routes
mcp_server = FastMCPServer(app, name="Your Server Name", version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, log_config=None)
```

### Step 4: Define Data Models

**models.py:**
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class YourRequest(BaseModel):
    field1: str
    field2: Optional[int] = None

class YourResponse(BaseModel):
    id: int
    data: str
    created_at: datetime
```

### Step 5: Create Routes

**routes.py:**
```python
from fastapi import APIRouter, HTTPException
from typing import List
from .models import YourRequest, YourResponse
from datetime import datetime
from shared.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/items", response_model=List[YourResponse])
async def get_items():
    """Get all items - this becomes an MCP tool automatically"""
    logger.info("Fetching items")
    
    # Your business logic here
    items = [
        YourResponse(id=1, data="Item 1", created_at=datetime.now()),
        YourResponse(id=2, data="Item 2", created_at=datetime.now())
    ]
    
    return items

@router.post("/items", response_model=YourResponse)
async def create_item(request: YourRequest):
    """Create a new item - this becomes an MCP tool automatically"""
    logger.info("Creating item", data=request.dict())
    
    # Your business logic here
    new_item = YourResponse(
        id=1,
        data=request.field1,
        created_at=datetime.now()
    )
    
    return new_item

@router.get("/items/{item_id}", response_model=YourResponse)
async def get_item(item_id: int):
    """Get item by ID - this becomes an MCP tool automatically"""
    logger.info("Fetching item", item_id=item_id)
    
    # Your business logic here
    if item_id not in [1, 2, 3]:
        raise HTTPException(404, "Item not found")
    
    return YourResponse(
        id=item_id,
        data=f"Item {item_id}",
        created_at=datetime.now()
    )
```

### Step 6: Register with Agent Host

Update `agent_host/orchestrator.py` to include your new server:

```python
async def initialize_servers(self) -> Dict[str, bool]:
    """Initialize all MCP servers"""
    
    servers = {
        "query_server": settings.QUERY_SERVER_URL,
        "transactional_server": settings.TRANSACTIONAL_SERVER_URL,
        "external_api_server": settings.EXTERNAL_API_SERVER_URL,
        "your_server_name": "http://localhost:8004"  # Add your server
    }
    
    # ... rest of the method
```

### Step 7: Update Configuration

Add to `shared/config.py`:

```python
class Settings(PydanticBaseSettings):
    # ... existing settings ...
    YOUR_SERVER_URL: str = "http://localhost:8004"
```

Add to `.env`:

```env
YOUR_SERVER_URL=http://localhost:8004
```

---

## Adding Routes and Tools

### Understanding Auto-Discovery

The FastMCP library automatically converts FastAPI routes into tools. Each route becomes a callable tool that the LLM can use.

### Route Naming Convention

Routes are converted to tool names using this pattern:
```
{http_method}_{path_with_underscores}
```

Examples:
- `GET /v1/users` → `get_v1_users`
- `POST /v1/orders` → `post_v1_orders`
- `GET /v1/products/{id}` → `get_v1_products_id`

The server name is prefixed when registered:
- `query_server_get_v1_users`
- `transactional_server_post_v1_orders`

### Adding a Simple GET Route

```python
@router.get("/data")
async def get_data():
    """
    Get data - docstring becomes tool description
    """
    return {"data": "your_data"}
```

### Adding a POST Route with Parameters

```python
from pydantic import BaseModel

class CreateRequest(BaseModel):
    name: str
    value: int

@router.post("/items")
async def create_item(request: CreateRequest):
    """
    Create a new item
    
    Parameters are automatically extracted from the Pydantic model
    """
    # Your logic
    return {"id": 1, "name": request.name, "value": request.value}
```

### Adding a Route with Path Parameters

```python
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    """
    Get item by ID
    
    Path parameters are automatically detected
    """
    return {"id": item_id, "name": f"Item {item_id}"}
```

### Adding a Route with Query Parameters

```python
from fastapi import Query

@router.get("/search")
async def search_items(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Result limit")
):
    """
    Search items with pagination
    
    Query parameters are automatically converted to tool parameters
    """
    return {"query": query, "limit": limit, "results": []}
```

### Complex Parameter Types

```python
from typing import List, Optional
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class FilterRequest(BaseModel):
    categories: List[str]
    status: Optional[Status] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

@router.post("/products/filter")
async def filter_products(filters: FilterRequest):
    """
    Filter products with complex criteria
    
    Supports lists, enums, and optional parameters
    """
    # Your filtering logic
    return {"filters": filters.dict(), "results": []}
```

### Best Practices for Route Design

1. **Clear Docstrings**: The docstring becomes the tool description
```python
@router.get("/analytics")
async def get_analytics():
    """
    Get comprehensive analytics data including user counts,
    product statistics, and revenue metrics
    """
    pass
```

2. **Use Pydantic Models**: Type-safe parameters that auto-convert
```python
class AnalyticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    metrics: List[str]
```

3. **Descriptive Parameter Names**: Clear names help the LLM understand
```python
async def create_order(
    user_id: int,
    product_id: int,
    quantity: int
):
    pass
```

4. **HTTP Status Codes**: Use appropriate status codes
```python
from fastapi import HTTPException

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if not exists(item_id):
        raise HTTPException(404, "Item not found")
    # Delete logic
    return {"message": "Deleted successfully"}
```

---

## Configuration

### Environment Variables

All configuration is managed through environment variables and `shared/config.py`.

**Available Settings:**

```python
# Server URLs
QUERY_SERVER_URL: str = "http://localhost:8001"
TRANSACTIONAL_SERVER_URL: str = "http://localhost:8002"
EXTERNAL_API_SERVER_URL: str = "http://localhost:8003"

# Agent Host
AGENT_HOST_PORT: int = 8000

# OpenAI
OPENAI_API_KEY: str  # Required
OPENAI_MODEL: str = "gpt-4"
OPENAI_TIMEOUT: int = 30

# MCP Client
MCP_CLIENT_TIMEOUT: int = 30
MCP_CLIENT_MAX_RETRIES: int = 3
MCP_CLIENT_RETRY_DELAY: float = 1.0

# Logging
LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT: str = "console"  # console or json
```

### Logging Configuration

Structured logging is configured in `shared/logging_config.py`. Logs include:

- Request/response tracking
- Tool execution timing
- Error details with context
- Health check status

Example log output:
```
2024-01-15 10:30:45 [INFO] MCPClientManager: Adding MCP server
  server_name=query_server base_url=http://localhost:8001
```

---

## Testing

### Manual Testing

Use the provided test script:

```bash
python test_mcp_system.py
```

This runs comprehensive tests including:
- System status checks
- Tool discovery
- Query execution
- Error handling
- Health monitoring

### Unit Testing Routes

```python
# tests/test_your_routes.py
import pytest
from fastapi.testclient import TestClient
from servers.your_server.main import app

client = TestClient(app)

def test_get_items():
    response = client.get("/v1/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item():
    response = client.post(
        "/v1/items",
        json={"field1": "test", "field2": 123}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == "test"
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_end_to_end_query():
    async with httpx.AsyncClient() as client:
        # Test agent host query
        response = await client.post(
            "http://localhost:8000/query",
            json={"query": "Get all users"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "users" in result["response"].lower()
```

### Testing Tool Discovery

```python
@pytest.mark.asyncio
async def test_tool_discovery():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] > 0
        
        # Verify specific tools exist
        tool_names = [t["function"]["name"] for t in data["tools"]]
        assert "query_server_get_v1_users" in tool_names
```

---

## Deployment

### Production Checklist

- [ ] Set strong `OPENAI_API_KEY`
- [ ] Configure production URLs in `.env`
- [ ] Set `LOG_LEVEL=WARNING` or `LOG_FORMAT=json`
- [ ] Enable HTTPS for all endpoints
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backup and recovery
- [ ] Review security settings

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "agent_host/main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  agent_host:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - query_server
      - transactional_server
      - external_api_server
    
  query_server:
    build:
      context: .
      dockerfile: servers/query_server/Dockerfile
    ports:
      - "8001:8001"
    
  transactional_server:
    build:
      context: .
      dockerfile: servers/transactional_server/Dockerfile
    ports:
      - "8002:8002"
    
  external_api_server:
    build:
      context: .
      dockerfile: servers/external_api_server/Dockerfile
    ports:
      - "8003:8003"
```

Start with:
```bash
docker-compose up -d
```

### Kubernetes Deployment

Create deployments for each service with appropriate resource limits, health checks, and service discovery.

---

## Troubleshooting

### Common Issues

**Issue: "Tool not found" errors**

Check that:
1. Server is running and accessible
2. Tool name matches the auto-generated format
3. Server is registered in `orchestrator.py`
4. Run `GET /tools` to verify available tools

**Issue: Connection refused**

Verify:
1. All servers are running on correct ports
2. URLs in `.env` match running services
3. No firewall blocking ports
4. Check health endpoint: `curl http://localhost:8000/health`

**Issue: OpenAI API errors**

Verify:
1. `OPENAI_API_KEY` is set correctly
2. API key has sufficient quota
3. Using supported model (gpt-4, gpt-3.5-turbo)
4. Check OpenAI status page

**Issue: Timeout errors**

Increase timeouts in `.env`:
```env
OPENAI_TIMEOUT=60
MCP_CLIENT_TIMEOUT=60
```

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
```

This provides detailed information about:
- Tool discovery
- Parameter extraction
- HTTP requests/responses
- Error stack traces

### Health Checks

Check system health:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Check MCP server info:
```bash
curl http://localhost:8001/mcp
```

---

## Best Practices

### 1. Server Organization

- **Separation of Concerns**: Keep read-only, transactional, and external APIs separate
- **Single Responsibility**: Each server handles one domain
- **Clear Naming**: Use descriptive server and route names

### 2. Error Handling

Always handle errors gracefully:

```python
from fastapi import HTTPException
from shared.logging_config import get_logger

logger = get_logger(__name__)

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    try:
        # Your logic
        item = fetch_item(item_id)
        if not item:
            logger.warning("Item not found", item_id=item_id)
            raise HTTPException(404, "Item not found")
        return item
    except Exception as e:
        logger.error("Failed to fetch item", item_id=item_id, error=str(e))
        raise HTTPException(500, f"Internal error: {str(e)}")
```

### 3. Logging

Log important events with context:

```python
logger.info("Processing order", 
           user_id=user_id, 
           product_id=product_id,
           quantity=quantity)
```

### 4. Parameter Validation

Use Pydantic validators:

```python
from pydantic import BaseModel, Field, validator

class OrderRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=1000, description="Order quantity")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be positive')
        return v
```

### 5. Documentation

- Write clear docstrings for all routes
- Document expected parameters
- Include examples in docstrings
- Keep API documentation up to date

### 6. Security

- Never commit API keys
- Use environment variables for secrets
- Validate all input parameters
- Implement rate limiting for production
- Add authentication/authorization as needed

### 7. Performance

- Use async/await consistently
- Implement caching where appropriate
- Monitor response times
- Set appropriate timeouts
- Use connection pooling for databases

### 8. Testing

- Test each route independently
- Write integration tests for workflows
- Test error conditions
- Verify tool discovery
- Test with various parameter combinations

---

## Support and Resources

### Documentation

- FastAPI: https://fastapi.tiangolo.com
- OpenAI API: https://platform.openai.com/docs
- Pydantic: https://docs.pydantic.dev

### Getting Help

1. Check logs in debug mode
2. Verify health endpoints
3. Test routes directly before orchestration
4. Review this guide thoroughly

### Contributing

When adding features:
1. Follow existing patterns
2. Add appropriate logging
3. Write tests
4. Update documentation
5. Test end-to-end

---

## Appendix: Complete Example

Here's a complete example of adding a new "Notification Server":

**Directory structure:**
```
servers/notification_server/
├── __init__.py
├── main.py
├── routes.py
└── models.py
```

**models.py:**
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class SendNotificationRequest(BaseModel):
    recipient: str
    type: NotificationType
    message: str
    priority: int = 1

class Notification(BaseModel):
    id: int
    recipient: str
    type: NotificationType
    message: str
    status: str
    sent_at: datetime
```

**routes.py:**
```python
from fastapi import APIRouter, HTTPException
from .models import SendNotificationRequest, Notification, NotificationType
from datetime import datetime
from shared.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

NOTIFICATIONS = []
NOTIFICATION_COUNTER = 1

@router.post("/notifications", response_model=Notification)
async def send_notification(request: SendNotificationRequest):
    """
    Send a notification to a recipient via email, SMS, or push notification
    """
    global NOTIFICATION_COUNTER
    
    logger.info("Sending notification",
               recipient=request.recipient,
               type=request.type,
               priority=request.priority)
    
    notification = Notification(
        id=NOTIFICATION_COUNTER,
        recipient=request.recipient,
        type=request.type,
        message=request.message,
        status="sent",
        sent_at=datetime.now()
    )
    
    NOTIFICATIONS.append(notification)
    NOTIFICATION_COUNTER += 1
    
    logger.info("Notification sent successfully", notification_id=notification.id)
    return notification

@router.get("/notifications/{notification_id}", response_model=Notification)
async def get_notification(notification_id: int):
    """
    Get notification by ID
    """
    notification = next((n for n in NOTIFICATIONS if n.id == notification_id), None)
    if not notification:
        raise HTTPException(404, "Notification not found")
    return notification
```

**main.py:**
```python
from fastapi import FastAPI
from .routes import router
from shared.fastmcp import FastMCPServer
from shared.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Notification Server",
    description="Handles all notification operations",
    version="1.0.0"
)

app.include_router(router, prefix="/v1")

mcp_server = FastMCPServer(app, name="Notification Server", version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, log_config=None)
```

**Update orchestrator.py:**
```python
servers = {
    "query_server": settings.QUERY_SERVER_URL,
    "transactional_server": settings.TRANSACTIONAL_SERVER_URL,
    "external_api_server": settings.EXTERNAL_API_SERVER_URL,
    "notification_server": "http://localhost:8005"
}
```

**Test it:**
```bash
# Start server
python servers/notification_server/main.py

# Test directly
curl -X POST http://localhost:8005/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "type": "email",
    "message": "Hello from MCP!"
  }'

# Test through agent
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Send an email notification to user@example.com saying hello"
  }'
```

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** MCP Development Team