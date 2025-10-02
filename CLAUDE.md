# AI Desktop - Project Context

## Project Overview
Web-based AI desktop environment (macOS/Windows-style interface in browser) with workflow automation, file management, terminal, and app ecosystem.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS 4, Framer Motion, Radix UI, Lucide Icons

**Deployment Target:** VPS with GitHub CI/CD pipeline → Build on VPS → Access via `vps-url:port`

---

## Quick Commands

```bash
# Development
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint check

# VPS Deployment (future)
git push origin main # Triggers pipeline → VPS pull → rebuild
pm2 restart ai-desktop # Manual restart on VPS
```

---

## Architecture

### Current State (Organized for VPS)
```
app/
├── api/                    # API routes (Next.js SSR/API)
│   ├── changelog/         # Version & changelog endpoint
│   │   └── route.ts
│   └── update/            # Update trigger endpoint
│       └── route.ts
├── page.tsx                # Entry point → renders Desktop
├── layout.tsx              # Root layout
└── globals.css             # Global styles (neutral color palette)

components/
├── apps/                   # Desktop applications
│   ├── app-store.tsx
│   ├── changelog.tsx      # ✨ NEW: Version management & updates
│   ├── chat-interface.tsx
│   ├── file-manager.tsx
│   ├── installed-apps.tsx
│   ├── mac-app-store.tsx
│   ├── system-monitor.tsx
│   ├── terminal.tsx
│   └── workflow-canvas.tsx
├── desktop/                # Desktop shell
│   ├── desktop.tsx
│   ├── desktop-context-menu.tsx
│   ├── desktop-icon-context-menu.tsx
│   ├── floating-dock-demo.tsx
│   ├── system-control-menu.tsx
│   ├── taskbar.tsx
│   └── window.tsx
├── auth/                   # Auth components
│   └── two-factor-auth.tsx
└── ui/                     # Shadcn components

config/
└── site.ts                 # App configuration

data/
├── desktop-apps.ts         # App configs
├── file-manager-data.ts    # Mock file data
└── installed-apps-data.ts  # Installed apps data

deployment/                 # VPS deployment files
├── auto-update.sh         # ✨ Auto-update script (polls GitHub)
├── deploy.sh              # Deployment script
├── ecosystem.config.js    # PM2 config (runs on port 80)
├── nginx.conf             # Nginx template (deprecated)
└── SETUP_AUTO_UPDATE.md   # Auto-update setup guide

version.json                # ✨ Version tracking (semantic versioning)

hooks/
├── use-desktop.ts          # Window management
├── use-file-manager.ts     # File operations
└── use-toast.ts            # Toast notifications

types/
└── index.ts                # Centralized type exports

utils/
├── desktop-utils.ts        # Window utilities
└── icon-mapper.ts          # Icon registry
```

### Future State (With Backend in Same App)
```
Frontend (Next.js Client) → app/api routes (SSR) → PostgreSQL
                                                 → Redis (sessions)
                                                 → OAuth services
```

---

## Code Conventions

### Icons
- **Always use icon-mapper.ts** - Never import Lucide icons directly in components
- Icon names are strings (e.g., `"Terminal"`, `"Folder"`, `"GitBranch"`)
- Get icons: `const IconComponent = getIcon("Terminal")`
- **Available icons:** See `iconRegistry` in `utils/icon-mapper.ts`
- **If icon doesn't exist in Lucide:** Remove from import and registry (e.g., `Tool` icon was removed)

### Components
- All components are **client-side** (`"use client"`)
- Use TypeScript interfaces for props
- Prefer Radix UI for accessible components
- Use Tailwind for styling (no CSS modules)

### State Management
- React hooks (`useState`, `useCallback`, `useEffect`)
- Custom hooks in `hooks/` for complex logic
- **No global state library yet** (Redux/Zustand not needed until backend)

### Styling
- Tailwind utility classes
- Dark mode: `dark:` prefix (controlled by `useTheme` hook)
- Glass effect: `glass-effect` custom class
- Responsive: `md:`, `lg:` breakpoints

### File Organization
- **Components:** One component per file, PascalCase naming
- **Hooks:** `use-*` prefix, kebab-case
- **Utils:** Pure functions, kebab-case
- **Data:** Mock data files, kebab-case

---

## Key Features & Implementation Notes

### 1. Window Management (components/window.tsx, hooks/use-desktop.ts)
- Draggable windows (drag from header)
- Resizable (8 resize handles: corners + edges)
- Minimize/Maximize/Close (macOS-style traffic lights)
- Z-index management (active window on top)
- Window constraints (can't drag off screen)
- **State:** Position, size, minimized/maximized flags
- **Animation:** Framer Motion for open/close

### 2. Authentication (components/two-factor-auth.tsx)
- **CURRENT:** Client-side only (fake 2FA)
- **ISSUE:** Can be bypassed via browser console
- **TODO:** Replace with NextAuth.js or Supabase Auth

### 3. Terminal (components/terminal.tsx)
- **CURRENT:** Mock terminal (simulated commands: `help`, `ls`, `clear`)
- **TODO for VPS:**
  - Backend WebSocket server
  - Spawn isolated Docker containers per user
  - OR keep as command simulator (safer)

### 4. Workflow Canvas (components/workflow-canvas.tsx)
- Visual node-based workflow builder
- **CURRENT:** Mock execution (setTimeout animations)
- **TODO for VPS:**
  - Backend API to execute workflows
  - Store OAuth tokens securely (GitHub, Slack, OpenAI)
  - Queue system (Bull/BullMQ)
  - Database persistence

### 5. File Manager (components/file-manager.tsx)
- **CURRENT:** Mock file system (data/file-manager-data.ts)
- **TODO for VPS:**
  - Backend file storage (S3, local filesystem with permissions)
  - Upload/download endpoints
  - User-isolated directories

### 6. Version Management & Update System ✨ NEW
- **Semantic Versioning:** v1.0.0 format (MAJOR.MINOR.PATCH)
- **Version Tracking:** `version.json` stores version, build date, current SHA
- **Auto-Detection:** Compares local SHA with GitHub latest commit
- **Visual Indicators:** "Update Available" badge when new version exists
- **One-Click Updates:** "Update Now" button triggers VPS script
- **Changelog Viewer:** Full-screen window (Power → Recent Updates)
  - Shows version badge, build info, commit SHA
  - Displays last 10 commits with author, date, GitHub links
  - Version comparison (current → latest SHA)
  - Update progress with loading states
  - Success/error messages with auto-reload
- **API Endpoints:**
  - `GET /api/changelog` - Version info & update availability
  - `POST /api/update` - Triggers `auto-update.sh` script on VPS
- **Auto-Update Script:** `deployment/auto-update.sh`
  - Polls GitHub for new commits every 5 min (cron job)
  - Executes: git pull → npm install → build → PM2 restart
  - Logs all activities to `logs/auto-update.log`

---

## Security Considerations

### Critical Issues (Before Production)
1. **2FA is fake** - Replace with real backend auth
2. **No user isolation** - All state is in browser memory
3. **Terminal** - If made real, requires containerization
4. **API keys** - Must be stored server-side, never in client code
5. **File uploads** - Need virus scanning, size limits, type validation

### VPS Deployment Checklist
- [ ] Environment variables (`.env.local` → VPS `.env`)
- [ ] HTTPS with SSL (Let's Encrypt)
- [ ] Rate limiting (nginx or API middleware)
- [ ] Input validation on all forms
- [ ] CORS configuration
- [ ] CSP headers
- [ ] Database connection pooling
- [ ] Error logging (Sentry, LogRocket)

---

## Database Schema (Future)

```sql
-- Users
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  password_hash VARCHAR,
  totp_secret VARCHAR,
  created_at TIMESTAMP
)

-- Window States (persist desktop layout)
windows (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  app_id VARCHAR,
  position JSONB,  -- {x, y}
  size JSONB,      -- {width, height}
  is_minimized BOOLEAN,
  is_maximized BOOLEAN,
  z_index INTEGER
)

-- Workflows
workflows (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  name VARCHAR,
  nodes JSONB,       -- [{id, type, position, ...}]
  connections JSONB, -- [{from, to}]
  is_active BOOLEAN,
  last_run TIMESTAMP
)

-- Files
files (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  name VARCHAR,
  path VARCHAR,
  content TEXT,
  size INTEGER,
  mime_type VARCHAR,
  created_at TIMESTAMP
)
```

---

## VPS Deployment Pipeline

### GitHub Actions Workflow (`.github/workflows/deploy.yml`)
```yaml
name: Deploy to VPS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: SSH to VPS
        run: |
          ssh user@vps-ip "cd /var/www/ai-desktop && \
          git pull origin main && \
          npm install && \
          npm run build && \
          pm2 restart ai-desktop"
```

### VPS Setup Commands
```bash
# Install dependencies
sudo apt update && sudo apt install -y nodejs npm nginx

# Clone repo
git clone <repo-url> /var/www/ai-desktop
cd /var/www/ai-desktop
npm install
npm run build

# Process manager
npm install -g pm2
pm2 start npm --name "ai-desktop" -- start
pm2 startup
pm2 save

# Nginx reverse proxy
sudo nano /etc/nginx/sites-available/ai-desktop
# (See nginx config in docs)
sudo ln -s /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## Environment Variables

```env
# Next.js
NEXT_PUBLIC_APP_URL=https://your-domain.com

# Database (when added)
DATABASE_URL=postgresql://user:pass@localhost:5432/aidesktop

# Auth (when added)
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=https://your-domain.com

# OAuth Integrations (when added)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
OPENAI_API_KEY=
```

---

## Common Issues & Solutions

### Issue: Icon import error
**Error:** `Attempted import error: 'IconName' is not exported from 'lucide-react'`
**Fix:** Remove icon from `utils/icon-mapper.ts` imports and `iconRegistry`

### Issue: Window dragging is laggy
**Fix:** Check if too many event listeners, optimize `handleMouseMove` in `use-desktop.ts`

### Issue: Dark mode not persisting
**Fix:** Add `localStorage` to `useTheme` hook (currently resets on refresh)

### Issue: 2FA bypass
**Fix:** This is expected - current implementation is client-only. Add backend auth.

---

## Development Workflow

### Adding a New App
1. Create component in `components/your-app.tsx`
2. Add to `DOCK_APPS` or `INSTALLED_APPS` in `data/desktop-apps.ts`
3. Register in `getAppComponent` map in `components/desktop.tsx`
4. Add icon to `utils/icon-mapper.ts` if needed
5. Add window config to `WINDOW_CONFIGS` in `data/desktop-apps.ts`

### Adding a New Icon
1. Check if it exists in Lucide React docs
2. Add to imports in `utils/icon-mapper.ts`
3. Add to `iconRegistry` object
4. Use via `getIcon("IconName")`

### Debugging Window Issues
- Check `use-desktop.ts` → `windows` state
- Verify `constrainWindowPosition` isn't over-constraining
- Check z-index in Window component (active = z-50, inactive = z-40)

---

## Testing Notes

- **No tests yet** - Add Jest/Vitest + React Testing Library
- **Manual testing:** Check window drag/resize on all screen sizes
- **Browser support:** Modern browsers only (Chrome, Firefox, Safari, Edge)

---

## Performance Optimization

- Memoize heavy components with `React.memo`
- Use `useCallback` for event handlers (already done in `use-desktop.ts`)
- Virtual scrolling for large lists (workflow nodes, file lists)
- Code splitting: `dynamic()` for heavy components (charts, monaco editor)

---

## Roadmap

### Phase 1: Current (UI Demo)
- ✅ Desktop environment UI
- ✅ Window management
- ✅ Mock apps (Terminal, Workflows, File Manager)
- ✅ Dark/light theme
- ✅ Responsive design

### Phase 2: Backend Integration
- [ ] Real authentication (NextAuth.js/Supabase)
- [ ] Database setup (PostgreSQL)
- [ ] API routes for CRUD operations
- [ ] Persist user desktop state
- [ ] Session management

### Phase 3: Real Features
- [ ] Working terminal (Docker containers)
- [ ] Workflow execution engine
- [ ] Real file storage
- [ ] OAuth integrations (GitHub, Slack, OpenAI)
- [ ] App marketplace backend

### Phase 4: VPS Production
- [ ] GitHub Actions CI/CD
- [ ] SSL certificates
- [ ] Monitoring (uptime, errors)
- [ ] Backups
- [ ] Multi-user support
- [ ] Rate limiting

---

## Contact & Notes

**Project Type:** Web Desktop Environment
**Deployment:** VPS via GitHub pipeline
**Status:** Phase 1 (UI complete, backend needed)

**Important Reminders:**
- All current features are mock/simulated
- Client-side only = no data persistence
- Security must be added before production
- VPS deployment ready for static demo, needs backend for real functionality
