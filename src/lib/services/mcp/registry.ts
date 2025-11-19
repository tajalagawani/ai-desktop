// MCP Registry - Manages MCP server configurations
import fs from 'fs';
import path from 'path';
import { MCPRegistry, MCPServer } from './types';

const DATA_DIR = path.join(process.cwd(), 'data');
const REGISTRY_FILE = path.join(DATA_DIR, 'mcp-servers.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Default registry with ACT Workflow built-in
const DEFAULT_REGISTRY: MCPRegistry = {
  servers: [
    {
      id: 'act-workflow',
      name: 'ACT Workflow MCP',
      description: '150+ workflow automation nodes for integrations, AI, databases, and APIs',
      type: 'built-in',
      command: 'node',
      args: [process.env.ACT_ROOT ? `${process.env.ACT_ROOT}/mcp/index.js` : '/var/www/act/mcp/index.js'],
      cwd: process.env.ACT_ROOT ? `${process.env.ACT_ROOT}/mcp` : '/var/www/act/mcp',
      env: {},
      status: 'stopped',
      pm2Name: 'mcp-act-workflow',
      toolCount: 13,
      addedAt: new Date().toISOString(),
    },
  ],
  lastUpdated: new Date().toISOString(),
};

export class MCPRegistryManager {
  private registry: MCPRegistry;

  constructor() {
    this.registry = this.loadRegistry();
  }

  private loadRegistry(): MCPRegistry {
    try {
      if (fs.existsSync(REGISTRY_FILE)) {
        const data = fs.readFileSync(REGISTRY_FILE, 'utf-8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('[MCP Registry] Error loading registry:', error);
    }

    // Return default registry if file doesn't exist or is invalid
    this.saveRegistry(DEFAULT_REGISTRY);
    return DEFAULT_REGISTRY;
  }

  private saveRegistry(registry: MCPRegistry): void {
    try {
      registry.lastUpdated = new Date().toISOString();
      fs.writeFileSync(REGISTRY_FILE, JSON.stringify(registry, null, 2), 'utf-8');
      this.registry = registry;
    } catch (error) {
      console.error('[MCP Registry] Error saving registry:', error);
      throw error;
    }
  }

  // Get all servers
  getServers(): MCPServer[] {
    return this.registry.servers;
  }

  // Get server by ID
  getServer(id: string): MCPServer | undefined {
    return this.registry.servers.find((s) => s.id === id);
  }

  // Add new server
  addServer(server: Omit<MCPServer, 'addedAt'>): MCPServer {
    const newServer: MCPServer = {
      ...server,
      addedAt: new Date().toISOString(),
    };

    this.registry.servers.push(newServer);
    this.saveRegistry(this.registry);
    return newServer;
  }

  // Update server
  updateServer(id: string, updates: Partial<MCPServer>): MCPServer | null {
    const index = this.registry.servers.findIndex((s) => s.id === id);
    if (index === -1) return null;

    this.registry.servers[index] = {
      ...this.registry.servers[index],
      ...updates,
    };

    this.saveRegistry(this.registry);
    return this.registry.servers[index];
  }

  // Delete server
  deleteServer(id: string): boolean {
    const initialLength = this.registry.servers.length;
    this.registry.servers = this.registry.servers.filter((s) => s.id !== id);

    if (this.registry.servers.length < initialLength) {
      this.saveRegistry(this.registry);
      return true;
    }

    return false;
  }

  // Get servers by status
  getServersByStatus(status: MCPServer['status']): MCPServer[] {
    return this.registry.servers.filter((s) => s.status === status);
  }

  // Get servers by type
  getServersByType(type: MCPServer['type']): MCPServer[] {
    return this.registry.servers.filter((s) => s.type === type);
  }
}

// Singleton instance
let registryInstance: MCPRegistryManager;

export function getRegistry(): MCPRegistryManager {
  if (!registryInstance) {
    registryInstance = new MCPRegistryManager();
  }
  return registryInstance;
}
