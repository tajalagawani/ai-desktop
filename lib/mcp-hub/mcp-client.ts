// MCP Client - Communicates with MCP servers via stdio
import { spawn, ChildProcess } from 'child_process';
import { MCPServer, MCPTool } from './types';

interface MCPRequest {
  jsonrpc: '2.0';
  id: number;
  method: string;
  params?: any;
}

interface MCPResponse {
  jsonrpc: '2.0';
  id: number;
  result?: any;
  error?: {
    code: number;
    message: string;
  };
}

export class MCPClient {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }>();
  private buffer = '';

  constructor(private server: MCPServer) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.process = spawn(this.server.command, this.server.args, {
        cwd: this.server.cwd,
        env: { ...process.env, ...this.server.env },
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      if (!this.process.stdout || !this.process.stdin) {
        reject(new Error('Failed to create process streams'));
        return;
      }

      // Handle stdout (MCP responses)
      this.process.stdout.on('data', (data) => {
        this.buffer += data.toString();
        this.processBuffer();
      });

      // Handle stderr (errors and logs)
      this.process.stderr?.on('data', (data) => {
        console.error(`[MCP Client ${this.server.id}] stderr:`, data.toString());
      });

      // Handle process exit
      this.process.on('exit', (code) => {
        console.log(`[MCP Client ${this.server.id}] Process exited with code ${code}`);
        this.cleanup();
      });

      // Initialize connection
      this.sendRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
          experimental: {},
          sampling: {},
        },
        clientInfo: {
          name: 'ai-desktop-mcp-hub',
          version: '1.0.0',
        },
      }).then(() => {
        resolve();
      }).catch(reject);
    });
  }

  private processBuffer(): void {
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const response: MCPResponse = JSON.parse(line);

        const pending = this.pendingRequests.get(response.id);
        if (pending) {
          this.pendingRequests.delete(response.id);

          if (response.error) {
            pending.reject(new Error(response.error.message));
          } else {
            pending.resolve(response.result);
          }
        }
      } catch (error) {
        console.error('[MCP Client] Failed to parse response:', line, error);
      }
    }
  }

  private async sendRequest(method: string, params?: any): Promise<any> {
    if (!this.process || !this.process.stdin) {
      throw new Error('Not connected');
    }

    const id = ++this.requestId;
    const request: MCPRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params,
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });

      const requestStr = JSON.stringify(request) + '\n';
      this.process!.stdin!.write(requestStr);

      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  async listTools(): Promise<MCPTool[]> {
    try {
      const result = await this.sendRequest('tools/list');
      return result.tools || [];
    } catch (error) {
      console.error('[MCP Client] Failed to list tools:', error);
      throw error;
    }
  }

  async callTool(name: string, args: Record<string, any>): Promise<any> {
    try {
      const result = await this.sendRequest('tools/call', {
        name,
        arguments: args,
      });
      return result;
    } catch (error) {
      console.error('[MCP Client] Failed to call tool:', error);
      throw error;
    }
  }

  cleanup(): void {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
    this.pendingRequests.clear();
  }

  disconnect(): void {
    this.cleanup();
  }
}

// Create a temporary connection to get tools
export async function discoverTools(server: MCPServer): Promise<MCPTool[]> {
  const client = new MCPClient(server);

  try {
    await client.connect();
    const tools = await client.listTools();
    return tools;
  } finally {
    client.disconnect();
  }
}

// Execute a tool
export async function executeTool(
  server: MCPServer,
  toolName: string,
  parameters: Record<string, any>
): Promise<any> {
  const client = new MCPClient(server);

  try {
    await client.connect();
    const result = await client.callTool(toolName, parameters);
    return result;
  } finally {
    client.disconnect();
  }
}
