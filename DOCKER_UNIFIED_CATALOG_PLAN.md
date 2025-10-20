# Docker Unified Catalog - Dynamic Service Registry Implementation Plan

## Mission Statement
Build a zero-hardcode, production-ready dynamic service registry that auto-discovers all services (infrastructure + ACT flows), updates in real-time, integrates with Flow Architect agent, properly manages VPS resources, and provides complete cleanup functionality.

## Context & Background

### The Problem
- Service catalog is currently hardcoded in JSON files
- Flow Architect agent reads static catalogs that don't reflect actual running services
- Service Manager and Flow Manager are disconnected systems
- No real-time awareness of what's actually running
- Agent can't generate correct connection strings for actual services
- VPS disk space accumulates with unused Docker images and volumes

### The Vision
Create a unified, dynamic catalog that:
1. **Auto-discovers** services from multiple sources (Docker, GitHub, Docker Hub)
2. **Real-time updates** when services start/stop
3. **Agent integration** - Flow Architect reads live catalog
4. **VPS optimized** - proper cleanup, volume management, image deletion
5. **Zero hardcoding** - everything discovered dynamically

## System Architecture

### Three Core Systems to Unify

1. **Service Manager** (`/api/services`)
   - Manages 100+ infrastructure services (MySQL, PostgreSQL, Redis, etc.)
   - Docker-based installation and management
   - Located in: `app/api/services/route.ts`

2. **Flow Manager** (`/api/flows`)
   - Manages ACT flows (APIs, scheduled tasks, integrations)
   - Discovers .flow files and controls Docker containers
   - Located in: `app/api/flows/route.ts`

3. **Service Catalog** (currently static JSON)
   - Used by Flow Architect agent for workflow generation
   - Current: `flow-architect/catalogs/service-catalog.json`
   - **Will be replaced by:** Dynamic API at `/api/catalog`

### Service Discovery Sources (Hybrid Approach)

1. **Docker SDK (Local)**
   - Inspect running containers
   - Extract metadata from labels
   - Real-time status and resource usage
   - Connection string generation

2. **Docker Hub API**
   - Fetch official image metadata
   - Get latest versions
   - Service descriptions
   - Default configurations

3. **GitHub YAML Registry**
   - Community-curated service definitions
   - Custom AI Desktop configurations
   - Extended metadata not in Docker images

## Implementation Status

### ✅ Phase 1: Docker SDK Foundation (COMPLETED)
- [x] Installed Docker SDK (dockerode) and YAML parser
- [x] Created ServiceRegistry class with Docker integration
- [x] Implemented Docker Hub API fetcher
- [x] Built local Docker image scanner
- [x] Added VPS-optimized cleanup (docker rmi -f)
- [x] Created volume cleanup utilities
- [x] Added disk space monitoring
- **Files created:**
  - `lib/service-registry.ts` - Core ServiceRegistry class

### 🚧 Phase 3: Unified Catalog API (IN PROGRESS)
- [x] Created unified catalog API GET /api/catalog
- [ ] Build catalog merger (infrastructure + flows + external)
- [ ] Add real-time status tracking
- **Files created:**
  - `app/api/catalog/route.ts` - Unified catalog endpoint

### 📋 Phase 2: GitHub Registry (PENDING)
- [ ] Create GitHub YAML registry structure
- [ ] Build service metadata extractor
- [ ] Implement smart label system

### 📋 Phase 4: Flow Integration (PENDING)
- [ ] Extract ACI routes from flow files
- [ ] Build flow metadata parser
- [ ] Hook catalog updater into Flow Manager

### 📋 Phase 5: Agent Integration (PENDING)
- [ ] Update Flow Architect to use live catalog
- [ ] Add connection string generator
- [ ] Implement service availability checker

### 📋 Phase 6: UI Updates (PENDING)
- [ ] Update Service Manager UI
- [ ] Add flow services section
- [ ] Build unified search

### 📋 Phase 7: Testing & Documentation (PENDING)
- [ ] Create VPS cleanup script
- [ ] Test end-to-end integration
- [ ] Document the system

## Key Code Components

### ServiceRegistry Class (`lib/service-registry.ts`)
```typescript
export class ServiceRegistry {
  // Docker Hub API integration
  async fetchFromDockerHub(imageName: string): Promise<ServiceMetadata>

  // Local Docker scanning
  async scanLocalImages(): Promise<ServiceMetadata[]>

  // GitHub registry
  async fetchCommunityRegistry(): Promise<ServiceMetadata[]>

  // Real-time status
  async getContainerStatus(serviceId: string): Promise<ServiceMetadata>

  // Unified catalog
  async getUnifiedCatalog(): Promise<ServiceMetadata[]>

  // VPS management
  async getVPSStatus(): Promise<VPSStatus>
  async cleanupAll(): Promise<CleanupResult>
}
```

### Unified Catalog API (`app/api/catalog/route.ts`)
```typescript
// GET /api/catalog
// Query params: ?type=infrastructure|flow|external&status=running|stopped
// Returns: Unified catalog with all services

// POST /api/catalog/refresh
// Body: { source: 'docker-hub' | 'github' | 'all' | 'cleanup' }
// Refreshes catalog or performs VPS cleanup
```

### Service Metadata Structure
```typescript
interface ServiceMetadata {
  id: string
  name: string
  type: 'infrastructure' | 'flow' | 'external'
  category: string
  status: 'running' | 'stopped' | 'available'

  // Docker info
  dockerImage?: string
  containerName?: string
  ports?: Port[]
  volumes?: string[]

  // Connection info
  connection?: {
    host: string
    port: number
    string?: string  // Full connection string
  }

  // For flows - API endpoints
  endpoints?: {
    path: string
    method: string
    description: string
  }[]

  // Resources (VPS monitoring)
  resources?: {
    cpuPercent?: number
    memoryUsage?: number
    diskUsage?: number
  }
}
```

## VPS-Specific Optimizations

### True Image Deletion
```bash
# Current Service Manager already implements:
docker rm -f <container>      # Remove container
docker volume rm <volumes>     # Remove volumes
docker rmi -f <image>         # FORCE remove image
docker image prune -f         # Clean dangling images
```

### Comprehensive Cleanup
```typescript
// ServiceRegistry.cleanupAll() performs:
1. Stop all AI Desktop containers
2. Remove all containers
3. Remove all volumes
4. Force remove all images
5. System prune
6. Report disk space freed
```

### Disk Space Monitoring
```typescript
// VPSStatus provides:
- Total/used/available disk space
- Docker image count
- Container count
- Volume count
- Total Docker size
```

## Next Implementation Steps

### Immediate Priority: Complete Catalog API
1. **Test the catalog API**
   ```bash
   curl http://localhost:3000/api/catalog
   curl http://localhost:3000/api/catalog?type=flow
   curl http://localhost:3000/api/catalog?status=running
   ```

2. **Fix flow file parsing**
   - Enhance ACI route extraction
   - Parse all node types correctly
   - Extract complete metadata

3. **Add GitHub Registry**
   - Create `ai-desktop/service-registry` repo
   - Define `services.yml` schema
   - Implement fetching in ServiceRegistry

### Integration with Flow Architect

1. **Update agent to use live catalog**
   ```typescript
   // In flow-architect contexts
   const catalog = await fetch('http://localhost:3000/api/catalog')
   const services = catalog.services.filter(s => s.status === 'running')
   ```

2. **Generate correct connection strings**
   ```typescript
   // Based on actually running services
   const postgres = services.find(s => s.id === 'postgresql')
   const connectionString = postgres.connection.string
   ```

## Docker Label System

### Standard Labels for AI Desktop Services
```yaml
labels:
  ai-desktop.service.id: "mysql"
  ai-desktop.service.name: "MySQL 8.0"
  ai-desktop.service.category: "database"
  ai-desktop.service.version: "8.0"
  ai-desktop.service.ports: "3306"
  ai-desktop.service.volumes: "/var/lib/mysql"
  ai-desktop.service.capabilities: "sql,transactions,relations"
```

## Testing Checklist

- [ ] ServiceRegistry can scan local Docker images
- [ ] Catalog API returns all infrastructure services
- [ ] Catalog API returns all flow services
- [ ] Flow endpoints are correctly extracted
- [ ] Real-time status reflects actual container state
- [ ] Connection strings are correctly generated
- [ ] VPS cleanup removes images and volumes
- [ ] Disk space monitoring works
- [ ] Agent can fetch and use live catalog
- [ ] Service Manager shows unified view

## Error Handling & Edge Cases

1. **Docker not running** - Graceful fallback to static catalog
2. **Network issues** - Cache Docker Hub/GitHub data locally
3. **Large catalogs** - Implement pagination
4. **Slow container inspection** - Add caching layer
5. **Disk space critical** - Auto-cleanup old images

## Migration Path

### Phase 1: Shadow Mode
- Keep static catalogs
- Add dynamic catalog alongside
- Log differences for validation

### Phase 2: Agent Migration
- Update agent to prefer dynamic catalog
- Fall back to static if unavailable

### Phase 3: Full Migration
- Remove static catalogs
- All systems use dynamic catalog
- Complete real-time operation

## Environment Variables Needed

```env
# Docker Hub API (optional, for rate limits)
DOCKER_HUB_USERNAME=
DOCKER_HUB_TOKEN=

# GitHub Registry
GITHUB_REGISTRY_URL=https://raw.githubusercontent.com/ai-desktop/service-registry/main/services.yml

# VPS Settings
MAX_DOCKER_DISK_USAGE_GB=50
AUTO_CLEANUP_THRESHOLD_GB=45
```

## Monitoring & Observability

### Health Check Endpoints
- `/api/catalog/health` - Catalog API health
- `/api/catalog/stats` - Service statistics
- `/api/catalog/vps` - VPS resource status

### Metrics to Track
- Catalog refresh time
- Service discovery latency
- Docker API response time
- Disk space usage trend
- Image/container growth rate

## Security Considerations

1. **No credentials in catalog** - Use environment variables
2. **Rate limiting** - Prevent catalog API abuse
3. **Authentication** - Protect cleanup operations
4. **Firewall rules** - Already handled by Service Manager
5. **Container isolation** - Use Docker networks

## Success Criteria

✅ The system is successful when:
1. No hardcoded service definitions remain
2. Agent always has current service information
3. Connection strings are always correct
4. VPS disk space is managed automatically
5. Services auto-register when started
6. UI shows unified service view
7. Flow endpoints are discoverable
8. Complete system cleanup is one command

## Current Git Branch

**Branch:** `docker-unified-catalog`
**Base:** `main`
**Status:** Active development

## Files Modified/Created in This Branch

1. `lib/service-registry.ts` - Core ServiceRegistry class
2. `app/api/catalog/route.ts` - Unified catalog API
3. `.gitignore` - Added temp ACT files pattern
4. `package.json` - Added dockerode and js-yaml

## Commands for Quick Setup

```bash
# Install dependencies
npm install

# Test catalog API
curl http://localhost:3000/api/catalog | jq

# Test VPS status
curl http://localhost:3000/api/catalog | jq '.vps'

# Force cleanup (BE CAREFUL!)
curl -X POST http://localhost:3000/api/catalog/refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "cleanup"}'
```

## Notes for Future Sessions

1. **Priority:** Complete flow endpoint extraction - it's partially working
2. **Remember:** Service Manager already has good cleanup code (lines 271-321)
3. **VPS Focus:** User emphasized volume management and image deletion
4. **Agent Context:** Flow Architect needs live catalog for connection strings
5. **User Preference:** Wants transparency, not hidden implementation details

## Contact & References

- **Original Service Manager:** `app/api/services/route.ts`
- **Original Flow Manager:** `app/api/flows/route.ts`
- **Static Service Catalog:** `flow-architect/catalogs/service-catalog.json`
- **Flow Architect Agent:** `flow-architect/.claude/agents/flow-architect.md`

---

**Last Updated:** 2024-10-20
**Author:** AI Desktop Team with Claude
**Version:** 1.0.0