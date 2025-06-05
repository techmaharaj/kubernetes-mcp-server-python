#!/usr/bin/env python3
"""
MCP Kubernetes Server - Simple Demo Version

This server exposes Kubernetes operations as MCP tools that Claude can use.
Perfect for demonstrating remote MCP capabilities in homelab setups.
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Import MCP SDK components
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

# Import our modules
from mcp_config import HOST, PORT, SERVER_NAME
from k8s_tools import (
    get_pods_info, 
    create_simple_pod, 
    delete_pod_by_name, 
    get_cluster_status,
    run_kubectl
)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage application startup and shutdown."""
    print(f"🚀 {SERVER_NAME} starting up...")
    
    # Test kubectl connectivity
    result = await run_kubectl(["version", "--client"])
    if result["success"]:
        print("✅ kubectl connectivity verified")
    else:
        print(f"⚠️ kubectl warning: {result['error']}")
    
    try:
        yield {"status": "ready"}
    finally:
        print(f"🔒 {SERVER_NAME} shutting down...")


# Create the MCP server
mcp = FastMCP(SERVER_NAME, lifespan=app_lifespan)


# === MCP TOOLS ===

@mcp.tool()
async def get_pods(namespace: str = "default") -> str:
    """Get all pods in a Kubernetes namespace with their status."""
    return await get_pods_info(namespace)


@mcp.tool()
async def create_pod(name: str, image: str, namespace: str = "default") -> str:
    """Create a simple Kubernetes pod with the specified name and container image."""
    return await create_simple_pod(name, image, namespace)


@mcp.tool()
async def delete_pod(name: str, namespace: str = "default") -> str:
    """Delete a Kubernetes pod by name."""
    return await delete_pod_by_name(name, namespace)


@mcp.tool()
async def get_cluster_info() -> str:
    """Get general Kubernetes cluster information and node status."""
    return await get_cluster_status()


# === MCP RESOURCES ===

@mcp.resource("cluster://status")
def cluster_status() -> str:
    """Current cluster status as a resource."""
    return "Use the get_cluster_info tool for live cluster status information."


# === WEB SERVER SETUP ===

# Create ASGI application with SSE mount
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)


if __name__ == "__main__":
    print(f"🚀 MCP Kubernetes Server")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print(f"📡 SSE Endpoint: http://{HOST}:{PORT}/sse")
    print(f"📋 Tools: get_pods, create_pod, delete_pod, get_cluster_info")
    print(f"📚 Resource: cluster://status")
    print()
    print("For remote access:")
    print("1. Start ngrok: ngrok http 8080")
    print("2. Use ngrok HTTPS URL + /sse in Claude Web")
    print()
    
    uvicorn.run(app, host=HOST, port=PORT)