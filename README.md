# AI Desktop

A modern, web-based desktop environment built with Next.js, featuring workflow automation, file management, terminal access, and an integrated app ecosystem.

**🌐 Live Demo:** http://92.112.181.127

![AI Desktop](public/placeholder.jpg)

## ✨ Features

- 🖥️ **Desktop Environment** - Full macOS-style desktop interface in the browser
- 🪟 **Window Management** - Draggable, resizable windows with minimize/maximize
- ⚡ **Workflow Automation** - Visual workflow builder with node-based editor
- 📁 **File Manager** - Browse and manage files
- 💻 **Terminal** - Integrated terminal interface (simulated)
- 📊 **System Monitor** - Real-time system performance metrics
- 🤖 **AI Chat Interface** - Built-in AI assistant
- 🎨 **Dark/Light Mode** - Theme switching
- 🔐 **2FA Authentication** - Two-factor authentication (UI only, backend needed)

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop

# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Production Deployment

**See [CLEAN_DEPLOY.md](CLEAN_DEPLOY.md) for the simplest deployment method (runs directly on port 80)**

```bash
# Quick deploy on VPS
ssh root@your-vps
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
npm install
npm run build
pm2 start deployment/ecosystem.config.js
pm2 save
```

## 📁 Project Structure

```
ai-desktop/
├── app/                    # Next.js app directory
│   ├── api/               # API routes (future backend)
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
│
├── components/
│   ├── apps/              # Desktop applications
│   │   ├── app-store.tsx
│   │   ├── file-manager.tsx
│   │   ├── terminal.tsx
│   │   ├── workflow-canvas.tsx
│   │   └── ...
│   ├── desktop/           # Desktop shell components
│   │   ├── desktop.tsx
│   │   ├── taskbar.tsx
│   │   ├── window.tsx
│   │   └── ...
│   ├── auth/              # Authentication components
│   └── ui/                # Reusable UI components (shadcn/ui)
│
├── config/                # App configuration
├── data/                  # Mock data (for now)
├── deployment/            # VPS deployment files
│   ├── deploy.sh         # Deployment script
│   ├── ecosystem.config.js # PM2 configuration
│   └── nginx.conf        # Nginx configuration
├── hooks/                 # Custom React hooks
├── lib/                   # Utility libraries
├── public/                # Static assets
├── types/                 # TypeScript types
└── utils/                 # Helper functions
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
# Add more as you implement backend features
```

### Site Configuration

Edit `config/site.ts` to customize app settings:

```typescript
export const siteConfig = {
  name: "AI Desktop",
  description: "Your description",
  url: "https://your-domain.com",
}
```

## 🌐 VPS Deployment

**⚡ Quick Deploy:** See [CLEAN_DEPLOY.md](CLEAN_DEPLOY.md) for the fastest method (5 minutes)

**📚 Detailed Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions

### Simple VPS Setup (Port 80 Direct)

```bash
ssh root@your-vps
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

Run the PM2 startup command it outputs, then visit `http://your-vps-ip`

### Update Deployed App

```bash
cd /var/www/ai-desktop
git pull origin main
npm install
npm run build
pm2 restart ai-desktop
```

### Useful Commands

```bash
pm2 status              # Check app status
pm2 logs ai-desktop     # View logs
pm2 restart ai-desktop  # Restart app
pm2 monit              # Monitor resources
```

## 🛠️ Development

### Adding a New App

1. Create component in `components/apps/your-app.tsx`
2. Add to `DOCK_APPS` or `INSTALLED_APPS` in `data/desktop-apps.ts`
3. Register in `getAppComponent` in `components/desktop/desktop.tsx`
4. Add window config to `WINDOW_CONFIGS` in `data/desktop-apps.ts`

### Adding a New Icon

1. Check if it exists in [Lucide React](https://lucide.dev)
2. Add to imports in `utils/icon-mapper.ts`
3. Add to `iconRegistry` object
4. Use via `getIcon("IconName")`

## 📚 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 4
- **UI Components:** Radix UI + shadcn/ui
- **Icons:** Lucide React
- **Animation:** Framer Motion
- **Deployment:** PM2 on VPS (runs directly on port 80)

## 🎯 Roadmap

### Phase 1: ✅ UI Demo (Current)
- ✅ Desktop environment UI
- ✅ Window management
- ✅ Mock apps
- ✅ VPS deployment ready

### Phase 2: 🔄 Backend Integration (Next)
- [ ] Real authentication (NextAuth.js/Supabase)
- [ ] Database setup (PostgreSQL)
- [ ] API routes for CRUD operations
- [ ] User session management

### Phase 3: 🚀 Real Features
- [ ] Working terminal (Docker containers)
- [ ] Workflow execution engine
- [ ] Real file storage
- [ ] OAuth integrations

### Phase 4: 📊 Production
- [ ] Multi-user support
- [ ] Rate limiting
- [ ] Monitoring & analytics
- [ ] Automated backups

## 🐛 Troubleshooting

### Build fails with TypeScript errors
```bash
# TypeScript errors are currently ignored in next.config.mjs
# Fix types gradually and remove ignoreBuildErrors
```

### PM2 process not starting
```bash
pm2 logs ai-desktop
pm2 describe ai-desktop
```

### Nginx not proxying correctly
```bash
sudo nginx -t  # Test configuration
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Port 3000 already in use
```bash
# Find process
lsof -i :3000
# Kill it
kill -9 <PID>
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-desktop/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ai-desktop/discussions)

---

Built with ❤️ using Next.js
