# 🚀 One-Command VPS Installation (Lightweight - No PostgreSQL)

## ⚡ Single Command Install

**SSH into your VPS and run this ONE command:**

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/ai-desktop/lightweight-client/install.sh | bash
```

That's it! 🎉

---

## 📋 What It Does

The script automatically:
1. ✅ Stops old processes
2. ✅ Installs Node.js 18+, PM2, Nginx
3. ✅ Clones repository
4. ✅ Installs dependencies (backend + frontend)
5. ✅ Creates data directories
6. ✅ Configures environment
7. ✅ Starts backend with PM2
8. ✅ Starts frontend with PM2
9. ✅ Configures Nginx
10. ✅ Opens in browser at http://YOUR_VPS_IP

---

## 🔧 Manual Installation (If Preferred)

If you prefer to run commands manually:

### Step 1: SSH into VPS
```bash
ssh root@92.112.181.127
# Password: O0Nk734.PIF&KZ6,sPz@
```

### Step 2: Run This One Command
```bash
bash <(curl -fsSL https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/install-ai-desktop.sh)
```

---

## 🎯 What You Get

After installation completes:
- ✅ Backend API running on port 3006
- ✅ Frontend running on port 3005
- ✅ Nginx proxying on port 80
- ✅ JSON file storage (no database!)
- ✅ PM2 auto-restart enabled
- ✅ All git features working
- ✅ Real-time stats enabled

Access at: **http://92.112.181.127**

---

## 📊 Installation Time

- **Total**: ~3-5 minutes
- **Downloads**: ~200 MB
- **Disk Space**: ~500 MB
- **Memory**: ~300 MB

---

## 🔍 Verify Installation

```bash
# Check backend
curl http://localhost:3006/health

# Check frontend
curl http://localhost:3005

# Check PM2
pm2 status

# View logs
pm2 logs
```

---

## 🛠️ Post-Install Commands

```bash
# View backend logs
pm2 logs ai-desktop-backend

# View frontend logs
pm2 logs ai-desktop-frontend

# Restart services
pm2 restart all

# Update to latest
cd /root/ai-desktop && git pull && pm2 restart all
```

---

**That's all you need!** One command and you're done! 🚀
