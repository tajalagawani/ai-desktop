# AI Desktop

A modern, web-based desktop environment built with Next.js, featuring workflow automation, file management, terminal access, and an integrated app ecosystem.

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
git clone https://github.com/yourusername/ai-desktop.git
cd ai-desktop

# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
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

### Prerequisites

- Ubuntu 20.04+ VPS
- Node.js 18+ installed
- PM2 installed globally: `npm install -g pm2`
- Nginx installed: `sudo apt install nginx`
- Domain name (optional but recommended)

### Initial VPS Setup

```bash
# 1. SSH into your VPS
ssh user@your-vps-ip

# 2. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 3. Install PM2
sudo npm install -g pm2

# 4. Install Nginx
sudo apt install -y nginx

# 5. Clone your repository
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
cd /var/www
git clone https://github.com/yourusername/ai-desktop.git
cd ai-desktop

# 6. Install dependencies and build
npm install
npm run build

# 7. Configure PM2
pm2 start deployment/ecosystem.config.js
pm2 save
pm2 startup

# 8. Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ai-desktop
# Edit the file and replace your-domain.com with your actual domain
sudo ln -s /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 9. Your app should now be running!
# Visit http://your-vps-ip or http://your-domain.com
```

### GitHub Actions CI/CD

This project includes automated deployment via GitHub Actions.

**Setup:**

1. Generate SSH key on your VPS:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions"
   cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
   cat ~/.ssh/id_ed25519  # Copy this private key
   ```

2. Add secrets to your GitHub repository:
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VPS_HOST`: Your VPS IP or domain
     - `VPS_USER`: SSH username (e.g., `ubuntu`, `deploy`)
     - `VPS_SSH_KEY`: The private key from step 1
     - `VPS_PORT`: SSH port (optional, default is 22)

3. Push to main branch:
   ```bash
   git push origin main
   # Deployment will trigger automatically!
   ```

### Manual Deployment

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Run the deployment script
cd /var/www/ai-desktop
bash deployment/deploy.sh
```

## 🔒 SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is set up automatically
# Test renewal: sudo certbot renew --dry-run
```

After SSL is set up, uncomment the HTTPS server block in `/etc/nginx/sites-available/ai-desktop`.

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
- **Deployment:** PM2 + Nginx on VPS

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
