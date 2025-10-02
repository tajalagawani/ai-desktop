// PM2 Ecosystem Configuration for AI Desktop
// This file defines how PM2 should run the application on VPS

module.exports = {
  apps: [
    {
      name: 'ai-desktop',
      script: 'npm',
      args: 'start',
      cwd: '/var/www/ai-desktop', // Update this to your actual path on VPS
      version: '1.0.0', // Application version
      instances: '1', // Use '1' for single instance, or 'max' for cluster mode
      exec_mode: 'fork', // Use 'cluster' for load balancing with multiple instances
      watch: false, // Don't watch files in production
      autorestart: true, // Automatically restart if app crashes
      max_restarts: 10, // Max restart attempts
      min_uptime: '10s', // Minimum uptime before considered stable
      max_memory_restart: '1G', // Restart if memory exceeds 1GB

      // Environment variables
      env: {
        NODE_ENV: 'production',
        PORT: 80,
      },

      // Logging
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // Time before killing process on reload
      kill_timeout: 5000,
    },
  ],
};
