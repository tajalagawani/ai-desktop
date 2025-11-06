# Deploy Todo API - Instructions

## Overview

The **Todo API** flow has been created at:
```
/Users/tajnoah/Downloads/ai-desktop/flow-architect/flows/todo-api.flow
```

This is a complete task management API with full CRUD operations.

## Configuration

- **Agent Name**: `todo-api-agent`
- **Port**: `9001`
- **Mode**: Agent (Persistent Service)
- **Database**: Neon PostgreSQL (requires DATABASE_URL env var)

## Endpoints

Once deployed, the following endpoints will be available:

### List All Todos
```bash
GET http://localhost:9001/api/todos
```

### Create Todo
```bash
POST http://localhost:9001/api/todos
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high"
}
```

### Get Specific Todo
```bash
GET http://localhost:9001/api/todos/:id
```

### Update Todo
```bash
PUT http://localhost:9001/api/todos/:id
Content-Type: application/json

{
  "status": "completed",
  "priority": "low"
}
```

### Delete Todo
```bash
DELETE http://localhost:9001/api/todos/:id
```

### Filter by Status
```bash
GET http://localhost:9001/api/todos/status/pending
GET http://localhost:9001/api/todos/status/completed
```

## Deployment Methods

### Method 1: Python Script (Recommended)

Run the deployment script:

```bash
cd /Users/tajnoah/Downloads/ai-desktop/flow-architect
python3 deploy-todo-api.py
```

This script will:
- Call the deployment API
- Wait for service to start
- Check health status
- Display access information

### Method 2: Direct API Call (curl)

```bash
curl -X POST http://localhost:3000/api/flows \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "flowName": "todo-api"
  }'
```

### Method 3: Via ACT Execute API

If the flow file is already in the flows directory, you can also use:

```bash
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d "{
    \"flowContent\": \"$(cat flows/todo-api.flow)\",
    \"flowName\": \"todo-api.flow\"
  }"
```

This will automatically deploy if it detects agent configuration.

## What Happens During Deployment

1. **Docker Compose Generation**
   - Python script reads the .flow file
   - Generates docker-compose.yml entry for this service
   - Configures port mapping (9001:9000)

2. **Container Creation**
   - Docker pulls ACT base image (if not present)
   - Creates container named `act-todo-api`
   - Mounts flow file into container
   - Sets up networking

3. **Service Startup**
   - ACT runtime initializes
   - Creates Neon database table (todos)
   - Registers API routes
   - Starts Flask server on port 9001
   - Health endpoint becomes available

4. **Verification**
   - System checks container is running
   - Polls health endpoint at `/health`
   - Confirms API routes are accessible

## Checking Deployment Status

### Check if service is running:
```bash
docker ps | grep todo-api
```

### Check service health:
```bash
curl http://localhost:9001/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent": "todo-api-agent",
  "version": "1.0.0",
  "uptime": "..."
}
```

### View logs:
```bash
docker logs act-todo-api
```

Or via API:
```bash
curl "http://localhost:3000/api/flows?flowName=todo-api&action=logs&lines=100"
```

### Get detailed status:
```bash
curl http://localhost:3000/api/flows | jq '.flows[] | select(.name == "todo-api")'
```

## Testing the API

### 1. Create a todo:
```bash
curl -X POST http://localhost:9001/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test todo",
    "description": "Testing the API",
    "priority": "medium"
  }'
```

### 2. List all todos:
```bash
curl http://localhost:9001/api/todos
```

### 3. Get specific todo:
```bash
curl http://localhost:9001/api/todos/1
```

### 4. Update todo:
```bash
curl -X PUT http://localhost:9001/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### 5. Filter by status:
```bash
curl http://localhost:9001/api/todos/status/completed
```

### 6. Delete todo:
```bash
curl -X DELETE http://localhost:9001/api/todos/1
```

## Managing the Service

### Stop the service:
```bash
curl -X POST http://localhost:3000/api/flows \
  -H "Content-Type: application/json" \
  -d '{"action": "stop", "flowName": "todo-api"}'
```

### Restart the service:
```bash
curl -X POST http://localhost:3000/api/flows \
  -H "Content-Type: application/json" \
  -d '{"action": "restart", "flowName": "todo-api"}'
```

### Remove the service:
```bash
curl -X POST http://localhost:3000/api/flows \
  -H "Content-Type: application/json" \
  -d '{"action": "remove", "flowName": "todo-api"}'
```

## Database Schema

The service automatically creates this table on first run:

```sql
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);
CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority);
```

## Environment Variables

The flow requires a DATABASE_URL environment variable. This should be configured in:

```
/Users/tajnoah/Downloads/ai-desktop/signature-system/signatures/user.act.sig
```

Or set in the ACT Docker environment.

## Troubleshooting

### Service won't start
1. Check if port 9001 is already in use:
   ```bash
   lsof -i :9001
   ```

2. Check Docker logs:
   ```bash
   docker logs act-todo-api
   ```

3. Verify Docker is running:
   ```bash
   docker ps
   ```

### Database connection fails
1. Verify DATABASE_URL is set in signature file
2. Check Neon database is accessible
3. Verify credentials are correct

### Health check fails
1. Wait 10-15 seconds after starting (service needs time to initialize)
2. Check logs for Python errors
3. Verify all node types (neon, aci, py) are available

## Flow File Location

The complete flow definition is at:
```
/Users/tajnoah/Downloads/ai-desktop/flow-architect/flows/todo-api.flow
```

You can view it with:
```bash
cat /Users/tajnoah/Downloads/ai-desktop/flow-architect/flows/todo-api.flow
```

## Next Steps

After deployment:

1. **Test basic functionality** - Create, read, update, delete todos
2. **Integrate with frontend** - Use the API in a web application
3. **Add authentication** - Extend with user authentication if needed
4. **Monitor usage** - Check logs and health endpoint
5. **Scale if needed** - Adjust Docker resources as usage grows

---

**Ready to deploy!** Run one of the deployment methods above to start the Todo API service.
