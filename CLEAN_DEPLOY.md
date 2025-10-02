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
apt install -y nodejs git
npm install -g pm2
mkdir -p /var/www
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
npm install
npm run build
mkdir -p logs
pm2 start deployment/ecosystem.config.js
pm2 save
pm2 startup systemd
```

Copy and run the PM2 startup command it outputs, then:

```bash
pm2 status
```

**Done!** Visit: http://92.112.181.127

---

## Quick Restart Commands

```bash
cd /var/www/ai-desktop
git pull origin main
npm install
npm run build
pm2 restart ai-desktop
```

## Check Status

```bash
pm2 status
pm2 logs ai-desktop
```
