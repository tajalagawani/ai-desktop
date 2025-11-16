module.exports = {
  apps: [
    {
      name: 'ai-desktop',
      script: './server.js',
      env: {
        PORT: 80,
        NODE_ENV: 'production'
      },
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    }
  ]
}
