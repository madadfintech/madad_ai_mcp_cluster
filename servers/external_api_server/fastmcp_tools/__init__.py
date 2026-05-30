from fastmcp import FastMCP


mcp = FastMCP("Madad MCP Cluster")

from . import auth, communications, kyc, mcp_agent, offers  # noqa: E402,F401


__all__ = ["mcp"]
