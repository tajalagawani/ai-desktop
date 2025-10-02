# 🚀 VPS Deployment Checklist

Complete guide to deploying AI Desktop on your VPS.

**⚡ For the fastest deployment, see [CLEAN_DEPLOY.md](CLEAN_DEPLOY.md) instead!**

This guide covers the detailed setup with Nginx reverse proxy. If you just want the app running quickly on port 80, use CLEAN_DEPLOY.md.

## ✅ Pre-Deployment Checklist

### 1. VPS Requirements
- [ ] Ubuntu 20.04+ server provisioned
- [ ] At least 2GB RAM
- [ ] 20GB storage minimum
- [ ] SSH access configured
- [ ] Domain name pointed to VPS IP (optional but recommended)

### 2. Local Setup
- [ ] Project builds successfully (`npm run build`)
- [ ] All environment variables documented in `.env.example`
- [ ] Git repository is up to date
- [ ] Removed sensitive data from code
- [ ] Updated `deployment/deploy.sh` with correct paths
- [ ] Updated `deployment/nginx.conf` with your domain

---

## 🔧 VPS Initial Setup

### Step 1: Connect to VPS
```bash
ssh root@your-vps-ip
```

### Step 2: Create Deployment User (Security Best Practice)
```bash
# Create user
adduser deploy
usermod -aG sudo deploy

# Setup SSH for new user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Switch to deploy user
su - deploy
```

### Step 3: Install Node.js
```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v18.x.x
npm --version
```

### Step 4: Install PM2
```bash
sudo npm install -g pm2

# Verify
pm2 --version
```

### Step 5: Install Nginx
```bash
sudo apt update
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify
sudo systemctl status nginx
```

### Step 6: Setup Firewall (Optional but Recommended)
```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 📦 Deploy Application

### Step 7: Clone Repository
```bash
# Create app directory
sudo mkdir -p /var/www
sudo chown deploy:deploy /var/www

# Clone your repo
cd /var/www
git clone https://github.com/yourusername/ai-desktop.git
cd ai-desktop
```

### Step 8: Install Dependencies
```bash
npm install
```

### Step 9: Create Environment File
```bash
# Copy example
cp .env.example .env.local

# Edit with your values
nano .env.local
# Set NEXT_PUBLIC_APP_URL to your domain or VPS IP
```

### Step 10: Build Application
```bash
npm run build
```

### Step 11: Setup PM2
```bash
# Start the application
pm2 start deployment/ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Run the command that PM2 outputs

# Check status
pm2 status
pm2 logs ai-desktop
```

### Step 12: Configure Nginx
```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ai-desktop

# Edit the config
sudo nano /etc/nginx/sites-available/ai-desktop
# Replace "your-domain.com" with your actual domain or VPS IP

# Enable the site
sudo ln -s /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 13: Test Deployment
```bash
# Visit your site
# http://your-vps-ip or http://your-domain.com

# Check PM2 logs if issues
pm2 logs ai-desktop

# Check Nginx logs if issues
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 SSL Certificate (HTTPS)

### Step 14: Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### Step 15: Generate Certificate
```bash
# For your domain
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts
# Select option 2 to redirect HTTP to HTTPS
```

### Step 16: Uncomment HTTPS in Nginx
```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/ai-desktop

# Uncomment the HTTPS server block
# Comment out the HTTP proxy section

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 17: Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

---

## 🔄 Setup GitHub Actions (Auto-Deploy)

### Step 18: Generate SSH Key for GitHub Actions
```bash
# On VPS as deploy user
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Add public key to authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Copy private key (you'll need this for GitHub)
cat ~/.ssh/github_actions
# Copy the entire output including -----BEGIN and -----END lines
```

### Step 19: Add GitHub Secrets
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `VPS_HOST`: Your VPS IP or domain
   - `VPS_USER`: `deploy` (or your deployment user)
   - `VPS_SSH_KEY`: The private key from Step 18
   - `VPS_PORT`: `22` (or your custom SSH port)

### Step 20: Test Auto-Deploy
```bash
# On your local machine
git add .
git commit -m "Test auto-deploy"
git push origin main

# Check GitHub Actions tab in your repo
# Watch the deployment process
```

---

## 🎯 Post-Deployment

### Verify Everything Works
- [ ] Website loads at your domain/IP
- [ ] HTTPS is working (if configured)
- [ ] Desktop environment loads
- [ ] Windows can be opened/closed/moved
- [ ] All apps are functional
- [ ] No console errors in browser
- [ ] PM2 process is running (`pm2 status`)
- [ ] Nginx is proxying correctly

### Setup Monitoring
```bash
# PM2 Monitoring
pm2 monit

# Check resource usage
htop

# Setup log rotation for PM2
pm2 install pm2-logrotate
```

### Backup Strategy
```bash
# Create backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/deploy/backups"
mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/ai-desktop_$DATE.tar.gz /var/www/ai-desktop

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t | tail -n +8 | xargs -r rm

echo "Backup completed: $BACKUP_DIR/ai-desktop_$DATE.tar.gz"
```

```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/deploy/backup.sh
```

---

## 🐛 Troubleshooting

### App not loading
```bash
# Check PM2
pm2 status
pm2 logs ai-desktop --lines 50

# Check if port 3000 is listening
sudo lsof -i :3000

# Restart PM2
pm2 restart ai-desktop
```

### Nginx 502 Bad Gateway
```bash
# Check if Next.js is running
pm2 status

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx SSL config
sudo nano /etc/nginx/sites-available/ai-desktop
```

### GitHub Actions Deployment Fails
```bash
# Check SSH key permissions on VPS
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# Test SSH connection from local machine
ssh -i path/to/private/key deploy@your-vps-ip

# Check deployment script permissions
chmod +x /var/www/ai-desktop/deployment/deploy.sh
```

### Out of Memory
```bash
# Check memory usage
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🔄 Regular Maintenance

### Weekly
- [ ] Check PM2 logs for errors
- [ ] Monitor disk space (`df -h`)
- [ ] Check for security updates (`sudo apt update && sudo apt upgrade`)

### Monthly
- [ ] Review backups
- [ ] Test SSL certificate auto-renewal
- [ ] Check resource usage trends

### As Needed
- [ ] Update Node.js version
- [ ] Update dependencies (`npm update`)
- [ ] Review and rotate logs

---

## 📚 Useful Commands

```bash
# PM2
pm2 status                  # Show all processes
pm2 logs ai-desktop         # View logs
pm2 restart ai-desktop      # Restart app
pm2 stop ai-desktop         # Stop app
pm2 delete ai-desktop       # Remove from PM2
pm2 monit                   # Resource monitor

# Nginx
sudo systemctl status nginx      # Check status
sudo systemctl reload nginx      # Reload config
sudo nginx -t                    # Test config
sudo tail -f /var/log/nginx/error.log  # Watch errors

# System
htop                        # Resource usage
df -h                       # Disk space
free -h                     # Memory usage
sudo systemctl reboot       # Reboot server

# Git
cd /var/www/ai-desktop
git pull origin main        # Pull latest code
npm install                 # Update dependencies
npm run build               # Rebuild
pm2 restart ai-desktop      # Restart

# Logs
journalctl -xe              # System logs
pm2 logs ai-desktop --lines 100  # Last 100 PM2 logs
sudo tail -f /var/log/nginx/access.log  # Nginx access logs
```

---

## ✅ Deployment Complete!

Your AI Desktop should now be:
- ✅ Running on your VPS
- ✅ Accessible via your domain
- ✅ Secured with HTTPS (if configured)
- ✅ Auto-deploying on git push (if configured)
- ✅ Monitored with PM2
- ✅ Backed up regularly

**Next Steps:**
1. Test all features
2. Setup monitoring/alerts
3. Configure analytics
4. Plan backend integration

Need help? Check:
- `README.md` for development info
- `CLAUDE.md` for code conventions
- GitHub Issues for known problems
