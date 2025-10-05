# ACT Multi-Flow Deployment Guide

Run multiple ACT workflows simultaneously, each on its own port, from a single Docker setup.

## 🌟 Features

- **Auto-Discovery**: Automatically finds all `.flow` files in `flows/` directory
- **Dynamic Port Management**: Each flow runs on its own port (defined in the flow file)
- **Independent Containers**: Each flow runs in its own Docker container
- **Hot Reload**: Built-in file watching for each flow (manual restart required)
- **Validation**: Automatic port conflict detection and flow validation
- **Management Tools**: Generated Makefile and status scripts

## 📁 Directory Structure

```
act-docker/
├── flows/                    # Place all your .flow files here
│   ├── restaurant.flow       # Port 3225
│   ├── ecommerce.flow        # Port 3226
│   └── crm.flow             # Port 3227
├── act/                      # ACT framework code
├── startup.sh               # Main startup script (auto-generates config)
├── docker-compose-generator.py  # Generates docker-compose.yml
├── flow_discovery.py        # Flow discovery and validation
├── docker-compose.yml       # Auto-generated (don't edit manually)
├── Makefile                 # Auto-generated shortcuts
└── status.sh                # Auto-generated health checker
```

## 🚀 Quick Start

### 1. Add Your Flow Files

Place all your `.flow` files in the `flows/` directory:

```bash
# Each flow file MUST have a port defined:
# [deployment]
# port = 3225
```

**Example flow files:**
- `flows/restaurant.flow` → Port 3225
- `flows/ecommerce.flow` → Port 3226
- `flows/crm.flow` → Port 3227

### 2. Start All Flows

```bash
./startup.sh
```

Or rebuild from scratch:

```bash
./startup.sh --build
```

**What happens:**
1. Scans `flows/` directory
2. Validates all flow files (port conflicts, syntax)
3. Generates `docker-compose.yml` with one service per flow
4. Generates `Makefile` with management shortcuts
5. Generates `status.sh` health checker
6. Starts all Docker containers

### 3. Check Status

```bash
./status.sh
```

Or:

```bash
make status
docker-compose ps
```

## 📊 Managing Flows

### View Logs

```bash
# All flows
docker-compose logs -f

# Specific flow
docker-compose logs -f act-restaurant
```

Or use Makefile:

```bash
make logs
make logs-restaurant
```

### Stop/Start Flows

```bash
# All flows
make start
make stop
make restart

# Specific flow
make start-restaurant
make stop-restaurant
make restart-restaurant
```

Or:

```bash
docker-compose start act-restaurant
docker-compose stop act-restaurant
docker-compose restart act-restaurant
```

### Rebuild After Changes

When you modify a flow file:

```bash
# Regenerate config and restart
./startup.sh --build
```

Or:

```bash
make rebuild
```

### Clean Up

```bash
# Stop and remove all containers
docker-compose down

# Stop, remove containers, and delete volumes
docker-compose down -v
```

Or:

```bash
make clean
```

## 🔍 Flow Discovery

### List All Flows

```bash
python3 flow_discovery.py
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Discovered 3 flow(s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 restaurant
   Port: 3225
   Mode: agent
   Agent: Restaurant Management API
   File: restaurant.flow

⚡ ecommerce
   Port: 3226
   Mode: miniact
   Agent: E-commerce Backend
   File: ecommerce.flow
```

### Flow Validation

The system automatically validates:
- ✅ Each flow has a unique port
- ✅ No duplicate flow names
- ✅ Ports are in valid range (1-65535)
- ⚠️  Warns if ports are in privileged range (< 1024)

## 🌐 Access Your Flows

Each flow runs on its own port:

```bash
# Restaurant flow
curl http://localhost:3225/health
curl http://localhost:3225/api/info

# E-commerce flow
curl http://localhost:3226/health
curl http://localhost:3226/api/info
```

### Agent Mode vs MiniACT Mode

**Agent Mode** (has ACI routes):
- HTTP server with custom routes
- Access via: `http://localhost:{port}/aci/{route}`
- Status: `http://localhost:{port}/api/status`

**MiniACT Mode** (no routes):
- Execute workflow manually
- POST: `http://localhost:{port}/execute`
- POST: `http://localhost:{port}/execute/node/{id}`

## 🔧 Advanced Usage

### Generate Config Without Starting

```bash
python3 docker-compose-generator.py
```

This creates:
- `docker-compose.yml` - Docker configuration
- `Makefile` - Management shortcuts
- `status.sh` - Health checker script

### Custom Flows Directory

```bash
python3 flow_discovery.py /path/to/flows
python3 docker-compose-generator.py /path/to/flows
```

### JSON Output

```bash
python3 flow_discovery.py --json > flows.json
```

## 📝 Flow File Requirements

Each `.flow` file MUST include a port definition:

```ini
[deployment]
port = 3225
environment = production

[agent]
agent_name = My Agent Name
```

**Port Assignment:**
- Each flow needs a unique port
- Recommended range: 3000-9999
- Avoid: 80, 443, 8080 (common conflicts)

## 🐛 Troubleshooting

### "Port already in use"

```bash
# Find what's using the port
lsof -i :3225

# Stop the conflicting service
kill -9 <PID>

# Or change the port in your flow file
```

### "No valid flows found"

- Check that `.flow` files are in `flows/` directory
- Verify each flow has `port = XXXX` in `[deployment]` section
- Run: `python3 flow_discovery.py` to see errors

### "Container keeps restarting"

```bash
# Check logs
docker-compose logs act-restaurant

# Common issues:
# - Invalid flow syntax
# - Missing dependencies
# - Port conflicts
```

### Hot Reload Not Working

Hot reload **detects** changes but requires **manual restart**:

```bash
# After changing flow file:
docker-compose restart act-restaurant

# Or rebuild:
./startup.sh --build
```

## 📚 API Endpoints

Each flow exposes:

### Health & Status
- `GET /health` - Health check
- `GET /api/info` - Flow information
- `GET /api/status` - Current status
- `GET /api/nodes` - All nodes
- `GET /api/routes` - All routes (agent mode)

### Execution (MiniACT mode)
- `POST /execute` - Run entire workflow
- `POST /execute/node/{id}` - Run specific node
- `POST /reload` - Force reload flow file

### Agent Mode Routes
- Custom routes defined in flow file
- Access via: `/aci/{route_path}`

## 🎯 Production Deployment

### VPS Setup

1. Clone repository:
```bash
git clone <repo> /opt/act-docker
cd /opt/act-docker
```

2. Add flow files:
```bash
mkdir flows
# Upload your .flow files to flows/
```

3. Start:
```bash
./startup.sh --build
```

4. Setup systemd (optional):
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

[Install]
WantedBy=multi-user.target
```

### Monitoring

```bash
# Watch all logs in real-time
docker-compose logs -f

# Check health of all flows
./status.sh

# View container stats
docker stats
```

## 🔐 Security Notes

- **Firewall**: Only expose necessary ports
- **Environment Variables**: Store secrets in `.env` (not in flow files)
- **Networks**: Flows share `act-network` bridge (isolated from host)
- **Volumes**: ACT code is mounted read-only in containers

## ❓ FAQ

**Q: Can I run flows on the same port?**
A: No, each flow needs a unique port. The system will detect conflicts.

**Q: How many flows can I run?**
A: Limited only by server resources. Each flow = 1 container.

**Q: Do I need to rebuild when adding a new flow?**
A: Yes, run `./startup.sh --build` to regenerate config and start new flow.

**Q: Can flows communicate with each other?**
A: Yes, they're on the same `act-network`. Access via container name:
```
http://act-restaurant:3225/api/data
```

**Q: What happens if a flow crashes?**
A: Docker restarts it automatically (`restart: unless-stopped`).

## 📞 Support

- GitHub Issues: Report bugs and feature requests
- Logs: `docker-compose logs` for debugging
- Validation: `python3 flow_discovery.py` to check flows

---

**Generated by ACT Multi-Flow System**
