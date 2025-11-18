#!/usr/bin/env node
/**
 * ACT Tools Integration for Claude Agent SDK
 *
 * Wraps all 150+ ACT nodes as Agent SDK tools, making them available
 * for autonomous agent execution.
 *
 * This allows Claude Agent to:
 * - Execute any ACT node operation directly
 * - Use signature authentication automatically
 * - Combine multiple nodes autonomously
 * - Handle errors and retries intelligently
 */

import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import toml from '@iarna/toml';
import { readFile } from 'fs/promises';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MCP_SERVER_PATH = join(__dirname, '../mcp/index.js');
const SIGNATURE_PATH = join(__dirname, '../mcp/signatures/user.act.sig');

/**
 * Execute MCP tool via subprocess
 */
async function executeMcpTool(toolName, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [MCP_SERVER_PATH], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`MCP tool failed: ${stderr}`));
        return;
      }

      try {
        const lines = stdout.trim().split('\n');
        const lastLine = lines[lines.length - 1];
        const response = JSON.parse(lastLine);

        if (response.error) {
          reject(new Error(response.error.message || 'MCP tool error'));
        } else {
          // Extract content from MCP response
          const content = response.result?.content?.[0]?.text;
          if (content) {
            try {
              resolve(JSON.parse(content));
            } catch {
              resolve(content);
            }
          } else {
            resolve(response.result);
          }
        }
      } catch (error) {
        reject(new Error(`Failed to parse MCP response: ${error.message}`));
      }
    });

    // Send request
    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      },
      id: 1
    };

    proc.stdin.write(JSON.stringify(request) + '\n');
    proc.stdin.end();
  });
}

/**
 * Load authenticated nodes from signature
 */
async function loadSignature() {
  try {
    const content = await readFile(SIGNATURE_PATH, 'utf-8');
    const signature = toml.parse(content);

    const authenticatedNodes = [];
    for (const [key, value] of Object.entries(signature)) {
      if (key.startsWith('node:') && !key.includes('.')) {
        const nodeType = key.replace('node:', '');
        if (value.authenticated) {
          authenticatedNodes.push({
            type: nodeType,
            enabled: value.enabled,
            operations: Object.keys(signature[`${key}.operations`] || {})
          });
        }
      }
    }

    return authenticatedNodes;
  } catch (error) {
    console.warn('Failed to load signature:', error.message);
    return [];
  }
}

/**
 * Create Agent SDK tool for executing ACT nodes
 */
export const executeActNode = tool({
  name: 'execute_act_node',
  description: `Execute any of 150+ ACT workflow nodes (GitHub, Slack, OpenAI, databases, etc.).

Use this to:
- Fetch data from APIs (GitHub, Slack, weather, etc.)
- Send messages (Slack, email, Teams)
- Query databases (PostgreSQL, MongoDB, Redis)
- Call AI services (OpenAI, Claude)
- Process data (Python code execution)
- And 140+ more integrations

Examples:
- execute_act_node({node_type: "github", operation: "list_repos", params: {owner: "octocat"}})
- execute_act_node({node_type: "slack", operation: "post_message", params: {channel: "#general", text: "Hello"}})
- execute_act_node({node_type: "openai", operation: "chat_completion", params: {model: "gpt-4", messages: [...]}})
`,
  parameters: z.object({
    node_type: z.string().describe('Node type (e.g., "github", "slack", "openai", "neon")'),
    operation: z.string().describe('Operation name (e.g., "list_repos", "post_message", "chat_completion")'),
    params: z.record(z.any()).describe('Operation parameters as key-value pairs')
  }),
  execute: async ({ node_type, operation, params }) => {
    try {
      const result = await executeMcpTool('execute_node_operation', {
        node_type,
        operation,
        params,
        override_defaults: false
      });

      return {
        success: true,
        result: result.result || result,
        metadata: {
          node_type,
          operation,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        node_type,
        operation
      };
    }
  }
});

/**
 * Create Agent SDK tool for discovering ACT nodes
 */
export const listActNodes = tool({
  name: 'list_act_nodes',
  description: `List all 150+ available ACT nodes and their capabilities.

Returns node types grouped by category:
- AI: openai, gemini, rag, prompt_templating
- Communication: slack, email, teams, telegram
- Database: neon (PostgreSQL), mongodb, redis, dynamodb
- Cloud: aws, s3, google_cloud, azure
- Development: github, linear, asana, monday
- And many more...

Use this to discover what nodes are available before executing them.`,
  parameters: z.object({}),
  execute: async () => {
    try {
      const result = await executeMcpTool('list_available_nodes', {});
      return {
        nodes: result.nodes || [],
        count: result.count || 0,
        categories: {
          'AI/ML': ['openai', 'gemini', 'rag', 'embedding_similarity'],
          'Communication': ['slack', 'email', 'teams', 'telegram'],
          'Database': ['neon', 'postgresql', 'mongodb', 'redis'],
          'Cloud': ['aws', 's3', 'google_cloud', 'azure'],
          'Development': ['github', 'linear', 'asana', 'monday'],
          'Payment': ['stripe', 'paypal', 'square', 'coinbase'],
          'Core': ['py', 'if', 'loop', 'timer', 'set']
        }
      };
    } catch (error) {
      return { error: error.message };
    }
  }
});

/**
 * Create Agent SDK tool for getting node details
 */
export const getActNodeInfo = tool({
  name: 'get_act_node_info',
  description: `Get detailed information about a specific ACT node, including:
- Available operations
- Required parameters for each operation
- Authentication requirements
- Usage examples

Use this after list_act_nodes to understand how to use a specific node.`,
  parameters: z.object({
    node_type: z.string().describe('Node type to get info for (e.g., "github", "slack")')
  }),
  execute: async ({ node_type }) => {
    try {
      const [nodeInfo, operations] = await Promise.all([
        executeMcpTool('get_node_info', { node_type }),
        executeMcpTool('list_node_operations', { node_type })
      ]);

      return {
        type: node_type,
        description: nodeInfo.description || '',
        operations: operations.operations || [],
        authenticated: nodeInfo.authenticated || false,
        ...nodeInfo
      };
    } catch (error) {
      return { error: error.message };
    }
  }
});

/**
 * Create Agent SDK tool for checking authentication
 */
export const checkActAuth = tool({
  name: 'check_act_authentication',
  description: `Check which ACT nodes are authenticated and ready to use.

Returns list of authenticated nodes with their available operations.
Nodes that require authentication but aren't set up will not appear.

Use this to know which nodes you can execute immediately.`,
  parameters: z.object({}),
  execute: async () => {
    try {
      const authenticated = await loadSignature();
      return {
        authenticated_nodes: authenticated,
        count: authenticated.length,
        ready_to_use: authenticated.filter(n => n.enabled).map(n => n.type)
      };
    } catch (error) {
      return { error: error.message };
    }
  }
});

/**
 * Create Agent SDK tool for searching operations
 */
export const searchActOperations = tool({
  name: 'search_act_operations',
  description: `Search for ACT node operations by keyword.

Examples:
- "send" → find all operations that send messages/data
- "list" → find all operations that list/fetch data
- "create" → find all operations that create resources
- "database" → find all database-related operations`,
  parameters: z.object({
    query: z.string().describe('Search query (e.g., "send", "list", "create")')
  }),
  execute: async ({ query }) => {
    try {
      const result = await executeMcpTool('search_operations', { query });
      return result;
    } catch (error) {
      return { error: error.message };
    }
  }
});

/**
 * Get all ACT tools for Agent SDK
 */
export function getAllActTools() {
  return [
    executeActNode,
    listActNodes,
    getActNodeInfo,
    checkActAuth,
    searchActOperations
  ];
}

/**
 * Example: Using ACT tools in an Agent SDK workflow
 */
export async function exampleAgentWorkflow() {
  const { query } = await import('@anthropic-ai/claude-agent-sdk');

  const result = query({
    prompt: `
      Help me analyze the ACT repository:

      1. List available ACT nodes
      2. Check which nodes are authenticated
      3. If GitHub is authenticated, fetch repository info
      4. If Slack is authenticated, send a summary

      Be autonomous - use the ACT tools to complete this task.
    `,
    options: {
      model: 'claude-sonnet-4-20250514',
      tools: getAllActTools(),
      permissionMode: 'default'
    }
  });

  for await (const message of result) {
    if (message.type === 'assistant') {
      console.log('Agent:', message.content);
    }
    if (message.type === 'tool_use') {
      console.log('Using:', message.name);
    }
    if (message.type === 'result') {
      console.log('Result:', message.result);
    }
  }
}

// CLI usage
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.log('🔧 ACT Tools Integration for Claude Agent SDK\n');
  console.log('Available tools:');
  console.log('  - execute_act_node       Execute any ACT node operation');
  console.log('  - list_act_nodes         List all 150+ available nodes');
  console.log('  - get_act_node_info      Get details about a specific node');
  console.log('  - check_act_authentication  Check authenticated nodes');
  console.log('  - search_act_operations  Search operations by keyword\n');

  console.log('Usage in Agent SDK:');
  console.log(`
import { query } from '@anthropic-ai/agent-sdk';
import { getAllActTools } from './act-tools-integration.js';

const result = query({
  prompt: "Your autonomous task here",
  options: {
    tools: getAllActTools()
  }
});
`);
}

export default {
  executeActNode,
  listActNodes,
  getActNodeInfo,
  checkActAuth,
  searchActOperations,
  getAllActTools,
  exampleAgentWorkflow
};
