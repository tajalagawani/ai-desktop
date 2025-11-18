# VPS Deployment Scripts

This directory contains automated deployment scripts for AI Desktop on VPS.

## Quick Start

```bash
SSH_PASSWORD='your_password' \
  ./vps-complete-install.sh \
  root@YOUR_VPS_IP \
  sk-ant-api03-YOUR_API_KEY
```

## Files

- **vps-complete-install.sh** - Complete automated installation from scratch
- **README.md** - This file

## Requirements

- Clean Ubuntu 20.04/22.04 VPS
- Root SSH access
- `sshpass` installed locally

## What It Installs

- Node.js 22
- PM2
- Nginx
- ACT System
- AI Desktop
- All dependencies

## Time

~10-15 minutes

## Documentation

See parent directory:
- `QUICK_INSTALL.md` - Quick reference
- `VPS_COMPLETE_INSTALLATION_GUIDE.md` - Full guide
- `DEPLOYMENT_SUMMARY.md` - Technical details
