#!/usr/bin/env node
/**
 * Flow Architect MCP Server
 * Provides Claude with tools to manage signatures and execute nodes
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// Import execution tools
import { executeNodeOperation } from './tools/execution/execute-node-operation.js';

// Import signature tools
import { getSignatureInfo } from './tools/signature/get-signature-info.js';
import { addNodeToSignature } from './tools/signature/add-node.js';
import { removeNodeFromSignature } from './tools/signature/remove-node.js';
import { updateNodeDefaults } from './tools/signature/update-node-defaults.js';
import { validateSignature } from './tools/signature/validate-signature.js';

// Import catalog tools
import { listAvailableNodes } from './tools/catalog/list-available-nodes.js';
import { getNodeInfo } from './tools/catalog/get-node-info.js';
import { listNodeOperations } from './tools/catalog/list-node-operations.js';
import { searchOperationsTool } from './tools/catalog/search-operations.js';
import { getOperationDetailsTool } from './tools/catalog/get-operation-details.js';

// Import validation tools
import { validateParams } from './tools/validation/validate-params.js';

// Import utility tools
import { getSystemStatus } from './tools/utility/get-system-status.js';

// Import UI tools
import requestNodeAuthTool from './tools/ui/request-node-auth.js';
import requestParametersTool from './tools/ui/request-parameters.js';

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
  // EXECUTION TOOLS
  {
    name: 'execute_node_operation',
    description: 'Execute a single node operation using signature authentication. Instantly executes pre-authenticated operations without approval prompts.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type (e.g., "github", "openai")' },
        operation: { type: 'string', description: 'Operation name (e.g., "list_issues")' },
        params: { type: 'object', description: 'Runtime parameters', default: {} },
        override_defaults: { type: 'boolean', description: 'Skip defaults merge', default: false },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type', 'operation']
    }
  },

  // SIGNATURE TOOLS
  {
    name: 'get_signature_info',
    description: 'Get information about authenticated nodes. Shows which nodes are authenticated and their available operations.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Specific node type (optional)' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      }
    }
  },
  {
    name: 'add_node_to_signature',
    description: 'Authenticate a node and add to signature. Validates credentials and stores them securely.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type (e.g., "github")' },
        auth: { type: 'object', description: 'Auth credentials (e.g., {access_token: "xxx"})' },
        defaults: { type: 'object', description: 'Default parameters', default: {} },
        operations: { type: 'array', description: 'Optional: specific operation names to include (e.g., ["list_repos", "get_user"])' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type', 'auth']
    }
  },
  {
    name: 'remove_node_from_signature',
    description: 'Remove node authentication from signature file.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type to remove' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type']
    }
  },
  {
    name: 'update_node_defaults',
    description: 'Update default parameters for an authenticated node.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type' },
        defaults: { type: 'object', description: 'New default parameters' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type', 'defaults']
    }
  },
  {
    name: 'validate_signature',
    description: 'Validate signature file format and content.',
    inputSchema: {
      type: 'object',
      properties: {
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      }
    }
  },

  // CATALOG TOOLS
  {
    name: 'list_available_nodes',
    description: 'List all available nodes from catalog. Filter by category or authentication status.',
    inputSchema: {
      type: 'object',
      properties: {
        category: { type: 'string', description: 'Filter by category (optional)' },
        authenticated_only: { type: 'boolean', description: 'Show only authenticated', default: false },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      }
    }
  },
  {
    name: 'get_node_info',
    description: 'Get detailed information about a specific node type.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type']
    }
  },
  {
    name: 'list_node_operations',
    description: 'List all operations available for a specific node with their parameters and descriptions.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type (e.g., "github")' }
      },
      required: ['node_type']
    }
  },
  {
    name: 'search_operations',
    description: 'Search for operations across all nodes by keyword.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query (e.g., "list", "create", "repository")' }
      },
      required: ['query']
    }
  },
  {
    name: 'get_operation_details',
    description: 'Get detailed information about a specific operation including parameters, examples, and usage.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type (e.g., "github")' },
        operation: { type: 'string', description: 'Operation name (e.g., "list_repositories")' }
      },
      required: ['node_type', 'operation']
    }
  },

  // VALIDATION TOOLS
  {
    name: 'validate_params',
    description: 'Validate parameters before execution. Checks required params and merges with defaults.',
    inputSchema: {
      type: 'object',
      properties: {
        node_type: { type: 'string', description: 'Node type' },
        operation: { type: 'string', description: 'Operation name' },
        params: { type: 'object', description: 'Parameters to validate' },
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      },
      required: ['node_type', 'operation', 'params']
    }
  },

  // UTILITY TOOLS
  {
    name: 'get_system_status',
    description: 'Get MCP server status and health information.',
    inputSchema: {
      type: 'object',
      properties: {
        signature_path: { type: 'string', default: 'signatures/user.act.sig' }
      }
    }
  },

  // UI INTERACTION TOOLS
  // NOTE: request_node_auth removed - use add_node_to_signature for inline authentication
  {
    name: 'request_parameters',
    description: requestParametersTool.description,
    inputSchema: requestParametersTool.inputSchema
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
      // Execution
      case 'execute_node_operation':
        return await executeNodeOperation(args);

      // Signature
      case 'get_signature_info':
        return await getSignatureInfo(args);
      case 'add_node_to_signature':
        return await addNodeToSignature(args);
      case 'remove_node_from_signature':
        return await removeNodeFromSignature(args);
      case 'update_node_defaults':
        return await updateNodeDefaults(args);
      case 'validate_signature':
        return await validateSignature(args);

      // Catalog
      case 'list_available_nodes':
        return await listAvailableNodes(args);
      case 'get_node_info':
        return await getNodeInfo(args);
      case 'list_node_operations':
        return await listNodeOperations(args);
      case 'search_operations':
        return await searchOperationsTool(args);
      case 'get_operation_details':
        return await getOperationDetailsTool(args);

      // Validation
      case 'validate_params':
        return await validateParams(args);

      // Utility
      case 'get_system_status':
        return await getSystemStatus(args);

      // UI Interaction
      case 'request_parameters':
        return await requestParametersTool.execute(args);

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

// CLI mode - direct tool execution
async function cliMode(toolName, paramsJson) {
  try {
    const params = JSON.parse(paramsJson);

    let result;
    switch (toolName) {
      // Execution
      case 'execute_node_operation':
        result = await executeNodeOperation(params);
        break;

      // Signature
      case 'get_signature_info':
        result = await getSignatureInfo(params);
        break;
      case 'add_node_to_signature':
        result = await addNodeToSignature(params);
        break;
      case 'remove_node_from_signature':
        result = await removeNodeFromSignature(params);
        break;
      case 'update_node_defaults':
        result = await updateNodeDefaults(params);
        break;
      case 'validate_signature':
        result = await validateSignature(params);
        break;

      // Catalog
      case 'list_available_nodes':
        result = await listAvailableNodes(params);
        break;
      case 'get_node_info':
        result = await getNodeInfo(params);
        break;
      case 'list_node_operations':
        result = await listNodeOperations(params);
        break;
      case 'search_operations':
        result = await searchOperationsTool(params);
        break;
      case 'get_operation_details':
        result = await getOperationDetailsTool(params);
        break;

      // Validation
      case 'validate_params':
        result = await validateParams(params);
        break;

      // Utility
      case 'get_system_status':
        result = await getSystemStatus(params);
        break;

      // UI Interaction
      case 'request_parameters':
        result = await requestParametersTool.execute(params);
        break;

      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }

    // Extract data from MCP response format
    if (result && result.content && result.content[0] && result.content[0].text) {
      const data = JSON.parse(result.content[0].text);
      // Use process.stdout.write for large outputs to avoid buffering issues
      process.stdout.write(JSON.stringify(data));
    } else {
      process.stdout.write(JSON.stringify({ status: 'error', error: 'Invalid response format' }));
    }
  } catch (error) {
    console.log(JSON.stringify({
      status: 'error',
      error: error.message,
      tool: toolName
    }));
    process.exit(1);
  }
}

// Start server or CLI mode
async function main() {
  // Check if running in CLI mode (with arguments)
  if (process.argv.length >= 4) {
    const toolName = process.argv[2];
    const paramsJson = process.argv[3];
    await cliMode(toolName, paramsJson);
    process.exit(0);
  } else {
    // Standard MCP server mode
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('Flow Architect MCP Server running');
    console.error('Version: 1.0.0');
    console.error('Tools: 13 available');
    console.error('  - Execution: execute_node_operation');
    console.error('  - Signature: get_signature_info, add_node_to_signature, remove_node_from_signature, update_node_defaults, validate_signature');
    console.error('  - Catalog: list_available_nodes, get_node_info, list_node_operations, search_operations, get_operation_details');
    console.error('  - Validation: validate_params');
    console.error('  - Utility: get_system_status');
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
