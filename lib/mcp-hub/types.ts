// MCP Hub Type Definitions

export type MCPServerStatus = 'running' | 'stopped' | 'error' | 'starting';

export type MCPServerType = 'built-in' | 'custom';

export interface MCPServer {
  id: string;
  name: string;
  description: string;
  type: MCPServerType;
  command: string;
  args: string[];
  cwd?: string;
  env?: Record<string, string>;
  status: MCPServerStatus;
  pm2Name: string;
  toolCount: number;
  addedAt: string;
  lastStarted?: string;
  lastStopped?: string;
  error?: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties?: Record<string, any>;
    required?: string[];
  };
}

export interface MCPToolExecution {
  id: string;
  serverId: string;
  toolName: string;
  parameters: Record<string, any>;
  result?: any;
  error?: string;
  executedAt: string;
  duration: number;
}

export interface MCPRegistry {
  servers: MCPServer[];
  lastUpdated: string;
}
