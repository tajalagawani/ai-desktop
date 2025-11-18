#!/usr/bin/env node
/**
 * Test suite for Flow Architect Agent
 */

import FlowArchitectAgent from './index.js';
import { readFile, unlink } from 'fs/promises';
import { existsSync } from 'fs';
import toml from '@iarna/toml';
import chalk from 'chalk';

const tests = [
  {
    name: 'Simple API Wrapper',
    request: 'Build a flow that creates an API to fetch GitHub user info',
    expectedNodes: ['aci', 'py', 'github'],
    timeout: 60000
  },
  {
    name: 'Scheduled Sync',
    request: 'Create a flow that syncs data from an API to PostgreSQL every day at 9 AM',
    expectedNodes: ['timer', 'py', 'neon'],
    timeout: 60000
  },
  {
    name: 'AI Integration',
    request: 'Build a customer support bot that uses OpenAI to analyze emails and creates Slack notifications',
    expectedNodes: ['openai', 'slack', 'py'],
    timeout: 90000
  }
];

async function runTest(test) {
  console.log(chalk.bold(`\n🧪 Testing: ${test.name}`));
  console.log(chalk.gray(`Request: ${test.request}\n`));

  const agent = new FlowArchitectAgent({ verbose: false });

  try {
    const result = await agent.generateFlow(test.request, {
      validate: true,
      dryRun: true  // Don't save during tests
    });

    // Validate TOML is parseable
    let parsedFlow;
    try {
      parsedFlow = toml.parse(result.flow);
      console.log(chalk.green('✓ Valid TOML generated'));
    } catch (error) {
      throw new Error(`Invalid TOML: ${error.message}`);
    }

    // Check workflow section exists
    if (!parsedFlow.workflow) {
      throw new Error('Missing [workflow] section');
    }
    console.log(chalk.green('✓ Workflow section present'));

    // Check start node exists
    if (!parsedFlow.workflow.start_node) {
      throw new Error('Missing start_node');
    }
    const startNodeKey = `node:${parsedFlow.workflow.start_node}`;
    if (!parsedFlow[startNodeKey]) {
      throw new Error(`Start node "${parsedFlow.workflow.start_node}" not found`);
    }
    console.log(chalk.green('✓ Start node valid'));

    // Check expected nodes are used
    const nodeKeys = Object.keys(parsedFlow).filter(k => k.startsWith('node:'));
    const nodeTypes = nodeKeys.map(k => parsedFlow[k].type).filter(Boolean);

    console.log(chalk.gray(`  Nodes used: ${nodeTypes.join(', ')}`));

    const missingNodes = test.expectedNodes.filter(n => !nodeTypes.includes(n));
    if (missingNodes.length > 0) {
      console.log(chalk.yellow(`⚠ Expected nodes not found: ${missingNodes.join(', ')}`));
    } else {
      console.log(chalk.green('✓ All expected nodes present'));
    }

    // Check edges exist
    if (!parsedFlow.edges) {
      throw new Error('Missing [edges] section');
    }
    console.log(chalk.green('✓ Edges section present'));

    console.log(chalk.green.bold(`\n✅ Test passed: ${test.name}`));
    return { success: true, test: test.name };

  } catch (error) {
    console.log(chalk.red.bold(`\n❌ Test failed: ${test.name}`));
    console.log(chalk.red(`Error: ${error.message}`));
    return { success: false, test: test.name, error: error.message };
  }
}

async function runAllTests() {
  console.log(chalk.bold.cyan('\n🚀 Flow Architect Agent Test Suite\n'));
  console.log(chalk.gray('─'.repeat(60)));

  const results = [];

  for (const test of tests) {
    const result = await runTest(test);
    results.push(result);

    // Add delay between tests
    if (test !== tests[tests.length - 1]) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  // Summary
  console.log(chalk.gray('\n' + '─'.repeat(60)));
  console.log(chalk.bold.cyan('\n📊 Test Summary\n'));

  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  console.log(chalk.green(`✓ Passed: ${passed}/${tests.length}`));
  if (failed > 0) {
    console.log(chalk.red(`✗ Failed: ${failed}/${tests.length}`));
    console.log('\nFailed tests:');
    results.filter(r => !r.success).forEach(r => {
      console.log(chalk.red(`  • ${r.test}: ${r.error}`));
    });
  }

  console.log();

  if (failed === 0) {
    console.log(chalk.green.bold('🎉 All tests passed!\n'));
    process.exit(0);
  } else {
    console.log(chalk.red.bold('❌ Some tests failed\n'));
    process.exit(1);
  }
}

// Check for API key
if (!process.env.ANTHROPIC_API_KEY) {
  console.error(chalk.red('\n❌ Error: ANTHROPIC_API_KEY environment variable not set'));
  console.error(chalk.gray('\nSet it with:'));
  console.error(chalk.cyan('  export ANTHROPIC_API_KEY=sk-ant-your-key-here'));
  console.error();
  process.exit(1);
}

runAllTests().catch(error => {
  console.error(chalk.red('\n❌ Test suite failed:'), error);
  process.exit(1);
});
