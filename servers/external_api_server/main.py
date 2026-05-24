from fastapi import FastAPI
from .routes import router
from shared.fastmcp import FastMCPServer
from shared.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="External API Server",
    description="Wrapped external services",
    version="1.0.0"
)

app.include_router(router, prefix="/v1")

mcp_server = FastMCPServer(app, name="External API Server", version="1.0.0")

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8003")), log_config=None)
