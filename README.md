# AI Desktop

A lightweight, web-based AI desktop environment with integrated development tools, deployment automation, and Claude AI integration.

## 🚀 Quick Start (VPS Installation)

### Prerequisites
- Ubuntu/Debian VPS
- Root or sudo access
- Node.js 18+ (installation steps below)

### Installation Steps

```bash
# 1. Install system dependencies
apt update && apt install -y curl git nginx

# 2. Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 3. Install PM2 and code-server
npm install -g pm2
curl -fsSL https://code-server.dev/install.sh | sh

# 4. Clone repository
cd /root
git clone -b lightweight-client https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop

# 5. Install backend dependencies
cd backend
npm install --production
cd ..

# 6. Install frontend dependencies and build
npm install
npm run build

# 7. Configure environment variables (edit as needed)
# Backend: backend/.env
# Frontend: .env

# 8. Create data directories
mkdir -p /var/www/repositories /var/www/github /var/www/ai-desktop/{data,logs}

# 9. Start services
cd backend && pm2 start server.js --name ai-desktop-backend
cd .. && pm2 start npm --name ai-desktop-frontend -- start
pm2 save
pm2 startup

# 10. Configure Nginx (see Nginx Configuration section below)
```

After installation, access AI Desktop at: `http://YOUR_VPS_IP`

---

## 📋 Features

### 🖥️ Desktop Environment
- Draggable, resizable windows
- macOS-inspired interface
- Multiple apps running simultaneously
- Dock with quick access to apps

### 🛠️ Development Tools
- **VS Code Browser**: Full VS Code in the browser (via code-server)
- **GitHub Integration**: Clone and manage repositories
- **File Manager**: Browse and manage files on the VPS
- **Terminal**: Built-in terminal access
- **Deployment System**: One-click deployment for web apps (Next.js, React, Node.js, etc.)

### 🤖 AI Integration
- **Flow Builder**: Visual workflow builder with Claude AI
- **MCP Hub**: Model Context Protocol server management
- **Security Center**: Secure credential storage for integrations

### 📊 System Tools
- **System Monitor**: Real-time CPU, memory, disk usage
- **Service Manager**: Manage system services and PM2 processes
- **Deployment Logs**: Real-time build and runtime logs

---

## 🏗️ Architecture

### Lightweight Design
- **No Database**: Uses JSON file storage for simplicity
- **Development Mode**: Apps run with `npm run dev` for quick deployment
- **PM2 Process Manager**: Reliable process management with auto-restart
- **Nginx Reverse Proxy**: Single entry point for all services

### Storage Structure
```
/root/ai-desktop/              # Application code
/var/www/repositories/         # User git repositories
/var/www/github/               # GitHub clones
/var/www/ai-desktop/
├── data/                      # JSON storage
│   ├── repositories.json
│   ├── deployments.json
│   └── mcp-servers.json
└── logs/                      # Deployment logs
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):
```env
PORT=3006
NODE_ENV=production
FILE_MANAGER_ROOT=/var/www
```

**Frontend** (`.env`):
```env
PORT=3005
NEXT_PUBLIC_API_URL=http://localhost:3006
FILE_MANAGER_ROOT=/var/www
ANTHROPIC_API_KEY=your_api_key_here  # Optional, for Flow Builder
```

---

## 📚 Documentation

- [Lightweight Architecture](docs/LIGHTWEIGHT_CLIENT_ARCHITECTURE.md)
- [Flow Builder Architecture](docs/FLOW_BUILDER_ARCHITECTURE.md)
- [Flow Builder Guide](docs/FLOW_BUILDER_README.md)
- [Security Update Instructions](docs/SECURITY_UPDATE_INSTRUCTIONS.md)

---

## 🛠️ Management Commands

### PM2 Process Management
```bash
pm2 status                      # View all processes
pm2 logs                        # View all logs
pm2 logs ai-desktop-backend     # Backend logs only
pm2 logs ai-desktop-frontend    # Frontend logs only
pm2 restart all                 # Restart all services
pm2 restart ai-desktop-backend  # Restart backend only
```

### Data Management
```bash
# View repositories
cat /var/www/ai-desktop/data/repositories.json

# Clear all repositories
rm -rf /var/www/repositories/*
echo '{"repositories":[]}' > /var/www/ai-desktop/data/repositories.json

# View deployments
cat /var/www/ai-desktop/data/deployments.json
pm2 list | grep deployment  # See running deployments
```

### Nginx Management
```bash
nginx -t                        # Test configuration
systemctl restart nginx         # Restart nginx
systemctl status nginx          # Check status
tail -f /var/log/nginx/error.log  # View error logs
```

---

## 🔐 Security

### Firewall Configuration
The installation script automatically configures UFW to allow:
- Port 22 (SSH)
- Port 80 (HTTP)

### API Keys
- Store API keys in `.env` files (never commit to git)
- Use Security Center in the UI for secure MCP server credentials
- Encryption key auto-generated during installation

---

## 🐛 Troubleshooting

### Backend Not Starting
```bash
pm2 logs ai-desktop-backend
# Check for port conflicts or missing dependencies
```

### Frontend Build Errors
```bash
cd /root/ai-desktop
npm install
npm run build
pm2 restart ai-desktop-frontend
```

### Nginx 502 Error
```bash
# Check if backend is running
pm2 status
# Restart services
pm2 restart all
systemctl restart nginx
```

### Deployment Fails
```bash
# Check deployment logs
ls -la /var/www/ai-desktop/logs/
cat /var/www/ai-desktop/logs/DEPLOYMENT_ID.log

# Check PM2 processes
pm2 list | grep deployment
pm2 logs deployment-DEPLOYMENT_ID
```

---

## 🚧 Development

### Local Development
```bash
# Clone repository
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop

# Install dependencies
npm install
cd backend && npm install && cd ..

# Start backend
cd backend && npm start

# Start frontend (in new terminal)
npm run dev
```

### Branch Information
- `main` - Stable releases
- `lightweight-client` - Latest lightweight architecture (recommended for VPS)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 🙏 Acknowledgments

- Built with Next.js, React, and Express
- Uses Claude AI by Anthropic
- Inspired by macOS interface design
- Powered by code-server for browser-based VS Code

---

## 📞 Support

For issues and questions:
- GitHub Issues: [https://github.com/tajalagawani/ai-desktop/issues](https://github.com/tajalagawani/ai-desktop/issues)

---

**Made with ❤️ for developers who love automation**
