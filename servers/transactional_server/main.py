from fastapi import FastAPI
from .routes import router
from shared.fastmcp import FastMCPServer
from shared.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Transactional Server",
    description="State-changing operations",
    version="1.0.0"
)

app.include_router(router, prefix="/v1")

mcp_server = FastMCPServer(app, name="Transactional Server", version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_config=None)