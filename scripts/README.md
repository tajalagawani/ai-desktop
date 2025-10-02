# AI Desktop VPS Security Scripts

These scripts implement comprehensive UFW firewall security based on Hostinger best practices.

## Setup Instructions

Run these scripts **in order** on your VPS:

### 1. Setup UFW Firewall (Required)
```bash
bash scripts/setup-ufw-security.sh
```

**What it does:**
- Installs UFW firewall
- Sets secure defaults (deny incoming, allow outgoing)
- Opens only SSH (22) and HTTP (80)
- Enables logging for security monitoring

### 2. Create UFW Application Profiles (Required)
```bash
bash scripts/create-ufw-profiles.sh
```

**What it does:**
- Creates UFW profiles for all services (MySQL, PostgreSQL, Redis, etc.)
- Better organization than raw port numbers
- Enables easy firewall management

### 3. Setup Sudo Permissions (Required)
```bash
bash scripts/setup-sudo-permissions.sh
```

**What it does:**
- Allows the app to manage firewall without password prompts
- Enables automatic port opening when installing services
- Secure: Only allows specific firewall commands

### 4. Update and Restart App
```bash
cd /var/www/ai-desktop
git pull origin main
npm run build
pm2 restart ai-desktop
```

## Security Features

✅ **Default Deny Policy** - All incoming connections blocked by default
✅ **Rate Limiting** - 6 connections per 30 seconds per port (prevents brute force)
✅ **Automatic Port Management** - Ports open/close with service install/remove
✅ **UFW Profiles** - Organized firewall rules with descriptions
✅ **Logging** - All connection attempts logged to `/var/log/ufw.log`
✅ **Clean Firewall Rules** - Each rule has a comment indicating which service

## Usage

After setup, firewall management is automatic:

- **Install a service** → Firewall port opens with rate limiting
- **Remove a service** → Firewall port closes automatically
- **Check status** → `sudo ufw status numbered`
- **View logs** → `sudo tail -f /var/log/ufw.log`

## Manual Firewall Management

```bash
# Allow a service by profile
sudo ufw allow 'AI-Desktop-MySQL'

# Allow a port with rate limiting
sudo ufw limit 3306/tcp comment 'MySQL'

# Delete a rule by number
sudo ufw status numbered
sudo ufw delete [number]

# View all available profiles
sudo ufw app list | grep AI-Desktop

# Reset firewall (danger!)
sudo ufw reset
```

## Security Best Practices

1. **Change default passwords** immediately after installing services
2. **Use SSH keys** instead of password authentication
3. **Disable root login** via SSH
4. **Monitor logs** regularly: `sudo tail -f /var/log/ufw.log`
5. **Limit service access** to specific IPs when possible
6. **Update regularly** with `apt-get update && apt-get upgrade`

## Troubleshooting

**Can't access service after installation:**
1. Check if UFW is enabled: `sudo ufw status`
2. Check if port is open: `sudo ufw status numbered`
3. Check if container is running: `docker ps`
4. Check if port is listening: `sudo netstat -tulpn | grep [PORT]`

**UFW blocks everything after enabling:**
- SSH (22) and HTTP (80) should be allowed before enabling
- If locked out, use VPS console to disable: `sudo ufw disable`

**Firewall rules not created automatically:**
- Check sudo permissions: `sudo -l | grep ufw`
- Check app logs: `pm2 logs ai-desktop`
