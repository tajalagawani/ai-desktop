# Quick VPS Deployment Guide

## ⚡ 5-Minute Deploy

### 1. Prepare VPS (One-time)
```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Install requirements
apt update && apt install -y nginx nodejs npm
npm install -g pm2
mkdir -p /var/www/ai-desktop /root/ai-desktop

# Exit VPS
exit
```

### 2. Deploy from Local Machine
```bash
# Update deployment script with your VPS IP
nano scripts/deploy-lightweight.sh
# Change line 17: VPS_HOST="YOUR_VPS_IP"

# Make executable and deploy
chmod +x scripts/deploy-lightweight.sh
./scripts/deploy-lightweight.sh
# Choose option 1 (Full deployment)
```

### 3. Configure on VPS
```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Setup backend environment
cd /root/ai-desktop/backend
cat > .env << 'EOF'
PORT=3006
NODE_ENV=production
CLIENT_URL=http://YOUR_VPS_IP
CORS_ORIGINS=http://YOUR_VPS_IP,http://YOUR_VPS_IP:80
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
DATA_DIR=./data
EOF

# Start backend
pm2 start server.js --name ai-desktop-backend
pm2 save
pm2 startup  # Follow the instructions shown
```

### 4. Setup Nginx
```bash
# Still on VPS
cat > /etc/nginx/sites-available/ai-desktop << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /socket.io/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable and restart nginx
ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

### 5. Verify
```bash
# Check backend
curl http://localhost:3006/health
# Should return: {"success":true,"status":"healthy",...}

# Check PM2
pm2 status
# Should show ai-desktop-backend running

# Exit VPS
exit

# Test from your machine
curl http://YOUR_VPS_IP/
# Should return HTML

curl http://YOUR_VPS_IP:3006/health
# Should return health check JSON
```

## 🎉 Done!

Visit: `http://YOUR_VPS_IP`

## 🔧 Common Commands

### On VPS
```bash
# View logs
pm2 logs ai-desktop-backend

# Restart backend
pm2 restart ai-desktop-backend

# Check status
pm2 status

# Check nginx
nginx -t
systemctl status nginx

# View nginx logs
tail -f /var/log/nginx/error.log
```

### From Local
```bash
# Redeploy backend only
./scripts/deploy-lightweight.sh  # Choose option 2

# Redeploy frontend only
./scripts/deploy-lightweight.sh  # Choose option 3

# Full redeploy
./scripts/deploy-lightweight.sh  # Choose option 1
```

## 📊 What's Running

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3005 | http://YOUR_VPS_IP (via nginx on 80) |
| Backend API | 3006 | http://YOUR_VPS_IP:3006 |
| Nginx | 80 | Routes all traffic |

## 🛠️ Troubleshooting

### Backend won't start
```bash
pm2 logs ai-desktop-backend
# Check for errors
```

### Nginx error
```bash
nginx -t
# Fix any config errors shown
```

### Can't access from browser
```bash
# Check firewall
ufw status
ufw allow 80
ufw allow 443
ufw allow 22
```

### Need to update code
```bash
# From local machine
./scripts/deploy-lightweight.sh
# On VPS
pm2 restart ai-desktop-backend
```

## 📝 Architecture

```
[Browser] → [Nginx :80] → [Frontend :3005]
                        ↓
                [Backend API :3006]
                        ↓
                [JSON Files in backend/data/]
```

---

**That's it!** You're deployed! 🚀
