# Current State of VS Code Integration

## What You Had Before (Working)
- One code-server running on port 8888
- Accessed at: `http://92.112.181.127:8888`
- No Nginx needed
- Simple setup that worked

## What We Tried to Build (Complex & Broken)
- Multiple code-server instances (ports 8888-8899)
- Nginx reverse proxy on port 80
- Dynamic URL routing: `/vscode/repo-name/`
- Automatic folder parameter redirects
- Isolated user-data directories for each repo
- **Result: MESSY and CONFUSING**

## Current Problems
1. **Old code-server still running** on port 8888 from before
2. **New code-servers failing** to start (timeout errors)
3. **Multiple implementations mixed together**
4. **Unclear what works and what doesn't**

## Files That Control VS Code

### 1. Code Server Manager
**File**: `lib/vscode/code-server-manager.ts`
**Purpose**: Starts/stops code-server processes
**Status**: Modified many times, probably broken

### 2. Nginx Config Manager
**File**: `lib/vscode/nginx-config.ts`
**Purpose**: Creates Nginx configs for each repo
**Status**: Added redirect logic that might be broken

### 3. Port Manager
**File**: `lib/vscode/port-manager.ts`
**Purpose**: Tracks which ports are in use
**Status**: Works, but database might be corrupted
**Database**: `data/vscode-ports.json`

### 4. Repository Registry
**File**: `lib/repositories/registry.ts`
**Purpose**: Tracks all cloned repositories
**Status**: Should work fine
**Database**: `data/repositories.json`

### 5. VS Code Editor App
**File**: `components/apps/code-editor.tsx`
**Purpose**: UI to start/stop VS Code instances
**Status**: Changed from embedded view to card grid

### 6. Start API Route
**File**: `app/api/code-server/start/route.ts`
**Purpose**: API endpoint to start a VS Code instance
**Status**: Has complex logic for checking existing instances

## What's Currently Installed on VPS

### Old Setup (Still Running!)
```bash
# This old process is STILL running:
PID 884956: /usr/lib/code-server /var/www --auth none --port 8888
```
This is the OLD setup that's blocking everything!

### Installation Scripts
**Files**:
- `deployment/fresh-install.sh`
- `deployment/fresh-install-auto.sh`
- `deployment/nginx-setup.sh`

**Status**: Modified to remove netcat, might have issues

## Clean Up Plan

### Step 1: Kill Everything
```bash
# Kill ALL code-server processes
pkill -9 code-server

# Remove ALL temp data
rm -rf /tmp/code-server-*
rm -rf /var/www/vscode-workspaces

# Clean databases
rm -f /var/www/ai-desktop/data/vscode-ports.json

# Remove old Nginx configs
rm -rf /etc/nginx/vscode-projects/*
```

### Step 2: Decide What You Want

**Option A: Keep it SIMPLE (Recommended)**
- Go back to basic setup
- One code-server on port 8888
- No Nginx complexity
- Direct access: `http://IP:8888`




## My Recommendation

**Let's RESET to SIMPLE and WORKING:**

1. Remove all the complex Nginx stuff
2. Remove port management complexity
3. Remove redirect logic
4. Go back to: **One code-server per repo, accessed directly by port**

This means:
- actmcp → port 8888 → `http://IP:8888`
- pytorch → port 8889 → `http://IP:8889`
- Simple, clean, works

**No Nginx, no redirects, no confusion.**

## What Do You Want?

Please tell me:
1. Do you want SIMPLE (one server, direct port access)?
2. Or do you want COMPLEX (multiple servers, Nginx routing)?

Once you decide, I'll clean up EVERYTHING and give you ONLY what you need.

I'm truly sorry for the confusion. Let's fix this properly, step by step.
