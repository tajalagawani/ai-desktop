#!/usr/bin/env node
/**
 * Execute ACT flows with autonomous agent mode
 */

import { query } from '@anthropic-ai/claude-agent-sdk';
import { getAllActTools } from './act-tools-integration.js';
import { readFile } from 'fs/promises';
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

/**
 * Parse ACT flow file using custom INI-like format (NOT TOML)
 * ACT uses Python's configparser which accepts colons in section names: [node:Name]
 */
function parseActFlow(content) {
  const flow = { workflow: {}, parameters: {}, edges: {} };
  const sections = {};

  let currentSection = null;
  const lines = content.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();

    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith(';')) continue;

    // Section header: [section] or [node:Name]
    const sectionMatch = trimmed.match(/^\[([^\]]+)\]$/);
    if (sectionMatch) {
      currentSection = sectionMatch[1];
      sections[currentSection] = {};
      continue;
    }

    // Key-value pair
    const kvMatch = trimmed.match(/^([^=]+?)\s*=\s*(.+)$/);
    if (kvMatch && currentSection) {
      const key = kvMatch[1].trim();
      let value = kvMatch[2].trim();

      // Parse value type
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1); // Remove quotes
      } else if (value === 'true') {
        value = true;
      } else if (value === 'false') {
        value = false;
      } else if (!isNaN(value)) {
        value = Number(value);
      }

      sections[currentSection][key] = value;
    }
  }

  // Map sections to flow structure
  for (const [sectionName, sectionData] of Object.entries(sections)) {
    if (sectionName === 'workflow') {
      flow.workflow = sectionData;
    } else if (sectionName === 'parameters') {
      flow.parameters = sectionData;
    } else if (sectionName === 'edges') {
      flow.edges = sectionData;
    } else if (sectionName.startsWith('node:')) {
      flow[sectionName] = sectionData;
    }
  }

  return flow;
}

export async function executeFlowWithAgent(flowPath, parameters = {}, options = {}) {
  const flowContent = await readFile(flowPath, 'utf-8');
  const flow = parseActFlow(flowContent);

  const {
    model = 'claude-sonnet-4-20250514',
    autonomyLevel = 'medium',
    onProgress = null
  } = options;

  const nodeNames = Object.keys(flow).filter(k => k.startsWith('node:'));
  const availableNodes = nodeNames.map(k => ({
    name: k.replace('node:', ''),
    type: flow[k].type,
    operation: flow[k].operation,
    config: flow[k]
  }));

  const agentPrompt = `Execute this workflow autonomously:

Workflow: ${flow.workflow.name}
Description: ${flow.workflow.description}
Start Node: ${flow.workflow.start_node}

Available Nodes:
${availableNodes.map(n => `- ${n.name} (${n.type}.${n.operation})`).join('\n')}

Parameters Provided:
${JSON.stringify(parameters, null, 2)}

Your Mission:
1. Use check_act_authentication to see what's available
2. Execute nodes in logical order to achieve the workflow goal
3. Use execute_act_node for each step
4. Handle errors and retry if needed
5. Return final results

Execute now!`;

  const result = query({
    prompt: agentPrompt,
    options: {
      model,
      tools: getAllActTools(),
      permissionMode: autonomyLevel,
      allowedTools: [
        'execute_act_node',
        'list_act_nodes',
        'get_act_node_info',
        'check_act_authentication',
        'search_act_operations',
        'TodoWrite'
      ]
    }
  });

  const execution = {
    flow: flow.workflow.name,
    startedAt: new Date().toISOString(),
    steps: [],
    finalResult: null
  };

  for await (const message of result) {
    if (message.type === 'tool_use' && message.name === 'execute_act_node') {
      execution.steps.push({
        node: message.input.node_type,
        operation: message.input.operation,
        timestamp: new Date().toISOString()
      });
    }

    if (onProgress) {
      onProgress(message);
    }

    if (message.type === 'result') {
      execution.finalResult = message.result;
      execution.completedAt = new Date().toISOString();
    }
  }

  return execution;
}

if (process.argv[1] === import.meta.url) {
  const flowPath = process.argv[2];

  if (!flowPath) {
    console.error('Usage: node agent-executor.js <flow-file>');
    process.exit(1);
  }

  executeFlowWithAgent(flowPath, {}, {
    onProgress: (msg) => {
      if (msg.type === 'assistant') console.log('Agent:', msg.content);
      if (msg.type === 'tool_use') console.log('Executing:', msg.name);
    }
  }).then(result => {
    console.log('\nExecution Complete:');
    console.log(JSON.stringify(result, null, 2));
  }).catch(console.error);
}
