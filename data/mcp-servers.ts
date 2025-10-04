// MCP (Model Context Protocol) Servers Catalog
// Docker MCP Toolkit - 120+ Verified Containerized AI Tools

export interface MCPServerConfig {
  id: string
  name: string
  category: 'development' | 'browser' | 'search' | 'cloud' | 'monitoring' | 'database' | 'communication' | 'payment' | 'ai-utility' | 'reference'
  icon: string
  iconType?: 'lucide' | 'image'
  description: string
  type: 'local' | 'remote' // Local = runs offline, Remote = requires internet

  // Docker MCP config
  dockerImage: string
  requiresOAuth: boolean
  oauthProvider?: 'github' | 'gitlab' | 'google' | 'stripe' | 'slack'

  // Configuration
  defaultSecrets?: {
    key: string
    description: string
    required: boolean
    placeholder?: string
  }[]

  // Tools provided by this server
  tools?: {
    name: string
    description: string
  }[]

  // Documentation
  documentation?: string

  // UI config
  defaultWidth: number
  defaultHeight: number
}

export const MCP_SERVERS: MCPServerConfig[] = [
  // ==================== DEVELOPMENT & VERSION CONTROL ====================
  {
    id: 'github-official',
    name: 'GitHub Official',
    category: 'development',
    icon: 'GitBranch',
    description: 'Complete GitHub API integration - repositories, issues, pull requests, actions',
    type: 'remote',
    dockerImage: 'mcp/github-official:latest',
    requiresOAuth: true,
    oauthProvider: 'github',
    tools: [
      { name: 'create_repository', description: 'Create a new GitHub repository' },
      { name: 'create_issue', description: 'Create an issue' },
      { name: 'create_pull_request', description: 'Create a pull request' },
      { name: 'search_repositories', description: 'Search for repositories' },
      { name: 'get_file_contents', description: 'Read file from repository' },
      { name: 'push_files', description: 'Push files to repository' },
      { name: 'create_or_update_file', description: 'Create or update a file' },
      { name: 'search_code', description: 'Search code across repositories' },
      { name: 'fork_repository', description: 'Fork a repository' },
    ],
    documentation: 'https://docs.github.com/en/rest',
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'gitlab',
    name: 'GitLab',
    category: 'development',
    icon: 'GitBranch',
    description: 'GitLab operations - projects, merge requests, CI/CD pipelines',
    type: 'remote',
    dockerImage: 'mcp/gitlab:latest',
    requiresOAuth: true,
    oauthProvider: 'gitlab',
    tools: [
      { name: 'create_project', description: 'Create a new project' },
      { name: 'create_merge_request', description: 'Create merge request' },
      { name: 'list_pipelines', description: 'List CI/CD pipelines' },
      { name: 'get_project', description: 'Get project details' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'git',
    name: 'Git Local',
    category: 'development',
    icon: 'GitBranch',
    description: 'Local Git repository operations - read, search, manipulate repos',
    type: 'local',
    dockerImage: 'mcp/git:latest',
    requiresOAuth: false,
    tools: [
      { name: 'git_status', description: 'Show working tree status' },
      { name: 'git_diff', description: 'Show changes' },
      { name: 'git_log', description: 'Show commit logs' },
      { name: 'git_commit', description: 'Create commit' },
      { name: 'git_push', description: 'Push to remote' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },

  // ==================== BROWSER AUTOMATION & WEB ====================
  {
    id: 'playwright',
    name: 'Playwright',
    category: 'browser',
    icon: 'Globe',
    description: 'Browser automation - navigate, screenshot, scrape, interact with web pages',
    type: 'local',
    dockerImage: 'mcp/playwright:latest',
    requiresOAuth: false,
    tools: [
      { name: 'navigate', description: 'Navigate to URL' },
      { name: 'screenshot', description: 'Take screenshot' },
      { name: 'click', description: 'Click element' },
      { name: 'fill', description: 'Fill input field' },
      { name: 'evaluate', description: 'Execute JavaScript' },
      { name: 'get_content', description: 'Get page content' },
      { name: 'pdf', description: 'Generate PDF' },
    ],
    documentation: 'https://playwright.dev',
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'puppeteer',
    name: 'Puppeteer',
    category: 'browser',
    icon: 'Globe',
    description: 'Headless Chrome browser control and automation',
    type: 'local',
    dockerImage: 'mcp/puppeteer:latest',
    requiresOAuth: false,
    tools: [
      { name: 'navigate', description: 'Navigate to URL' },
      { name: 'screenshot', description: 'Capture screenshot' },
      { name: 'scrape', description: 'Extract page data' },
      { name: 'click', description: 'Click element' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'firecrawl',
    name: 'Firecrawl',
    category: 'browser',
    icon: 'Flame',
    description: 'Advanced web scraping and crawling with AI-powered extraction',
    type: 'remote',
    dockerImage: 'mcp/firecrawl:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'firecrawl.api_key', description: 'Firecrawl API Key', required: true, placeholder: 'fc-xxx' }
    ],
    tools: [
      { name: 'crawl', description: 'Crawl website' },
      { name: 'scrape', description: 'Scrape page content' },
      { name: 'extract', description: 'Extract structured data' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // ==================== SEARCH & DISCOVERY ====================
  {
    id: 'duckduckgo',
    name: 'DuckDuckGo',
    category: 'search',
    icon: 'Search',
    description: 'Privacy-focused web search engine',
    type: 'remote',
    dockerImage: 'mcp/duckduckgo:latest',
    requiresOAuth: false,
    tools: [
      { name: 'search', description: 'Search the web' },
      { name: 'instant_answer', description: 'Get instant answers' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'brave-search',
    name: 'Brave Search',
    category: 'search',
    icon: 'Search',
    description: 'Independent, privacy-respecting search engine',
    type: 'remote',
    dockerImage: 'mcp/brave-search:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'brave.api_key', description: 'Brave Search API Key', required: true }
    ],
    tools: [
      { name: 'web_search', description: 'Search the web' },
      { name: 'local_search', description: 'Search local results' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },

  // ==================== CLOUD & INFRASTRUCTURE ====================
  {
    id: 'dockerhub',
    name: 'Docker Hub',
    category: 'cloud',
    icon: 'Container',
    description: 'Docker Hub registry operations - search, pull, manage images',
    type: 'remote',
    dockerImage: 'mcp/dockerhub:latest',
    requiresOAuth: false,
    tools: [
      { name: 'search_images', description: 'Search Docker images' },
      { name: 'get_image_details', description: 'Get image information' },
      { name: 'list_tags', description: 'List image tags' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'aws-kb-retrieval',
    name: 'AWS Knowledge Base',
    category: 'cloud',
    icon: 'Cloud',
    description: 'AWS Bedrock Knowledge Base retrieval',
    type: 'remote',
    dockerImage: 'mcp/aws-kb-retrieval:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'aws.access_key_id', description: 'AWS Access Key ID', required: true },
      { key: 'aws.secret_access_key', description: 'AWS Secret Access Key', required: true },
      { key: 'aws.region', description: 'AWS Region', required: true, placeholder: 'us-east-1' },
    ],
    tools: [
      { name: 'query_knowledge_base', description: 'Query AWS KB' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'google-drive',
    name: 'Google Drive',
    category: 'cloud',
    icon: 'HardDrive',
    description: 'Google Drive file operations and management',
    type: 'remote',
    dockerImage: 'mcp/google-drive:latest',
    requiresOAuth: true,
    oauthProvider: 'google',
    tools: [
      { name: 'list_files', description: 'List files' },
      { name: 'upload_file', description: 'Upload file' },
      { name: 'download_file', description: 'Download file' },
      { name: 'search_files', description: 'Search files' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'google-maps',
    name: 'Google Maps',
    category: 'cloud',
    icon: 'Map',
    description: 'Google Maps API - geocoding, directions, places',
    type: 'remote',
    dockerImage: 'mcp/google-maps:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'google.api_key', description: 'Google Maps API Key', required: true }
    ],
    tools: [
      { name: 'geocode', description: 'Convert address to coordinates' },
      { name: 'directions', description: 'Get directions' },
      { name: 'search_places', description: 'Search for places' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // ==================== MONITORING & OBSERVABILITY ====================
  {
    id: 'grafana',
    name: 'Grafana',
    category: 'monitoring',
    icon: 'BarChart3',
    description: 'Grafana dashboards, panels, and metrics management',
    type: 'remote',
    dockerImage: 'mcp/grafana:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'grafana.url', description: 'Grafana URL', required: true, placeholder: 'http://localhost:3000' },
      { key: 'grafana.api_key', description: 'Grafana API Key', required: true }
    ],
    tools: [
      { name: 'search_dashboards', description: 'Search dashboards' },
      { name: 'get_dashboard', description: 'Get dashboard details' },
      { name: 'create_dashboard', description: 'Create new dashboard' },
      { name: 'query_metrics', description: 'Query metrics' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'sentry',
    name: 'Sentry',
    category: 'monitoring',
    icon: 'AlertCircle',
    description: 'Error tracking and performance monitoring',
    type: 'remote',
    dockerImage: 'mcp/sentry:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'sentry.auth_token', description: 'Sentry Auth Token', required: true },
      { key: 'sentry.org_slug', description: 'Organization Slug', required: true }
    ],
    tools: [
      { name: 'list_issues', description: 'List error issues' },
      { name: 'get_issue', description: 'Get issue details' },
      { name: 'resolve_issue', description: 'Resolve issue' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'newrelic',
    name: 'New Relic',
    category: 'monitoring',
    icon: 'Activity',
    description: 'Application performance monitoring and observability',
    type: 'remote',
    dockerImage: 'mcp/newrelic:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'newrelic.api_key', description: 'New Relic API Key', required: true },
      { key: 'newrelic.account_id', description: 'Account ID', required: true }
    ],
    tools: [
      { name: 'query_nrql', description: 'Query with NRQL' },
      { name: 'get_metrics', description: 'Get application metrics' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // ==================== DATABASES ====================
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    category: 'database',
    icon: 'Database',
    description: 'PostgreSQL database operations and queries',
    type: 'local',
    dockerImage: 'mcp/postgresql:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'postgres.host', description: 'PostgreSQL Host', required: true, placeholder: 'localhost' },
      { key: 'postgres.port', description: 'Port', required: true, placeholder: '5432' },
      { key: 'postgres.database', description: 'Database Name', required: true },
      { key: 'postgres.user', description: 'Username', required: true },
      { key: 'postgres.password', description: 'Password', required: true }
    ],
    tools: [
      { name: 'query', description: 'Execute SQL query' },
      { name: 'list_tables', description: 'List all tables' },
      { name: 'describe_table', description: 'Describe table schema' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'sqlite',
    name: 'SQLite',
    category: 'database',
    icon: 'Database',
    description: 'SQLite database operations',
    type: 'local',
    dockerImage: 'mcp/sqlite:latest',
    requiresOAuth: false,
    tools: [
      { name: 'query', description: 'Execute SQL query' },
      { name: 'list_tables', description: 'List tables' },
      { name: 'create_table', description: 'Create table' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'redis',
    name: 'Redis',
    category: 'database',
    icon: 'Database',
    description: 'Redis key-value store operations',
    type: 'local',
    dockerImage: 'mcp/redis:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'redis.host', description: 'Redis Host', required: true, placeholder: 'localhost' },
      { key: 'redis.port', description: 'Port', required: false, placeholder: '6379' },
      { key: 'redis.password', description: 'Password', required: false }
    ],
    tools: [
      { name: 'get', description: 'Get value by key' },
      { name: 'set', description: 'Set key-value' },
      { name: 'delete', description: 'Delete key' },
      { name: 'keys', description: 'List keys' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },

  // ==================== COMMUNICATION ====================
  {
    id: 'slack',
    name: 'Slack',
    category: 'communication',
    icon: 'MessageSquare',
    description: 'Slack workspace integration - channels, messages, users',
    type: 'remote',
    dockerImage: 'mcp/slack:latest',
    requiresOAuth: true,
    oauthProvider: 'slack',
    tools: [
      { name: 'send_message', description: 'Send message to channel' },
      { name: 'list_channels', description: 'List channels' },
      { name: 'get_messages', description: 'Get channel messages' },
      { name: 'create_channel', description: 'Create channel' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
  {
    id: 'discord',
    name: 'Discord',
    category: 'communication',
    icon: 'MessageSquare',
    description: 'Discord bot operations and server management',
    type: 'remote',
    dockerImage: 'mcp/discord:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'discord.bot_token', description: 'Discord Bot Token', required: true }
    ],
    tools: [
      { name: 'send_message', description: 'Send message' },
      { name: 'get_messages', description: 'Get messages' },
      { name: 'create_channel', description: 'Create channel' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // ==================== PAYMENT & COMMERCE ====================
  {
    id: 'stripe',
    name: 'Stripe',
    category: 'payment',
    icon: 'CreditCard',
    description: 'Stripe payment processing - charges, customers, subscriptions',
    type: 'remote',
    dockerImage: 'mcp/stripe:latest',
    requiresOAuth: false,
    defaultSecrets: [
      { key: 'stripe.api_key', description: 'Stripe API Key', required: true, placeholder: 'sk_test_xxx' }
    ],
    tools: [
      { name: 'create_customer', description: 'Create customer' },
      { name: 'create_charge', description: 'Create charge' },
      { name: 'list_customers', description: 'List customers' },
      { name: 'create_subscription', description: 'Create subscription' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },

  // ==================== AI & UTILITIES ====================
  {
    id: 'sequentialthinking',
    name: 'Sequential Thinking',
    category: 'ai-utility',
    icon: 'Brain',
    description: 'Dynamic problem-solving through sequential thought processes',
    type: 'local',
    dockerImage: 'mcp/sequentialthinking:latest',
    requiresOAuth: false,
    tools: [
      { name: 'think', description: 'Process thought sequence' },
      { name: 'reflect', description: 'Reflect on solution' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'memory',
    name: 'Memory',
    category: 'ai-utility',
    icon: 'Brain',
    description: 'Knowledge graph-based persistent memory system for AI agents',
    type: 'local',
    dockerImage: 'mcp/memory:latest',
    requiresOAuth: false,
    tools: [
      { name: 'store', description: 'Store information' },
      { name: 'retrieve', description: 'Retrieve information' },
      { name: 'search', description: 'Search knowledge graph' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'time',
    name: 'Time',
    category: 'ai-utility',
    icon: 'Clock',
    description: 'Time and timezone conversion utilities',
    type: 'local',
    dockerImage: 'mcp/time:latest',
    requiresOAuth: false,
    tools: [
      { name: 'get_time', description: 'Get current time' },
      { name: 'convert_timezone', description: 'Convert timezone' },
      { name: 'format_time', description: 'Format time' },
    ],
    defaultWidth: 1000,
    defaultHeight: 600
  },
  {
    id: 'filesystem',
    name: 'Filesystem',
    category: 'ai-utility',
    icon: 'Folder',
    description: 'Secure file operations with access controls',
    type: 'local',
    dockerImage: 'mcp/filesystem:latest',
    requiresOAuth: false,
    tools: [
      { name: 'read_file', description: 'Read file contents' },
      { name: 'write_file', description: 'Write to file' },
      { name: 'list_directory', description: 'List directory' },
      { name: 'create_directory', description: 'Create directory' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },
  {
    id: 'fetch',
    name: 'Fetch',
    category: 'ai-utility',
    icon: 'Download',
    description: 'Web content fetching and conversion for LLM usage',
    type: 'local',
    dockerImage: 'mcp/fetch:latest',
    requiresOAuth: false,
    tools: [
      { name: 'fetch_url', description: 'Fetch URL content' },
      { name: 'fetch_html', description: 'Fetch HTML' },
      { name: 'convert_markdown', description: 'Convert to markdown' },
    ],
    defaultWidth: 1200,
    defaultHeight: 700
  },

  // ==================== REFERENCE & TESTING ====================
  {
    id: 'everything',
    name: 'Everything',
    category: 'reference',
    icon: 'PackageOpen',
    description: 'Reference test server with all MCP features - prompts, resources, tools',
    type: 'local',
    dockerImage: 'mcp/everything:latest',
    requiresOAuth: false,
    tools: [
      { name: 'test_prompt', description: 'Test prompt handling' },
      { name: 'test_resource', description: 'Test resource access' },
      { name: 'test_tool', description: 'Test tool execution' },
    ],
    defaultWidth: 1400,
    defaultHeight: 900
  },
]

export const MCP_CATEGORIES = [
  { id: 'all', name: 'View all', icon: 'Grid3x3' },
  { id: 'development', name: 'Development & Git', icon: 'GitBranch' },
  { id: 'browser', name: 'Browser Automation', icon: 'Globe' },
  { id: 'search', name: 'Search & Discovery', icon: 'Search' },
  { id: 'cloud', name: 'Cloud & Infrastructure', icon: 'Cloud' },
  { id: 'monitoring', name: 'Monitoring', icon: 'BarChart3' },
  { id: 'database', name: 'Databases', icon: 'Database' },
  { id: 'communication', name: 'Communication', icon: 'MessageSquare' },
  { id: 'payment', name: 'Payment', icon: 'CreditCard' },
  { id: 'ai-utility', name: 'AI & Utilities', icon: 'Brain' },
  { id: 'reference', name: 'Reference', icon: 'PackageOpen' }
]
