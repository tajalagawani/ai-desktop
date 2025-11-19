# VPS Deployment Checklist - Lightweight Architecture

## Pre-Deployment Checklist

### ✅ Local Environment
- [ ] All code committed to git
- [ ] Backend running locally on port 3006
- [ ] Frontend running locally on port 3005
- [ ] All features tested locally
- [ ] Git changes tracking working
- [ ] VS Code Manager working
- [ ] GitHub App working
- [ ] Documentation updated

### ✅ VPS Requirements
- [ ] Ubuntu 20.04+ or Debian 11+
- [ ] At least 2GB RAM
- [ ] At least 20GB disk space
- [ ] Root or sudo access
- [ ] Public IP address
- [ ] SSH access configured

### ✅ Required Software on VPS
- [ ] Node.js 18+ installed
- [ ] PM2 installed globally (`npm install -g pm2`)
- [ ] Nginx installed
- [ ] Git installed (optional, for repository management)
- [ ] Firewall configured (UFW recommended)

## Deployment Steps

### 1. Update Environment Configuration

**Backend .env** (`backend/.env`):
```bash
# Production Environment
PORT=3000
NODE_ENV=production

# Client URL
CLIENT_URL=http://YOUR_VPS_IP

# CORS Configuration
CORS_ORIGINS=http://YOUR_VPS_IP

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/ai-desktop/backend.log

# File Manager
FILE_MANAGER_ROOT=/var/www

# Show hidden files
SHOW_HIDDEN_FILES=false

# Data Directory
DATA_DIR=./data
```

**Frontend .env** (`.env.production`):
```bash
# Production Environment
NODE_ENV=production
PORT=3005

# Public URL
NEXT_PUBLIC_APP_URL=http://YOUR_VPS_IP
NEXT_PUBLIC_APP_NAME="AI Desktop"
NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP:3000

# Security
SESSION_SECRET=GENERATE_32_CHAR_SECRET_KEY

# CORS
ALLOWED_ORIGINS=http://YOUR_VPS_IP

# Anthropic API (optional)
ANTHROPIC_API_KEY=

# File Manager
FILE_MANAGER_ROOT=/var/www

# Logging
LOG_LEVEL=info

# Feature Flags
ENABLE_TWO_FACTOR=true
ENABLE_WORKFLOWS=true
ENABLE_TERMINAL=true
```

### 2. Prepare VPS

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install PM2
npm install -g pm2

# Install Nginx
apt install -y nginx

# Create directories
mkdir -p /root/ai-desktop
mkdir -p /var/www/ai-desktop
mkdir -p /var/log/ai-desktop

# Set permissions
chmod -R 755 /var/www/ai-desktop
chown -R www-data:www-data /var/www/ai-desktop
```

### 3. Deploy Using Script

```bash
# On your local machine
cd /path/to/ai-desktop

# Make script executable
chmod +x scripts/deploy-lightweight.sh

# Run deployment
./scripts/deploy-lightweight.sh

# Select: 1) Full deployment (backend + client)
```

### 4. Verify Deployment

```bash
# Check PM2 status
ssh root@YOUR_VPS_IP "pm2 list"

# Check logs
ssh root@YOUR_VPS_IP "pm2 logs ai-desktop-backend --lines 50"

# Check Nginx status
ssh root@YOUR_VPS_IP "systemctl status nginx"

# Test health endpoint
curl http://YOUR_VPS_IP/health

# Test API
curl http://YOUR_VPS_IP/api/vscode/list
```

### 5. Configure Firewall

```bash
# On VPS
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS (if using SSL)
ufw enable
```

### 6. Set Up PM2 Startup

```bash
# On VPS
pm2 startup
pm2 save

# This ensures PM2 starts on boot
```

## Post-Deployment Verification

### ✅ Backend Health Check
- [ ] Health endpoint responds: `curl http://YOUR_VPS_IP/health`
- [ ] PM2 shows process running: `pm2 list`
- [ ] Logs show no errors: `pm2 logs ai-desktop-backend`
- [ ] Data directory exists: `/root/ai-desktop/backend/data`
- [ ] JSON files created when needed

### ✅ Frontend Access
- [ ] Homepage loads: `http://YOUR_VPS_IP`
- [ ] No console errors in browser
- [ ] Assets loading correctly (CSS, JS, images)
- [ ] Navigation works

### ✅ Core Features
- [ ] VS Code Manager loads
- [ ] Can clone repository
- [ ] Can see git changes
- [ ] Repository stats showing
- [ ] GitHub app working
- [ ] Changes view working
- [ ] File Manager accessible
- [ ] Terminal works (if enabled)

### ✅ API Endpoints
```bash
# Test key endpoints
curl http://YOUR_VPS_IP/api/vscode/list
curl http://YOUR_VPS_IP/api/vscode/status
curl http://YOUR_VPS_IP/api/files
curl http://YOUR_VPS_IP/api/system-stats
```

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
pm2 logs ai-desktop-backend --err

# Check if port is in use
lsof -i :3000

# Restart PM2
pm2 restart ai-desktop-backend

# Check environment
cat /root/ai-desktop/backend/.env
```

### Nginx 502 Bad Gateway
```bash
# Check backend is running
pm2 list

# Check nginx config
nginx -t

# Check nginx logs
tail -f /var/log/nginx/error.log

# Restart nginx
systemctl restart nginx
```

### Git Changes Not Showing
```bash
# Verify repository paths
ls -la /var/www/github/

# Check git is installed
which git

# Test git command manually
cd /var/www/github/your-repo && git status --porcelain

# Check backend logs
pm2 logs ai-desktop-backend | grep -i "git"
```

### File Permission Issues
```bash
# Fix www-data permissions
chown -R www-data:www-data /var/www

# Fix data directory permissions
chmod -R 755 /root/ai-desktop/backend/data
```

## Maintenance

### Update Deployment
```bash
# Pull latest changes locally
git pull origin main

# Run deployment script again
./scripts/deploy-lightweight.sh
```

### Backup Data
```bash
# On VPS
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /root/ai-desktop/backend/data/

# Download backup
scp root@YOUR_VPS_IP:/root/backup-*.tar.gz ./backups/
```

### Monitor Resources
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check CPU usage
top

# Check PM2 metrics
pm2 monit
```

### View Logs
```bash
# Backend logs
pm2 logs ai-desktop-backend

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# System logs
journalctl -u nginx -f
```

## Security Checklist

- [ ] SSH key-based authentication enabled
- [ ] Password authentication disabled
- [ ] Firewall configured (UFW)
- [ ] Only necessary ports open (22, 80, 443)
- [ ] Strong passwords/keys used
- [ ] .env files not world-readable
- [ ] Regular security updates enabled
- [ ] PM2 logs not world-readable

## Performance Optimization

- [ ] PM2 cluster mode enabled (optional)
- [ ] Nginx gzip compression enabled
- [ ] Static assets cached
- [ ] Rate limiting configured
- [ ] Database connection pooling (N/A for JSON storage)

## Rollback Plan

If deployment fails:
```bash
# Stop new version
pm2 stop ai-desktop-backend

# Restore from backup
tar -xzf /root/backup-YYYYMMDD.tar.gz -C /

# Start previous version
pm2 start ai-desktop-backend

# Restart nginx
systemctl restart nginx
```

---

**Architecture**: Lightweight (JSON Storage, No PostgreSQL)
**Date**: 2025-11-19
**Status**: Production Ready ✅
