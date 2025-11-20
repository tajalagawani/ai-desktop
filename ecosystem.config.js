/**
 * PM2 Ecosystem Configuration
 * Manages all AI Desktop services
 */

module.exports = {
  apps: [
    {
      name: 'ai-desktop-websocket',
      script: './backend/websocket-server.js',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'production',
        WS_PORT: 3007,
      },
      env_development: {
        NODE_ENV: 'development',
        WS_PORT: 3007,
      },
      error_file: './storage/logs/websocket-error.log',
      out_file: './storage/logs/websocket-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
    },
    {
      name: 'ai-desktop-backend',
      script: './backend/server.js',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'production',
        PORT: 3006,
        WS_SERVER_URL: 'http://localhost:3007',
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 3006,
        WS_SERVER_URL: 'http://localhost:3007',
      },
      error_file: './storage/logs/backend-error.log',
      out_file: './storage/logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
    },
    {
      name: 'ai-desktop-frontend',
      script: 'npm',
      args: 'start',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'production',
        PORT: 3005,
        NEXT_PUBLIC_API_URL: 'http://localhost:3006',
        NEXT_PUBLIC_WS_URL: 'http://localhost:3007',
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 3005,
        NEXT_PUBLIC_API_URL: 'http://localhost:3006',
        NEXT_PUBLIC_WS_URL: 'http://localhost:3007',
      },
      error_file: './storage/logs/frontend-error.log',
      out_file: './storage/logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
    },
  ],
}
