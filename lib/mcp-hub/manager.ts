// MCP Manager - Handles MCP server lifecycle (start/stop/restart)
import { exec, spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';
import { MCPServer } from './types';
import { getRegistry } from './registry';

const execAsync = promisify(exec);

// Check if PM2 is available
let pm2Available = false;
execAsync('pm2 -v').then(() => {
  pm2Available = true;
}).catch(() => {
  console.log('[MCP Manager] PM2 not available, using direct process spawning');
});

// Store running processes for non-PM2 mode
const runningProcesses = new Map<string, ChildProcess>();

export class MCPManager {
  private registry = getRegistry();

  // Start an MCP server
  async startServer(id: string): Promise<{ success: boolean; message: string }> {
    const server = this.registry.getServer(id);
    if (!server) {
      return { success: false, message: 'Server not found' };
    }

    if (server.status === 'running') {
      return { success: false, message: 'Server is already running' };
    }

    try {
      // Update status to starting
      this.registry.updateServer(id, { status: 'starting' });

      if (pm2Available) {
        // Use PM2 (VPS mode)
        const envVars = Object.entries(server.env || {})
          .map(([key, value]) => `${key}="${value}"`)
          .join(' ');

        const cwdOption = server.cwd ? `--cwd "${server.cwd}"` : '';
        const argsString = server.args.map((arg) => `"${arg}"`).join(' ');

        const pm2Command = `pm2 start ${server.command} --name "${server.pm2Name}" ${cwdOption} -- ${argsString}`;
        const fullCommand = envVars ? `${envVars} ${pm2Command}` : pm2Command;

        console.log(`[MCP Manager] Starting server with PM2: ${fullCommand}`);

        await execAsync(fullCommand);
      } else {
        // Use direct process spawning (local mode)
        console.log(`[MCP Manager] Starting server directly: ${server.command} ${server.args.join(' ')}`);

        const childProcess = spawn(server.command, server.args, {
          cwd: server.cwd,
          env: { ...process.env, ...server.env },
          stdio: ['pipe', 'pipe', 'pipe'], // Keep stdin/stdout/stderr open for MCP protocol
          detached: true,
        });

        // Keep the process running
        childProcess.unref();
        runningProcesses.set(id, childProcess);

        // Monitor for immediate crashes
        let crashed = false;
        const crashHandler = () => {
          crashed = true;
        };

        childProcess.on('exit', crashHandler);

        // Check if childProcess started successfully
        await new Promise((resolve, reject) => {
          setTimeout(() => {
            childProcess.removeListener('exit', crashHandler);
            if (crashed || childProcess.exitCode !== null) {
              runningProcesses.delete(id);
              reject(new Error('Process exited immediately'));
            } else {
              resolve(true);
            }
          }, 500);
        });
      }

      // Update status to running
      this.registry.updateServer(id, {
        status: 'running',
        lastStarted: new Date().toISOString(),
        error: undefined,
      });

      return { success: true, message: 'Server started successfully' };
    } catch (error: any) {
      console.error(`[MCP Manager] Error starting server ${id}:`, error);

      this.registry.updateServer(id, {
        status: 'error',
        error: error.message,
      });

      return { success: false, message: error.message };
    }
  }

  // Stop an MCP server
  async stopServer(id: string): Promise<{ success: boolean; message: string }> {
    const server = this.registry.getServer(id);
    if (!server) {
      return { success: false, message: 'Server not found' };
    }

    if (server.status === 'stopped') {
      return { success: false, message: 'Server is already stopped' };
    }

    try {
      if (pm2Available) {
        await execAsync(`pm2 stop ${server.pm2Name}`);
      } else {
        const childProcess = runningProcesses.get(id);
        if (childProcess) {
          childProcess.kill();
          runningProcesses.delete(id);
        }
      }

      this.registry.updateServer(id, {
        status: 'stopped',
        lastStopped: new Date().toISOString(),
        error: undefined,
      });

      return { success: true, message: 'Server stopped successfully' };
    } catch (error: any) {
      console.error(`[MCP Manager] Error stopping server ${id}:`, error);
      return { success: false, message: error.message };
    }
  }

  // Restart an MCP server
  async restartServer(id: string): Promise<{ success: boolean; message: string }> {
    const server = this.registry.getServer(id);
    if (!server) {
      return { success: false, message: 'Server not found' };
    }

    try {
      if (server.status === 'running') {
        if (pm2Available) {
          await execAsync(`pm2 restart ${server.pm2Name}`);
        } else {
          await this.stopServer(id);
          await new Promise(resolve => setTimeout(resolve, 500));
          return await this.startServer(id);
        }
      } else {
        return await this.startServer(id);
      }

      this.registry.updateServer(id, {
        status: 'running',
        lastStarted: new Date().toISOString(),
        error: undefined,
      });

      return { success: true, message: 'Server restarted successfully' };
    } catch (error: any) {
      console.error(`[MCP Manager] Error restarting server ${id}:`, error);

      this.registry.updateServer(id, {
        status: 'error',
        error: error.message,
      });

      return { success: false, message: error.message };
    }
  }

  // Delete an MCP server (stop and remove from PM2)
  async deleteServer(id: string): Promise<{ success: boolean; message: string }> {
    const server = this.registry.getServer(id);
    if (!server) {
      return { success: false, message: 'Server not found' };
    }

    // Don't allow deleting built-in servers
    if (server.type === 'built-in') {
      return { success: false, message: 'Cannot delete built-in servers' };
    }

    try {
      // Stop and delete from PM2
      try {
        await execAsync(`pm2 delete ${server.pm2Name}`);
      } catch (error) {
        // Ignore errors if process doesn't exist
        console.log(`[MCP Manager] PM2 process ${server.pm2Name} not found, continuing...`);
      }

      // Remove from registry
      this.registry.deleteServer(id);

      return { success: true, message: 'Server deleted successfully' };
    } catch (error: any) {
      console.error(`[MCP Manager] Error deleting server ${id}:`, error);
      return { success: false, message: error.message };
    }
  }

  // Get server status
  async getServerStatus(id: string): Promise<MCPServer['status']> {
    const server = this.registry.getServer(id);
    if (!server) return 'stopped';

    try {
      if (pm2Available) {
        const { stdout } = await execAsync(`pm2 jlist`);
        const processes = JSON.parse(stdout);
        const process = processes.find((p: any) => p.name === server.pm2Name);

        if (!process) return 'stopped';

        switch (process.pm2_env.status) {
          case 'online':
            return 'running';
          case 'stopped':
            return 'stopped';
          case 'errored':
            return 'error';
          case 'launching':
            return 'starting';
          default:
            return 'stopped';
        }
      } else {
        const childProcess = runningProcesses.get(id);
        if (childProcess && childProcess.exitCode === null) {
          return 'running';
        }
        return 'stopped';
      }
    } catch (error) {
      console.error(`[MCP Manager] Error getting status for ${id}:`, error);
      return 'stopped';
    }
  }

  // Sync all server statuses with PM2
  async syncStatuses(): Promise<void> {
    const servers = this.registry.getServers();

    for (const server of servers) {
      const status = await this.getServerStatus(server.id);
      if (status !== server.status) {
        this.registry.updateServer(server.id, { status });
      }
    }
  }
}

// Singleton instance
let managerInstance: MCPManager;

export function getManager(): MCPManager {
  if (!managerInstance) {
    managerInstance = new MCPManager();
  }
  return managerInstance;
}
