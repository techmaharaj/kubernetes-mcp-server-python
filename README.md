# 🚀 MCP Kubernetes Server

A simple MCP (Model Context Protocol) server that lets Claude control your Kubernetes cluster remotely. This was used at the KCD Bangalore 2025 talk - [Let's Understand MCP: The USB Type-C Plug For Your AI Apps](https://kcd-blr-2025.sessionize.com/session/882097). Here's the [presentation deck](https://www.canva.com/design/DAGpjWJbsL0/Dwq0tnU6ea1oDXu5YBiv-Q/view?utm_content=DAGpjWJbsL0&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h30aac90f2c) that I used for the talk.

This is a very simple implementation of the MCP Python SDK to show how to create a MCP server and configure that on the Claude web app as a remote MCP.

## ✨ Features

- **get_pods** - List all pods in any namespace with status details
- **create_pod** - Create simple pods for demonstrations
- **delete_pod** - Clean up demo pods
- **get_cluster_info** - Show cluster and node status information

## 📋 Prerequisites

### System Requirements
- **Python 3.9+** installed
- **kubectl** installed and configured
- **Access to a Kubernetes cluster** (k3s, k8s, etc.)
- **Network access** to your cluster from the server

### For Remote Access (Claude Web)
- **ngrok account** (free tier works fine)
- **Claude Pro subscription** (for remote MCP feature)

## 🚀 Installation & Setup

### 1. Clone/Download the Project

```bash
# Create project directory
mkdir mcp-k8s-server
cd mcp-k8s-server

# Copy all the files (main.py, k8s_tools.py, mcp_config.py, requirements.txt)
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python3 -m venv mcp-env

# Activate virtual environment
source mcp-env/bin/activate  # On macOS/Linux
# or
mcp-env\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Kubernetes Access
```bash
# Test kubectl connectivity
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

* If kubectl isn't configured, you'll need to:
 - Copy kubeconfig from your cluster
 - Set KUBECONFIG environment variable

### 🖥️ Running the Server
Local Development

```bash
# Start the MCP server
python main.py
You should see output like:
🚀 MCP Kubernetes Server
🌐 Server: http://0.0.0.0:8080
📡 SSE Endpoint: http://0.0.0.0:8080/sse
📋 Tools: get_pods, create_pod, delete_pod, get_cluster_info
📚 Resource: cluster://status
```

For remote access:
1. Start ngrok: ngrok http 8080 --host-header="localhost:8080"
2. Use ngrok HTTPS URL + /sse in Claude Web

Test Local Connectivity
```bash
# In another terminal, test the server
curl http://localhost:8080/sse
# Should return SSE connection info
```

### 🌐 Remote Access Setup (For Claude Web)
#### 1. Install and Setup ngrok
```bash
# Install ngrok (if not already installed)
# Visit: https://ngrok.com/download

# Sign up for free account at https://ngrok.com
# Get your auth token from dashboard

# Configure ngrok
ngrok config add-authtoken YOUR_AUTH_TOKEN
```
#### 2. Create Public Tunnel
```bash
# In a new terminal (keep server running)
ngrok http 8080 --host-header="localhost:8080"
```
You'll see output like:
```bash
ngrok                                                               

Session Status               online
Account                      your-email@example.com
Version                      3.x.x
Region                       United States (us)
Latency                      45ms
Web Interface                http://127.0.0.1:4040
Forwarding                   https://abc123.ngrok-free.app -> http://localhost:8080

Connections                  ttl     opn     rt1     rt5     p50     p90
                             0       0       0.00    0.00    0.00    0.00
```
**Important**: Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)

**Note**: The `--host-header="localhost:8080"` flag is required for MCP SDK versions >= 1.20 to pass host validation.

#### 3. Test Remote Access
```bash
# Test the public endpoint
curl https://abc123.ngrok-free.app/sse
```

### 🔧 Claude Web Configuration

#### 1. Access Claude Web Settings

- Navigate to claude.ai
- Click on your profile and navigate to "Settings" -> "Integrations"

#### 2. Add Your MCP Server

- Click "Add Server" or "Add Integration"
- Server Name: Homelab K8s (or any name you prefer)
- Server URL: https://your-ngrok-url.ngrok-free.app/sse
- Click "Save" or "Add"

![Setting up remote MCP on Claude web](</images/claude-integration.png>)

_Note: It might give a connection/authentication error since we have not configured any authentication._

## 🎯 Usage

- Start a new chat
- Click the "Search & Tools" button and you'll find the integration that you just added

![Setting up remote MCP on Claude web](</images/claude-list-tools.png>)

- Click on the "Homelab k8s" tool that you just added, it will list all the tools it supports

- Ask it to "list all pods" and you should see that Claude uses the Homelab k8s MCP tool, which is running on our homelab system, and executes the respective `kubectl` command and returns the response. 

![Setting up remote MCP on Claude web](</images/claude-chat.png>)
