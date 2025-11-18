#!/usr/bin/env node
/**
 * Autonomous ACT Agent
 * Executes tasks using 150+ ACT nodes autonomously
 */

import { query } from '@anthropic-ai/claude-agent-sdk';
import { getAllActTools } from './act-tools-integration.js';
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

export async function runAutonomousAgent(task, options = {}) {
  const {
    model = 'claude-sonnet-4-20250514',
    permissionMode = 'default',
    onProgress = null
  } = options;

  const result = query({
    prompt: task,
    options: {
      model,
      tools: getAllActTools(),
      permissionMode,
      allowedTools: [
        'execute_act_node',
        'list_act_nodes',
        'get_act_node_info',
        'check_act_authentication',
        'search_act_operations',
        'TodoWrite',
        'Bash',
        'Read',
        'Write'
      ]
    }
  });

  let finalResult = null;

  for await (const message of result) {
    if (onProgress) {
      onProgress(message);
    }

    if (message.type === 'result') {
      finalResult = message.result;
    }
  }

  return finalResult;
}

if (process.argv[1] === import.meta.url) {
  const task = process.argv.slice(2).join(' ');

  if (!task) {
    console.error('Usage: node autonomous-agent.js <task>');
    process.exit(1);
  }

  runAutonomousAgent(task, {
    onProgress: (msg) => {
      if (msg.type === 'assistant') console.log('Agent:', msg.content);
      if (msg.type === 'tool_use') console.log('Tool:', msg.name);
    }
  }).then(result => {
    console.log('\nResult:', JSON.stringify(result, null, 2));
  }).catch(console.error);
}
