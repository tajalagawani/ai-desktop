# ACT Docker - Production-Ready Workflow Automation Platform

**ACT (Automated Coordination & Tasks)** is a powerful, production-ready workflow automation platform that runs multiple workflows simultaneously in Docker containers, each on its own port.

## 🌟 Key Features

- ✅ **Multi-Flow Architecture** - Run unlimited workflows simultaneously
- ✅ **Auto-Discovery** - Automatically finds and deploys all `.flow` files
- ✅ **Auto-Port Assignment** - Flows without ports get auto-assigned (9000+)
- ✅ **Dynamic Port Management** - Each workflow runs on its own port (no hardcoding)
- ✅ **Two Execution Modes** - Agent mode (HTTP routes) & MiniACT mode (workflow execution)
- ✅ **Hot Reload** - Detects flow file changes (manual restart to apply)
- ✅ **Production Ready** - Health checks, logging, error recovery, validation
- ✅ **Zero Configuration** - Just add `.flow` files and run `./startup.sh`
- ✅ **Independent Containers** - Each workflow isolated in its own Docker container
- ✅ **REST API** - Full API for monitoring, execution, and management
- ✅ **Management API** - Centralized control panel for all flows (Port 8000)

## 📁 Project Structure

```
act-docker/
├── flows/                          # 🎯 Put all your .flow files here
│   ├── restaurant.flow            # Port 3225 - Restaurant Management API
│   ├── restaurant2.flow           # Port 8081 - Restaurant v2
│   └── risk.flow                  # Port 8088 - Risk Management
│
├── act/                            # ACT Framework Core
│   ├── production_runner.py       # Main entry point (supports all modes)
│   ├── agent_server.py            # HTTP server with API endpoints
│   ├── execution_manager.py       # Workflow execution engine
│   ├── miniact_executor.py        # MiniACT mode executor
│   ├── flow_watcher.py            # Hot reload file watcher
│   ├── actfile_parser.py          # Flow file parser
│   ├── workflow_engine.py         # Workflow execution logic
│   ├── node_context.py            # Node execution context
│   └── nodes/                     # 100+ pre-built integration nodes
│       ├── OpenaiNode.py          # OpenAI/Claude integration
│       ├── PostgreSQLNode.py      # Database operations
│       ├── SlackNode.py           # Slack notifications
│       ├── GitHubNode.py          # GitHub operations
│       └── ...                    # 100+ more nodes
│
├── startup.sh                      # 🚀 Main startup script
├── flow_discovery.py              # Flow discovery & validation
├── docker-compose-generator.py    # Auto-generates docker-compose.yml
├── docker-compose.yml             # Auto-generated (don't edit)
├── Makefile                       # Auto-generated shortcuts
├── status.sh                      # Auto-generated health checker
├── Dockerfile                     # Production Docker image
└── requirements.txt               # Python dependencies

```

## 🚀 Quick Start (30 Seconds)

### 1. Add Your Flow Files

```bash
# Place your .flow files in the flows/ directory
cp my-workflow.flow flows/

# Each flow MUST have a port defined:
# [deployment]
# port = 3225
```

### 2. Start Everything

```bash
./startup.sh
```

**That's it!** The system will:
1. ✅ Scan `flows/` directory
2. ✅ Validate all flows (port conflicts, syntax)
3. ✅ Generate `docker-compose.yml` automatically
4. ✅ Build Docker images
5. ✅ Start all containers
6. ✅ Display access points

### 3. Access Your Workflows

```bash
# Check status
./status.sh

# View logs
docker-compose logs -f

# Access APIs
curl http://localhost:3225/health
curl http://localhost:8081/api/info
curl http://localhost:8088/api/status
```

## 📊 Execution Modes

ACT automatically detects the mode based on your flow file content:

### 🌐 Agent Mode (HTTP Server with Routes)

**Triggered when:** Flow contains ACI nodes or route definitions

**Features:**
- HTTP server with custom API routes
- RESTful endpoints defined in flow file
- Real-time request/response handling
- Database integrations, external APIs, etc.

**Example Access:**
```bash
# Custom routes
curl http://localhost:3225/aci/orders
curl http://localhost:3225/aci/customers

# System endpoints
GET  /health              # Health check
GET  /api/info            # Flow information
GET  /api/status          # Current status
GET  /api/nodes           # All loaded nodes
GET  /api/routes          # All available routes
POST /reload              # Force reload flow file
```

### ⚡ MiniACT Mode (Workflow Execution)

**Triggered when:** Flow has NO routes (workflow only)

**Features:**
- Execute workflow from start node
- Manual trigger via API
- Execute entire workflow or single nodes
- Auto-execute on load (optional)

**Example Access:**
```bash
# Execute entire workflow
curl -X POST http://localhost:3226/execute \
  -H "Content-Type: application/json" \
  -d '{"input": "data"}'

# Execute specific node
curl -X POST http://localhost:3226/execute/node/process_data \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}'

# System endpoints
GET  /health              # Health check
GET  /api/info            # Flow information
GET  /api/status          # Current status
POST /reload              # Force reload
```

### 🔄 WAITING Mode (Empty Flow)

**Triggered when:** No flow file or empty flow file

**Features:**
- Server starts on port 9999 (default)
- Minimal health endpoints
- Watches for flow file creation
- Auto-detects when flow is added

**Example:**
```bash
# Server running but waiting
curl http://localhost:9999/health
# Response: {"status": "waiting", "message": "No flow file loaded"}

# Add flow file and restart
cp myflow.flow flows/
./startup.sh --build
```

## 🛠️ Management Commands

### Using Makefile (Auto-generated)

```bash
# Start all flows
make start

# Stop all flows
make stop

# Restart all flows
make restart

# View logs from all flows
make logs

# Check status
make status

# Rebuild everything
make rebuild

# Clean up (stop and remove)
make clean

# Individual flow commands
make start-restaurant
make stop-restaurant
make restart-restaurant
make logs-restaurant
```

### Using Docker Compose Directly

```bash
# Start all flows
docker-compose up -d

# Start with rebuild
docker-compose up --build -d

# Stop all
docker-compose stop

# Stop specific flow
docker-compose stop act-restaurant

# Restart specific flow
docker-compose restart act-restaurant

# View logs
docker-compose logs -f act-restaurant

# Remove everything
docker-compose down -v
```

### Using Startup Script

```bash
# Normal start (use existing images)
./startup.sh

# Rebuild from scratch
./startup.sh --build

# The script will:
# 1. Discover all .flow files
# 2. Validate (ports, syntax)
# 3. Generate docker-compose.yml
# 4. Generate Makefile
# 5. Generate status.sh
# 6. Start containers
```

## 📝 Flow File Format

Each `.flow` file uses INI-style format:

```ini
[workflow]
start_node = start

[deployment]
port = 3225
environment = production

[agent]
agent_name = My API Server
description = My awesome API

[node:start]
type = start_node
next = process

[node:process]
type = openai_node
prompt = "Process this data"
model = "gpt-4"
next = respond

[node:respond]
type = aci_node
route = /api/process
method = POST
response = {{ process.output }}

[edges]
start -> process
process -> respond
```

### Required Sections

1. **[workflow]** - Defines workflow structure
   - `start_node` - Entry point node ID

2. **[deployment]** - Port configuration (REQUIRED)
   - `port` - Unique port number (1024-65535)
   - `environment` - production/development

3. **[agent]** - Agent metadata (optional)
   - `agent_name` - Display name
   - `description` - Agent description

4. **[node:*]** - Node definitions
   - `type` - Node type (see 100+ available nodes)
   - Node-specific parameters
   - `next` - Next node ID

5. **[edges]** - Workflow connections
   - Format: `node_id -> next_node_id`

## 🔌 Available Nodes (100+)

### AI & LLM
- `OpenaiNode` - GPT-4, ChatGPT, embeddings
- `ClaudeNode` - Anthropic Claude
- `HuggingFaceNode` - HuggingFace models
- `RAGNode` - Retrieval-augmented generation
- `EmbeddingSimilarityNode` - Vector similarity
- `FunctionCallingNode` - LLM function calling

### Databases
- `PostgreSQLNode` - PostgreSQL operations
- `MongoDBNode` - MongoDB operations
- `RedisNode` - Redis cache/queue
- `DynamodbNode` - AWS DynamoDB
- `SnowflakeNode` - Snowflake data warehouse
- `Neo4jNode` - Graph database
- `PineconeNode` - Vector database
- `VectorDatabaseNode` - Generic vector DB

### Cloud & Infrastructure
- `AwsNode` - AWS operations (S3, Lambda, etc.)
- `AzureNode` - Microsoft Azure
- `GoogleCloudNode` - Google Cloud Platform
- `KubernetesNode` - K8s orchestration
- `DockerNode` - Docker operations
- `TerraformNode` - Infrastructure as code

### APIs & Integrations
- `GitHubNode` - GitHub API
- `SlackNode` - Slack messaging
- `DiscordNode` - Discord bot
- `TeamsNode` - Microsoft Teams
- `TelegramNode` - Telegram bot
- `TwilioNode` - SMS/Voice
- `EmailNode` - Email sending
- `RequestNode` - Generic HTTP requests

### Business & CRM
- `SalesforceNode` - Salesforce CRM
- `HubSpotNode` - HubSpot CRM
- `IntercomNode` - Customer messaging
- `ZendeskNode` - Support tickets
- `NotionNode` - Notion workspace
- `AsanaNode` - Project management
- `JiraNode` - Issue tracking
- `ClickUpNode` - Task management

### E-commerce & Payments
- `ShopifyNode` - E-commerce platform
- `StripeNode` - Payment processing
- `PayPalNode` - PayPal payments
- `SquareNode` - Square payments
- `WiseNode` - Money transfers

### Data & Analytics
- `GoogleAnalyticsNode` - Analytics data
- `PowerBINode` - Business intelligence
- `TableauNode` - Data visualization
- `DatadogNode` - Monitoring & metrics
- `GoogleSheetsNode` - Spreadsheets
- `AirtableNode` - Database/spreadsheet hybrid

### Utilities
- `CodeNode` - Execute Python code
- `CommandNode` - Run shell commands
- `IfNode` - Conditional branching
- `LoopNode` - Iteration
- `SwitchNode` - Multi-way branching
- `FilterNode` - Data filtering
- `AggregateNode` - Data aggregation
- `StringOperationsNode` - String manipulation
- `NumberOperationsNode` - Math operations
- `DateTimeNode` - Date/time operations
- `ValidationNode` - Data validation
- `SanitizationNode` - Data sanitization
- `HashNode` - Hashing/encryption
- `UUIDNode` - UUID generation
- `RandomNode` - Random data generation

### File & Storage
- `S3Node` - AWS S3 storage
- `DropboxNode` - Dropbox storage
- `BoxNode` - Box storage
- `OneDriveNode` - Microsoft OneDrive
- `GoogleDriveNode` - Google Drive
- `FileConvertNode` - File conversion

### Specialized
- `OpenCVNode` - Computer vision
- `PointCloudNode` - 3D data processing
- `QRCodeNode` - QR code generation
- `ContentModerationNode` - Content filtering
- `TokenCountingNode` - Token counting
- `RateLimiterNode` - Rate limiting
- `BatchProcessorNode` - Batch processing

[See full node list in `act/nodes/` directory]

## 🔍 Flow Discovery & Validation

### Discover Flows

```bash
# Scan flows directory
python3 flow_discovery.py

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 Discovered 3 flow(s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 🌐 restaurant
#    Port: 3225
#    Mode: agent
#    Agent: Restaurant Management API
#    File: restaurant.flow
#
# ⚡ restaurant2
#    Port: 8081
#    Mode: agent
#    Agent: Restaurant v2 API
#    File: restaurant2.flow
```

### Validation Rules

The system automatically validates:
- ✅ Each flow has a unique port
- ✅ No duplicate flow names
- ✅ Ports are in valid range (1-65535)
- ✅ Flow syntax is valid
- ⚠️  Warns if ports < 1024 (privileged)
- ❌ Errors on port conflicts

### Generate Config Only (No Start)

```bash
# Just generate docker-compose.yml, Makefile, status.sh
python3 docker-compose-generator.py

# Custom flows directory
python3 docker-compose-generator.py /path/to/flows
```

## 📡 API Reference

All flows expose these endpoints:

### Health & Status

```bash
GET /health
# Response: {"status": "healthy", "mode": "agent", "port": 3225}

GET /api/info
# Response: {
#   "name": "Restaurant Management API",
#   "mode": "agent",
#   "port": 3225,
#   "environment": "production",
#   "uptime": 3600
# }

GET /api/status
# Response: {
#   "status": "running",
#   "mode": "agent",
#   "flow_loaded": true,
#   "nodes_count": 45,
#   "routes_count": 12
# }

GET /api/nodes
# Response: [
#   {"id": "start", "type": "start_node"},
#   {"id": "auth", "type": "aci_node", "route": "/auth"}
# ]

GET /api/routes  # Agent mode only
# Response: [
#   {"path": "/api/orders", "method": "POST", "node": "create_order"},
#   {"path": "/api/customers", "method": "GET", "node": "get_customers"}
# ]
```

### Execution (MiniACT Mode)

```bash
POST /execute
Content-Type: application/json
{
  "input": {"key": "value"}
}
# Response: {
#   "execution_id": 123,
#   "status": "success",
#   "duration_seconds": 2.5,
#   "result": {...}
# }

POST /execute/node/{node_id}
Content-Type: application/json
{
  "input": {"param": "value"}
}
# Response: {
#   "node_id": "process_data",
#   "status": "success",
#   "output": {...}
# }
```

### Management

```bash
POST /reload
# Force reload flow file (hot reload)
# Response: {"status": "reloaded", "changes_detected": true}
```

## 🔥 Hot Reload

Each flow has a built-in file watcher that detects changes:

### How It Works
1. File watcher monitors flow file for changes
2. Detects modifications (compares content & timestamp)
3. **Logs notification** (does NOT auto-restart)
4. **You manually restart** when ready

### Trigger Reload

```bash
# Option 1: Restart specific flow
docker-compose restart act-restaurant

# Option 2: Restart all flows
./startup.sh --build

# Option 3: Use API endpoint
curl -X POST http://localhost:3225/reload
```

### What Gets Reloaded
- ✅ Node configurations
- ✅ Route definitions
- ✅ Workflow structure
- ✅ Port changes (requires rebuild)
- ✅ Agent metadata

## 🔐 Port Management

### Port Priority (Highest to Lowest)
1. **Environment Variable** - `ACT_PORT=3225`
2. **Flow File** - `port = 3225` in `[deployment]` section
3. **Default** - `9999` (when no port found)

### Port Assignment Rules
- Each flow needs a unique port
- Recommended range: **3000-9999**
- Avoid: 80, 443, 8080 (common conflicts)
- System validates port conflicts automatically

### Current Port Assignments
```
restaurant   → 3225
restaurant2  → 8081
risk         → 8088
```

## 🐛 Troubleshooting

### "Port already in use"

```bash
# Find what's using the port
lsof -i :3225

# Kill the process
kill -9 <PID>

# Or change port in flow file and restart
./startup.sh --build
```

### "No valid flows found"

```bash
# Check flows directory
ls flows/

# Verify flow syntax
python3 flow_discovery.py

# Common issues:
# - Flow file missing [deployment] section
# - No port defined
# - Invalid INI format
```

### "Container keeps restarting"

```bash
# Check logs
docker-compose logs act-restaurant

# Common causes:
# - Invalid flow syntax
# - Missing node dependencies
# - Port conflicts
# - Python errors in custom nodes
```

### "Hot reload not working"

```bash
# Hot reload DETECTS but doesn't auto-restart (by design)

# After changing flow:
docker-compose restart act-restaurant

# Or rebuild:
./startup.sh --build
```

### "Import errors for nodes"

```bash
# Check requirements.txt has all dependencies
pip install -r requirements.txt

# Rebuild Docker image
docker-compose build --no-cache
./startup.sh --build
```

## 🚀 Production Deployment

### VPS Setup

```bash
# 1. Clone repository
git clone <repo> /opt/act-docker
cd /opt/act-docker

# 2. Add flow files
mkdir flows
# Upload your .flow files to flows/

# 3. Start
./startup.sh --build

# 4. Check status
./status.sh
```

### Environment Variables

Create `.env` file (optional):
```bash
# Port override (optional, flow file takes precedence)
ACT_PORT=3225

# API keys (use in flows)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Systemd Service (Auto-start on boot)

```bash
# Create /etc/systemd/system/act-multi-flow.service
[Unit]
Description=ACT Multi-Flow Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/act-docker
ExecStart=/opt/act-docker/startup.sh
ExecStop=/usr/local/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable act-multi-flow
sudo systemctl start act-multi-flow
sudo systemctl status act-multi-flow
```

### Nginx Reverse Proxy (Optional)

```nginx
# /etc/nginx/sites-available/act

# Restaurant API
server {
    listen 80;
    server_name restaurant.example.com;

    location / {
        proxy_pass http://localhost:3225;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Restaurant v2 API
server {
    listen 80;
    server_name restaurant2.example.com;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable
sudo ln -s /etc/nginx/sites-available/act /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Monitoring

```bash
# Real-time logs
docker-compose logs -f

# Container stats
docker stats

# Health check all flows
./status.sh

# Individual health
curl http://localhost:3225/health
curl http://localhost:8081/health
curl http://localhost:8088/health
```

### Backup & Recovery

```bash
# Backup flows
tar -czf flows-backup-$(date +%Y%m%d).tar.gz flows/

# Backup generated configs
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml Makefile status.sh

# Restore
tar -xzf flows-backup-20250105.tar.gz
./startup.sh --build
```

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      VPS / Server                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              Docker Network                     │    │
│  │              (act-network)                      │    │
│  │                                                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │   Container │  │   Container │  │Container│ │    │
│  │  │   act-rest. │  │   act-rest2 │  │act-risk │ │    │
│  │  │   Port 3225 │  │   Port 8081 │  │Port 8088│ │    │
│  │  │             │  │             │  │         │ │    │
│  │  │  ┌────────┐ │  │  ┌────────┐ │  │┌──────┐ │ │    │
│  │  │  │ Agent  │ │  │  │ Agent  │ │  ││MiniACT││ │    │
│  │  │  │ Server │ │  │  │ Server │ │  ││Exec.  ││ │    │
│  │  │  └────────┘ │  │  └────────┘ │  │└──────┘ │ │    │
│  │  │  ┌────────┐ │  │  ┌────────┐ │  │┌──────┐ │ │    │
│  │  │  │ Exec.  │ │  │  │ Exec.  │ │  ││Exec.  ││ │    │
│  │  │  │Manager │ │  │  │Manager │ │  ││Manager││ │    │
│  │  │  └────────┘ │  │  └────────┘ │  │└──────┘ │ │    │
│  │  │  ┌────────┐ │  │  ┌────────┐ │  │┌──────┐ │ │    │
│  │  │  │  Flow  │ │  │  │  Flow  │ │  ││ Flow  ││ │    │
│  │  │  │Watcher │ │  │  │Watcher │ │  ││Watcher││ │    │
│  │  │  └────────┘ │  │  └────────┘ │  │└──────┘ │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  │                                                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │           Volume Mounts                         │    │
│  │  • ./act → /app/act (shared code)              │    │
│  │  • ./flows/restaurant.flow → /app/flow         │    │
│  │  • ./flows/restaurant2.flow → /app/flow        │    │
│  │  • ./flows/risk.flow → /app/flow               │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

External Access:
→ http://server-ip:3225  (Restaurant API)
→ http://server-ip:8081  (Restaurant v2 API)
→ http://server-ip:8088  (Risk Management)
```

## 🎛️ Management API

ACT includes a **centralized Management API** running on port 8000 to control all flows from a UI or scripts.

### Start Management API

```bash
python3 flow_manager_api.py
```

Or add to docker-compose (see below).

### Management Endpoints

#### Flow Management
```bash
# List all flows
GET http://localhost:8000/api/flows

# Get specific flow
GET http://localhost:8000/api/flows/{name}

# Get flow status
GET http://localhost:8000/api/flows/{name}/status

# Restart flow
POST http://localhost:8000/api/flows/{name}/restart

# Stop flow
POST http://localhost:8000/api/flows/{name}/stop

# Start flow
POST http://localhost:8000/api/flows/{name}/start

# Get flow logs
GET http://localhost:8000/api/flows/{name}/logs?lines=100

# Check flow health
GET http://localhost:8000/api/flows/{name}/health

# Reload all flows
POST http://localhost:8000/api/flows/reload-all
```

#### System Management
```bash
# System statistics
GET http://localhost:8000/api/system/stats

# Rebuild all flows
POST http://localhost:8000/api/system/rebuild

# Health check
GET http://localhost:8000/health
```

### Example: List All Flows

```bash
curl http://localhost:8000/api/flows | jq .
```

**Response:**
```json
{
  "total": 4,
  "flows": [
    {
      "name": "math",
      "port": 9000,
      "mode": "miniact",
      "auto_assigned": true,
      "container": {
        "running": true,
        "status": "running"
      },
      "health": {
        "status": "healthy",
        "port": 9000
      }
    },
    {
      "name": "restaurant",
      "port": 5544,
      "mode": "agent",
      "container": {
        "running": true,
        "status": "running"
      },
      "health": {
        "status": "healthy",
        "port": 5544
      }
    }
  ]
}
```

### Example: Restart Flow

```bash
curl -X POST http://localhost:8000/api/flows/restaurant/restart
```

**Response:**
```json
{
  "success": true,
  "message": "Flow 'restaurant' restarted successfully"
}
```

### Example: System Stats

```bash
curl http://localhost:8000/api/system/stats | jq .
```

**Response:**
```json
{
  "flows": {
    "total": 4,
    "running": 4,
    "healthy": 4,
    "stopped": 0
  },
  "system": {
    "flows_directory": "./flows",
    "docker_compose": "docker-compose.yml"
  }
}
```

## 🧪 Development Workflow

### Adding a New Flow

```bash
# 1. Create flow file
nano flows/my-new-flow.flow

# 2. Define port in flow
[deployment]
port = 3300

# 3. Add nodes and routes
[node:start]
type = start_node
...

# 4. Start (auto-discovers)
./startup.sh --build

# 5. Test
curl http://localhost:3300/health
```

### Modifying Existing Flow

```bash
# 1. Edit flow file
nano flows/restaurant.flow

# 2. Restart container
docker-compose restart act-restaurant

# 3. Verify
curl http://localhost:3225/api/info
```

### Creating Custom Nodes

```python
# act/nodes/MyCustomNode.py
from act.nodes.base_node import BaseNode, NodeSchema, NodeParameter
from pydantic import Field

class MyCustomNodeSchema(NodeSchema):
    node_type: str = Field("my_custom_node", const=True)

    class Parameters:
        input_text: str = NodeParameter(
            name="input_text",
            type="string",
            description="Text to process"
        )

class MyCustomNode(BaseNode):
    def execute(self, context):
        params = self.node_def.get('parameters', {})
        text = params.get('input_text', '')

        # Your logic here
        result = text.upper()

        return {"output": result}
```

Register in `act/nodes/__init__.py`:
```python
from .MyCustomNode import MyCustomNode
```

Use in flow:
```ini
[node:custom]
type = my_custom_node
input_text = "hello world"
next = respond
```

## 📚 Common Use Cases

### 1. REST API Backend (Agent Mode)

```ini
[deployment]
port = 3000

[node:create_user]
type = aci_node
route = /api/users
method = POST
next = save_to_db

[node:save_to_db]
type = postgresql_node
query = INSERT INTO users ...
```

### 2. Data Processing Pipeline (MiniACT Mode)

```ini
[deployment]
port = 3001

[node:start]
type = start_node
next = fetch_data

[node:fetch_data]
type = request_node
url = https://api.example.com/data
next = process

[node:process]
type = openai_node
prompt = "Analyze this data"
next = save_results

[node:save_results]
type = s3_node
bucket = my-results
```

### 3. Webhook Processor (Agent Mode)

```ini
[deployment]
port = 3002

[node:webhook]
type = aci_node
route = /webhook/stripe
method = POST
next = validate

[node:validate]
type = validation_node
schema = {...}
next = notify_slack

[node:notify_slack]
type = slack_node
channel = #payments
message = "Payment received"
```

### 4. Scheduled Job (MiniACT + External Trigger)

```ini
[deployment]
port = 3003

[workflow]
auto_execute = true  # Run on load

[node:start]
type = start_node
next = fetch_daily_data

[node:fetch_daily_data]
type = google_sheets_node
spreadsheet = "Daily Reports"
next = analyze

[node:analyze]
type = claude_node
prompt = "Summarize this data"
next = email_report

[node:email_report]
type = email_node
to = admin@company.com
```

## 🔑 Environment Variables Reference

```bash
# Port Configuration
ACT_PORT=3225                    # Override port (optional)

# API Keys
OPENAI_API_KEY=sk-...           # OpenAI
ANTHROPIC_API_KEY=sk-ant-...    # Claude
HUGGINGFACE_API_KEY=hf_...      # HuggingFace

# Databases
DATABASE_URL=postgresql://...    # PostgreSQL
MONGODB_URI=mongodb://...        # MongoDB
REDIS_URL=redis://...           # Redis

# Cloud Providers
AWS_ACCESS_KEY_ID=...           # AWS
AWS_SECRET_ACCESS_KEY=...
AZURE_CREDENTIALS=...           # Azure
GOOGLE_APPLICATION_CREDENTIALS=...  # GCP

# Integrations
SLACK_BOT_TOKEN=xoxb-...        # Slack
GITHUB_TOKEN=ghp_...            # GitHub
STRIPE_SECRET_KEY=sk_...        # Stripe
TWILIO_AUTH_TOKEN=...           # Twilio

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
PYTHONUNBUFFERED=1             # Force unbuffered output
```

## 📖 Additional Documentation

- `README_MULTI_FLOW.md` - Detailed multi-flow guide
- `act/FLOW_CREATION_GUIDE.md` - Flow creation tutorial
- `act/nodes/CreateNewNodeInstructions.md` - Custom node development
- `act/nodes/NODE_CONVERSION_PROGRESS.md` - Node conversion status

## 🤝 Support & Contributing

### Getting Help
- Check logs: `docker-compose logs -f`
- Validate flows: `python3 flow_discovery.py`
- Check status: `./status.sh`
- Review this README

### Common Commands Cheat Sheet

```bash
# Discovery & Validation
python3 flow_discovery.py              # List all flows
python3 docker-compose-generator.py    # Generate configs

# Startup
./startup.sh                           # Start all
./startup.sh --build                   # Rebuild & start

# Management
make start                             # Start all
make stop                              # Stop all
make restart                           # Restart all
make logs                              # View logs
make status                            # Check status
make rebuild                           # Rebuild all
make clean                             # Remove all

# Individual Flows
make start-restaurant                  # Start one
make logs-restaurant                   # Logs for one
docker-compose restart act-restaurant  # Restart one

# Monitoring
./status.sh                           # Health check all
docker-compose ps                     # Container status
docker stats                          # Resource usage

# Debugging
docker-compose logs -f act-restaurant  # Live logs
docker exec -it act-restaurant bash    # Shell into container
curl http://localhost:3225/health      # API test
```

## 📄 License

[Your License Here]

---

**ACT Docker - Production-Ready Workflow Automation Platform**
*Build, deploy, and scale workflow automation in minutes*

🚀 Get started: `./startup.sh`
📊 Check status: `./status.sh`
📚 Learn more: See documentation above
