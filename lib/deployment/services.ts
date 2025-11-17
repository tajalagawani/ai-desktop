import { exec } from 'child_process'
import { promisify } from 'util'
import { RunningService } from './types'
import { INSTALLABLE_SERVICES } from '@/data/installable-services'

const execAsync = promisify(exec)

export async function getRunningServices(): Promise<RunningService[]> {
  try {
    const { stdout } = await execAsync(
      'docker ps --filter "label=ai-desktop-service=true" --format "{{.Names}}|{{.Ports}}"'
    )

    if (!stdout.trim()) {
      return []
    }

    const services: RunningService[] = []

    for (const line of stdout.trim().split('\n')) {
      const [containerName, ports] = line.split('|')
      const serviceId = containerName.replace('ai-desktop-', '')

      // Find service config
      const serviceConfig = INSTALLABLE_SERVICES.find(s => s.id === serviceId)
      if (!serviceConfig) continue

      // Extract port number from Docker port mapping (e.g., "0.0.0.0:3306->3306/tcp")
      const portMatch = ports.match(/0\.0\.0\.0:(\d+)/)
      const port = portMatch ? parseInt(portMatch[1]) : serviceConfig.ports?.[0] || 0

      // Get credentials
      const credentials = serviceConfig.defaultCredentials

      // Generate connection string
      const connectionString = generateConnectionString(
        serviceId,
        port,
        credentials
      )

      services.push({
        id: serviceId,
        name: serviceConfig.name,
        containerName,
        port,
        type: getCategoryType(serviceConfig.category),
        category: serviceConfig.category,
        connectionString,
        credentials
      })
    }

    return services
  } catch (error: any) {
    console.error('Error getting running services:', error)
    return []
  }
}

function getCategoryType(category: string): RunningService['type'] {
  switch (category) {
    case 'database':
      return 'database'
    case 'queue':
      return 'queue'
    case 'search':
      return 'search'
    case 'tool':
      return 'tool'
    default:
      // Redis, KeyDB, Memcached are databases but also cache
      return 'other'
  }
}

function generateConnectionString(
  serviceId: string,
  port: number,
  credentials?: { username?: string; password?: string; port?: number }
): string {
  const host = 'localhost'
  const user = credentials?.username || 'root'
  const pass = credentials?.password || ''

  switch (serviceId) {
    case 'mysql':
    case 'mysql57':
    case 'mariadb':
      return `mysql://${user}:${pass}@${host}:${port}/`

    case 'postgresql':
    case 'timescaledb':
      return `postgresql://${user}:${pass}@${host}:${port}/postgres`

    case 'mongodb':
      return `mongodb://${host}:${port}`

    case 'redis':
    case 'keydb':
      return `redis://${host}:${port}`

    case 'couchdb':
      return `http://${user}:${pass}@${host}:${port}`

    case 'arangodb':
      return `http://${host}:${port}`

    case 'neo4j':
      return `bolt://${host}:${port}`

    case 'influxdb':
      return `http://${host}:${port}`

    case 'questdb':
      return `http://${host}:${port}`

    case 'victoriametrics':
      return `http://${host}:${port}`

    case 'cassandra':
    case 'scylladb':
      return `${host}:${port}`

    case 'clickhouse':
      return `http://${host}:${port}`

    case 'elasticsearch':
      return `http://${host}:${port}`

    case 'rabbitmq':
      return `amqp://${user}:${pass}@${host}:${port}`

    case 'mssql':
      return `sqlserver://${host}:${port}`

    case 'cockroachdb':
      return `postgresql://${host}:${port}/defaultdb?sslmode=disable`

    case 'memcached':
      return `${host}:${port}`

    default:
      return `http://${host}:${port}`
  }
}

export function generateEnvVarsFromServices(
  services: RunningService[],
  customEnvVars: Record<string, string> = {}
): Record<string, string> {
  const envVars: Record<string, string> = { ...customEnvVars }

  for (const service of services) {
    const prefix = getEnvPrefix(service.id)

    // Add connection string
    envVars[`${prefix}_URL`] = service.connectionString

    // Add individual connection details
    envVars[`${prefix}_HOST`] = 'localhost'
    envVars[`${prefix}_PORT`] = service.port.toString()

    if (service.credentials?.username) {
      envVars[`${prefix}_USER`] = service.credentials.username
    }

    if (service.credentials?.password) {
      envVars[`${prefix}_PASSWORD`] = service.credentials.password
    }

    // Add database name for SQL databases
    if (['mysql', 'mysql57', 'mariadb', 'postgresql', 'timescaledb'].includes(service.id)) {
      envVars[`${prefix}_DATABASE`] = 'app_db'
    }
  }

  return envVars
}

function getEnvPrefix(serviceId: string): string {
  switch (serviceId) {
    case 'mysql':
    case 'mysql57':
    case 'mariadb':
      return 'MYSQL'
    case 'postgresql':
    case 'timescaledb':
      return 'POSTGRES'
    case 'mongodb':
      return 'MONGO'
    case 'redis':
    case 'keydb':
      return 'REDIS'
    case 'elasticsearch':
      return 'ELASTICSEARCH'
    case 'rabbitmq':
      return 'RABBITMQ'
    default:
      return serviceId.toUpperCase().replace(/-/g, '_')
  }
}
