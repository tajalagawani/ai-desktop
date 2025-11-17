import fs from 'fs'
import { execSync } from 'child_process'
import path from 'path'

const NGINX_CONFIGS_DIR = '/etc/nginx/vscode-projects'

export class NginxConfigManager {
  /**
   * Generate Nginx location block configuration for a VS Code project
   */
  generateConfig(projectName: string, port: number, repoPath?: string): string {
    // Sanitize project name for use in URLs
    const safeName = projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

    return `# Auto-generated config for ${projectName}
# Generated at: ${new Date().toISOString()}
# Repository: ${repoPath || 'N/A'}
location /vscode/${safeName}/ {
    ${repoPath ? `# Automatically open the repository folder on initial access
    # Only redirect if: no folder param AND no query string at all
    set $redirect_needed 0;
    if ($arg_folder = "") {
        set $redirect_needed 1;
    }
    if ($args != "") {
        set $redirect_needed 0;
    }
    if ($redirect_needed = 1) {
        return 302 $scheme://$http_host/vscode/${safeName}/?folder=${repoPath};
    }
    ` : ''}
    proxy_pass http://localhost:${port}/;
    proxy_http_version 1.1;

    # WebSocket support (critical for VS Code)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_cache_bypass $http_upgrade;

    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeouts for long-running operations
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;

    # Allow large file uploads
    client_max_body_size 500M;
}
`
  }

  /**
   * Write Nginx configuration file for a project
   */
  writeConfig(projectName: string, port: number, repoPath?: string): void {
    try {
      const safeName = projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()
      const configPath = path.join(NGINX_CONFIGS_DIR, `${safeName}.conf`)
      const config = this.generateConfig(projectName, port, repoPath)

      // Ensure directory exists
      if (!fs.existsSync(NGINX_CONFIGS_DIR)) {
        console.log(`[Nginx] Creating config directory: ${NGINX_CONFIGS_DIR}`)
        fs.mkdirSync(NGINX_CONFIGS_DIR, { recursive: true })
      }

      fs.writeFileSync(configPath, config, 'utf-8')
      console.log(`[Nginx] Config written: ${configPath} with folder=${repoPath}`)
    } catch (error) {
      console.error('[Nginx] Failed to write config:', error)
      throw error
    }
  }

  /**
   * Remove Nginx configuration file for a project
   */
  removeConfig(projectName: string): void {
    try {
      const safeName = projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()
      const configPath = path.join(NGINX_CONFIGS_DIR, `${safeName}.conf`)

      if (fs.existsSync(configPath)) {
        fs.unlinkSync(configPath)
        console.log(`[Nginx] Config removed: ${configPath}`)
      } else {
        console.log(`[Nginx] Config file not found: ${configPath}`)
      }
    } catch (error) {
      console.error('[Nginx] Failed to remove config:', error)
      throw error
    }
  }

  /**
   * Test Nginx configuration syntax
   */
  testConfig(): boolean {
    try {
      execSync('nginx -t', { stdio: 'pipe' })
      console.log('[Nginx] Config test passed')
      return true
    } catch (error: any) {
      console.error('[Nginx] Config test failed:', error.message)
      return false
    }
  }

  /**
   * Reload Nginx to apply configuration changes
   */
  reload(): boolean {
    try {
      // Test config first
      if (!this.testConfig()) {
        console.error('[Nginx] Refusing to reload - config test failed')
        return false
      }

      // Reload Nginx
      execSync('systemctl reload nginx', { stdio: 'pipe' })
      console.log('[Nginx] Reloaded successfully')
      return true
    } catch (error: any) {
      console.error('[Nginx] Reload failed:', error.message)
      return false
    }
  }

  /**
   * Check if Nginx is installed and running
   */
  checkNginxStatus(): { installed: boolean; running: boolean } {
    let installed = false
    let running = false

    try {
      execSync('which nginx', { stdio: 'pipe' })
      installed = true
    } catch {
      installed = false
    }

    if (installed) {
      try {
        execSync('systemctl is-active nginx', { stdio: 'pipe' })
        running = true
      } catch {
        running = false
      }
    }

    return { installed, running }
  }

  /**
   * List all VS Code project configs
   */
  listConfigs(): string[] {
    try {
      if (!fs.existsSync(NGINX_CONFIGS_DIR)) {
        return []
      }

      const files = fs.readdirSync(NGINX_CONFIGS_DIR)
      return files.filter(f => f.endsWith('.conf')).map(f => f.replace('.conf', ''))
    } catch (error) {
      console.error('[Nginx] Failed to list configs:', error)
      return []
    }
  }
}
