# 🚀 AI Desktop - One-Command Installation

## ⚡ Installation (30 seconds)

SSH into your VPS and run **ONE command**:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/lightweight-client/install.sh)
```

**That's it!** The script will:
1. Clean up any old installation
2. Install Node.js, PM2, Nginx
3. Clone the repository
4. Install all dependencies
5. Configure everything automatically
6. Start backend + frontend with PM2
7. Setup Nginx reverse proxy
8. Auto-start on boot

**Total time:** 2-3 minutes

---

## 🌐 Access Your App

After installation completes, visit:

**http://YOUR_VPS_IP**

For your server:
**http://92.112.181.127**

---

## 📋 What Gets Installed

✅ **Backend** (Port 3006)
- Express.js API server
- Socket.IO for real-time updates
- JSON file storage (no database!)
- PM2 process management

✅ **Frontend** (Port 3005)
- Next.js application
- Desktop UI
- VS Code Manager
- GitHub Desktop
- Terminal, File Manager, etc.

✅ **Nginx** (Port 80)
- Reverse proxy
- Routes all traffic
- WebSocket support

✅ **Data Storage**
- JSON files in `/root/ai-desktop/backend/data/`
- No PostgreSQL required!
- Easy backup (just copy the folder)

---

## 🔍 Verify Installation

```bash
# Check services
pm2 status

# Should show:
# ┌─────────────────────┬────┬─────────┬──────┐
# │ Name                │ id │ status  │ cpu  │
# ├─────────────────────┼────┼─────────┼──────┤
# │ ai-desktop-backend  │ 0  │ online  │ 0%   │
# │ ai-desktop-frontend │ 1  │ online  │ 0%   │
# └─────────────────────┴────┴─────────┴──────┘

# Test backend
curl http://localhost:3006/health

# Should return:
# {"success":true,"status":"healthy",...}

# Test frontend
curl http://localhost:3005

# Should return HTML
```

---

## 🛠️ Useful Commands

```bash
# View logs (all services)
pm2 logs

# View backend logs only
pm2 logs ai-desktop-backend

# View frontend logs only
pm2 logs ai-desktop-frontend

# Restart everything
pm2 restart all

# Stop everything
pm2 stop all

# Check PM2 status
pm2 status

# Monitor in real-time
pm2 monit

# Check Nginx
nginx -t
systemctl status nginx
```

---

## 🔄 Update to Latest Version

```bash
cd /root/ai-desktop

# Pull latest code
git pull

# Reinstall dependencies
cd backend && npm install --production
cd .. && npm install

# Rebuild frontend
npm run build

# Restart services
pm2 restart all

# Check logs
pm2 logs
```

---

## 🗑️ Uninstall

```bash
# Stop and remove PM2 processes
pm2 delete all
pm2 kill

# Remove application
rm -rf /root/ai-desktop

# Remove Nginx config
rm /etc/nginx/sites-enabled/ai-desktop
rm /etc/nginx/sites-available/ai-desktop
systemctl restart nginx
```

---

## 🐛 Troubleshooting

### Installation Failed

```bash
# Re-run the installation script
bash <(curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/lightweight-client/install.sh)
```

### Services Won't Start

```bash
# Check PM2 logs
pm2 logs

# Check if ports are in use
lsof -i :3006  # Backend
lsof -i :3005  # Frontend

# Kill processes on ports if needed
kill -9 $(lsof -t -i:3006)
kill -9 $(lsof -t -i:3005)

# Restart
pm2 restart all
```

### Can't Access from Browser

```bash
# Check firewall
ufw status
ufw allow 80
ufw allow 443
ufw allow 22

# Check Nginx
nginx -t
systemctl restart nginx

# Check if services are running
pm2 status
```

### Out of Memory

```bash
# Check memory
free -h

# Restart with lower memory limits
pm2 delete all
pm2 start backend/server.js --name ai-desktop-backend --max-memory-restart 200M
pm2 start npm --name ai-desktop-frontend --max-memory-restart 300M -- start
pm2 save
```

---

## 📊 System Requirements

**Minimum:**
- 512 MB RAM
- 1 CPU core
- 2 GB disk space
- Ubuntu 20.04+ or Debian 11+

**Recommended:**
- 1 GB RAM
- 2 CPU cores
- 5 GB disk space
- Ubuntu 22.04 or Debian 12

---

## 🔒 Security Notes

After installation:
1. Setup firewall (ufw)
2. Use SSH keys (disable password login)
3. Keep system updated
4. Consider SSL/HTTPS with Let's Encrypt
5. Regular backups of `/root/ai-desktop/backend/data/`

---

## ✨ Features Included

✅ VS Code Manager - Manage code-server instances
✅ GitHub Desktop - Git operations & repository management
✅ Terminal - Built-in terminal access
✅ File Manager - Browse and manage files
✅ System Monitor - Resource monitoring
✅ Service Manager - Docker container management
✅ Real-time Git Stats - Live file change tracking
✅ Diff Viewer - View file changes
✅ Repository Cards - Visual repository management

---

## 📞 Support

**Logs**: `pm2 logs`
**Status**: `pm2 status`
**Restart**: `pm2 restart all`

**Issues?** Check:
1. PM2 logs for errors
2. Nginx configuration
3. Firewall settings
4. Available memory/disk

---

**Enjoy AI Desktop!** 🎉
