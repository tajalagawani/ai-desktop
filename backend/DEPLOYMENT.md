# Backend Deployment Guide

## Quick Setup

### Mac (Development)

```bash
cd backend
./setup.sh
npm run dev
```

Backend will run on: **http://localhost:3006**

### VPS (Production)

```bash
cd backend
./setup.sh
npm run pm2:start
```

Backend will run on: **http://localhost:3000** (nginx proxies to port 80)

---

## Detailed Setup Instructions

### 1. Development (Mac)

#### Prerequisites
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@18

# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
```

#### Setup Backend
```bash
cd backend
./setup.sh
```

The script will:
- ✅ Check Node.js version
- ✅ Check PostgreSQL
- ✅ Create database `ai_desktop_dev`
- ✅ Install npm dependencies
- ✅ Create `.env` file
- ✅ Run database migrations

#### Start Development Server
```bash
npm run dev
```

Backend runs on: **http://localhost:3006**

#### Test
```bash
curl http://localhost:3006/health
```

---

### 2. Production (VPS)

#### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install PM2
sudo npm install -g pm2

# Install nginx
sudo apt install -y nginx
```

#### Setup Backend
```bash
# Upload backend folder to VPS
scp -r backend root@YOUR_VPS_IP:/root/ai-desktop/

# SSH into VPS
ssh root@YOUR_VPS_IP

# Navigate to backend
cd /root/ai-desktop/backend

# Run setup
./setup.sh
```

The script will:
- ✅ Check Node.js version
- ✅ Check PostgreSQL
- ✅ Create database `ai_desktop`
- ✅ Create database user with secure password
- ✅ Install npm dependencies
- ✅ Create `.env` file with production settings
- ✅ Run database migrations

**IMPORTANT:** The script will generate a database password. **Save it!**

#### Configure Nginx

```bash
# Copy nginx template
sudo cp nginx.conf.example /etc/nginx/sites-available/ai-desktop-backend

# Edit configuration
sudo nano /etc/nginx/sites-available/ai-desktop-backend

# Replace YOUR_VPS_IP_OR_DOMAIN with your actual IP/domain

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-desktop-backend /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### Start Backend with PM2

```bash
npm run pm2:start
```

#### Verify Deployment

```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs ai-desktop-backend

# Test health endpoint (internal)
curl http://localhost:3000/health

# Test health endpoint (external via nginx)
curl http://YOUR_VPS_IP/health
```

---

## Environment Variables

### Development (.env)
```env
PORT=3006
NODE_ENV=development
CLIENT_URL=http://localhost:3005
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_desktop_dev
DB_USER=postgres
DB_PASSWORD=postgres
```

### Production (.env)
```env
PORT=3000
NODE_ENV=production
CLIENT_URL=http://YOUR_VPS_IP
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_desktop
DB_USER=ai_desktop_user
DB_PASSWORD=GENERATED_PASSWORD
JWT_SECRET=GENERATED_SECRET
CORS_ORIGINS=http://YOUR_VPS_IP
LOG_FILE=/var/log/ai-desktop/backend.log
```

---

## PM2 Commands (Production)

```bash
# Start
npm run pm2:start

# Stop
npm run pm2:stop

# Restart
npm run pm2:restart

# Delete
npm run pm2:delete

# View logs
npm run pm2:logs

# Monitor
npm run pm2:monit

# Save PM2 configuration (auto-restart on reboot)
pm2 save
pm2 startup
```

---

## Database Management

### Development

```bash
# Connect to database
psql -d ai_desktop_dev -U postgres

# List tables
\dt

# Query data
SELECT * FROM mcp_servers;

# Exit
\q
```

### Production

```bash
# Connect to database
psql -d ai_desktop -U ai_desktop_user

# You'll be prompted for password (from .env file)

# List tables
\dt

# Query data
SELECT * FROM mcp_servers;

# Exit
\q
```

### Database Backup

```bash
# Backup
pg_dump -U ai_desktop_user ai_desktop > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql -U ai_desktop_user ai_desktop < backup_20250119_120000.sql
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3006 (Mac)
lsof -i :3006

# Find process using port 3000 (VPS)
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
# Mac:
brew services list | grep postgresql

# VPS:
sudo systemctl status postgresql

# Restart PostgreSQL
# Mac:
brew services restart postgresql@14

# VPS:
sudo systemctl restart postgresql
```

### Check Database Credentials

```bash
# View .env file
cat .env | grep DB_

# Test connection
psql -h localhost -U ai_desktop_user -d ai_desktop
```

### PM2 Issues

```bash
# View PM2 logs
pm2 logs ai-desktop-backend --lines 100

# Restart with logs
pm2 restart ai-desktop-backend && pm2 logs

# Delete and restart
pm2 delete ai-desktop-backend
npm run pm2:start
```

### Nginx Issues

```bash
# Check nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View nginx logs
sudo tail -f /var/log/nginx/ai-desktop-backend.error.log

# Restart nginx
sudo systemctl restart nginx
```

---

## Health Checks

### Development
```bash
curl http://localhost:3006/health
curl http://localhost:3006/api/status
```

### Production
```bash
# Internal
curl http://localhost:3000/health

# External (via nginx)
curl http://YOUR_VPS_IP/health
curl http://YOUR_VPS_IP/api/status
```

---

## Monitoring

### System Resources

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Database size
du -sh /var/lib/postgresql/
```

### Backend Logs

```bash
# PM2 logs
pm2 logs ai-desktop-backend

# Application logs (if configured)
tail -f /var/log/ai-desktop/backend.log

# Nginx logs
tail -f /var/log/nginx/ai-desktop-backend.access.log
tail -f /var/log/nginx/ai-desktop-backend.error.log
```

---

## Security Checklist

### Production

- [ ] Strong database password generated
- [ ] JWT secret generated
- [ ] Firewall configured (UFW)
- [ ] PostgreSQL only accessible from localhost
- [ ] Regular database backups
- [ ] PM2 auto-restart on reboot enabled
- [ ] Nginx rate limiting (optional)
- [ ] SSL certificate (optional but recommended)

### Setup UFW Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (if using SSL)
sudo ufw allow 443/tcp

# Deny direct access to backend port
sudo ufw deny 3000/tcp

# Check status
sudo ufw status
```

---

## SSL Setup (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (automatically configured by certbot)
sudo certbot renew --dry-run
```

---

## Quick Reference

| Environment | Port | URL |
|-------------|------|-----|
| Mac Dev | 3006 | http://localhost:3006 |
| VPS Internal | 3000 | http://localhost:3000 |
| VPS External | 80 | http://YOUR_VPS_IP |

| Command | Description |
|---------|-------------|
| `./setup.sh` | Initial setup |
| `npm run dev` | Start development |
| `npm run pm2:start` | Start production |
| `npm run pm2:logs` | View logs |
| `curl /health` | Health check |

---

## Support

If you encounter issues:

1. Check logs: `pm2 logs ai-desktop-backend`
2. Check database: `psql -d ai_desktop -U ai_desktop_user`
3. Check nginx: `sudo nginx -t`
4. Restart services: `pm2 restart all && sudo systemctl restart nginx`
