#!/usr/bin/env node
/**
 * Simple Flow Generator - Works WITHOUT MCP server
 * Generates ACT flows using Claude API directly
 */

import Anthropic from '@anthropic-ai/sdk';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

async function generateFlow(request) {
  console.log('🤖 Generating flow...\n');
  console.log(`Request: ${request}\n`);

  const prompt = `You are an expert at creating ACT workflow files.

User wants: ${request}

Create a complete .flow file (TOML format) with:

1. [workflow] section with name, description, start_node
2. [node:*] sections for each step
3. [edges] section showing flow
4. [configuration] if it's an API (agent_enabled = true, agent_port = 9000)

Available node types:
- py: Python code execution
- aci: API server (for creating REST APIs)
- openai: OpenAI integration
- slack: Slack integration
- email: Email sending
- neon: PostgreSQL database
- redis: Redis cache
- timer: Scheduled tasks

For HTTP requests, use py node with requests library.

Return ONLY valid TOML, no explanation.`;

  const message = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [{
      role: 'user',
      content: prompt
    }]
  });

  const flowContent = message.content[0].text;

  console.log('✅ Flow generated!\n');

  // Simple validation - check for basic structure
  const hasWorkflow = flowContent.includes('[workflow]');
  const hasNodes = flowContent.match(/\[node:/);

  if (hasWorkflow && hasNodes) {
    console.log('✓ Flow structure looks valid');
  } else {
    console.warn('⚠️  Warning: Generated flow may be incomplete');
  }

  // Save
  const filename = request
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 50);

  const path = join('../flows', `${filename}.flow`);
  await writeFile(path, flowContent, 'utf-8');

  console.log(`\n💾 Saved: ${path}`);
  console.log(`\nRun with:`);
  console.log(`  python act/miniact_executor.py ${path}`);

  return { path, content: flowContent };
}

if (process.argv.length < 3) {
  console.error('Usage: node simple-flow-generator.js "your request"');
  process.exit(1);
}

const request = process.argv.slice(2).join(' ');
generateFlow(request).catch(console.error);
