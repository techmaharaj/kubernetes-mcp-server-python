"""Kubernetes operations for MCP tools."""

import asyncio
import json
import subprocess
import tempfile
import os
from typing import Dict, Any, List

from mcp_config import DEFAULT_NAMESPACE, KUBECTL_TIMEOUT


async def run_kubectl(cmd: List[str]) -> Dict[str, Any]:
    """Execute kubectl command and return result."""
    try:
        full_cmd = ["kubectl"] + cmd
        print(f"🔧 Running: {' '.join(full_cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), 
            timeout=KUBECTL_TIMEOUT
        )
        
        if process.returncode == 0:
            output = stdout.decode().strip()
            try:
                return {"success": True, "data": json.loads(output)}
            except json.JSONDecodeError:
                return {"success": True, "data": output}
        else:
            return {"success": False, "error": stderr.decode().strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_pods_info(namespace: str = DEFAULT_NAMESPACE) -> str:
    """Get formatted pod information."""
    result = await run_kubectl(["get", "pods", "-n", namespace, "-o", "json"])
    
    if not result["success"]:
        return f"❌ Error: {result['error']}"
    
    pods_data = result["data"]
    if not pods_data.get("items"):
        return f"No pods found in namespace '{namespace}'"
    
    # Format pod information
    pods = []
    for pod in pods_data["items"]:
        name = pod["metadata"]["name"]
        status = pod["status"]["phase"]
        
        # Get ready status
        ready = "Unknown"
        if "containerStatuses" in pod["status"]:
            containers = pod["status"]["containerStatuses"]
            ready_count = sum(1 for c in containers if c.get("ready", False))
            total_count = len(containers)
            ready = f"{ready_count}/{total_count}"
        
        # Get restart count
        restarts = 0
        if "containerStatuses" in pod["status"]:
            restarts = sum(c.get("restartCount", 0) for c in pod["status"]["containerStatuses"])
        
        pods.append(f"• {name}: {status} (Ready: {ready}, Restarts: {restarts})")
    
    return f"📋 Pods in namespace '{namespace}':\n" + "\n".join(pods)


async def create_simple_pod(name: str, image: str, namespace: str = DEFAULT_NAMESPACE) -> str:
    """Create a simple Kubernetes pod."""
    # Create pod manifest
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {"created-by": "mcp-server", "demo": "true"}
        },
        "spec": {
            "containers": [{
                "name": name,
                "image": image,
                "ports": [{"containerPort": 80}] if "nginx" in image.lower() else []
            }],
            "restartPolicy": "Never"
        }
    }
    
    # Write to temp file and apply
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest, f, indent=2)
        temp_file = f.name
    
    try:
        result = await run_kubectl(["apply", "-f", temp_file])
        if result["success"]:
            return f"✅ Pod '{name}' created successfully in namespace '{namespace}' with image '{image}'"
        else:
            return f"❌ Failed to create pod: {result['error']}"
    finally:
        os.unlink(temp_file)


async def delete_pod_by_name(name: str, namespace: str = DEFAULT_NAMESPACE) -> str:
    """Delete a Kubernetes pod."""
    result = await run_kubectl(["delete", "pod", name, "-n", namespace])
    
    if result["success"]:
        return f"✅ Pod '{name}' deleted successfully from namespace '{namespace}'"
    else:
        return f"❌ Failed to delete pod: {result['error']}"


async def get_cluster_status() -> str:
    """Get Kubernetes cluster information."""
    # Get cluster info
    cluster_result = await run_kubectl(["cluster-info"])
    if not cluster_result["success"]:
        return f"❌ Error getting cluster info: {cluster_result['error']}"
    
    # Get nodes
    nodes_result = await run_kubectl(["get", "nodes", "-o", "json"])
    
    info_lines = [
        "🏗️ Kubernetes Cluster Information:",
        "",
        cluster_result["data"],
        ""
    ]
    
    if nodes_result["success"] and nodes_result["data"].get("items"):
        info_lines.append("📊 Node Status:")
        for node in nodes_result["data"]["items"]:
            node_name = node["metadata"]["name"]
            conditions = node["status"]["conditions"]
            is_ready = any(
                condition["type"] == "Ready" and condition["status"] == "True"
                for condition in conditions
            )
            status = "Ready" if is_ready else "NotReady"
            info_lines.append(f"• {node_name}: {status}")
    else:
        info_lines.append("❌ Could not retrieve node information")
    
    return "\n".join(info_lines)