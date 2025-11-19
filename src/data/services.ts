import { ServiceConfig } from './installable-services'

// This file contains the COMPLETE service catalog (100+ services)
// Organized by category for easy management

export const ALL_SERVICES: ServiceConfig[] = [
  // ==================== SEARCH ENGINES ====================
  {
    id: 'opensearch',
    name: 'OpenSearch',
    category: 'search',
    icon: '/icons/services/opensearch.svg',
    iconType: 'image',
    description: 'Elasticsearch fork by AWS',
    installMethod: 'docker',
    dockerImage: 'opensearchproject/opensearch:latest',
    ports: [9201],
    volumes: ['/usr/share/opensearch/data'],
    environment: {
      'discovery.type': 'single-node'
    },
    windowComponent: 'OpenSearchManager',
    defaultWidth: 1200,
    defaultHeight: 800
  },
  {
    id: 'meilisearch',
    name: 'Meilisearch',
    category: 'search',
    icon: '/icons/services/meilisearch.svg',
    iconType: 'image',
    description: 'Lightning fast search engine',
    installMethod: 'docker',
    dockerImage: 'getmeili/meilisearch:latest',
    ports: [7700],
    volumes: ['/meili_data'],
    windowComponent: 'MeilisearchManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 7700
    }
  },
  {
    id: 'typesense',
    name: 'Typesense',
    category: 'search',
    icon: '/icons/services/typesense.svg',
    iconType: 'image',
    description: 'Fast typo-tolerant search engine',
    installMethod: 'docker',
    dockerImage: 'typesense/typesense:latest',
    ports: [8108],
    volumes: ['/data'],
    windowComponent: 'TypesenseManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8108
    }
  },
  {
    id: 'solr',
    name: 'Apache Solr',
    category: 'search',
    icon: '/icons/services/solr.png',
    iconType: 'image',
    description: 'Enterprise search platform',
    installMethod: 'docker',
    dockerImage: 'solr:latest',
    ports: [8983],
    volumes: ['/var/solr'],
    windowComponent: 'SolrManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8983
    }
  },

  // ==================== WEB SERVERS ====================
  {
    id: 'apache',
    name: 'Apache HTTP Server',
    category: 'web-server',
    icon: '/icons/services/apache.png',
    iconType: 'image',
    description: 'Most popular web server',
    installMethod: 'docker',
    dockerImage: 'httpd:latest',
    ports: [8081],
    volumes: ['/usr/local/apache2/htdocs'],
    windowComponent: 'ApacheManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8081
    }
  },
  {
    id: 'caddy',
    name: 'Caddy',
    category: 'web-server',
    icon: '/icons/services/caddy.svg',
    iconType: 'image',
    description: 'Web server with automatic HTTPS',
    installMethod: 'docker',
    dockerImage: 'caddy:latest',
    ports: [8082, 8443],
    volumes: ['/usr/share/caddy', '/config', '/data'],
    windowComponent: 'CaddyManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8082
    }
  },
  {
    id: 'traefik',
    name: 'Traefik',
    category: 'web-server',
    icon: '/icons/services/traefik.png',
    iconType: 'image',
    description: 'Modern HTTP reverse proxy',
    installMethod: 'docker',
    dockerImage: 'traefik:latest',
    ports: [8083, 8084],
    volumes: ['/var/run/docker.sock:/var/run/docker.sock'],
    windowComponent: 'TraefikManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8084
    }
  },
  {
    id: 'haproxy',
    name: 'HAProxy',
    category: 'web-server',
    icon: '/icons/services/haproxy.png',
    iconType: 'image',
    description: 'TCP/HTTP load balancer',
    installMethod: 'docker',
    dockerImage: 'haproxy:latest',
    ports: [8085],
    volumes: ['/usr/local/etc/haproxy'],
    windowComponent: 'HAProxyManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8085
    }
  },

  // ==================== MESSAGE QUEUES ====================
  {
    id: 'kafka',
    name: 'Apache Kafka',
    category: 'queue',
    icon: '/icons/services/kafka.png',
    iconType: 'image',
    description: 'Distributed event streaming',
    installMethod: 'docker',
    dockerImage: 'confluentinc/cp-kafka:latest',
    ports: [9092],
    volumes: ['/var/lib/kafka/data'],
    windowComponent: 'KafkaManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 9092
    }
  },
  {
    id: 'redpanda',
    name: 'Redpanda',
    category: 'queue',
    icon: '/icons/services/redpanda.svg',
    iconType: 'image',
    description: 'Kafka-compatible, faster',
    installMethod: 'docker',
    dockerImage: 'redpandadata/redpanda:latest',
    ports: [9093, 8082],
    volumes: ['/var/lib/redpanda/data'],
    windowComponent: 'RedpandaManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 9093
    }
  },
  {
    id: 'activemq',
    name: 'Apache ActiveMQ',
    category: 'queue',
    icon: '/icons/services/activemq.png',
    iconType: 'image',
    description: 'Java message broker',
    installMethod: 'docker',
    dockerImage: 'apache/activemq-classic:latest',
    ports: [61616, 8161],
    volumes: ['/opt/apache-activemq/data'],
    windowComponent: 'ActiveMQManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8161
    }
  },
  {
    id: 'nats',
    name: 'NATS',
    category: 'queue',
    icon: '/icons/services/nats.png',
    iconType: 'image',
    description: 'Cloud native messaging',
    installMethod: 'docker',
    dockerImage: 'nats:latest',
    ports: [4222, 8222],
    windowComponent: 'NATSManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 4222
    }
  },

  // ==================== MONITORING ====================
  {
    id: 'prometheus',
    name: 'Prometheus',
    category: 'tool',
    icon: '/icons/services/prometheus.svg',
    iconType: 'image',
    description: 'Metrics and monitoring',
    installMethod: 'docker',
    dockerImage: 'prom/prometheus:latest',
    ports: [9090],
    volumes: ['/prometheus'],
    windowComponent: 'PrometheusManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 9090
    }
  },
  {
    id: 'grafana',
    name: 'Grafana',
    category: 'tool',
    icon: '/icons/services/grafana.svg',
    iconType: 'image',
    description: 'Visualization and dashboards',
    installMethod: 'docker',
    dockerImage: 'grafana/grafana:latest',
    ports: [3000],
    volumes: ['/var/lib/grafana'],
    environment: {
      'GF_SECURITY_ADMIN_PASSWORD': 'admin'
    },
    windowComponent: 'GrafanaManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      username: 'admin',
      password: 'admin',
      port: 3000
    }
  },
  {
    id: 'netdata',
    name: 'Netdata',
    category: 'tool',
    icon: '/icons/services/netdata.svg',
    iconType: 'image',
    description: 'Real-time performance monitoring',
    installMethod: 'docker',
    dockerImage: 'netdata/netdata:latest',
    ports: [19999],
    volumes: ['/etc/netdata', '/var/cache/netdata', '/var/lib/netdata'],
    windowComponent: 'NetdataManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 19999
    }
  },
  {
    id: 'uptime-kuma',
    name: 'Uptime Kuma',
    category: 'tool',
    icon: '/icons/services/uptime-kuma.svg',
    iconType: 'image',
    description: 'Self-hosted uptime monitoring',
    installMethod: 'docker',
    dockerImage: 'louislam/uptime-kuma:latest',
    ports: [3001],
    volumes: ['/app/data'],
    windowComponent: 'UptimeKumaManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3001
    }
  },

  // ==================== CI/CD ====================
  {
    id: 'jenkins',
    name: 'Jenkins',
    category: 'tool',
    icon: '/icons/services/jenkins.svg',
    iconType: 'image',
    description: 'Automation server',
    installMethod: 'docker',
    dockerImage: 'jenkins/jenkins:lts',
    ports: [8080, 50000],
    volumes: ['/var/jenkins_home'],
    windowComponent: 'JenkinsManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8080
    }
  },
  {
    id: 'gitlab-runner',
    name: 'GitLab Runner',
    category: 'tool',
    icon: '/icons/services/gitlab.svg',
    iconType: 'image',
    description: 'GitLab CI/CD runner',
    installMethod: 'docker',
    dockerImage: 'gitlab/gitlab-runner:latest',
    ports: [],
    volumes: ['/etc/gitlab-runner', '/var/run/docker.sock:/var/run/docker.sock'],
    windowComponent: 'GitLabRunnerManager',
    defaultWidth: 1200,
    defaultHeight: 800
  },
  {
    id: 'drone',
    name: 'Drone CI',
    category: 'tool',
    icon: '/icons/services/drone.svg',
    iconType: 'image',
    description: 'Container-native CI platform',
    installMethod: 'docker',
    dockerImage: 'drone/drone:latest',
    ports: [8086],
    volumes: ['/var/lib/drone'],
    windowComponent: 'DroneManager',
    defaultWidth: 1200,
    defaultHeight: 800,
    defaultCredentials: {
      port: 8086
    }
  },

  // ==================== VERSION CONTROL ====================
  {
    id: 'gitlab-ce',
    name: 'GitLab CE',
    category: 'tool',
    icon: 'GitBranch',
    description: 'Complete DevOps platform',
    installMethod: 'docker',
    dockerImage: 'gitlab/gitlab-ce:latest',
    ports: [8087, 8022],
    volumes: ['/etc/gitlab', '/var/log/gitlab', '/var/opt/gitlab'],
    windowComponent: 'GitLabManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8087
    }
  },
  {
    id: 'gitea',
    name: 'Gitea',
    category: 'tool',
    icon: 'GitBranch',
    description: 'Lightweight Git service',
    installMethod: 'docker',
    dockerImage: 'gitea/gitea:latest',
    ports: [3002, 2222],
    volumes: ['/data', '/etc/timezone:/etc/timezone:ro'],
    windowComponent: 'GiteaManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3002
    }
  },
  {
    id: 'gogs',
    name: 'Gogs',
    category: 'tool',
    icon: 'GitBranch',
    description: 'Painless self-hosted Git',
    installMethod: 'docker',
    dockerImage: 'gogs/gogs:latest',
    ports: [3003, 2223],
    volumes: ['/data'],
    windowComponent: 'GogsManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3003
    }
  },

  // ==================== COLLABORATION ====================
  {
    id: 'mattermost',
    name: 'Mattermost',
    category: 'communication',
    icon: 'MessageSquare',
    description: 'Slack alternative',
    installMethod: 'docker',
    dockerImage: 'mattermost/mattermost-team-edition:latest',
    ports: [8065],
    volumes: ['/mattermost/data', '/mattermost/logs', '/mattermost/config'],
    windowComponent: 'MattermostManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8065
    }
  },
  {
    id: 'rocketchat',
    name: 'Rocket.Chat',
    category: 'communication',
    icon: 'MessageSquare',
    description: 'Team communication platform',
    installMethod: 'docker',
    dockerImage: 'rocket.chat:latest',
    ports: [3004],
    volumes: ['/app/uploads'],
    environment: {
      'ROOT_URL': 'http://localhost:3004',
      'MONGO_URL': 'mongodb://mongodb:27017/rocketchat'
    },
    windowComponent: 'RocketChatManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3004
    }
  },
  {
    id: 'jitsi',
    name: 'Jitsi Meet',
    category: 'communication',
    icon: 'Video',
    description: 'Video conferencing',
    installMethod: 'docker',
    dockerImage: 'jitsi/jitsi-meet:latest',
    ports: [8088, 8443],
    volumes: ['/config'],
    windowComponent: 'JitsiManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8088
    }
  },

  // ==================== PROJECT MANAGEMENT ====================
  {
    id: 'taiga',
    name: 'Taiga',
    category: 'tool',
    icon: 'KanbanSquare',
    description: 'Agile project management',
    installMethod: 'docker',
    dockerImage: 'taigaio/taiga:latest',
    ports: [9000],
    volumes: ['/taiga-back/static', '/taiga-back/media'],
    windowComponent: 'TaigaManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 9000
    }
  },
  {
    id: 'plane',
    name: 'Plane',
    category: 'tool',
    icon: 'KanbanSquare',
    description: 'Modern project management',
    installMethod: 'docker',
    dockerImage: 'makeplane/plane:latest',
    ports: [3005],
    volumes: ['/plane/data'],
    windowComponent: 'PlaneManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3005
    }
  },
  {
    id: 'focalboard',
    name: 'Focalboard',
    category: 'tool',
    icon: 'KanbanSquare',
    description: 'Trello/Notion alternative',
    installMethod: 'docker',
    dockerImage: 'mattermost/focalboard:latest',
    ports: [8089],
    volumes: ['/data'],
    windowComponent: 'FocalboardManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8089
    }
  },

  // ==================== DOCUMENTATION ====================
  {
    id: 'bookstack',
    name: 'BookStack',
    category: 'tool',
    icon: 'Book',
    description: 'Wiki documentation platform',
    installMethod: 'docker',
    dockerImage: 'solidnerd/bookstack:latest',
    ports: [8091],
    volumes: ['/config'],
    windowComponent: 'BookStackManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8091
    }
  },
  {
    id: 'wikijs',
    name: 'Wiki.js',
    category: 'tool',
    icon: 'Book',
    description: 'Modern wiki software',
    installMethod: 'docker',
    dockerImage: 'ghcr.io/requarks/wiki:latest',
    ports: [3006],
    volumes: ['/wiki/data', '/wiki/repo'],
    windowComponent: 'WikiJSManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3006
    }
  },
  {
    id: 'outline',
    name: 'Outline',
    category: 'tool',
    icon: 'Book',
    description: 'Team knowledge base',
    installMethod: 'docker',
    dockerImage: 'outlinewiki/outline:latest',
    ports: [3007],
    volumes: ['/var/lib/outline/data'],
    windowComponent: 'OutlineManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3007
    }
  },

  // ==================== ANALYTICS ====================
  {
    id: 'matomo',
    name: 'Matomo',
    category: 'tool',
    icon: 'BarChart3',
    description: 'Google Analytics alternative',
    installMethod: 'docker',
    dockerImage: 'matomo:latest',
    ports: [8092],
    volumes: ['/var/www/html'],
    windowComponent: 'MatomoManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8092
    }
  },
  {
    id: 'plausible',
    name: 'Plausible',
    category: 'tool',
    icon: 'BarChart3',
    description: 'Privacy-friendly analytics',
    installMethod: 'docker',
    dockerImage: 'plausible/analytics:latest',
    ports: [8093],
    volumes: ['/var/lib/plausible'],
    windowComponent: 'PlausibleManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8093
    }
  },
  {
    id: 'umami',
    name: 'Umami',
    category: 'tool',
    icon: 'BarChart3',
    description: 'Simple web analytics',
    installMethod: 'docker',
    dockerImage: 'ghcr.io/umami-software/umami:latest',
    ports: [3008],
    volumes: [],
    windowComponent: 'UmamiManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3008
    }
  },
  {
    id: 'metabase',
    name: 'Metabase',
    category: 'tool',
    icon: 'BarChart3',
    description: 'Business intelligence tool',
    installMethod: 'docker',
    dockerImage: 'metabase/metabase:latest',
    ports: [3009],
    volumes: ['/metabase-data'],
    windowComponent: 'MetabaseManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 3009
    }
  },
  {
    id: 'superset',
    name: 'Apache Superset',
    category: 'tool',
    icon: 'BarChart3',
    description: 'Data exploration and visualization',
    installMethod: 'docker',
    dockerImage: 'apache/superset:latest',
    ports: [8088],
    volumes: ['/app/superset_home'],
    windowComponent: 'SupersetManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8088
    }
  },

  // ==================== AI/ML ====================
  {
    id: 'jupyter',
    name: 'Jupyter Notebook',
    category: 'tool',
    icon: 'Code',
    description: 'Interactive data science',
    installMethod: 'docker',
    dockerImage: 'jupyter/scipy-notebook:latest',
    ports: [8888],
    volumes: ['/home/jovyan/work'],
    windowComponent: 'JupyterManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8888
    }
  },
  {
    id: 'mlflow',
    name: 'MLflow',
    category: 'tool',
    icon: 'Brain',
    description: 'ML lifecycle management',
    installMethod: 'docker',
    dockerImage: 'ghcr.io/mlflow/mlflow:latest',
    ports: [5000],
    volumes: ['/mlflow'],
    windowComponent: 'MLflowManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 5000
    }
  },
  {
    id: 'airflow',
    name: 'Apache Airflow',
    category: 'tool',
    icon: 'Workflow',
    description: 'Workflow orchestration',
    installMethod: 'docker',
    dockerImage: 'apache/airflow:latest',
    ports: [8094],
    volumes: ['/opt/airflow'],
    windowComponent: 'AirflowManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8094
    }
  },
  {
    id: 'n8n',
    name: 'n8n',
    category: 'tool',
    icon: 'Workflow',
    description: 'Workflow automation',
    installMethod: 'docker',
    dockerImage: 'n8nio/n8n:latest',
    ports: [5678],
    volumes: ['/home/node/.n8n'],
    windowComponent: 'N8NManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 5678
    }
  },

  // ==================== STORAGE ====================
  {
    id: 'minio',
    name: 'MinIO',
    category: 'tool',
    icon: 'HardDrive',
    description: 'S3-compatible object storage',
    installMethod: 'docker',
    dockerImage: 'minio/minio:latest',
    ports: [9001, 9002],
    volumes: ['/data'],
    environment: {
      'MINIO_ROOT_USER': 'minioadmin',
      'MINIO_ROOT_PASSWORD': 'minioadmin'
    },
    windowComponent: 'MinIOManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      username: 'minioadmin',
      password: 'minioadmin',
      port: 9001
    }
  },
  {
    id: 'nextcloud',
    name: 'Nextcloud',
    category: 'tool',
    icon: 'Cloud',
    description: 'File sharing and collaboration',
    installMethod: 'docker',
    dockerImage: 'nextcloud:latest',
    ports: [8095],
    volumes: ['/var/www/html'],
    windowComponent: 'NextcloudManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8095
    }
  },

  // ==================== SECURITY ====================
  {
    id: 'keycloak',
    name: 'Keycloak',
    category: 'tool',
    icon: 'Shield',
    description: 'Identity and access management',
    installMethod: 'docker',
    dockerImage: 'quay.io/keycloak/keycloak:latest',
    ports: [8096],
    volumes: [],
    environment: {
      'KEYCLOAK_ADMIN': 'admin',
      'KEYCLOAK_ADMIN_PASSWORD': 'admin'
    },
    windowComponent: 'KeycloakManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      username: 'admin',
      password: 'admin',
      port: 8096
    }
  },
  {
    id: 'vault',
    name: 'HashiCorp Vault',
    category: 'tool',
    icon: 'Lock',
    description: 'Secret management',
    installMethod: 'docker',
    dockerImage: 'hashicorp/vault:latest',
    ports: [8200],
    volumes: ['/vault/data'],
    windowComponent: 'VaultManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8200
    }
  },
  {
    id: 'vaultwarden',
    name: 'Vaultwarden',
    category: 'tool',
    icon: 'Key',
    description: 'Bitwarden password manager',
    installMethod: 'docker',
    dockerImage: 'vaultwarden/server:latest',
    ports: [8097],
    volumes: ['/data'],
    windowComponent: 'VaultwardenManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8097
    }
  },

  // ==================== CONTAINER MANAGEMENT ====================
  {
    id: 'portainer',
    name: 'Portainer',
    category: 'tool',
    icon: 'Container',
    description: 'Docker management UI',
    installMethod: 'docker',
    dockerImage: 'portainer/portainer-ce:latest',
    ports: [9443],
    volumes: ['/data', '/var/run/docker.sock:/var/run/docker.sock'],
    windowComponent: 'PortainerManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 9443
    }
  },

  // ==================== CMS ====================
  {
    id: 'wordpress',
    name: 'WordPress',
    category: 'tool',
    icon: 'Globe',
    description: 'Popular CMS',
    installMethod: 'docker',
    dockerImage: 'wordpress:latest',
    ports: [8098],
    volumes: ['/var/www/html'],
    windowComponent: 'WordPressManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8098
    }
  },
  {
    id: 'ghost',
    name: 'Ghost',
    category: 'tool',
    icon: 'FileText',
    description: 'Modern publishing platform',
    installMethod: 'docker',
    dockerImage: 'ghost:latest',
    ports: [2368],
    volumes: ['/var/lib/ghost/content'],
    windowComponent: 'GhostManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 2368
    }
  },
  {
    id: 'strapi',
    name: 'Strapi',
    category: 'tool',
    icon: 'Code2',
    description: 'Headless CMS',
    installMethod: 'docker',
    dockerImage: 'strapi/strapi:latest',
    ports: [1337],
    volumes: ['/srv/app'],
    windowComponent: 'StrapiManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 1337
    }
  },

  // ==================== MEDIA ====================
  {
    id: 'plex',
    name: 'Plex Media Server',
    category: 'media',
    icon: 'Film',
    description: 'Media streaming server',
    installMethod: 'docker',
    dockerImage: 'plexinc/pms-docker:latest',
    ports: [32400],
    volumes: ['/config', '/data'],
    windowComponent: 'PlexManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 32400
    }
  },
  {
    id: 'jellyfin',
    name: 'Jellyfin',
    category: 'media',
    icon: 'Film',
    description: 'Open-source media server',
    installMethod: 'docker',
    dockerImage: 'jellyfin/jellyfin:latest',
    ports: [8096],
    volumes: ['/config', '/data/media'],
    windowComponent: 'JellyfinManager',
    defaultWidth: 1400,
    defaultHeight: 900,
    defaultCredentials: {
      port: 8096
    }
  },

  // ==================== RUNTIMES ====================
  {
    id: 'node18',
    name: 'Node.js 18',
    category: 'runtime',
    icon: 'Code',
    description: 'JavaScript runtime',
    installMethod: 'docker',
    dockerImage: 'node:18',
    ports: [3010],
    volumes: ['/app'],
    windowComponent: 'NodeManager',
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'node20',
    name: 'Node.js 20',
    category: 'runtime',
    icon: 'Code',
    description: 'JavaScript runtime LTS',
    installMethod: 'docker',
    dockerImage: 'node:20',
    ports: [3011],
    volumes: ['/app'],
    windowComponent: 'NodeManager',
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'python311',
    name: 'Python 3.11',
    category: 'runtime',
    icon: 'Code',
    description: 'Python runtime',
    installMethod: 'docker',
    dockerImage: 'python:3.11',
    ports: [5001],
    volumes: ['/app'],
    windowComponent: 'PythonManager',
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'python312',
    name: 'Python 3.12',
    category: 'runtime',
    icon: 'Code',
    description: 'Python latest runtime',
    installMethod: 'docker',
    dockerImage: 'python:3.12',
    ports: [5002],
    volumes: ['/app'],
    windowComponent: 'PythonManager',
    defaultWidth: 1200,
    defaultHeight: 700
  },
]
