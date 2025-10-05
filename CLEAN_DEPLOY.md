# Clean Deployment - Port 80 Direct

App now runs directly on port 80 (no Nginx needed).

## Clean Install Commands

```bash
ssh root@92.112.181.127
```

**Step 1: Remove old installation**
```bash
pm2 delete all
pm2 kill
apt remove --purge nginx nginx-common -y
apt autoremove -y
rm -rf /var/www/ai-desktop
rm -rf /root/.pm2
```

**Step 2: Fresh install**
```bash
apt update && apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs git python3 python3-pip
npm install -g pm2

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
apt install docker-compose -y

# Clone and setup
mkdir -p /var/www
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
npm install
npm run build
mkdir -p logs

# Setup ACT Docker flows
cd components/apps/act-docker
pip3 install flask flask-cors requests
mkdir -p flows
python3 docker-compose-generator.py
docker-compose up -d --build
cd /var/www/ai-desktop

# Start Next.js app
pm2 start deployment/ecosystem.config.js
pm2 save
pm2 startup systemd
```

Copy and run the PM2 startup command it outputs, then:

```bash
pm2 status
```

**Done!** Visit: http://your-vps-ip

---

## Optional: Setup Auto-Updates

Enable automatic deployment when you push to GitHub:

```bash
# Make script executable
chmod +x deployment/auto-update.sh

# Setup cron job (checks every 5 minutes)
crontab -e
# Add this line:
# */5 * * * * /var/www/ai-desktop/deployment/auto-update.sh >> /var/www/ai-desktop/logs/auto-update.log 2>&1
```

**See [SETUP_AUTO_UPDATE.md](deployment/SETUP_AUTO_UPDATE.md) for complete guide**

---

## Manual Update Commands

```bash
cd /var/www/ai-desktop
git pull origin main
npm install
npm run build

# Update ACT Docker flows
cd components/apps/act-docker
python3 docker-compose-generator.py
docker-compose down
docker-compose up -d --build
cd /var/www/ai-desktop

# Restart Next.js
pm2 restart ai-desktop
```

## Check Status

```bash
pm2 status
pm2 logs ai-desktop

# Check ACT Docker flows
docker ps --filter "name=act-"
docker-compose -f /var/www/ai-desktop/components/apps/act-docker/docker-compose.yml logs

# Check auto-update logs (if enabled)
tail -f /var/www/ai-desktop/logs/auto-update.log
```

## Add Your Flow Files

To add your .flow files to the VPS:

```bash
# From your local machine:
scp /path/to/your/*.flow root@92.112.181.127:/var/www/ai-desktop/components/apps/act-docker/flows/

# Then on VPS:
cd /var/www/ai-desktop/components/apps/act-docker
python3 docker-compose-generator.py
docker-compose up -d --build
```
