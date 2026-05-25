import os

import uvicorn
from fastapi import FastAPI

from .fastmcp_tools import mcp


mcp_app = mcp.http_app(path="/mcp", stateless_http=True)
app = FastAPI(
    title="Madad FastMCP Server",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)


@app.get("/health")
async def health():
    return {"status": "healthy", "server": "madad-fastmcp"}


app.mount("/", mcp_app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8003")), log_config=None)
