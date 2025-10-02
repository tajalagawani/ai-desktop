// Installable Services Registry

export interface ServiceConfig {
  id: string
  name: string
  category: 'database' | 'web-server' | 'runtime' | 'tool' | 'queue' | 'search'
  icon: string
  description: string
  version?: string

  // Installation config
  installMethod: 'docker' | 'apt' | 'snap'
  dockerImage?: string
  ports?: number[]
  volumes?: string[]
  environment?: Record<string, string>

  // UI config
  windowComponent: string
  defaultWidth: number
  defaultHeight: number

  // Service control
  startCommand?: string
  stopCommand?: string
  statusCommand?: string

  // Documentation
  documentation?: string
  defaultCredentials?: {
    username?: string
    password?: string
    port?: number
  }
}

export const INSTALLABLE_SERVICES: ServiceConfig[] = [
  // Databases
  {
    id: 'mysql',
    name: 'MySQL',
    category: 'database',
    icon: 'Database',
    description: 'Popular open-source relational database',
    installMethod: 'docker',
    dockerImage: 'mysql:8.0',
    ports: [3306],
    volumes: ['/var/lib/mysql'],
    environment: {
      MYSQL_ROOT_PASSWORD: 'changeme'
    },
    windowComponent: 'MySQLManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'root',
      password: 'changeme',
      port: 3306
    }
  },
  {
    id: 'neo4j',
    name: 'Neo4j',
    category: 'database',
    icon: 'Network',
    description: 'Graph database for connected data',
    installMethod: 'docker',
    dockerImage: 'neo4j:latest',
    ports: [7474, 7687],
    volumes: ['/data', '/logs'],
    environment: {
      NEO4J_AUTH: 'neo4j/password'
    },
    windowComponent: 'Neo4jBrowser',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      username: 'neo4j',
      password: 'password',
      port: 7474
    }
  },
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    category: 'database',
    icon: 'Database',
    description: 'Advanced open-source relational database',
    installMethod: 'docker',
    dockerImage: 'postgres:16',
    ports: [5432],
    volumes: ['/var/lib/postgresql/data'],
    environment: {
      POSTGRES_PASSWORD: 'changeme'
    },
    windowComponent: 'PostgreSQLManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'postgres',
      password: 'changeme',
      port: 5432
    }
  },
  {
    id: 'mongodb',
    name: 'MongoDB',
    category: 'database',
    icon: 'Database',
    description: 'NoSQL document database',
    installMethod: 'docker',
    dockerImage: 'mongo:7',
    ports: [27017],
    volumes: ['/data/db'],
    windowComponent: 'MongoDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 27017
    }
  },
  {
    id: 'redis',
    name: 'Redis',
    category: 'database',
    icon: 'Box',
    description: 'In-memory data structure store',
    installMethod: 'docker',
    dockerImage: 'redis:7-alpine',
    ports: [6379],
    volumes: ['/data'],
    windowComponent: 'RedisManager',
    defaultWidth: 1000,
    defaultHeight: 600,
    defaultCredentials: {
      port: 6379
    }
  },

  // Web Servers
  {
    id: 'nginx',
    name: 'Nginx',
    category: 'web-server',
    icon: 'Server',
    description: 'High-performance web server',
    installMethod: 'docker',
    dockerImage: 'nginx:alpine',
    ports: [8080],
    volumes: ['/usr/share/nginx/html', '/etc/nginx/conf.d'],
    windowComponent: 'NginxManager',
    defaultWidth: 1200,
    defaultHeight: 800
  },

  // Runtimes
  {
    id: 'php',
    name: 'PHP-FPM',
    category: 'runtime',
    icon: 'Code',
    description: 'PHP FastCGI Process Manager',
    installMethod: 'docker',
    dockerImage: 'php:8.3-fpm',
    ports: [9000],
    volumes: ['/var/www/html'],
    windowComponent: 'PHPManager',
    defaultWidth: 1000,
    defaultHeight: 700
  },

  // Tools
  {
    id: 'phpmyadmin',
    name: 'phpMyAdmin',
    category: 'tool',
    icon: 'Database',
    description: 'MySQL web administration tool',
    installMethod: 'docker',
    dockerImage: 'phpmyadmin:latest',
    ports: [8081],
    environment: {
      PMA_HOST: 'mysql'
    },
    windowComponent: 'PHPMyAdmin',
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'adminer',
    name: 'Adminer',
    category: 'tool',
    icon: 'Database',
    description: 'Database management in a single file',
    installMethod: 'docker',
    dockerImage: 'adminer:latest',
    ports: [8082],
    windowComponent: 'Adminer',
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // Search
  {
    id: 'elasticsearch',
    name: 'Elasticsearch',
    category: 'search',
    icon: 'Search',
    description: 'Distributed search and analytics engine',
    installMethod: 'docker',
    dockerImage: 'elasticsearch:8.11.0',
    ports: [9200, 9300],
    volumes: ['/usr/share/elasticsearch/data'],
    environment: {
      'discovery.type': 'single-node',
      'xpack.security.enabled': 'false'
    },
    windowComponent: 'ElasticsearchManager',
    defaultWidth: 1200,
    defaultHeight: 800
  },

  // Message Queues
  {
    id: 'rabbitmq',
    name: 'RabbitMQ',
    category: 'queue',
    icon: 'Layers',
    description: 'Message broker for distributed systems',
    installMethod: 'docker',
    dockerImage: 'rabbitmq:3-management',
    ports: [5672, 15672],
    windowComponent: 'RabbitMQManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      username: 'guest',
      password: 'guest',
      port: 15672
    }
  }
]

export const SERVICE_CATEGORIES = [
  { id: 'database', name: 'Databases', icon: 'Database' },
  { id: 'web-server', name: 'Web Servers', icon: 'Server' },
  { id: 'runtime', name: 'Runtimes', icon: 'Code' },
  { id: 'tool', name: 'Tools', icon: 'Wrench' },
  { id: 'queue', name: 'Message Queues', icon: 'Layers' },
  { id: 'search', name: 'Search Engines', icon: 'Search' }
]
