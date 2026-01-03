from fastapi import FastAPI
from .routes import router
from shared.fastmcp import FastMCPServer
from shared.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="Query Server", 
    description="Read-only data endpoints with static content",
    version="1.0.0"
)

# Include routes
app.include_router(router, prefix="/v1")

# Initialize FastMCP
mcp_server = FastMCPServer(app, name="Query Server", version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_config=None)