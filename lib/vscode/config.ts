/**
 * VS Code Manager Configuration
 * All constants and settings for code-server management
 */

export const VSCODE_CONFIG = {
  // Port range for code-server instances
  // Separate from services (which use 3000-4000 range)
  PORT_RANGE_START: 8880,
  PORT_RANGE_END: 8899,

  // Maximum concurrent instances
  MAX_INSTANCES: 20,

  // Nginx configuration
  NGINX_CONFIG_DIR: '/etc/nginx/vscode-projects',
  NGINX_INCLUDE_PATH: '/etc/nginx/vscode-projects/*.conf',

  // URL paths
  BASE_URL_PATH: '/vscode',

  // Timeouts
  STARTUP_TIMEOUT: 60000, // 60 seconds to wait for code-server to start (increased)
  PORT_CHECK_INTERVAL: 1000, // Check port every 1 second

  // code-server settings
  CODE_SERVER_ARGS: [
    '--auth', 'none',
    '--disable-telemetry',
    '--disable-update-check',
    '--disable-workspace-trust',
  ],

  // Process detection
  PROCESS_GREP_PATTERN: 'code-server',
} as const

export type VSCodeConfig = typeof VSCODE_CONFIG
