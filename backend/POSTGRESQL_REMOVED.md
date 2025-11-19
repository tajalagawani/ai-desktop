# PostgreSQL Removed - Lightweight JSON Storage

## Summary

Successfully removed PostgreSQL completely and converted all backend APIs to use lightweight JSON file storage. The application is now truly lightweight with no database dependencies.

## What Changed

### Files Converted to JSON Storage

1. **Repositories API** (`app/api/repositories.js`)
   - Storage: `data/repositories.json`
   - Operations: Create, Read, Update, Delete repositories
   - Tracks VS Code instances, ports, and running status

2. **Deployments API** (`app/api/deployments.js`)
   - Storage: `data/deployments.json`
   - Operations: Create, start, stop, restart, delete deployments
   - PM2 process management still works as before

3. **VS Code Manager API** (`app/api/vscode.js`)
   - Storage: `data/repositories.json` (shared with repositories)
   - Operations: Start/stop code-server instances
   - Process tracking with PIDs

4. **Flow Builder API** (`app/api/flow-builder.js`)
   - Storage: `data/flow-sessions.json`
   - Operations: Session and message management
   - In-memory message storage within sessions

5. **MCP Hub API** (`app/api/mcp.js`)
   - Storage: Already using `.mcp.json` and `data/mcp-servers.json`
   - No changes needed (already file-based)

6. **Services Manager API** (`app/api/services.js`)
   - Storage: Already using `/tmp/services.json`
   - No changes needed (already file-based)

7. **Git Config API** (`app/api/git-config.js`)
   - No storage needed (directly uses git commands)
   - No changes needed

### Files Removed

- `/backend/lib/db.js` - PostgreSQL connection pool
- `/backend/migrations/` - All migration files
  - `001_initial_schema.sql`
  - `002_add_mcp_slug.sql`
  - `migrate.js`

### Dependencies Changed

**Removed:**
- `pg` (PostgreSQL client)
- `pg-hstore` (PostgreSQL serialization)

**Added:**
- `uuid` (For generating message IDs in flow builder)

### New Files Created

1. **JSON Storage Helper** (`lib/json-storage.js`)
   - `readJSON(filePath)` - Read JSON file safely
   - `writeJSON(filePath, data)` - Write JSON file with pretty formatting
   - `getDataPath(filename)` - Get path to data directory

2. **Data Directory** (`data/`)
   - Created automatically on first write
   - Stores all JSON files:
     - `repositories.json`
     - `deployments.json`
     - `flow-sessions.json`
     - `mcp-servers.json` (already existed)

## Benefits

### Lightweight
- No database server required
- No connection pools or complex query management
- Simple file I/O operations

### Portable
- All data in human-readable JSON files
- Easy to backup (just copy `data/` directory)
- Easy to migrate between machines

### Simpler Deployment
- No database setup required
- No migrations to run
- Just copy files and run

### Development
- Easy to inspect data (just open JSON files)
- Easy to reset (just delete JSON files)
- No database GUI tools needed

## Data Structure Examples

### Repositories (`data/repositories.json`)
```json
{
  "repositories": [
    {
      "id": 1,
      "name": "my-project",
      "path": "/Users/user/projects/my-project",
      "type": "git",
      "port": 8100,
      "url": "http://localhost:8100",
      "branch": "main",
      "running": true,
      "pid": 12345,
      "created_at": "2025-11-19T18:00:00.000Z",
      "updated_at": "2025-11-19T18:30:00.000Z"
    }
  ]
}
```

### Deployments (`data/deployments.json`)
```json
{
  "deployments": [
    {
      "id": 1,
      "repositoryId": 1,
      "name": "my-project",
      "domain": null,
      "port": 3000,
      "status": "running",
      "mode": "fork",
      "instances": 1,
      "pid": 23456,
      "memory": null,
      "cpu": null,
      "uptime": null,
      "createdAt": "2025-11-19T18:00:00.000Z",
      "updatedAt": "2025-11-19T18:30:00.000Z"
    }
  ]
}
```

### Flow Sessions (`data/flow-sessions.json`)
```json
{
  "sessions": [
    {
      "id": 1,
      "status": "idle",
      "prompt": "Create a contact form",
      "output": null,
      "messages": [
        {
          "id": "uuid-here",
          "sessionId": 1,
          "role": "user",
          "content": "Create a contact form",
          "toolResults": [],
          "createdAt": "2025-11-19T18:00:00.000Z"
        }
      ],
      "userId": "default-user",
      "createdAt": "2025-11-19T18:00:00.000Z",
      "updatedAt": "2025-11-19T18:30:00.000Z"
    }
  ]
}
```

## Testing Results

All endpoints tested and working:

✅ `GET /api/repositories` - List repositories
✅ `POST /api/repositories` - Create repository
✅ `PUT /api/repositories` - Update repository
✅ `DELETE /api/repositories` - Delete repository

✅ `GET /api/deployments` - List deployments
✅ `POST /api/deployments` - Create deployment
✅ `POST /api/deployments/:id/action` - Start/stop/restart/delete

✅ `GET /api/vscode/list` - List repositories
✅ `POST /api/vscode/start` - Start code-server
✅ `POST /api/vscode/stop` - Stop code-server

✅ `GET /api/flow-builder/sessions` - List sessions
✅ `POST /api/flow-builder/sessions` - Create session
✅ `PATCH /api/flow-builder/sessions/:id` - Update session
✅ `DELETE /api/flow-builder/sessions/:id` - Delete session
✅ `GET /api/flow-builder/messages` - List messages
✅ `POST /api/flow-builder/messages` - Create message

✅ `GET /api/mcp` - List MCP servers (reads from config files)
✅ `POST /api/mcp/:id/action` - Start/stop MCP servers

## Migration Steps (if you have existing data)

If you had data in PostgreSQL that you want to migrate:

1. **Export existing data** (before upgrading):
   ```bash
   # Export repositories
   psql $DATABASE_URL -c "COPY repositories TO '/tmp/repositories.csv' CSV HEADER;"

   # Export deployments
   psql $DATABASE_URL -c "COPY deployments TO '/tmp/deployments.csv' CSV HEADER;"
   ```

2. **Convert to JSON** (after upgrading):
   - Write a simple script to read CSV and write JSON
   - Or manually create JSON files from CSV data

3. **Place files in data directory**:
   ```bash
   cp converted-data.json backend/data/repositories.json
   ```

## Server Startup

The server now shows:

```
╔═══════════════════════════════════════════════╗
║                                               ║
║   🚀 AI Desktop Backend Server                ║
║                                               ║
║   Environment: development                    ║
║   Port: 3006                                  ║
║   Health: http://localhost:3006/health        ║
║   API: http://localhost:3006/api              ║
║                                               ║
║   Socket.IO: ✅ Ready                          ║
║   CORS: ✅ Configured                          ║
║   Storage: ✅ JSON Files (Lightweight)         ║
║   MCP: ✅ Reading from config files            ║
║                                               ║
╚═══════════════════════════════════════════════╝
```

## Environment Variables

You can now **remove** these from your `.env`:
- `DATABASE_URL` (no longer needed)
- Any PostgreSQL-related variables

Keep these:
- `PORT` - Server port (default: 3006 on Mac, 3000 on VPS)
- `NODE_ENV` - Environment (development/production)
- `CLIENT_URL` - Frontend URL for CORS

## Backup Strategy

Since all data is in JSON files, backing up is simple:

```bash
# Backup all data
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data/

# Restore from backup
tar -xzf backup-20251119.tar.gz -C backend/
```

## Deployment

No special deployment steps needed:

1. Copy `backend/` directory to server
2. Run `npm install`
3. Run `node server.js` or `pm2 start server.js`
4. Done!

No database setup, no migrations, no connection strings.

---

**Date**: 2025-11-19
**Status**: ✅ Complete and Tested
**Impact**: Significantly simplified - removed ~16 dependencies, removed database complexity
