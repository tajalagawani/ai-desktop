# 🤖 ACP Agent - AI Context Protocol Manager

**ACP Agent** is a powerful desktop application for managing Docker MCP (Model Context Protocol) servers on your VPS. It provides a visual interface to discover, install, configure, and manage 30+ AI-powered containerized tools.

---

## 🎯 What is ACP Agent?

**ACP Agent** = **AI Context Protocol Agent** for the VPS
- **Main Agent**: The VPS running Docker MCP Gateway
- **Sub-Agents**: Individual MCP servers (GitHub, Playwright, Grafana, Stripe, etc.)
- **No multi-user**: Single VPS instance (same architecture as Service Manager)

---

## ✨ Features

### 📊 Dashboard
- **Real-time statistics**: Total, enabled, available servers
- **Gateway control**: Start/stop MCP Gateway on custom port
- **Quick actions**: Refresh, settings, configuration

### 🔍 MCP Server Management
- **Browse 30+ servers** organized by category:
  - Development & Git (GitHub, GitLab, Git)
  - Browser Automation (Playwright, Puppeteer, Firecrawl)
  - Search & Discovery (DuckDuckGo, Brave Search)
  - Cloud & Infrastructure (Docker Hub, AWS, Google Drive, Google Maps)
  - Monitoring (Grafana, Sentry, New Relic)
  - Databases (PostgreSQL, SQLite, Redis)
  - Communication (Slack, Discord)
  - Payment (Stripe)
  - AI & Utilities (Sequential Thinking, Memory, Time, Filesystem, Fetch)
  - Reference & Testing (Everything)

### ⚙️ Server Configuration
- **One-click enable/disable** for any MCP server
- **OAuth authorization** for GitHub, GitLab, Google, Slack, Stripe
- **Secret management** for API keys, tokens, credentials
- **Server details**: View tools, configuration, documentation
- **Search & filter**: Find servers by name, category, or description

### 🛠️ Server Details View
- **Tools list**: All available tools provided by the server
- **Configuration**: Docker image, type (local/remote), OAuth status
- **Secrets form**: Configure API keys and credentials
- **Documentation links**: Direct links to official docs

---

## 🚀 Getting Started

### Prerequisites

1. **Docker Desktop 4.42.0+** installed on your VPS
2. **Docker MCP Toolkit** enabled in Docker Desktop settings
3. **VPS running** the AI Desktop application

### Installation Steps

#### 1. Install Docker MCP Toolkit

```bash
# On your VPS
# Install Docker Desktop 4.42.0 or later
# Then enable MCP Toolkit:
# Docker Desktop → Settings → Beta features → Enable "Docker MCP Toolkit"
```

#### 2. Initialize MCP Catalog

```bash
docker mcp catalog init
```

#### 3. Launch ACP Agent

1. Open AI Desktop in your browser
2. Click **ACP Agent** in the dock
3. The app will check if Docker MCP is installed
4. Start using MCP servers!

---

## 📖 How to Use

### Enable an MCP Server

1. **Browse servers** in the main list view
2. **Click on a server** to view details
3. **Click "Enable"** button
4. Configure OAuth or secrets if required
5. Server is now available to AI agents!

### Configure OAuth (for GitHub, GitLab, etc.)

1. Select a server that requires OAuth (e.g., GitHub Official)
2. Click **"Authorize GitHub"** button
3. Complete OAuth flow in browser
4. Return to ACP Agent - server is authorized!

### Set API Keys/Secrets

1. Select a server that requires secrets (e.g., Stripe, Grafana)
2. Fill in the secrets form (API key, URL, etc.)
3. Click **"Save Secrets"**
4. Server can now access the configured services!

### Start MCP Gateway

The **MCP Gateway** is the aggregator that exposes all enabled servers to AI clients.

1. Go to left panel → **MCP Gateway** section
2. Set port (default: 8080)
3. Click **"Start Gateway"**
4. Gateway runs in background
5. Connect AI clients (Claude Desktop, VS Code, etc.) to `http://localhost:8080`

### Connect AI Clients

Once gateway is running, connect AI clients:

```bash
# Claude Desktop
docker mcp client connect claude-desktop --global

# VS Code
docker mcp client connect vscode
```

---

## 🔧 Available MCP Servers

### Development & Version Control
| Server | Description | OAuth |
|--------|-------------|-------|
| GitHub Official | Complete GitHub API integration | ✅ Yes |
| GitLab | GitLab operations & CI/CD | ✅ Yes |
| Git Local | Local Git repository operations | ❌ No |

### Browser Automation
| Server | Description | OAuth |
|--------|-------------|-------|
| Playwright | Browser automation & screenshots | ❌ No |
| Puppeteer | Headless Chrome control | ❌ No |
| Firecrawl | AI-powered web scraping | ❌ No (API key) |

### Search & Discovery
| Server | Description | OAuth |
|--------|-------------|-------|
| DuckDuckGo | Privacy-focused web search | ❌ No |
| Brave Search | Independent search engine | ❌ No (API key) |

### Cloud & Infrastructure
| Server | Description | OAuth |
|--------|-------------|-------|
| Docker Hub | Docker registry operations | ❌ No |
| AWS Knowledge Base | AWS Bedrock KB retrieval | ❌ No (AWS creds) |
| Google Drive | File operations | ✅ Yes |
| Google Maps | Geocoding, directions, places | ❌ No (API key) |

### Monitoring & Observability
| Server | Description | OAuth |
|--------|-------------|-------|
| Grafana | Dashboards & metrics | ❌ No (API key) |
| Sentry | Error tracking | ❌ No (API key) |
| New Relic | APM & observability | ❌ No (API key) |

### Databases
| Server | Description | OAuth |
|--------|-------------|-------|
| PostgreSQL | PostgreSQL operations | ❌ No (connection) |
| SQLite | SQLite database | ❌ No |
| Redis | Redis key-value store | ❌ No (connection) |

### Communication
| Server | Description | OAuth |
|--------|-------------|-------|
| Slack | Slack integration | ✅ Yes |
| Discord | Discord bot operations | ❌ No (bot token) |

### Payment & Commerce
| Server | Description | OAuth |
|--------|-------------|-------|
| Stripe | Payment processing | ❌ No (API key) |

### AI & Utilities
| Server | Description | OAuth |
|--------|-------------|-------|
| Sequential Thinking | Problem-solving AI | ❌ No |
| Memory | Knowledge graph persistence | ❌ No |
| Time | Time/timezone utilities | ❌ No |
| Filesystem | Secure file operations | ❌ No |
| Fetch | Web content fetching | ❌ No |

### Reference & Testing
| Server | Description | OAuth |
|--------|-------------|-------|
| Everything | Test server with all features | ❌ No |

---

## 🎨 UI Design

### Main Layout (2-Panel Design)

```
┌──────────────────────────────────────────────────────────────┐
│  ACP Agent - AI Context Protocol                             │
├────────────┬──────────────────────────────────────────────────┤
│            │                                                   │
│ Left Panel │              Right Panel                          │
│            │                                                   │
│ Stats:     │  Search: [Find MCP servers...]                   │
│  30 Total  │                                                   │
│  5 Enabled │  Categories: [All][Dev][Browser][Search]...      │
│  25 Avail  │                                                   │
│            │  ┌────────────────────────────────────┐          │
│ Gateway:   │  │ GitHub Official      ✅ Enabled    │          │
│  ● Running │  │ GitHub API integration             │          │
│  Port:8080 │  │ [⏸️ Disable] [⚙️ Config] [🔑 OAuth]│          │
│            │  └────────────────────────────────────┘          │
│ [🔄][⚙️]   │  [More servers...]                               │
└────────────┴──────────────────────────────────────────────────┘
```

### Server Detail View

```
┌──────────────────────────────────────────────────────────────┐
│  ← Back to MCP Servers                                        │
│                                                               │
│  🐙 GitHub Official                 ✅ Enabled  🌐 Remote    │
│  Development & Git                                            │
│                                                               │
│  [⏸️ Disable]                                                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  🔑 OAuth Authorization (github)                        │ │
│  │  [Authorize GitHub]                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Tabs: [🛠️ Tools] [⚙️ Configuration]                         │
│                                                               │
│  Tools (9):                                                   │
│  • create_repository - Create new GitHub repo                │
│  • create_issue - Create issue                               │
│  • create_pull_request - Create PR                           │
│  ... (6 more)                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Notes

### OAuth Flow
- OAuth tokens are managed by Docker MCP Toolkit
- Never stored in browser or application code
- Secure credential management via Docker secrets

### API Keys & Secrets
- Stored securely via `docker mcp secret set`
- Never exposed in logs or UI
- Encrypted at rest by Docker

### Gateway Security
- Runs locally on VPS (not exposed to internet)
- Use with trusted AI clients only
- CPU limited to 1 core, 2GB RAM max per server
- No default host filesystem access

---

## 🐛 Troubleshooting

### "Docker MCP CLI is not installed"

**Solution:**
1. Install Docker Desktop 4.42.0+
2. Open Docker Desktop → Settings → Beta features
3. Enable "Docker MCP Toolkit"
4. Restart Docker Desktop
5. Refresh ACP Agent

### "Failed to enable server"

**Possible causes:**
- Docker daemon not running
- Insufficient permissions
- Image not found in registry

**Solution:**
```bash
# Check Docker daemon
docker ps

# Pull image manually
docker pull mcp/github-official:latest

# Try enabling again in ACP Agent
```

### "OAuth authorization failed"

**Solution:**
1. Ensure you're logged into the OAuth provider (GitHub, GitLab, etc.)
2. Check browser for OAuth popup (may be blocked)
3. Complete OAuth flow in browser
4. Return to ACP Agent

### Gateway won't start

**Solution:**
```bash
# Check if port is already in use
lsof -i :8080

# Kill existing process
pkill -f "docker mcp gateway"

# Try different port in ACP Agent
# Or start manually:
docker mcp gateway run --port 8081
```

---

## 📚 CLI Commands Reference

### Server Management
```bash
# List enabled servers
docker mcp server ls

# Enable server
docker mcp server enable github-official

# Disable server
docker mcp server disable github-official

# Get server details
docker mcp server inspect github-official

# Reset (disable all)
docker mcp server reset
```

### Gateway Control
```bash
# Start gateway (stdio)
docker mcp gateway run

# Start gateway (streaming on port)
docker mcp gateway run --port 8080

# Start with verbose logging
docker mcp gateway run --verbose

# Stop gateway
pkill -f "docker mcp gateway"
```

### Secrets Management
```bash
# Set secret
docker mcp secret set grafana.api_key=glsa_xxx

# List secrets
docker mcp secret list

# Delete secret
docker mcp secret delete grafana.api_key
```

### OAuth
```bash
# Authorize GitHub
docker mcp oauth authorize github

# Authorize GitLab
docker mcp oauth authorize gitlab
```

### Configuration
```bash
# Read config
docker mcp config read

# Reset to defaults
docker mcp config reset

# View catalog
docker mcp catalog show docker-mcp
```

### Client Connection
```bash
# Connect Claude Desktop
docker mcp client connect claude-desktop --global

# Connect VS Code
docker mcp client connect vscode
```

---

## 🚀 Use Cases

### 1. GitHub Automation
**Enabled servers:** GitHub Official

**Example workflow:**
- AI agent creates repository
- Creates initial commit
- Opens pull request
- Reviews code changes

### 2. Web Scraping & Analysis
**Enabled servers:** Playwright, Firecrawl, DuckDuckGo

**Example workflow:**
- Search web for information
- Navigate to target sites
- Scrape content
- Extract structured data

### 3. Infrastructure Monitoring
**Enabled servers:** Grafana, New Relic, Docker Hub

**Example workflow:**
- Query Grafana dashboards
- Analyze metrics
- Search Docker images
- Monitor application health

### 4. Database Operations
**Enabled servers:** PostgreSQL, Redis

**Example workflow:**
- Execute SQL queries
- Manage data
- Cache operations
- Database migrations

### 5. Payment Processing
**Enabled servers:** Stripe

**Example workflow:**
- Create customers
- Process payments
- Manage subscriptions
- Handle refunds

---

## 📦 Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ACP Agent (UI)                        │
│  Next.js React Component with 2-panel layout            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
            ┌────────────────────┐
            │  /api/mcp (API)    │
            │  Next.js Route     │
            └────────┬───────────┘
                     │
                     ↓
         ┌───────────────────────┐
         │  Docker MCP CLI       │
         │  (docker mcp ...)     │
         └───────────┬───────────┘
                     │
                     ↓
    ┌────────────────────────────────────────┐
    │      Docker MCP Gateway                │
    │  Aggregates all enabled MCP servers    │
    │  Port: 8080 (configurable)             │
    └────────────────┬───────────────────────┘
                     │
                     ↓
    ┌─────────────────────────────────────────────┐
    │         MCP Servers (Containers)            │
    │  - mcp/github-official:latest               │
    │  - mcp/playwright:latest                    │
    │  - mcp/grafana:latest                       │
    │  - mcp/stripe:latest                        │
    │  - ... (30+ more servers)                   │
    └─────────────────────────────────────────────┘
```

---

## 🎯 Future Enhancements

- [ ] WebSocket support for real-time server logs
- [ ] Server health monitoring
- [ ] Custom MCP server installation (user-provided images)
- [ ] Server groups & batch operations
- [ ] Export/import server configurations
- [ ] Integration with workflow automation
- [ ] AI agent playground (test MCP tools directly)
- [ ] Server usage analytics

---

## 📄 License

Same as AI Desktop - MIT License

---

## 🤝 Contributing

MCP servers are community-driven! Submit new servers to:
- **Docker MCP Registry**: https://github.com/docker/mcp-registry
- **MCP Official Servers**: https://github.com/modelcontextprotocol/servers

---

## 🔗 Links

- **Docker MCP Docs**: https://docs.docker.com/ai/mcp-catalog-and-toolkit/
- **MCP Protocol**: https://modelcontextprotocol.io
- **AI Desktop**: http://92.112.181.127

---

**Ready to supercharge your VPS with AI Context Protocol! 🚀**
