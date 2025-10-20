import Docker from 'dockerode'
import yaml from 'js-yaml'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// Service metadata structure for unified catalog
export interface ServiceMetadata {
  id: string
  name: string
  type: 'infrastructure' | 'flow' | 'external'
  category: string
  description: string
  version?: string
  dockerImage?: string
  status: 'running' | 'stopped' | 'available' | 'not-installed'

  // Runtime information
  containerName?: string
  containerId?: string
  ports?: {
    internal: number
    external: number
    protocol: string
  }[]
  volumes?: string[]
  environment?: Record<string, string>

  // Connection information
  connection?: {
    host: string
    port: number
    string?: string
    username?: string
    password?: string
  }

  // Capabilities
  capabilities?: string[]
  endpoints?: {
    path: string
    method: string
    description: string
  }[]

  // Labels (for Docker-based discovery)
  labels?: Record<string, string>

  // Resources (VPS monitoring)
  resources?: {
    cpuPercent?: number
    memoryUsage?: number
    diskUsage?: number
  }

  // Source of discovery
  source: 'docker-local' | 'docker-hub' | 'github-registry' | 'flow-file'
}

// VPS resource monitoring
export interface VPSStatus {
  diskSpace: {
    total: string
    used: string
    available: string
    usedPercent: string
  }
  docker: {
    imageCount: number
    containerCount: number
    volumeCount: number
    totalSize: string
  }
}

export class ServiceRegistry {
  private docker: Docker
  private communityRegistryUrl = 'https://raw.githubusercontent.com/ai-desktop/service-registry/main/services.yml'
  private dockerHubApiBase = 'https://hub.docker.com/v2'

  constructor() {
    // Connect to Docker socket
    this.docker = new Docker({ socketPath: '/var/run/docker.sock' })
  }

  /**
   * Fetch service metadata from Docker Hub API
   */
  async fetchFromDockerHub(imageName: string): Promise<Partial<ServiceMetadata> | null> {
    try {
      const [repository, tag] = imageName.split(':')
      const [namespace, repo] = repository.includes('/')
        ? repository.split('/')
        : ['library', repository]

      const url = `${this.dockerHubApiBase}/repositories/${namespace}/${repo}`
      const response = await fetch(url)

      if (!response.ok) {
        return null
      }

      const data = await response.json()

      return {
        name: data.name || repo,
        description: data.description || '',
        version: tag || 'latest',
        source: 'docker-hub',
        type: 'infrastructure'
      }
    } catch (error) {
      console.warn(`Failed to fetch Docker Hub metadata for ${imageName}:`, error)
      return null
    }
  }

  /**
   * Scan local Docker images with ai-desktop labels
   */
  async scanLocalImages(): Promise<ServiceMetadata[]> {
    try {
      const images = await this.docker.listImages()
      const services: ServiceMetadata[] = []

      for (const image of images) {
        const labels = image.Labels || {}

        // Only process images with ai-desktop labels
        if (labels['ai-desktop.service.id']) {
          const serviceId = labels['ai-desktop.service.id']
          const imageName = image.RepoTags?.[0] || 'unknown'

          services.push({
            id: serviceId,
            name: labels['ai-desktop.service.name'] || serviceId,
            type: 'infrastructure',
            category: labels['ai-desktop.service.category'] || 'unknown',
            description: labels['ai-desktop.service.description'] || '',
            version: labels['ai-desktop.service.version'] || 'latest',
            dockerImage: imageName,
            status: 'available',
            source: 'docker-local',
            labels,
            ports: this.extractPortsFromLabels(labels),
            volumes: this.extractVolumesFromLabels(labels),
            capabilities: this.extractCapabilitiesFromLabels(labels)
          })
        }
      }

      return services
    } catch (error) {
      console.error('Failed to scan local images:', error)
      return []
    }
  }

  /**
   * Fetch popular services from Docker Hub
   */
  async fetchPopularServices(): Promise<ServiceMetadata[]> {
    const popularServices = [
      // Databases
      { image: 'mongo', name: 'MongoDB', category: 'database', port: 27017, description: 'NoSQL document database' },
      { image: 'postgres', name: 'PostgreSQL', category: 'database', port: 5432, description: 'Advanced relational database' },
      { image: 'mysql', name: 'MySQL', category: 'database', port: 3306, description: 'Popular relational database' },
      { image: 'redis', name: 'Redis', category: 'database', port: 6379, description: 'In-memory data store' },
      { image: 'neo4j', name: 'Neo4j', category: 'database', port: 7474, description: 'Graph database' },
      { image: 'mariadb', name: 'MariaDB', category: 'database', port: 3306, description: 'MySQL fork' },
      { image: 'cassandra', name: 'Cassandra', category: 'database', port: 9042, description: 'Distributed NoSQL database' },
      { image: 'couchdb', name: 'CouchDB', category: 'database', port: 5984, description: 'Document database with HTTP API' },
      { image: 'influxdb', name: 'InfluxDB', category: 'database', port: 8086, description: 'Time series database' },
      { image: 'elasticsearch', name: 'Elasticsearch', category: 'search', port: 9200, description: 'Search and analytics engine' },

      // Message Queues
      { image: 'rabbitmq', name: 'RabbitMQ', category: 'queue', port: 5672, description: 'Message broker' },
      { image: 'kafka', name: 'Apache Kafka', category: 'queue', port: 9092, description: 'Distributed streaming platform' },

      // Web Servers
      { image: 'nginx', name: 'Nginx', category: 'web-server', port: 80, description: 'High-performance web server' },
      { image: 'httpd', name: 'Apache HTTP', category: 'web-server', port: 80, description: 'Apache web server' },

      // Caching
      { image: 'memcached', name: 'Memcached', category: 'database', port: 11211, description: 'Memory caching system' },

      // Tools
      { image: 'phpmyadmin', name: 'phpMyAdmin', category: 'tool', port: 80, description: 'MySQL web interface' },
      { image: 'adminer', name: 'Adminer', category: 'tool', port: 8080, description: 'Database management tool' }
    ]

    const services: ServiceMetadata[] = []

    for (const svc of popularServices) {
      try {
        const metadata = await this.fetchFromDockerHub(svc.image)

        services.push({
          id: svc.image.replace('/', '-'),
          name: svc.name,
          type: 'infrastructure',
          category: svc.category,
          description: metadata?.description || svc.description,
          version: 'latest',
          dockerImage: `${svc.image}:latest`,
          status: 'available',
          source: 'docker-hub',
          ports: [{
            internal: svc.port,
            external: svc.port,
            protocol: 'tcp'
          }],
          volumes: [],
          environment: {}
        })
      } catch (error) {
        // If Docker Hub fetch fails, add with basic info
        services.push({
          id: svc.image.replace('/', '-'),
          name: svc.name,
          type: 'infrastructure',
          category: svc.category,
          description: svc.description,
          version: 'latest',
          dockerImage: `${svc.image}:latest`,
          status: 'available',
          source: 'docker-hub',
          ports: [{
            internal: svc.port,
            external: svc.port,
            protocol: 'tcp'
          }],
          volumes: [],
          environment: {}
        })
      }
    }

    return services
  }

  /**
   * Fetch community-curated service registry from GitHub
   */
  async fetchCommunityRegistry(): Promise<ServiceMetadata[]> {
    try {
      const response = await fetch(this.communityRegistryUrl)

      if (!response.ok) {
        // Fallback to popular services if community registry not available
        return this.fetchPopularServices()
      }

      const yamlContent = await response.text()
      const registry = yaml.load(yamlContent) as any

      if (!registry?.services) {
        return this.fetchPopularServices()
      }

      return registry.services.map((service: any) => ({
        id: service.id,
        name: service.name,
        type: 'external' as const,
        category: service.category || 'unknown',
        description: service.description || '',
        version: service.version || 'latest',
        dockerImage: service.dockerImage,
        status: 'available' as const,
        source: 'github-registry' as const,
        ports: service.ports?.map((p: number) => ({
          internal: p,
          external: p,
          protocol: 'tcp'
        })) || [],
        volumes: service.volumes || [],
        environment: service.environment || {},
        labels: service.labels || {},
        capabilities: service.capabilities || []
      }))
    } catch (error) {
      console.warn('Failed to fetch community registry, using popular services:', error)
      return this.fetchPopularServices()
    }
  }

  /**
   * Get real-time status of a specific service container
   */
  async getContainerStatus(serviceId: string): Promise<Partial<ServiceMetadata>> {
    try {
      const containerName = `ai-desktop-${serviceId}`
      const containers = await this.docker.listContainers({ all: true })

      const containerInfo = containers.find(c =>
        c.Names.some(n => n.includes(containerName))
      )

      if (!containerInfo) {
        return { status: 'not-installed' }
      }

      const container = this.docker.getContainer(containerInfo.Id)
      const inspect = await container.inspect()
      const stats = await container.stats({ stream: false })

      // Extract connection information from container
      const ports = this.extractActualPorts(containerInfo.Ports)
      const mainPort = ports[0]?.external

      return {
        status: containerInfo.State === 'running' ? 'running' : 'stopped',
        containerName: containerInfo.Names[0]?.replace(/^\//, ''),
        containerId: containerInfo.Id.substring(0, 12),
        ports,
        connection: mainPort ? {
          host: 'localhost',
          port: mainPort,
          string: this.generateConnectionString(serviceId, mainPort, inspect.Config.Env)
        } : undefined,
        resources: {
          cpuPercent: this.calculateCpuPercent(stats),
          memoryUsage: stats.memory_stats?.usage || 0,
          diskUsage: 0 // Will be calculated separately
        }
      }
    } catch (error) {
      return { status: 'not-installed' }
    }
  }

  /**
   * Get unified catalog merging all sources
   */
  async getUnifiedCatalog(): Promise<ServiceMetadata[]> {
    const [localImages, communityServices] = await Promise.all([
      this.scanLocalImages(),
      this.fetchCommunityRegistry()
    ])

    // Merge and deduplicate
    const servicesMap = new Map<string, ServiceMetadata>()

    // Add local images first (highest priority)
    for (const service of localImages) {
      servicesMap.set(service.id, service)
    }

    // Add community services if not already in local
    for (const service of communityServices) {
      if (!servicesMap.has(service.id)) {
        servicesMap.set(service.id, service)
      }
    }

    // Get running containers and update status
    const containers = await this.docker.listContainers({ all: true })

    for (const [serviceId, service] of servicesMap.entries()) {
      const containerStatus = await this.getContainerStatus(serviceId)
      servicesMap.set(serviceId, { ...service, ...containerStatus })
    }

    return Array.from(servicesMap.values())
  }

  /**
   * Get VPS disk space and Docker resource usage
   */
  async getVPSStatus(): Promise<VPSStatus> {
    try {
      // Get disk space for /var/lib/docker
      const { stdout: dfOutput } = await execAsync('df -h /var/lib/docker | tail -1')
      const [, total, used, available, usedPercent] = dfOutput.trim().split(/\s+/)

      // Get Docker system info
      const { stdout: dockerDf } = await execAsync('docker system df --format "{{json .}}"')

      // Count Docker resources
      const images = await this.docker.listImages()
      const containers = await this.docker.listContainers({ all: true })
      const volumes = await this.docker.listVolumes()

      // Get total Docker disk usage
      const { stdout: dockerSize } = await execAsync(
        'docker system df --format "{{.Size}}" | head -1'
      )

      return {
        diskSpace: {
          total,
          used,
          available,
          usedPercent: usedPercent.replace('%', '')
        },
        docker: {
          imageCount: images.length,
          containerCount: containers.length,
          volumeCount: volumes.Volumes?.length || 0,
          totalSize: dockerSize.trim()
        }
      }
    } catch (error) {
      console.error('Failed to get VPS status:', error)
      throw error
    }
  }

  /**
   * Comprehensive cleanup for VPS - removes ALL AI Desktop resources
   */
  async cleanupAll(): Promise<{
    containersRemoved: number
    imagesRemoved: number
    volumesRemoved: number
    diskFreed: string
  }> {
    try {
      const beforeStatus = await this.getVPSStatus()

      // 1. Stop and remove all AI Desktop containers
      const { stdout: containerIds } = await execAsync(
        'docker ps -aq --filter "label=ai-desktop-service=true"'
      )
      const containers = containerIds.trim().split('\n').filter(Boolean)

      if (containers.length > 0) {
        await execAsync(`docker rm -f ${containers.join(' ')}`)
      }

      // 2. Remove all AI Desktop volumes
      const { stdout: volumeIds } = await execAsync(
        'docker volume ls -q --filter "name=ai-desktop"'
      )
      const volumes = volumeIds.trim().split('\n').filter(Boolean)

      if (volumes.length > 0) {
        await execAsync(`docker volume rm ${volumes.join(' ')}`)
      }

      // 3. Remove all AI Desktop images
      const { stdout: imageIds } = await execAsync(
        'docker images -q --filter "label=ai-desktop.service.id"'
      )
      const images = imageIds.trim().split('\n').filter(Boolean)

      if (images.length > 0) {
        await execAsync(`docker rmi -f ${images.join(' ')}`)
      }

      // 4. Prune system
      await execAsync('docker system prune -af --volumes')

      const afterStatus = await this.getVPSStatus()

      return {
        containersRemoved: containers.length,
        imagesRemoved: images.length,
        volumesRemoved: volumes.length,
        diskFreed: this.calculateDiskFreed(beforeStatus, afterStatus)
      }
    } catch (error) {
      console.error('Cleanup failed:', error)
      throw error
    }
  }

  // ===== Helper Methods =====

  private extractPortsFromLabels(labels: Record<string, string>) {
    const portsLabel = labels['ai-desktop.service.ports']
    if (!portsLabel) return []

    return portsLabel.split(',').map(p => ({
      internal: parseInt(p),
      external: parseInt(p),
      protocol: 'tcp'
    }))
  }

  private extractVolumesFromLabels(labels: Record<string, string>): string[] {
    const volumesLabel = labels['ai-desktop.service.volumes']
    return volumesLabel ? volumesLabel.split(',') : []
  }

  private extractCapabilitiesFromLabels(labels: Record<string, string>): string[] {
    const capsLabel = labels['ai-desktop.service.capabilities']
    return capsLabel ? capsLabel.split(',') : []
  }

  private extractActualPorts(ports: any[]) {
    return ports.map(p => ({
      internal: p.PrivatePort,
      external: p.PublicPort || p.PrivatePort,
      protocol: p.Type || 'tcp'
    }))
  }

  private generateConnectionString(
    serviceId: string,
    port: number,
    env: string[]
  ): string {
    // Parse environment variables
    const envMap = new Map<string, string>()
    env.forEach(e => {
      const [key, value] = e.split('=')
      envMap.set(key, value)
    })

    // Generate connection string based on service type
    if (serviceId.includes('postgres')) {
      const password = envMap.get('POSTGRES_PASSWORD') || 'changeme'
      const db = envMap.get('POSTGRES_DB') || 'postgres'
      return `postgresql://postgres:${password}@localhost:${port}/${db}`
    }

    if (serviceId.includes('mysql')) {
      const password = envMap.get('MYSQL_ROOT_PASSWORD') || 'changeme'
      const db = envMap.get('MYSQL_DATABASE') || 'mysql'
      return `mysql://root:${password}@localhost:${port}/${db}`
    }

    if (serviceId.includes('redis')) {
      return `redis://localhost:${port}`
    }

    if (serviceId.includes('mongodb')) {
      const password = envMap.get('MONGO_INITDB_ROOT_PASSWORD') || 'changeme'
      return `mongodb://root:${password}@localhost:${port}`
    }

    return `tcp://localhost:${port}`
  }

  private calculateCpuPercent(stats: any): number {
    try {
      const cpuDelta = stats.cpu_stats.cpu_usage.total_usage -
                       stats.precpu_stats.cpu_usage.total_usage
      const systemDelta = stats.cpu_stats.system_cpu_usage -
                         stats.precpu_stats.system_cpu_usage
      const cpuCount = stats.cpu_stats.online_cpus || 1

      if (systemDelta > 0 && cpuDelta > 0) {
        return (cpuDelta / systemDelta) * cpuCount * 100
      }
    } catch {}

    return 0
  }

  private calculateDiskFreed(before: VPSStatus, after: VPSStatus): string {
    const beforeUsed = parseFloat(before.diskSpace.used)
    const afterUsed = parseFloat(after.diskSpace.used)
    const freed = beforeUsed - afterUsed

    return `${freed.toFixed(2)}G`
  }
}
