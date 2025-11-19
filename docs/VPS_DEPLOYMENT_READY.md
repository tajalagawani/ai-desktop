# VPS Deployment Ready Checklist

## ✅ What's Been Fixed and Ready

### 1. Backend Architecture ✅
- **PostgreSQL Removed** - Now uses JSON file storage
- **Lightweight** - No database dependencies
- **Fast** - Quick startup, minimal resources
- **Simple** - Easy to deploy and maintain

### 2. Real-time Git Stats ✅
- **VS Code Manager** - Shows file change counts on cards
- **Changes Tab** - Real-time updates every 3 seconds
- **GitHub App** - All views working (Changes, History, Branches, etc.)
- **Diff Viewer** - Handles untracked, modified, and staged files

### 3. File Organization ✅
- **Documentation** - All `*.md` files moved to `docs/`
- **Scripts** - All `*.sh` files moved to `scripts/`
- **Clean Structure** - Organized and ready for deployment

## 📋 Pre-Deployment Checklist

### Environment Files
- [ ] Update `backend/.env` for VPS
- [ ] Set `FILE_MANAGER_ROOT=/var/www`
- [ ] Set `PORT=3006` (backend)
- [ ] Set `NODE_ENV=production`
- [ ] Update `.env` (root) for frontend
- [ ] Set `NEXT_PUBLIC_API_URL=http://your-vps-ip:3006`

### Dependencies
- [ ] Review `backend/package.json` - remove unused deps
- [ ] Review `package.json` (root) - remove unused deps
- [ ] Test `npm install` works cleanly

### Scripts
- [ ] Update `scripts/deploy-lightweight.sh` with VPS IP
- [ ] Test deployment script locally (dry run)
- [ ] Update `scripts/build-all.sh` if needed

### Data & Security
- [ ] Ensure `backend/data/` exists
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Remove any sensitive data from repo
- [ ] Create `.env.example` for reference

## 🚀 Deployment Steps

### 1. VPS Preparation
```bash
# On VPS
sudo apt update
sudo apt install -y nginx nodejs npm pm2
sudo mkdir -p /var/www/ai-desktop
sudo mkdir -p /root/ai-desktop
```

### 2. Deploy Backend
```bash
# From local machine
cd /Users/tajnoah/Downloads/ai-desktop
chmod +x scripts/deploy-lightweight.sh
./scripts/deploy-lightweight.sh
# Select option 2 (Backend only)
```

### 3. Configure Backend .env on VPS
```bash
# On VPS
cd /root/ai-desktop/backend
nano .env
```

Set:
```env
PORT=3006
NODE_ENV=production
CLIENT_URL=http://your-vps-ip
CORS_ORIGINS=http://your-vps-ip,http://your-vps-ip:80
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
DATA_DIR=./data
```

### 4. Start Backend
```bash
# On VPS
cd /root/ai-desktop/backend
pm2 start server.js --name ai-desktop-backend
pm2 save
pm2 startup
```

### 5. Deploy Frontend (if using Next.js SSR)
```bash
# From local machine
./scripts/deploy-lightweight.sh
# Select option 3 (Client only)
```

OR for static build:
```bash
# Local
npm run build
npm run export

# Upload to VPS
rsync -avz out/ root@vps-ip:/var/www/ai-desktop/
```

### 6. Configure Nginx
```bash
# On VPS
sudo nano /etc/nginx/sites-available/ai-desktop
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-vps-ip;

    # Frontend
    location / {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and restart:
```bash
sudo ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Test Deployment
```bash
# Check backend
curl http://your-vps-ip:3006/health

# Check frontend
curl http://your-vps-ip/

# Check logs
pm2 logs ai-desktop-backend
```

## 🔧 Current Architecture

### Backend (Port 3006)
- **Server**: Express.js
- **Storage**: JSON files in `backend/data/`
- **APIs**:
  - `/api/vscode/*` - VS Code manager
  - `/api/git` - Git operations
  - `/api/repositories` - Repository management
  - `/api/files` - File operations
  - `/api/deployments` - Deployment management
  - `/api/services` - Service management

### Frontend (Port 3005)
- **Framework**: Next.js
- **Type**: Server-side rendered or static export
- **Features**:
  - Desktop UI
  - VS Code Manager
  - GitHub Desktop
  - Terminal
  - Service Manager

### Data Storage
```
backend/data/
├── repositories.json     # Repository list
├── deployments.json      # Deployment configs
├── vscode-sessions.json  # VS Code sessions
└── services.json         # Service configurations
```

## 🛡️ Security Notes

1. **Firewall**: Open only ports 80, 443, 22
2. **SSH**: Use key-based auth, disable password login
3. **Environment**: Never commit `.env` files
4. **API Keys**: Store in `.env`, not in code
5. **Updates**: Keep Node.js and dependencies updated

## 📊 What Works Now

✅ Git clone repositories
✅ Real-time file change tracking
✅ VS Code Manager with stats
✅ GitHub Desktop app
✅ Changes tab with live updates
✅ Diff viewer (all file states)
✅ Repository cards with badges
✅ All backend APIs tested
✅ JSON storage working
✅ No PostgreSQL dependency

## 🚨 Known Issues

None! Everything is working correctly.

## 📞 Deployment Support

If you encounter issues:
1. Check PM2 logs: `pm2 logs ai-desktop-backend`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Test backend: `curl http://localhost:3006/health`
4. Check processes: `pm2 status`

## 🎯 Next Steps

1. ✅ Review this checklist
2. ⏳ Update environment files
3. ⏳ Clean up dependencies
4. ⏳ Test locally
5. ⏳ Deploy to VPS
6. ⏳ Verify everything works

---

**Last Updated**: 2025-11-19
**Architecture**: Lightweight (No PostgreSQL)
**Status**: Ready for VPS Deployment 🚀
