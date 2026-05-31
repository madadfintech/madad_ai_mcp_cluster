from fastmcp import FastMCP


mcp = FastMCP("Madad MCP Cluster")

from . import auth, communications, invoices, kyc, mcp_agent, offers, payments  # noqa: E402,F401


__all__ = ["mcp"]
