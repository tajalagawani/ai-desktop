# 🚀 One-Command Installation

## Install AI Desktop on VPS

SSH into your VPS and run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/lightweight-client/install.sh)
```

**That's it!**

---

## 📋 What Happens

The script will ask you one question:

```
Do you want to install Flow Builder (ACT integration)?
  1) No  - Core features only (recommended for most users)
  2) Yes - Include Flow Builder with ACT workflow engine
Choice (1-2) [1]:
```

### Option 1: Core Features (Default)
**Installation time:** 2-3 minutes
**Features:**
- ✅ VS Code Manager
- ✅ GitHub Desktop
- ✅ Terminal
- ✅ File Manager
- ✅ Service Manager
- ✅ System Monitor
- ✅ Real-time Git Stats
- ✅ Repository Management

### Option 2: With Flow Builder
**Installation time:** 5-7 minutes
**Everything from Option 1 PLUS:**
- ✅ Flow Builder UI
- ✅ ACT Workflow Engine
- ✅ MCP Server (150+ nodes)
- ✅ Visual workflow editor
- ✅ AI-powered flow generation

---

## 🌐 Access Your App

After installation:

**Your VPS:** http://92.112.181.127

---

## ✨ Features Included (Core)

### VS Code Manager
- Start/stop code-server instances
- Multiple repositories support
- Real-time file change tracking
- Statistics on cards (modified/added/deleted)
- Live changes tab with 3-second updates

### GitHub Desktop
- Clone repositories with one click
- View changes in real-time
- Stage/unstage files
- Commit with GUI
- Push/pull operations
- Branch management
- View history with stats
- Diff viewer for all file states

### System Tools
- Built-in terminal
- File manager with upload/download
- Service manager (Docker containers)
- System resource monitoring
- Process management

---

## 🔧 Post-Install Commands

```bash
# View all services
pm2 status

# View logs
pm2 logs

# Restart everything
pm2 restart all

# Update to latest
cd /root/ai-desktop
git pull
npm install
npm run build
pm2 restart all
```

---

## 📊 System Requirements

**Minimum (Core Features):**
- 512 MB RAM
- 1 CPU core
- 2 GB disk space

**Recommended (With Flow Builder):**
- 1 GB RAM
- 2 CPU cores
- 5 GB disk space

---

## 🐛 Troubleshooting

### Installation Failed
```bash
# Re-run the installer
bash <(curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/lightweight-client/install.sh)
```

### Can't Access App
```bash
# Check if services are running
pm2 status

# Check backend health
curl http://localhost:3006/health

# Check logs
pm2 logs
```

### Services Not Starting
```bash
# Restart PM2
pm2 kill
pm2 resurrect

# Or restart manually
cd /root/ai-desktop/backend
pm2 start server.js --name ai-desktop-backend
cd /root/ai-desktop
pm2 start npm --name ai-desktop-frontend -- start
```

---

## 🎉 That's All!

One command and you're done. No complex setup, no manual configuration, everything automatic!

**Just run:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/lightweight-client/install.sh)
```

**Visit:** http://92.112.181.127

Enjoy! 🚀
