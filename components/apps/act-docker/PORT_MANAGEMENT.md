# ACT Dynamic Port Management

The ACT framework now supports **fully dynamic port configuration** that automatically reads from your flow file!

## How It Works

1. **Flow File** (`flow`) - Define your port in the `[configuration]` section:
   ```ini
   [configuration]
   port = 8083
   ```

2. **Automatic Detection** - The system automatically:
   - Reads the port from your flow file at startup
   - Configures Docker to expose that exact port
   - Updates the Flask server to listen on that port

## Quick Start

### Method 1: Automatic Sync (Recommended)

```bash
# 1. Edit your port in the flow file
vim flow
# Change: port = 8083 (or any port you want)

# 2. Sync the port to Docker configuration
./sync-port.sh

# 3. Rebuild and restart
docker-compose down
docker-compose up --build -d

# 4. Access your server
curl http://localhost:8083/api/health
```

### Method 2: Manual Docker Compose

```bash
# 1. Set port in .env file
echo "ACT_PORT=8083" > .env

# 2. Make sure flow file matches
# Edit flow file: port = 8083

# 3. Rebuild and restart
docker-compose down
docker-compose up --build -d
```

## Port Configuration Files

### 1. Flow File (`flow`)
```ini
[configuration]
agent_enabled = true
agent_name = "MyAPI"
port = 8083  # ← Change this to your desired port
debug = true
cors_enabled = true
```

### 2. Environment File (`.env`)
```bash
ACT_PORT=8083  # ← Should match flow file
```

### 3. Docker Compose (`docker-compose.yml`)
```yaml
ports:
  - "${ACT_PORT:-8080}:${ACT_PORT:-8080}"  # Auto-syncs with .env
```

## Changing Ports

To change from port 8083 to port 3000:

```bash
# 1. Edit flow file
sed -i '' 's/port = 8083/port = 3000/' flow

# 2. Run sync script
./sync-port.sh

# 3. Restart Docker
docker-compose down && docker-compose up --build -d

# 4. Verify
curl http://localhost:3000/api/health
```

## Multiple Flow Files

If you have multiple flow files with different ports:

```bash
# Flow file 1 (port 8080)
cp flow flow.8080
# Edit: port = 8080

# Flow file 2 (port 9000)
cp flow flow.9000
# Edit: port = 9000

# Run with specific flow
docker-compose down
cp flow.8080 flow
./sync-port.sh
docker-compose up -d
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8083

# Kill the process
kill -9 <PID>

# Or change to a different port in flow file
```

### Docker Not Exposing Port
```bash
# Check Docker port mapping
docker ps

# Verify .env file
cat .env | grep ACT_PORT

# Rebuild forcing sync
./sync-port.sh
docker-compose up --build -d --force-recreate
```

### Flow File vs Container Port Mismatch
```bash
# The entrypoint.sh script will show detected port
docker logs <container_id> | grep "Detected port"

# Should show:
# 🔌 Detected port: 8083
```

## Advanced: Custom Ports Per Environment

```bash
# Development (port 8080)
echo "ACT_PORT=8080" > .env.dev
docker-compose --env-file .env.dev up -d

# Staging (port 8081)
echo "ACT_PORT=8081" > .env.staging
docker-compose --env-file .env.staging up -d

# Production (port 80)
echo "ACT_PORT=80" > .env.prod
docker-compose --env-file .env.prod up -d
```

## Automated Port Detection

The `entrypoint.sh` script automatically:
- Scans the flow file for `port = <number>`
- Extracts the port number
- Sets it as an environment variable
- Passes it to the ACT server

You'll see this in the logs:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ACT Dynamic Port Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Flow file: /app/flow
🔌 Detected port: 8083
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## No More Hardcoding!

✅ **Before**: Had to manually edit multiple files
✅ **After**: Just change one line in your flow file!

The port is now:
- ✅ Read automatically from flow file
- ✅ Synced to Docker configuration
- ✅ Displayed in startup logs
- ✅ Completely dynamic - change anytime!
