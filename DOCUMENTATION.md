# AI Desktop - Complete Technical Documentation

> **Web-based AI Desktop Environment** - A comprehensive workflow automation and service management platform built with Next.js, featuring a macOS/Windows-style desktop interface, ACT workflow automation, and VPS service management.

**Version:** 1.0.0
**Last Updated:** 2025-10-16
**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS 4, Docker, Python ACT Framework

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Features](#core-features)
6. [Desktop Environment](#desktop-environment)
7. [Applications & Components](#applications--components)
8. [API Routes](#api-routes)
9. [ACT Workflow System](#act-workflow-system)
10. [Service Management](#service-management)
11. [Configuration & Setup](#configuration--setup)
12. [Development Guide](#development-guide)
13. [Deployment](#deployment)
14. [Security Considerations](#security-considerations)
15. [Future Roadmap](#future-roadmap)

---

## Project Overview

**AI Desktop** is a browser-based desktop environment that combines:

- **Desktop UI** - macOS-style window management system
- **Workflow Automation** - ACT Docker framework for API workflows
- **Service Management** - Docker-based VPS service installation/management
- **Terminal Integration** - Real-time WebSocket-based terminal
- **Action Builder** - AI-powered workflow creation using Claude AI
- **System Monitoring** - Real-time CPU, memory, network stats

### Key Value Propositions

1. **All-in-One Platform** - Manage workflows, services, and infrastructure from one interface
2. **No-Code Workflows** - Create API endpoints without writing boilerplate code
3. **Containerized Services** - Install databases, web servers in one click
4. **AI-Assisted** - Flow Architect agent helps build workflows
5. **Real-Time Monitoring** - Live logs, stats, and health checks

---

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Browser Client                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         React Desktop UI (Next.js 14)                 │   │
│  │  • Window Management  • Taskbar  • Dock  • Widgets  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────┴────────────────────────────────────┐
│                     Node.js Server (server.js)                │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Next.js App     │  │  WebSocket Server │                 │
│  │  • API Routes    │  │  • Terminal       │                 │
│  │  • SSR/ISR       │  │  • Logs Streaming │                 │
│  │  • File System   │  │  • Action Builder │                 │
│  └──────────────────┘  └──────────────────┘                 │
└──────────────────────┬──────────────────┬────────────────────┘
                       │                  │
         ┌─────────────┴────────┐  ┌─────┴────────────────┐
         │   Docker Engine      │  │  System Resources    │
         │  • ACT Containers    │  │  • systeminformation │
         │  • Service Containers│  │  • node-pty          │
         └──────────────────────┘  └──────────────────────┘
```

### Component Architecture

```
Frontend (React/Next.js)
    ↓
Desktop Manager (use-desktop.ts)
    ↓
┌─────────────┬──────────────┬─────────────────┐
│   Windows   │   Taskbar    │   Floating Dock  │
└─────────────┴──────────────┴─────────────────┘
    ↓
App Components
    ↓
API Routes (/app/api)
    ↓
┌──────────────┬────────────────┬─────────────────┐
│  File System │  Docker Engine │  System Stats    │
└──────────────┴────────────────┴─────────────────┘
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2.16 | React framework with SSR/API routes |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.1.9 | Utility-first styling |
| **Framer Motion** | latest | Animation library |
| **Radix UI** | latest | Accessible component primitives |
| **Lucide React** | 0.454.0 | Icon library |

### Backend & Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | - | Runtime environment |
| **node-pty** | 1.0.0 | Terminal emulation |
| **ws** | 8.18.3 | WebSocket server |
| **systeminformation** | 5.27.10 | System stats |
| **Docker** | - | Container runtime |
| **Python 3.11** | - | ACT framework runtime |
| **Flask** | - | ACT HTTP server |

### Key Libraries

- **clsx** + **tailwind-merge** - Conditional styling
- **zustand** - State management
- **react-hook-form** + **zod** - Form validation
- **recharts** - Data visualization
- **xterm.js** - Terminal UI
- **sonner** - Toast notifications
- **react-resizable-panels** - Resizable layouts

---

## Project Structure

```
ai-desktop/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes
│   │   ├── actions/              # Action Builder APIs
│   │   ├── changelog/            # Version management
│   │   ├── executions/           # Workflow execution
│   │   ├── files/                # File operations
│   │   ├── flows/                # ACT flow management
│   │   ├── flow-architect/       # Flow architect agent
│   │   ├── pm2-processes/        # Process management
│   │   ├── projects/             # Project management
│   │   ├── services/             # Docker service management
│   │   ├── system-logs/          # System logging
│   │   ├── system-stats/         # System monitoring
│   │   ├── terminal/             # Terminal WebSocket
│   │   ├── update/               # Auto-update system
│   │   └── workflows/            # Workflow CRUD
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Home page
│
├── components/                   # React Components
│   ├── apps/                     # Desktop Applications
│   │   ├── action-builder.tsx        # AI workflow builder
│   │   ├── app-store.tsx             # App marketplace
│   │   ├── changelog.tsx             # Version viewer
│   │   ├── chat-interface.tsx        # Chat UI
│   │   ├── claude-cli.tsx            # Claude CLI
│   │   ├── desktop-settings.tsx      # Settings panel
│   │   ├── file-manager.tsx          # File browser
│   │   ├── flow-manager.tsx          # ACT flow manager
│   │   ├── installed-apps.tsx        # App inventory
│   │   ├── mac-app-store.tsx         # App store UI
│   │   ├── service-details.tsx       # Service inspector
│   │   ├── service-manager.tsx       # Service control panel
│   │   ├── system-monitor.tsx        # System stats
│   │   ├── terminal.tsx              # Terminal emulator
│   │   └── workflow-canvas.tsx       # Visual workflow editor
│   │
│   ├── desktop/                  # Desktop Environment
│   │   ├── changelog-modal.tsx       # Update modal
│   │   ├── desktop-context-menu.tsx  # Right-click menu
│   │   ├── desktop-icon-context-menu.tsx
│   │   ├── desktop.tsx               # Main desktop manager
│   │   ├── floating-dock-demo.tsx    # macOS-style dock
│   │   ├── service-icon-context-menu.tsx
│   │   ├── system-control-menu.tsx   # Power menu
│   │   ├── taskbar.tsx               # Windows taskbar
│   │   ├── top-dock.tsx              # Top menubar
│   │   ├── widget.tsx                # Desktop widgets
│   │   └── window.tsx                # Window component
│   │
│   ├── auth/                     # Authentication
│   │   └── two-factor-auth.tsx       # 2FA (mock)
│   │
│   └── ui/                       # Shadcn UI Components
│       ├── accordion.tsx
│       ├── alert.tsx
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       └── ... (40+ components)
│
├── components/apps/act-docker/   # ACT Workflow System
│   ├── act/                      # Python ACT Framework
│   │   ├── agent_server.py           # HTTP server (Flask)
│   │   ├── execution_manager.py      # Workflow executor
│   │   ├── miniact_executor.py       # MiniACT mode
│   │   ├── actfile_parser.py         # TOML parser
│   │   ├── flow_watcher.py           # Hot reload
│   │   ├── node_context.py           # Execution context
│   │   └── nodes/                    # 100+ integration nodes
│   │       ├── OpenaiNode.py
│   │       ├── SlackNode.py
│   │       ├── GitHubNode.py
│   │       ├── PostgreSQLNode.py
│   │       └── ... (100+ nodes)
│   │
│   ├── flows/                    # Workflow Definitions
│   │   ├── math.flow                 # Example flow
│   │   ├── restaurant.flow           # ISS tracker API
│   │   ├── restaurant2.flow          # Demo flow
│   │   ├── risk.flow                 # Risk mgmt
│   │   └── test.flow                 # Weather API
│   │
│   ├── docker-compose.yml        # Auto-generated
│   ├── Dockerfile                # Container image
│   ├── startup.sh                # Launch script
│   └── requirements.txt          # Python deps
│
├── data/                         # Data & Configuration
│   ├── desktop-apps.ts               # App registry
│   ├── file-manager-data.ts          # Mock file data
│   ├── installable-services.ts       # Service catalog (35+ services)
│   └── installed-apps-data.ts        # App inventory
│
├── hooks/                        # Custom React Hooks
│   ├── use-desktop.ts                # Window management
│   ├── use-file-manager.ts           # File operations
│   └── use-toast.ts                  # Toast notifications
│
├── lib/                          # Utilities
│   ├── action-builder/               # Action builder utils
│   ├── claude/                       # Claude integration
│   ├── chat/                         # Chat storage
│   ├── flow-architect/               # Flow architect
│   ├── system-stats.ts               # System monitoring
│   └── utils.ts                      # Helpers
│
├── types/                        # TypeScript Types
│   ├── app.types.ts                  # App types
│   └── index.ts                      # Type exports
│
├── utils/                        # Utilities
│   ├── desktop-utils.ts              # Desktop helpers
│   └── icon-mapper.ts                # Icon registry
│
├── deployment/                   # Deployment Scripts
│   ├── auto-update.sh                # Auto-updater
│   ├── deploy.sh                     # Deployment
│   ├── ecosystem.config.js           # PM2 config
│   └── SETUP_AUTO_UPDATE.md          # Setup guide
│
├── flow-architect/               # Flow Architect Project
│   └── .mcp-server-claude-code/      # Agent config
│
├── server.js                     # Custom server (WebSocket + Next.js)
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
├── tailwind.config.ts            # Tailwind config
├── next.config.mjs               # Next.js config
└── version.json                  # Version tracking
```

---

## Core Features

### 1. Desktop Environment

**Window Management System**
- Draggable windows with collision detection
- 8-handle resizing (corners + edges)
- Min/Max/Close controls (macOS traffic lights)
- Z-index management (bring to front)
- Window constraints (stay on screen)
- Minimize to taskbar
- Multiple desktop backgrounds

**UI Components**
- **Floating Dock** - macOS-style application launcher (bottom)
- **Top Dock** - Menu bar with system controls (top)
- **Taskbar** - Windows-style task switcher (bottom)
- **Widgets** - CPU/Memory/Network monitors
- **Context Menus** - Right-click menus
- **System Control Menu** - Power/settings dropdown

### 2. Workflow Automation (ACT Framework)

**ACT Docker System**
- Multi-flow architecture (run unlimited workflows)
- Auto-discovery of `.flow` files
- Dynamic port assignment
- Two execution modes:
  - **Agent Mode** - HTTP API endpoints
  - **MiniACT Mode** - Workflow execution
- Hot reload support
- Health checks & monitoring
- 100+ pre-built integration nodes

**Flow Manager**
- Start/stop/restart flows
- View logs in real-time (WebSocket)
- Monitor container status
- Browse ACI routes
- Health status indicators
- Port management

### 3. Service Management

**Docker Service Installation**
- **35+ Pre-configured Services:**
  - **Databases:** MySQL, PostgreSQL, MongoDB, Redis, MariaDB, TimescaleDB, CouchDB, Neo4j, InfluxDB, Cassandra, ClickHouse, Elasticsearch, etc.
  - **Web Servers:** Nginx
  - **Tools:** PHPMyAdmin, Adminer
  - **Queues:** RabbitMQ
  - **Analytics:** Metabase, Grafana

**Service Features:**
- One-click installation
- Automatic port configuration (0.0.0.0 binding)
- Named volume creation for persistence
- UFW firewall integration
- Start/stop/restart/remove controls
- Real-time log streaming (WebSocket)
- Service inspector with details
- Resource monitoring

### 4. Action Builder

**AI-Powered Workflow Creation**
- Claude AI integration (Flow Architect agent)
- Natural language to workflow conversion
- Session management
- Real-time streaming output
- TOML workflow file generation
- Service catalog integration
- Node catalog awareness
- Project management

### 5. System Monitoring

**Real-Time Stats**
- CPU usage & temperature
- Memory usage (used/total/percentage)
- Disk usage
- Network stats (upload/download/ping)
- Process monitoring
- Live charts (Recharts)
- Auto-refresh

### 6. Terminal Integration

**Full Terminal Emulator**
- WebSocket-based PTY
- Real-time I/O
- Shell support (bash/zsh/etc)
- Resize support
- Multiple sessions
- xterm.js rendering
- ANSI color support

### 7. Version Management

**Auto-Update System**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Version tracking (`version.json`)
- GitHub integration
- Update detection
- One-click updates
- Changelog viewer
- Build timestamp tracking
- Commit SHA tracking

---

## Desktop Environment

### Window Component (`components/desktop/window.tsx`)

**Features:**
- Draggable from header
- 8 resize handles
- Min/Max/Close buttons
- Z-index management
- Snap to edges
- Remember position/size
- Framer Motion animations

**Props:**
```typescript
interface WindowProps {
  id: string
  title: string
  children: React.ReactNode
  onClose: () => void
  onMinimize: () => void
  onMaximize: () => void
  isActive: boolean
  isMinimized: boolean
  isMaximized: boolean
  zIndex: number
  initialPosition?: { x: number; y: number }
  initialSize?: { width: number; height: number }
}
```

### Desktop Manager (`components/desktop/desktop.tsx`)

**State Management:**
```typescript
interface WindowState {
  id: string
  title: string
  component: React.ReactNode
  isMinimized: boolean
  isMaximized: boolean
  zIndex: number
  position: { x: number; y: number }
  size: { width: number; height: number }
}
```

**Hooks:**
- `useDesktop()` - Window management
- `useMouseActivity()` - Mouse tracking
- `useTheme()` - Dark/light mode
- `useDockApps()` - Dock app management

### App Registry (`data/desktop-apps.ts`)

**App Configuration:**
```typescript
interface AppConfig {
  id: string                // Unique identifier
  name: string              // Display name
  icon: string              // Lucide icon name or image path
  iconType?: 'lucide' | 'image'
  category: string          // App category
  description?: string      // Description
  version?: string          // Version number
  isPinned?: boolean        // Pinned to dock
  isSystem?: boolean        // System app
}
```

**Window Configuration:**
```typescript
interface WindowConfig {
  defaultWidth: number      // Default width
  defaultHeight: number     // Default height
  minWidth: number          // Minimum width
  minHeight: number         // Minimum height
  resizable: boolean        // Can resize
  maximizable: boolean      // Can maximize
  minimizable: boolean      // Can minimize
  closable: boolean         // Can close
  openMaximized?: boolean   // Open maximized
}
```

---

## Applications & Components

### 1. Service Manager (`components/apps/service-manager.tsx`)

**Purpose:** Install and manage Docker services

**Features:**
- Service catalog with 35+ services
- Search and filter
- Category tabs (Database, Web Server, Tools, etc.)
- One-click installation
- Service control (start/stop/restart/remove)
- Real-time status
- Access URLs
- Default credentials display
- Opens service details in new window

**API Integration:**
- `GET /api/services` - List all services
- `POST /api/services` - Install/control services

### 2. Flow Manager (`components/apps/flow-manager.tsx`)

**Purpose:** Manage ACT workflow containers

**Features:**
- Flow discovery from filesystem
- Container status monitoring
- Health checks
- Start/stop/restart controls
- Real-time log streaming
- ACI route browsing
- Port information
- Mode indicators (agent/miniact)

**Tabs:**
- **Overview** - Status, ports, description
- **Logs** - Real-time container logs
- **ACI Routes** - HTTP endpoints (agent mode)

**API Integration:**
- `GET /api/flows` - List all flows
- `POST /api/flows` - Control flows (start/stop/restart/remove)

### 3. Action Builder (`components/apps/action-builder.tsx`)

**Purpose:** AI-powered workflow creation

**Features:**
- Claude AI integration (sonnet model)
- Chat interface
- Session management
- Real-time streaming
- TOML workflow generation
- Project selection
- Service catalog awareness
- File browser integration
- WebSocket communication

**Architecture:**
```
Action Builder Component
    ↓ WebSocket
Server (server.js)
    ↓ Child Process
Claude CLI (flow-architect agent)
    ↓ File System
flow-architect/ project
```

**API Integration:**
- `WebSocket ws://localhost:3000/api/action-builder/ws`
- `GET /api/actions` - List actions
- `GET /api/projects` - List projects
- `GET /api/flow-architect/catalogs/*` - Service/node catalogs

### 4. Terminal (`components/apps/terminal.tsx`)

**Purpose:** Full terminal emulator

**Features:**
- xterm.js based
- WebSocket PTY
- Real-time I/O
- Resize support
- Multiple tabs
- Theme support
- Copy/paste

**Architecture:**
```
Terminal Component (xterm.js)
    ↓ WebSocket
Server (node-pty)
    ↓ PTY
Shell Process (bash/zsh)
```

### 5. System Monitor (`components/apps/system-monitor.tsx`)

**Purpose:** Real-time system stats

**Features:**
- CPU usage & temperature
- Memory usage
- Disk usage
- Network stats
- Live charts
- Process list
- Auto-refresh (every 2s)

**API Integration:**
- `GET /api/system-stats` - Get system metrics

### 6. File Manager (`components/apps/file-manager.tsx`)

**Purpose:** Browse and manage files

**Features:**
- Tree view
- Breadcrumb navigation
- File/folder operations
- Search
- Multi-select
- Context menus
- File preview

**Note:** Currently uses mock data. API integration pending.

### 7. Changelog (`components/apps/changelog.tsx`)

**Purpose:** Version management and updates

**Features:**
- Current version display
- Build timestamp
- Commit SHA
- Update detection
- Changelog viewer (last 10 commits)
- One-click update
- Auto-reload after update

**API Integration:**
- `GET /api/changelog` - Get version info
- `POST /api/update` - Trigger update

---

## API Routes

### System & Monitoring

#### `GET /api/system-stats`
Get real-time system statistics

**Response:**
```typescript
{
  cpu: {
    usage: number       // % utilization
    temperature: number // Celsius
    cores: number
  }
  memory: {
    used: number       // GB
    total: number      // GB
    percentage: number // %
  }
  disk: {
    used: number       // GB
    total: number      // GB
    percentage: number // %
  }
  network: {
    download: number   // Mbps
    upload: number     // Mbps
    ping: number       // ms
  }
}
```

#### `GET /api/system-logs`
Retrieve system logs

#### `GET /api/pm2-processes`
List PM2 managed processes

### Services Management

#### `GET /api/services`
List all installable services and their status

**Response:**
```typescript
{
  dockerInstalled: boolean
  services: ServiceConfig[]  // 35+ services
}
```

**Service Status:**
- `not-installed` - Not installed
- `running` - Container running
- `exited` - Container stopped
- `created` - Container created but not started

#### `POST /api/services`
Install, start, stop, restart, or remove a service

**Request Body:**
```typescript
{
  action: 'install' | 'start' | 'stop' | 'restart' | 'remove'
  serviceId: string
}
```

**Actions:**
- `install` - Pull image, create container, open firewall
- `start` - Start stopped container
- `stop` - Stop running container
- `restart` - Restart container
- `remove` - Remove container + volumes + images + close firewall

**Features:**
- Automatic port binding (0.0.0.0)
- Named volume creation
- Environment variables
- UFW firewall integration
- Rate limiting for security
- Complete cleanup on remove

### Flows Management

#### `GET /api/flows`
List all ACT workflow flows and their status

**Query Parameters:**
- `flowName` - Get specific flow
- `action=logs` - Get flow logs
- `lines=100` - Number of log lines

**Response:**
```typescript
{
  success: boolean
  actInstalled: boolean
  total: number
  flows: FlowConfig[]
  timestamp: string
}
```

**FlowConfig:**
```typescript
{
  name: string                // Flow name
  port: number                // Port number
  mode: 'agent' | 'miniact'   // Execution mode
  agent_name?: string         // Agent name (if agent mode)
  description?: string        // Description
  file: string                // .flow filename
  auto_assigned?: boolean     // Port auto-assigned
  container: {
    running: boolean          // Container status
    status: string            // Docker status
    started_at?: string       // Start time
    pid?: number              // Process ID
    actualPort?: number       // Actual mapped port
  }
  health: {
    status: string            // healthy/unhealthy/stopped/timeout
    port?: number             // Health check port
  }
}
```

#### `POST /api/flows`
Control flow containers

**Request Body:**
```typescript
{
  action: 'start' | 'stop' | 'restart' | 'remove'
  flowName: string
}
```

**Features:**
- Auto-detection if container doesn't exist
- Automatic `up -d` fallback for non-existent containers
- Container verification after start
- 5-minute timeout for initial builds
- 30-second timeout for other operations

**Flow States:**
- `stopped` - Container not running
- `running` - Container active
- `not_found` - Container doesn't exist
- `error` - Container in error state

### Workflows (File-Based Storage)

#### `GET /api/workflows`
List all workflows

**Response:**
```typescript
{
  success: boolean
  workflows: WorkflowMetadata[]
  total: number
}
```

#### `POST /api/workflows`
Create new workflow

**Request Body:**
```typescript
{
  id: string
  title: string
  description?: string
}
```

**Creates:**
- `.act-workflows/{id}/metadata.json`
- `.act-workflows/{id}/workflow.toml`
- `.act-workflows/{id}/messages.json`

#### `GET /api/workflows/[id]`
Get workflow by ID

**Response:**
```typescript
{
  success: boolean
  workflow: {
    id: string
    title: string
    description?: string
    created: string
    updated: string
    toml: string            // TOML content
    messages: Message[]     // Chat messages
  }
}
```

#### `PATCH /api/workflows/[id]`
Update workflow

**Request Body:**
```typescript
{
  title?: string
  description?: string
  toml?: string
}
```

#### `DELETE /api/workflows/[id]`
Delete workflow

### Executions (Mock APIs)

#### `POST /api/executions/workflows`
Create workflow execution record

**Request Body:**
```typescript
{
  workflowId: string
  documentId?: string
  tomlContent: string
  version?: number
  metadata?: any
}
```

**Note:** Currently returns mock data. Real execution not implemented.

#### `POST /api/executions/nodes`
Create node execution record

**Request Body:**
```typescript
{
  nodeId: string
  workflowExecutionId: string
  input?: any
  result?: any
  status?: string
  error?: string
}
```

### Action Builder

#### `GET /api/actions`
List all saved actions

**Response:**
```typescript
{
  actions: Action[]
}
```

#### `GET /api/projects`
List all Flow Architect projects

**Response:**
```typescript
{
  projects: Project[]
}
```

#### `GET /api/flow-architect/catalogs/[filename]`
Get service or node catalog

**Filenames:**
- `services.json` - Available services
- `nodes.json` - Available node types

#### `GET /api/flow-architect/actions`
Get actions from Flow Architect project

### Version Management

#### `GET /api/changelog`
Get version information and check for updates

**Response:**
```typescript
{
  version: string           // Current version
  buildDate: string         // Build timestamp
  currentSHA: string        // Current commit
  latestSHA?: string        // Latest GitHub commit
  updateAvailable: boolean  // Update check result
  commits?: Commit[]        // Last 10 commits
}
```

#### `POST /api/update`
Trigger auto-update script

**Executes:**
```bash
./deployment/auto-update.sh
```

**Process:**
1. Git pull
2. npm install
3. npm run build
4. PM2 restart

### WebSocket Routes

#### `ws://localhost:3000/api/terminal/ws`
Terminal WebSocket for PTY sessions

**Messages:**
- `type: 'connected'` - Connection established
- `type: 'output'` - Terminal output
- `type: 'exit'` - Process exited

**Client Messages:**
- `type: 'input'` - Send input to terminal
- `type: 'resize'` - Resize terminal (cols, rows)

#### `ws://localhost:3000/api/services/logs/ws?container=<name>`
Stream Docker container logs

**Query Parameters:**
- `container` - Container name

**Messages:**
- `type: 'connected'` - Connection established
- `type: 'log'` - Log line
- `type: 'error'` - Error occurred
- `type: 'exit'` - Process exited

#### `ws://localhost:3000/api/action-builder/ws`
Action Builder Claude AI streaming

**Client Messages:**
- `type: 'start_chat'` - Start conversation
  ```typescript
  {
    type: 'start_chat'
    prompt: string
    sessionId?: string
    resume?: boolean
  }
  ```
- `type: 'stop_chat'` - Stop conversation

**Server Messages:**
- `type: 'connected'` - WebSocket connected
- `type: 'claude_output'` - Claude response chunk
- `type: 'complete'` - Conversation complete
- `type: 'error'` - Error occurred

---

## ACT Workflow System

### Overview

**ACT (Automated Coordination & Tasks)** is a Python-based workflow automation framework that runs inside Docker containers.

### Architecture

```
┌─────────────────────────────────────────────────┐
│         AI Desktop (Next.js Frontend)            │
│  Flow Manager UI → /api/flows → Docker Engine   │
└─────────────────────┬───────────────────────────┘
                      │
    ┌─────────────────┴──────────────────┐
    │                                     │
┌───▼─────────────┐            ┌─────────▼────────┐
│  act-restaurant │            │   act-test       │
│  Port: 5544     │            │   Port: 5524     │
│  Mode: Agent    │            │   Mode: Agent    │
└────────┬────────┘            └─────────┬────────┘
         │                               │
    ┌────▼─────────────────────────┬────▼────┐
    │  ACT Python Framework        │         │
    │  • agent_server.py (Flask)   │         │
    │  • execution_manager.py      │         │
    │  • actfile_parser.py         │         │
    │  • 100+ integration nodes    │         │
    └──────────────────────────────┴─────────┘
```

### Flow File Structure (TOML)

```toml
# =====================================================
# Example Flow - ISS Tracker API
# =====================================================
[workflow]
name = "Track ISS"
description = "API endpoint that fetches current ISS location"
start_node = DefineAPI

# =============================================
# Nodes
# =============================================

[node:FetchISSLocation]
type = py
label = "Fetch ISS coordinates"
code = """
import requests

def fetch_iss():
    response = requests.get('http://api.open-notify.org/iss-now.json')
    data = response.json()

    return {
        'latitude': float(data['iss_position']['latitude']),
        'longitude': float(data['iss_position']['longitude']),
        'timestamp': data['timestamp']
    }
"""
function = fetch_iss

[node:DefineAPI]
type = aci
label = "Define GET /api/iss endpoint"
mode = server
operation = add_route
route_path = /api/iss
methods = ["GET"]
handler = FetchISSLocation
description = "Get current ISS location"

# =============================================
# Edges (Execution Flow)
# =============================================
[edges]
DefineAPI = FetchISSLocation

# =============================================
# Configuration
# =============================================
[configuration]
agent_enabled = true
agent_name = "iss-tracker"
agent_version = "1.0.0"
host = "0.0.0.0"
port = 5566
debug = true
cors_enabled = true
```

### Execution Modes

#### 1. Agent Mode (HTTP API)

**When to use:** Create REST API endpoints

**Features:**
- HTTP server (Flask)
- Route definition with ACI nodes
- Request/response handling
- CORS support
- Health checks

**Detection:** Flow contains `type = aci` nodes

**Example Response:**
```json
{
  "aci_node_id_defining_route": "DefineAPI",
  "agent_name": "iss-tracker",
  "execution_outcome": "success",
  "message": "ACI Workflow for 'FetchISSLocation' processed.",
  "payload": {
    "execution_time": 0.33,
    "result": {
      "latitude": 2.8519,
      "longitude": -53.2189,
      "timestamp": 1760637615
    }
  },
  "route_handler_name": "FetchISSLocation",
  "workflow_execution_trace": null
}
```

#### 2. MiniACT Mode (Workflow)

**When to use:** Background automation, scheduled tasks

**Features:**
- Workflow execution
- Node chaining
- Conditional logic
- Loop support

**Detection:** Flow contains `[workflow]` section without ACI nodes

### Node Types

**ACT provides 100+ pre-built nodes:**

#### Integration Nodes
- **API:** HTTP, REST, GraphQL, WebSocket
- **Databases:** PostgreSQL, MySQL, MongoDB, Redis
- **Cloud:** AWS, Azure, GCP
- **Communication:** Slack, Discord, Email, SMS
- **CRM:** Salesforce, HubSpot, Pipedrive
- **Project Management:** Jira, Asana, ClickUp, Monday
- **File Storage:** S3, Dropbox, Box, OneDrive
- **Analytics:** Google Analytics, Mixpanel
- **Payment:** Stripe, PayPal, Coinbase
- **AI/ML:** OpenAI, Hugging Face

#### Utility Nodes
- **Data:** Transform, Filter, Aggregate, Batch
- **Control:** If, Loop, Branch
- **Python:** Custom code execution
- **Log:** Message logging

### Custom Python Nodes

```toml
[node:CustomNode]
type = py
label = "My Custom Node"
code = """
def my_function(param1, param2):
    # Your logic here
    result = param1 + param2
    return {
        'sum': result,
        'message': f'Sum is {result}'
    }
"""
function = my_function
param1 = 10
param2 = 20
```

### ACI Nodes (API Routes)

```toml
[node:DefineAPI]
type = aci
label = "Define API endpoint"
mode = server
operation = add_route
route_path = /api/my-endpoint
methods = ["GET", "POST"]
handler = MyHandlerNode
description = "My API endpoint description"
```

### Data Flow & References

**Access previous node output:**
```toml
[node:Node2]
type = log_message
message = "Result: {{Node1.result.value}}"
```

**Placeholders:**
- `{{NodeId.result.field}}` - Access node output
- `{{workflow.param}}` - Access workflow parameters
- `{{env.VAR}}` - Access environment variables

### Health Checks

All flows expose health endpoints:

```bash
curl http://localhost:5566/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_name": "iss-tracker",
  "mode": "agent",
  "routes": 1
}
```

### Flow Management

#### Add New Flow

1. Create `.flow` file in `components/apps/act-docker/flows/`
2. Add service to `docker-compose.yml`:
   ```yaml
   act-myflow:
     build: .
     container_name: act-myflow
     ports:
       - "8080:8080"
     environment:
       - ACT_PORT=8080
     volumes:
       - ./act:/app/act
       - ./flows/myflow.flow:/app/flow
     restart: unless-stopped
     networks:
       - act-network
   ```
3. Start container: `docker compose up -d act-myflow`
4. Flow appears in Flow Manager automatically

#### Update Flow

1. Edit `.flow` file
2. Restart container: `docker compose restart act-myflow`
3. Changes applied immediately

#### Remove Flow

1. Stop and remove container: `docker compose rm -sf act-myflow`
2. Remove service from `docker-compose.yml`
3. Optionally delete `.flow` file

### Troubleshooting

**Container not starting:**
```bash
# Check logs
docker compose logs act-myflow

# Common issues:
# - Port already in use
# - Syntax error in .flow file
# - Missing dependencies
```

**Flow not showing in UI:**
```bash
# Check if container is running
docker ps | grep act-

# Check API response
curl http://localhost:3000/api/flows
```

**Health check failing:**
```bash
# Test health endpoint
curl http://localhost:8080/health

# Check if port is correct in .flow file
# Check if container port matches docker-compose.yml
```

---

## Service Management

### Service Catalog

**35+ Pre-configured Services Available:**

| Category | Services |
|----------|----------|
| **SQL Databases** | MySQL 8.0, MySQL 5.7, MariaDB, PostgreSQL 17, TimescaleDB, MSSQL, CockroachDB |
| **NoSQL Databases** | MongoDB, Redis, KeyDB, CouchDB, ArangoDB, Neo4j, Cassandra, ScyllaDB |
| **Search Engines** | Elasticsearch |
| **Time Series** | InfluxDB, QuestDB, VictoriaMetrics |
| **Analytics** | ClickHouse, Metabase, Grafana |
| **Web Servers** | Nginx |
| **Database Tools** | PHPMyAdmin, Adminer |
| **Queues** | RabbitMQ |
| **Caching** | Memcached, Redis |

### Service Configuration

Each service is defined in `data/installable-services.ts`:

```typescript
{
  id: 'mysql',
  name: 'MySQL 8.0',
  category: 'database',
  icon: '/icons/services/mysql.svg',
  description: 'Popular open-source relational database',
  installMethod: 'docker',
  dockerImage: 'mysql:8.0',
  ports: [3306],
  volumes: ['/var/lib/mysql'],
  environment: {
    MYSQL_ROOT_PASSWORD: 'changeme'
  },
  windowComponent: 'MySQLManager',
  defaultWidth: 1200,
  defaultHeight: 700,
  defaultCredentials: {
    username: 'root',
    password: 'changeme',
    port: 3306
  }
}
```

### Installation Process

**API Flow:**
```
User clicks "Install"
    ↓
POST /api/services { action: 'install', serviceId: 'mysql' }
    ↓
1. Check Docker installed
2. Open firewall ports (UFW)
3. Build Docker run command:
   - Bind to 0.0.0.0 (all interfaces)
   - Create named volumes
   - Set environment variables
4. Execute: docker run -d --name ai-desktop-mysql ...
5. Verify container running
    ↓
Return success with access URL
```

### Firewall Integration

**UFW (Uncomplicated Firewall) Support:**

```typescript
// Priority: Try UFW profile first
await execAsync(`sudo ufw allow 'AI-Desktop-MySQL'`)

// Fallback: Raw port with rate limiting
await execAsync(`sudo ufw limit 3306/tcp comment 'AI Desktop - mysql'`)
```

**Security:**
- Rate limiting prevents brute force attacks
- Automatic cleanup on service removal
- Comments for tracking

### Volume Management

**Named Volumes for Persistence:**

```bash
# Volume naming: ai-desktop-{service}-{path}
ai-desktop-mysql-var-lib-mysql

# Benefits:
# - Data persists across container recreation
# - Easy backup/restore
# - Isolated per service
```

### Service Removal

**Complete Cleanup:**

```
User clicks "Remove"
    ↓
POST /api/services { action: 'remove', serviceId: 'mysql' }
    ↓
1. Stop and remove container
2. Remove all associated volumes
3. Remove Docker image (force)
4. Prune dangling images
5. Close firewall ports
    ↓
Return success
```

**Result:** Frees up disk space and closes security holes

### Service Details

**Inspector Window:**
- Container status
- Port mappings
- Volume mounts
- Environment variables
- Default credentials
- Access URLs
- Real-time logs

---

## Configuration & Setup

### Environment Variables

```env
# Next.js
PORT=3000
NODE_ENV=production

# Database (Future)
DATABASE_URL=postgresql://user:pass@localhost:5432/aidesktop

# Auth (Future)
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=https://your-domain.com

# Anthropic API (Action Builder)
ANTHROPIC_API_KEY=sk-ant-...

# OAuth (Future)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
```

### Version Configuration (`version.json`)

```json
{
  "version": "1.0.0",
  "buildDate": "2025-10-16T12:00:00Z",
  "currentSHA": "abc123def456",
  "environment": "production"
}
```

### Desktop Configuration

**Background Options:**
```typescript
const BACKGROUNDS = {
  'component-beams': { type: 'component' },
  'gradient-blue-purple': { type: 'gradient' },
  'gradient-emerald-cyan': { type: 'gradient' },
  'image-abstract': { type: 'image' },
  'image-waves': { type: 'image' },
  'image-mesh': { type: 'image' }
}
```

**Window Defaults:**
```typescript
const WINDOW_CONFIGS = {
  'service-manager': {
    defaultWidth: 1600,
    defaultHeight: 1000,
    minWidth: 1000,
    minHeight: 700,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true
  }
}
```

### ACT Docker Configuration

**Per-Flow Configuration:**
```toml
[configuration]
agent_enabled = true
agent_name = "my-flow"
agent_version = "1.0.0"
host = "0.0.0.0"
port = 8080
debug = true
cors_enabled = true
```

---

## Development Guide

### Getting Started

```bash
# Clone repository
git clone <repo-url>
cd ai-desktop

# Install dependencies
npm install

# Start development server
npm run dev

# Server runs on http://localhost:3000
```

### Development Server

The custom server (`server.js`) provides:
- Next.js app with hot reload
- WebSocket server for terminal/logs
- Action Builder integration
- Auto-initialization of Claude agents

```javascript
// server.js architecture
createServer()
  → Next.js handler
  → WebSocket upgrade
    → /api/terminal/ws (Terminal)
    → /api/services/logs/ws (Logs)
    → /api/action-builder/ws (Claude AI)
```

### Adding a New Desktop App

**1. Create Component**
```tsx
// components/apps/my-app.tsx
'use client'

export function MyApp() {
  return (
    <div className="h-full p-4">
      <h1>My App</h1>
      {/* Your app UI */}
    </div>
  )
}
```

**2. Register App**
```typescript
// data/desktop-apps.ts
export const DOCK_APPS: AppConfig[] = [
  // ... existing apps
  {
    id: 'my-app',
    name: 'My App',
    icon: 'AppWindow',
    category: 'utilities',
    description: 'My custom application'
  }
]

// Add window config
export const WINDOW_CONFIGS = {
  'my-app': {
    defaultWidth: 800,
    defaultHeight: 600,
    minWidth: 400,
    minHeight: 300,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true
  }
}
```

**3. Add to Component Map**
```typescript
// components/desktop/desktop.tsx
const getAppComponent = (id: string): React.ReactNode => {
  const componentMap = {
    // ... existing apps
    'my-app': <MyApp />
  }
  return componentMap[id] || null
}
```

**4. Add Icon (if custom)**
```typescript
// utils/icon-mapper.ts
import { AppWindow, /* other icons */ } from 'lucide-react'

export const iconRegistry = {
  // ... existing icons
  AppWindow
}
```

### Adding a New Icon

**1. Check Lucide React**
Visit: https://lucide.dev/icons

**2. Add to Registry**
```typescript
// utils/icon-mapper.ts
import { YourIcon } from 'lucide-react'

export const iconRegistry = {
  // ... existing
  YourIcon
}
```

**3. Use in Components**
```typescript
const IconComponent = getIcon('YourIcon')
return <IconComponent className="h-4 w-4" />
```

### Adding an API Route

**1. Create Route File**
```typescript
// app/api/my-route/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Your logic
    return NextResponse.json({ success: true, data: {} })
  } catch (error: any) {
    console.error('Error:', error)
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    // Your logic
    return NextResponse.json({ success: true })
  } catch (error: any) {
    console.error('Error:', error)
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}
```

**2. Use in Frontend**
```typescript
const response = await fetch('/api/my-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: 'value' })
})
const result = await response.json()
```

### Adding a New Service

**1. Add to Service Registry**
```typescript
// data/installable-services.ts
export const INSTALLABLE_SERVICES: ServiceConfig[] = [
  // ... existing services
  {
    id: 'myservice',
    name: 'My Service',
    category: 'database',
    icon: '/icons/services/myservice.svg',
    description: 'My custom service',
    installMethod: 'docker',
    dockerImage: 'myservice:latest',
    ports: [8080],
    volumes: ['/data'],
    environment: {
      MY_VAR: 'value'
    },
    windowComponent: 'MyServiceManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'admin',
      password: 'admin',
      port: 8080
    }
  }
]
```

**2. Add UFW Profile (Optional)**
```typescript
// app/api/services/route.ts
const UFW_PROFILES: Record<string, string> = {
  // ... existing
  'myservice': 'AI-Desktop-MyService'
}
```

**3. Add Service Icon**
Place icon at: `public/icons/services/myservice.svg`

### Creating an ACT Flow

**1. Create Flow File**
```toml
# components/apps/act-docker/flows/myflow.flow
[workflow]
name = "My Flow"
description = "My custom workflow"
start_node = DefineAPI

[node:MyNode]
type = py
code = """
def my_function():
    return {'message': 'Hello from my flow!'}
"""
function = my_function

[node:DefineAPI]
type = aci
mode = server
operation = add_route
route_path = /api/myendpoint
methods = ["GET"]
handler = MyNode

[edges]
DefineAPI = MyNode

[configuration]
agent_enabled = true
agent_name = "myflow"
port = 9000
```

**2. Add Docker Compose Service**
```yaml
# components/apps/act-docker/docker-compose.yml
  act-myflow:
    build: .
    container_name: act-myflow
    ports:
      - "9000:9000"
    environment:
      - ACT_PORT=9000
    volumes:
      - ./act:/app/act
      - ./flows/myflow.flow:/app/flow
    restart: unless-stopped
    networks:
      - act-network
```

**3. Start Container**
```bash
cd components/apps/act-docker
docker compose up -d act-myflow
```

**4. Test Endpoint**
```bash
curl http://localhost:9000/api/myendpoint
```

### Testing

**Manual Testing Checklist:**
- [ ] Window drag/resize on all screen sizes
- [ ] Desktop context menus
- [ ] Service installation/removal
- [ ] Flow start/stop/restart
- [ ] Terminal functionality
- [ ] WebSocket connections
- [ ] System stats updates
- [ ] Theme switching
- [ ] Log streaming

**Browser Support:**
- Chrome/Edge (Recommended)
- Firefox
- Safari (macOS)

---

## Deployment

### Local Development

```bash
npm run dev
```

Runs on `http://localhost:3000`

### Production Build

```bash
# Build Next.js app
npm run build

# Start production server
npm run start
```

### VPS Deployment

**Prerequisites:**
- Ubuntu 20.04+ / Debian 11+
- Node.js 18+
- Docker
- PM2 (process manager)
- Nginx (reverse proxy)

**1. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install PM2
sudo npm install -g pm2
```

**2. Clone and Build**
```bash
# Clone repository
git clone <repo-url> /var/www/ai-desktop
cd /var/www/ai-desktop

# Install dependencies
npm install

# Build
npm run build
```

**3. Configure PM2**
```javascript
// deployment/ecosystem.config.js
module.exports = {
  apps: [{
    name: 'ai-desktop',
    script: 'server.js',
    instances: 1,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
```

```bash
# Start with PM2
pm2 start deployment/ecosystem.config.js

# Enable startup
pm2 startup
pm2 save
```

**4. Configure Nginx**
```nginx
# /etc/nginx/sites-available/ai-desktop
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /api/terminal/ws {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**5. SSL Certificate**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

**6. Firewall**
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Auto-Update System

**Setup:**
```bash
# Make script executable
chmod +x deployment/auto-update.sh

# Add to crontab (every 5 minutes)
crontab -e
```

Add line:
```bash
*/5 * * * * /var/www/ai-desktop/deployment/auto-update.sh
```

**How it works:**
1. Polls GitHub every 5 minutes
2. Compares local SHA with remote
3. If different:
   - `git pull`
   - `npm install`
   - `npm run build`
   - `pm2 restart ai-desktop`
4. Logs to `logs/auto-update.log`

**Manual Update:**
```bash
# In UI: Power Menu → Recent Updates → Update Now
# Or via API:
curl -X POST http://localhost:3000/api/update
```

### Monitoring

**PM2 Logs:**
```bash
pm2 logs ai-desktop
pm2 monit
```

**Docker Logs:**
```bash
# All ACT containers
cd components/apps/act-docker
docker compose logs -f

# Specific flow
docker compose logs -f act-restaurant
```

**System Logs:**
```bash
# Auto-update logs
tail -f logs/auto-update.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Security Considerations

### Current State (Development Only)

**⚠️ NOT PRODUCTION READY - Security issues:**

1. **2FA is Client-Side Only**
   - Mock implementation
   - Can be bypassed via browser console
   - No server-side validation

2. **No User Authentication**
   - No user accounts
   - No session management
   - All state in browser memory

3. **No Authorization**
   - No role-based access control
   - No API authentication
   - Open endpoints

4. **Terminal Access**
   - Direct shell access
   - No sandboxing
   - Full system access

5. **Docker Socket Access**
   - Services API has Docker access
   - No rate limiting
   - Potential for abuse

6. **API Keys Exposed**
   - Action Builder requires API key
   - No secret management
   - Keys in environment variables

### Production Security Checklist

**Before deploying to production:**

- [ ] **Add Real Authentication**
  - NextAuth.js or Supabase Auth
  - Password hashing (bcrypt)
  - Session management
  - JWT tokens

- [ ] **Implement Authorization**
  - Role-based access control (RBAC)
  - API key authentication
  - Rate limiting (express-rate-limit)
  - CORS configuration

- [ ] **Secure Terminal**
  - Docker containerization per user
  - Limited shell (rbash)
  - Command whitelist
  - Session timeout

- [ ] **Secret Management**
  - Vault or AWS Secrets Manager
  - Environment variable encryption
  - API key rotation
  - Never commit secrets

- [ ] **Input Validation**
  - Sanitize all inputs
  - SQL injection prevention
  - XSS protection
  - File upload validation

- [ ] **Network Security**
  - HTTPS only (SSL/TLS)
  - CSP headers
  - HSTS
  - Secure cookies

- [ ] **Docker Security**
  - Run as non-root user
  - Read-only root filesystem
  - Drop capabilities
  - Resource limits (CPU/memory)

- [ ] **Monitoring & Logging**
  - Error tracking (Sentry)
  - Access logs
  - Security alerts
  - Audit trail

- [ ] **Database Security**
  - Parameterized queries
  - Connection encryption
  - Least privilege
  - Regular backups

- [ ] **Regular Updates**
  - Dependency updates
  - Security patches
  - CVE monitoring

### Recommended Security Additions

**1. Authentication (NextAuth.js)**
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials, req) {
        // Validate against database
        const user = await validateUser(credentials)
        if (user) {
          return user
        }
        return null
      }
    })
  ]
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
```

**2. API Route Protection**
```typescript
// lib/auth.ts
export async function requireAuth(req: NextRequest) {
  const session = await getServerSession(authOptions)
  if (!session) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  return session
}

// In API route:
export async function GET(request: NextRequest) {
  const session = await requireAuth(request)
  if (session instanceof NextResponse) return session

  // ... protected logic
}
```

**3. Rate Limiting**
```typescript
// middleware.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s')
})

export async function middleware(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'
  const { success } = await ratelimit.limit(ip)

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    )
  }

  return NextResponse.next()
}
```

---

## Future Roadmap

### Phase 1: Backend Integration (Q1 2025)

- [ ] Add PostgreSQL database
- [ ] Implement NextAuth.js
- [ ] User accounts & sessions
- [ ] Persist desktop state per user
- [ ] Real file storage (S3/local with permissions)
- [ ] Workflow persistence in database

### Phase 2: Enhanced Features (Q2 2025)

- [ ] Real terminal with Docker isolation
- [ ] Workflow execution engine
- [ ] OAuth integrations (GitHub, Slack, OpenAI)
- [ ] App marketplace backend
- [ ] Multi-user support
- [ ] Role-based access control

### Phase 3: Advanced Automation (Q3 2025)

- [ ] Visual workflow editor (drag-and-drop)
- [ ] Workflow templates
- [ ] Scheduled workflows (cron)
- [ ] Workflow analytics
- [ ] Error recovery & retry logic
- [ ] Workflow versioning

### Phase 4: Enterprise Features (Q4 2025)

- [ ] Team collaboration
- [ ] Audit logs
- [ ] SSO (SAML/OAuth)
- [ ] API keys per user
- [ ] Webhook support
- [ ] Custom integrations
- [ ] White-label branding

### Continuous Improvements

- [ ] Performance optimization
- [ ] Mobile responsive design
- [ ] PWA support
- [ ] Offline mode
- [ ] Dark/light theme persistence
- [ ] Keyboard shortcuts
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Internationalization (i18n)
- [ ] Unit & E2E tests
- [ ] Storybook component docs

---

## Contributing

### Code Style

- **TypeScript:** Strict mode enabled
- **Formatting:** Prettier (2 spaces, no semicolons)
- **Linting:** ESLint (Next.js recommended)
- **Components:** Functional components with hooks
- **Naming:**
  - Components: PascalCase
  - Files: kebab-case
  - Hooks: use-prefix
  - Types: PascalCase
  - Constants: UPPER_SNAKE_CASE

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Commit with descriptive messages
git commit -m "Add: New feature description"
git commit -m "Fix: Bug description"
git commit -m "Update: Enhancement description"

# Push and create PR
git push origin feature/my-feature
```

### Pull Request Guidelines

- Clear description of changes
- Screenshots for UI changes
- Tests for new features
- Update documentation
- Link related issues

---

## License

**Proprietary** - All rights reserved

---

## Support & Contact

**GitHub:** [Repository URL]
**Issues:** [Issues URL]
**Docs:** This file (DOCUMENTATION.md)

---

**Last Updated:** October 16, 2025
**Version:** 1.0.0
**Maintained By:** AI Desktop Team
