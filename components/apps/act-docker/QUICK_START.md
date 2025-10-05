# 🚀 ACT Quick Start - No Hardcoded Ports!

## The Easiest Way (One Command)

Change your port in the `flow` file, then run:

```bash
./run.sh
```

**That's it!** No manual steps needed.

## What It Does

1. ✅ Reads port from your `flow` file
2. ✅ Updates Docker configuration automatically
3. ✅ Rebuilds and restarts container
4. ✅ Shows you the access URLs

## Example

```bash
# Edit flow file - change port to 9000
vim flow
# port = 9000

# Run the script
./run.sh

# Output:
# 🔌 Detected port: 9000
# ✅ Updated .env file: ACT_PORT=9000
# 🚀 Starting container with port 9000...
# ✅ ACT is running!
# 
# 🌐 Access your server at:
#    📊 Dashboard:   http://localhost:9000/admin/dashboard
#    💚 Health:      http://localhost:9000/health
```

## Available Scripts

- **`./run.sh`** - Auto-detect port and start everything
- **`./sync-port.sh`** - Just sync port to .env (no restart)
- **`docker-compose down`** - Stop the server
- **`docker logs -f act-docker-act-1`** - View live logs

## How It Works

```
flow file (port = 7651)
    ↓
run.sh reads port
    ↓
Updates .env (ACT_PORT=7651)
    ↓
Docker Compose uses ${ACT_PORT}
    ↓
Container exposes 7651:7651
    ↓
Server listens on 7651
```

## No More Hardcoding!

✅ **Change port once** in flow file  
✅ **Run one command**: `./run.sh`  
✅ **Everything syncs automatically**

See `PORT_MANAGEMENT.md` for advanced usage.
