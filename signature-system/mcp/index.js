#!/usr/bin/env node

/**
 * Flow Architect MCP Server
 * Provides Claude with tools to manage signatures and execute nodes
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// Import tools
import { executeNodeOperation } from './tools/execution/execute-node-operation.js';
import { getSignatureInfo } from './tools/signature/get-signature-info.js';
import { addNodeToSignature } from './tools/signature/add-node.js';

// Create MCP server
const server = new Server(
  {
    name: 'flow-architect-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const tools = [
  {
    name: 'execute_node_operation',
    description: 'Execute a single node operation using signature authentication. Instantly executes pre-authenticated operations without approval prompts.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: {
          type: 'string',
          description: 'Node type (e.g., "github", "openai", "postgresql")'
        },
        operation: {
          type: 'string',
          description: 'Operation name (e.g., "list_issues", "create_completion")'
        },
        params: {
          type: 'object',
          description: 'Runtime parameters for the operation',
          default: {}
        },
        override_defaults: {
          type: 'boolean',
          description: 'If true, do not merge with node defaults',
          default: false
        },
        signature_path: {
          type: 'string',
          description: 'Path to signature file',
          default: 'signatures/user.act.sig'
        }
      },
      required: ['node_type', 'operation']
    }
  },
  {
    name: 'get_signature_info',
    description: 'Get information about authenticated nodes from the signature file. Shows which nodes are authenticated and available operations.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: {
          type: 'string',
          description: 'Specific node type to get info for (optional). If not provided, returns info for all authenticated nodes.'
        },
        signature_path: {
          type: 'string',
          description: 'Path to signature file',
          default: 'signatures/user.act.sig'
        }
      }
    }
  },
  {
    name: 'add_node_to_signature',
    description: 'Authenticate a node and add it to the signature file. This validates credentials and stores them securely in .env file.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: {
          type: 'string',
          description: 'Node type to authenticate (e.g., "github", "openai")'
        },
        auth: {
          type: 'object',
          description: 'Authentication credentials (e.g., {access_token: "xxx"} for GitHub)'
        },
        defaults: {
          type: 'object',
          description: 'Default parameters for this node (e.g., {owner: "user", repo: "repo"})',
          default: {}
        },
        signature_path: {
          type: 'string',
          description: 'Path to signature file',
          default: 'signatures/user.act.sig'
        }
      },
      required: ['node_type', 'auth']
    }
  }
];

// Register list tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Register call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'execute_node_operation':
        return await executeNodeOperation(args);

      case 'get_signature_info':
        return await getSignatureInfo(args);

      case 'add_node_to_signature':
        return await addNodeToSignature(args);

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'error',
          error: error.message,
          tool: name
        }, null, 2)
      }],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Flow Architect MCP Server running');
  console.error('Tools available: execute_node_operation, get_signature_info, add_node_to_signature');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
