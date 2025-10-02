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
  // ==================== DATABASES ====================

  // Relational (SQL)
  {
    id: 'mysql',
    name: 'MySQL 8.0',
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
    id: 'mysql57',
    name: 'MySQL 5.7',
    category: 'database',
    icon: 'Database',
    description: 'MySQL 5.7 for legacy applications',
    installMethod: 'docker',
    dockerImage: 'mysql:5.7',
    ports: [3307],
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
      port: 3307
    }
  },
  {
    id: 'mariadb',
    name: 'MariaDB',
    category: 'database',
    icon: 'Database',
    description: 'MySQL fork with enhanced features',
    installMethod: 'docker',
    dockerImage: 'mariadb:11',
    ports: [3308],
    volumes: ['/var/lib/mysql'],
    environment: {
      MYSQL_ROOT_PASSWORD: 'changeme'
    },
    windowComponent: 'MariaDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'root',
      password: 'changeme',
      port: 3308
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
    id: 'mssql',
    name: 'Microsoft SQL Server',
    category: 'database',
    icon: 'Database',
    description: 'Microsoft SQL Server for Linux',
    installMethod: 'docker',
    dockerImage: 'mcr.microsoft.com/mssql/server:2022-latest',
    ports: [1433],
    volumes: ['/var/opt/mssql'],
    environment: {
      'ACCEPT_EULA': 'Y',
      'SA_PASSWORD': 'YourStrong@Passw0rd'
    },
    windowComponent: 'MSSQLManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'sa',
      password: 'YourStrong@Passw0rd',
      port: 1433
    }
  },
  {
    id: 'cockroachdb',
    name: 'CockroachDB',
    category: 'database',
    icon: 'Database',
    description: 'Distributed SQL database',
    installMethod: 'docker',
    dockerImage: 'cockroachdb/cockroach:latest',
    ports: [26257, 8080],
    volumes: ['/cockroach/cockroach-data'],
    windowComponent: 'CockroachManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 26257
    }
  },

  // NoSQL Document
  {
    id: 'mongodb',
    name: 'MongoDB 7',
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
    id: 'couchdb',
    name: 'CouchDB',
    category: 'database',
    icon: 'Database',
    description: 'NoSQL document database with HTTP API',
    installMethod: 'docker',
    dockerImage: 'couchdb:latest',
    ports: [5984],
    volumes: ['/opt/couchdb/data'],
    environment: {
      'COUCHDB_USER': 'admin',
      'COUCHDB_PASSWORD': 'changeme'
    },
    windowComponent: 'CouchDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'admin',
      password: 'changeme',
      port: 5984
    }
  },
  {
    id: 'arangodb',
    name: 'ArangoDB',
    category: 'database',
    icon: 'Database',
    description: 'Multi-model database (document, graph, key-value)',
    installMethod: 'docker',
    dockerImage: 'arangodb:latest',
    ports: [8529],
    volumes: ['/var/lib/arangodb3'],
    environment: {
      'ARANGO_ROOT_PASSWORD': 'changeme'
    },
    windowComponent: 'ArangoDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'root',
      password: 'changeme',
      port: 8529
    }
  },

  // Key-Value Stores
  {
    id: 'redis',
    name: 'Redis 7',
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
  {
    id: 'memcached',
    name: 'Memcached',
    category: 'database',
    icon: 'Box',
    description: 'High-performance distributed memory caching',
    installMethod: 'docker',
    dockerImage: 'memcached:alpine',
    ports: [11211],
    windowComponent: 'MemcachedManager',
    defaultWidth: 1000,
    defaultHeight: 600,
    defaultCredentials: {
      port: 11211
    }
  },
  {
    id: 'keydb',
    name: 'KeyDB',
    category: 'database',
    icon: 'Box',
    description: 'Redis fork with better performance',
    installMethod: 'docker',
    dockerImage: 'eqalpha/keydb:latest',
    ports: [6380],
    volumes: ['/data'],
    windowComponent: 'KeyDBManager',
    defaultWidth: 1000,
    defaultHeight: 600,
    defaultCredentials: {
      port: 6380
    }
  },

  // Time-Series
  {
    id: 'influxdb',
    name: 'InfluxDB',
    category: 'database',
    icon: 'Database',
    description: 'Time series database',
    installMethod: 'docker',
    dockerImage: 'influxdb:2.7',
    ports: [8086],
    volumes: ['/var/lib/influxdb2'],
    windowComponent: 'InfluxDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 8086
    }
  },
  {
    id: 'timescaledb',
    name: 'TimescaleDB',
    category: 'database',
    icon: 'Database',
    description: 'PostgreSQL extension for time-series',
    installMethod: 'docker',
    dockerImage: 'timescale/timescaledb:latest-pg16',
    ports: [5433],
    volumes: ['/var/lib/postgresql/data'],
    environment: {
      'POSTGRES_PASSWORD': 'changeme'
    },
    windowComponent: 'TimescaleDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      username: 'postgres',
      password: 'changeme',
      port: 5433
    }
  },
  {
    id: 'questdb',
    name: 'QuestDB',
    category: 'database',
    icon: 'Database',
    description: 'Fast time-series database',
    installMethod: 'docker',
    dockerImage: 'questdb/questdb:latest',
    ports: [9000, 8812],
    volumes: ['/var/lib/questdb'],
    windowComponent: 'QuestDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 9000
    }
  },
  {
    id: 'victoriametrics',
    name: 'VictoriaMetrics',
    category: 'database',
    icon: 'Database',
    description: 'Fast time-series database and monitoring',
    installMethod: 'docker',
    dockerImage: 'victoriametrics/victoria-metrics:latest',
    ports: [8428],
    volumes: ['/victoria-metrics-data'],
    windowComponent: 'VictoriaMetricsManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 8428
    }
  },

  // Column-Family
  {
    id: 'cassandra',
    name: 'Apache Cassandra',
    category: 'database',
    icon: 'Database',
    description: 'Distributed NoSQL database',
    installMethod: 'docker',
    dockerImage: 'cassandra:latest',
    ports: [9042],
    volumes: ['/var/lib/cassandra'],
    windowComponent: 'CassandraManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 9042
    }
  },
  {
    id: 'scylladb',
    name: 'ScyllaDB',
    category: 'database',
    icon: 'Database',
    description: 'Cassandra-compatible, faster',
    installMethod: 'docker',
    dockerImage: 'scylladb/scylla:latest',
    ports: [9043],
    volumes: ['/var/lib/scylla'],
    windowComponent: 'ScyllaDBManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 9043
    }
  },

  // Analytics & Big Data
  {
    id: 'clickhouse',
    name: 'ClickHouse',
    category: 'database',
    icon: 'Database',
    description: 'Fast OLAP database for analytics',
    installMethod: 'docker',
    dockerImage: 'clickhouse/clickhouse-server:latest',
    ports: [8123, 9000],
    volumes: ['/var/lib/clickhouse'],
    windowComponent: 'ClickHouseManager',
    defaultWidth: 1200,
    defaultHeight: 700,
    defaultCredentials: {
      port: 8123
    }
  },

  // ==================== SEARCH ENGINES ====================
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
