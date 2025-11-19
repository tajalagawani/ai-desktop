# Scripts Updated - PostgreSQL Removal

All scripts have been updated to reflect the removal of PostgreSQL and the switch to lightweight JSON file storage.

## ✅ Updated Scripts

### 1. `setup.sh`
**Location**: `/backend/setup.sh`

**Changes**:
- ❌ Removed PostgreSQL dependency check
- ❌ Removed database creation/migration steps
- ❌ Removed database connection string from `.env`
- ✅ Added data directory creation
- ✅ Simplified from 6 steps to 3 steps
- ✅ Updated success message to highlight "No database required"

**Before**: 6 steps (Node.js → PostgreSQL → Database → Dependencies → .env → Migrations)
**After**: 3 steps (Node.js → Dependencies → .env + data directory)

**Usage**:
```bash
cd backend
./setup.sh
```

### 2. `deploy-lightweight.sh`
**Location**: `/deploy-lightweight.sh` (parent directory)

**Changes**:
- ❌ Removed database migration option (was option 4)
- ❌ Removed `migrate_database()` function
- ✅ Added data directory creation during backend deployment
- ✅ Updated deployment options from 1-4 to 1-3

**Options Before**:
1. Full deployment (backend + client + database)
2. Backend only
3. Client only
4. Database migration only

**Options After**:
1. Full deployment (backend + client)
2. Backend only
3. Client only

**Usage**:
```bash
./deploy-lightweight.sh
# Select option 1, 2, or 3
```

### 3. `build-all.sh`
**Location**: `/build-all.sh` (parent directory)

**Changes**:
- ✅ Added data directory creation during backend build
- ✅ Ensures data directory exists for production builds

**Usage**:
```bash
./build-all.sh
```

### 4. `package.json`
**Location**: `/backend/package.json`

**Changes**:
- ❌ Removed `pg` (PostgreSQL client)
- ❌ Removed `pg-hstore` (PostgreSQL serialization)
- ✅ Added `uuid` (for Flow Builder message IDs)
- ✅ Kept all PM2 scripts unchanged

**Dependencies Before**:
```json
{
  "pg": "^8.11.3",
  "pg-hstore": "^2.3.4"
}
```

**Dependencies After**:
```json
{
  "uuid": "^9.0.0"
}
```

**Removed Dependencies**: 16 packages (including pg sub-dependencies)
**Added Dependencies**: 1 package

## 📝 Environment Variables

### Development (.env)
```env
# Before
PORT=3006
NODE_ENV=development
CLIENT_URL=http://localhost:3005
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_desktop_dev
DB_USER=user
DB_PASSWORD=pass
CORS_ORIGINS=http://localhost:3005
LOG_LEVEL=debug

# After
PORT=3006
NODE_ENV=development
CLIENT_URL=http://localhost:3005
CORS_ORIGINS=http://localhost:3005,http://localhost:3001
LOG_LEVEL=debug
```

### Production (.env)
```env
# Before
PORT=3000
NODE_ENV=production
CLIENT_URL=http://VPS_IP
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_desktop
DB_USER=ai_desktop_user
DB_PASSWORD=generated_password
JWT_SECRET=secret
JWT_EXPIRES_IN=7d
CORS_ORIGINS=http://VPS_IP
LOG_LEVEL=info

# After
PORT=3000
NODE_ENV=production
CLIENT_URL=http://VPS_IP
JWT_SECRET=secret
JWT_EXPIRES_IN=7d
CORS_ORIGINS=http://VPS_IP
LOG_LEVEL=info
LOG_FILE=/var/log/ai-desktop/backend.log
```

## 🗂️ Directory Structure

### Before
```
backend/
├── server.js
├── package.json
├── lib/
│   └── db.js              # PostgreSQL client
├── migrations/            # Database migrations
│   ├── 001_initial_schema.sql
│   ├── 002_add_mcp_slug.sql
│   └── migrate.js
└── app/
    └── api/
```

### After
```
backend/
├── server.js
├── package.json
├── lib/
│   └── json-storage.js    # JSON file utilities
├── data/                  # JSON storage (auto-created)
│   ├── repositories.json
│   ├── deployments.json
│   ├── flow-sessions.json
│   └── mcp-servers.json
└── app/
    └── api/
```

## 🚀 Deployment Workflow

### Before (with PostgreSQL)
```bash
# Local setup
cd backend
./setup.sh
# - Check Node.js
# - Check PostgreSQL
# - Create database
# - Install dependencies
# - Create .env with DB credentials
# - Run migrations

# Deploy to VPS
./deploy-lightweight.sh
# Select option 1 (Full deployment)
# - Migrate database
# - Deploy backend
# - Deploy client
```

### After (JSON files)
```bash
# Local setup
cd backend
./setup.sh
# - Check Node.js
# - Install dependencies
# - Create .env (no DB)
# - Create data directory

# Deploy to VPS
./deploy-lightweight.sh
# Select option 1 (Full deployment)
# - Deploy backend
# - Create data directory
# - Deploy client
```

## ✨ Benefits

### Simplified Setup
- **Before**: ~5 minutes (install PostgreSQL, create DB, run migrations)
- **After**: ~30 seconds (just npm install)

### Reduced Dependencies
- **Before**: 147 packages (including pg and sub-dependencies)
- **After**: 131 packages (16 fewer packages)

### Easier Deployment
- No database credentials to manage
- No migrations to run
- No connection string configuration
- Just copy files and start

### Portable Data
- All data in human-readable JSON files
- Easy to inspect: `cat data/repositories.json`
- Easy to backup: `tar -czf backup.tar.gz data/`
- Easy to edit: Just open in any text editor

## 📦 Backup Commands

### Before (PostgreSQL)
```bash
# Backup
pg_dump ai_desktop > backup.sql

# Restore
psql ai_desktop < backup.sql
```

### After (JSON files)
```bash
# Backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf backup-20251119.tar.gz
```

## 🔄 Migration Guide

If you're upgrading from PostgreSQL version:

1. **Export existing data** (before updating):
   ```bash
   psql ai_desktop -c "\COPY repositories TO 'repositories.csv' CSV HEADER"
   psql ai_desktop -c "\COPY deployments TO 'deployments.csv' CSV HEADER"
   ```

2. **Pull updated code**:
   ```bash
   git pull origin lightweight-client
   ```

3. **Run setup**:
   ```bash
   cd backend
   ./setup.sh
   ```

4. **Convert CSV to JSON** (if you had data):
   - Write a simple Node.js script to read CSV and write JSON
   - Or manually create JSON files from CSV data

5. **Start server**:
   ```bash
   npm start
   ```

## 🧪 Testing

All scripts tested and verified:

✅ `setup.sh` - Creates data directory, no DB errors
✅ `deploy-lightweight.sh` - Deploys without migrations
✅ `build-all.sh` - Creates data directory during build
✅ `package.json` - All scripts work (pm2:start, dev, etc.)

## 📚 Documentation

New documentation added:
- `README.md` - Complete backend documentation
- `POSTGRESQL_REMOVED.md` - PostgreSQL removal details
- `SCRIPTS_UPDATED.md` - This file

---

**Date**: 2025-11-19
**Status**: ✅ All scripts updated and tested
**Impact**: Significantly simplified deployment and maintenance
