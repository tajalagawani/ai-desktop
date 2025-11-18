# 🚀 Fresh VPS Installation - Clean Start

## ⚠️ IMPORTANT: Use the New Installation Script

**For AI Desktop with Flow Builder (ACT integration), use:**
```bash
curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/main/deployment/vps-with-act-install.sh | bash
```

This installs:
- ✅ AI Desktop (all features)
- ✅ ACT Workflow Engine
- ✅ MCP Server (150+ nodes)
- ✅ Flow Builder integration
- ✅ PM2 process management

---

## ⚠️ Warning: This Will Delete Everything

The installation script will completely remove old installations and start fresh.

---

## 📋 Complete Fresh Install Commands

### Step 1: Stop and Clean Everything

```bash
# Stop PM2 and all processes
pm2 delete all
pm2 kill
pm2 save --force

# Remove old application
rm -rf /var/www/ai-desktop

# Remove PM2 data
rm -rf /root/.pm2

# Clean up any old docker containers/volumes (OPTIONAL - only if you want to reset Docker too)
# docker stop $(docker ps -aq)
# docker rm $(docker ps -aq)
# docker volume prune -f
```

### Step 2: System Update

```bash
# Update system
apt update && apt upgrade -y

# Install/Update Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs git python3 python3-pip build-essential

# Install PM2
npm install -g pm2

# Verify installations
node --version
npm --version
pm2 --version
```

### Step 3: Install/Update Docker (if needed)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify Docker
docker --version
docker compose version
```

### Step 4: Clone and Setup Application

```bash
# Create directory
mkdir -p /var/www
cd /var/www

# Clone fresh repository
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop

# Install dependencies
npm install

# Build the application
npm run build

# Create logs directory
mkdir -p logs
```

### Step 5: Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables (optional)
nano .env

# Set SESSION_SECRET (IMPORTANT for production)
# Generate with: openssl rand -base64 32
```

### Step 6: Start Application

```bash
# Start with PM2
pm2 start npm --name "ai-desktop" -- start

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup systemd

# Run the command PM2 outputs (will look like this):
# sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u root --hp /root
```

### Step 7: Verify Installation

```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs ai-desktop --lines 50

# Check if app is responding
curl http://localhost:3005

# Check memory usage
free -h

# Check disk space
df -h
```

---

## 🌐 Access Your Application

Once deployed, access at:
- **Local**: `http://localhost:3005`
- **Public**: `http://YOUR_VPS_IP` or `http://92.112.181.127`

---

## 🔄 Future Updates (After Fresh Install)

When you need to update the app after this fresh install:

```bash
cd /var/www/ai-desktop

# Pull latest changes
git pull origin main

# Install any new dependencies
npm install

# Rebuild
npm run build

# Restart PM2
pm2 restart ai-desktop

# View logs
pm2 logs ai-desktop --lines 20
```

---

## 🛠️ Troubleshooting

### App Won't Start

```bash
# Check PM2 logs
pm2 logs ai-desktop

# Check if port 3000 is in use
lsof -i :3000

# Kill process on port 3000 if needed
kill -9 $(lsof -t -i:3000)

# Restart
pm2 restart ai-desktop
```

### Node Modules Issues

```bash
cd /var/www/ai-desktop

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
pm2 restart ai-desktop
```

### Build Fails

```bash
# Check Node version (should be 18.x)
node --version

# If wrong version, reinstall Node
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Try build again
cd /var/www/ai-desktop
npm run build
```

### PM2 Process Crashes

```bash
# View error logs
pm2 logs ai-desktop --err --lines 50

# Delete and restart
pm2 delete ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save
```

---

## 📊 Monitoring Commands

```bash
# PM2 Dashboard
pm2 monit

# System Resources
htop

# Disk Usage
du -sh /var/www/ai-desktop

# Memory Usage
free -h

# Docker Containers (if using Service Manager)
docker ps

# Docker Resource Usage
docker stats
```

---

## 🔒 Security Checklist

After fresh install:

- [ ] Set strong SESSION_SECRET in .env
- [ ] Update system packages: `apt update && apt upgrade`
- [ ] Configure firewall (ufw)
- [ ] Set up SSH key authentication
- [ ] Disable root SSH login
- [ ] Configure automatic security updates
- [ ] Setup SSL/HTTPS with Nginx (optional)
- [ ] Enable fail2ban (optional)

---

## 📦 What's Included Now

Your fresh installation includes:

✅ **Terminal** - Command line interface
✅ **Claude CLI** - AI coding assistant
✅ **System Monitor** - Resource monitoring
✅ **File Manager** - File browsing
✅ **Service Manager** - Docker service management
✅ **System Widgets** - System metrics widgets
✅ **Desktop Settings** - Configuration

❌ **Removed**: Workflows, Flow Manager, ACT Docker, Action Builder, Security Center

---

## 🎯 Clean Installation Stats

- **Bundle Size**: 221 kB (down from 225 kB)
- **API Routes**: 9 endpoints
- **Apps**: 6 core apps
- **Build Time**: ~30-60 seconds
- **Memory Usage**: ~200-300 MB
- **No ACT/Workflow dependencies**

---

## ⚡ One-Liner Full Install

For experienced users, here's the complete installation in one command:

```bash
pm2 delete all && pm2 kill && rm -rf /var/www/ai-desktop /root/.pm2 && apt update && apt upgrade -y && mkdir -p /var/www && cd /var/www && git clone https://github.com/tajalagawani/ai-desktop.git && cd ai-desktop && npm install && npm run build && mkdir -p logs && pm2 start npm --name "ai-desktop" -- start && pm2 save && pm2 logs ai-desktop
```

**Note**: Run PM2 startup command manually after this completes.

---

## 🆘 Need Help?

- Check logs: `pm2 logs ai-desktop`
- View errors: `pm2 logs ai-desktop --err`
- Restart app: `pm2 restart ai-desktop`
- Full reset: Run Step 1 again

---

**Ready to deploy!** 🚀

Start with Step 1 and work through each step carefully.
