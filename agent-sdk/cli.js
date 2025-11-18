#!/usr/bin/env node
/**
 * ACT Flow Architect CLI
 *
 * Interactive CLI for generating ACT workflows with AI
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import FlowArchitectAgent from './index.js';
import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const program = new Command();

program
  .name('act-flow-architect')
  .description('AI Agent that generates ACT workflow files')
  .version('1.0.0');

program
  .command('generate')
  .alias('g')
  .description('Generate a new ACT flow from description')
  .argument('<request>', 'Natural language description of the flow')
  .option('-o, --output <path>', 'Output file path')
  .option('-m, --model <model>', 'Claude model to use', 'claude-sonnet-4-20250514')
  .option('--no-validate', 'Skip flow validation')
  .option('--dry-run', 'Generate but don\'t save')
  .option('-v, --verbose', 'Verbose output')
  .action(async (request, options) => {
    const spinner = ora('Initializing Flow Architect Agent...').start();

    try {
      const agent = new FlowArchitectAgent({
        model: options.model,
        verbose: options.verbose
      });

      spinner.text = 'Generating flow...';

      const result = await agent.generateFlow(request, {
        outputPath: options.output,
        validate: options.validate,
        dryRun: options.dryRun
      });

      spinner.succeed('Flow generated successfully!');

      if (!options.dryRun) {
        console.log(chalk.green(`\n✓ Flow saved to: ${result.path}`));
        console.log(chalk.gray(`\nRun it with:`));
        console.log(chalk.cyan(`  python act/miniact_executor.py ${result.path}`));
      } else {
        console.log(chalk.yellow('\n⚠ Dry run - flow not saved'));
      }

      if (result.metadata?.needs_auth?.length > 0) {
        console.log(chalk.yellow(`\n⚠ Authentication needed for: ${result.metadata.needs_auth.join(', ')}`));
        console.log(chalk.gray(`Use: claude "add <node_type> to signature with <credentials>"`));
      }

    } catch (error) {
      spinner.fail('Flow generation failed');
      console.error(chalk.red(`\nError: ${error.message}`));
      process.exit(1);
    }
  });

program
  .command('examples')
  .alias('e')
  .description('Show example flow requests')
  .action(() => {
    console.log(chalk.bold('\n📚 Example Flow Requests:\n'));

    const examples = [
      {
        category: 'API Integration',
        requests: [
          'Build a flow that sends GitHub issues to Slack daily',
          'Create an API that fetches weather data and stores in PostgreSQL',
          'Sync Monday.com tasks to Asana every hour'
        ]
      },
      {
        category: 'Data Processing',
        requests: [
          'Process CSV files and send summary via email',
          'Extract data from API, transform it, and load to database',
          'Generate daily reports from PostgreSQL and post to Slack'
        ]
      },
      {
        category: 'AI-Powered',
        requests: [
          'Analyze customer feedback with OpenAI and categorize in database',
          'Auto-respond to support emails using Claude',
          'Generate blog posts from topics and publish to CMS'
        ]
      },
      {
        category: 'Automation',
        requests: [
          'Monitor website uptime and alert on Slack if down',
          'Backup database to S3 every night at 2 AM',
          'Auto-create Jira tickets from Slack messages'
        ]
      }
    ];

    examples.forEach(({ category, requests }) => {
      console.log(chalk.cyan(`${category}:`));
      requests.forEach(req => {
        console.log(chalk.gray(`  • ${req}`));
      });
      console.log();
    });

    console.log(chalk.gray('Usage:'));
    console.log(chalk.white('  act-flow-architect generate "Your request here"'));
  });

program
  .command('list-nodes')
  .alias('ln')
  .description('List all available ACT nodes')
  .option('-c, --category <category>', 'Filter by category')
  .action(async (options) => {
    const spinner = ora('Fetching available nodes...').start();

    try {
      // Quick check using MCP
      const { execSync } = await import('child_process');
      const mcpPath = join(__dirname, '../mcp/index.js');

      const result = execSync(`node ${mcpPath}`, {
        input: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'list_available_nodes',
            arguments: {}
          },
          id: 1
        }),
        encoding: 'utf-8'
      });

      const parsed = JSON.parse(result);
      const nodes = parsed.result?.content?.[0]?.text
        ? JSON.parse(parsed.result.content[0].text).nodes
        : [];

      spinner.succeed(`Found ${nodes.length} nodes`);

      console.log(chalk.bold('\n📦 Available ACT Nodes:\n'));

      // Group by category (simplified)
      const categories = {
        'Core': ['py', 'if', 'set', 'loop', 'timer'],
        'AI': ['openai', 'gemini', 'rag', 'prompt_templating'],
        'Database': ['neon', 'postgresql', 'mongodb', 'redis'],
        'Communication': ['slack', 'email', 'teams', 'telegram'],
        'Cloud': ['aws', 's3', 'google_cloud', 'azure'],
      };

      Object.entries(categories).forEach(([cat, nodeTypes]) => {
        const available = nodeTypes.filter(n => nodes.includes(n));
        if (available.length > 0) {
          console.log(chalk.cyan(`${cat}:`));
          console.log(chalk.gray(`  ${available.join(', ')}`));
        }
      });

      console.log(chalk.gray(`\n...and ${nodes.length - 20} more`));

    } catch (error) {
      spinner.fail('Failed to fetch nodes');
      console.error(chalk.red(`Error: ${error.message}`));
    }
  });

program
  .command('check-auth')
  .alias('ca')
  .description('Check which nodes are authenticated')
  .action(async () => {
    const spinner = ora('Checking authentication status...').start();

    try {
      const { execSync } = await import('child_process');
      const mcpPath = join(__dirname, '../mcp/index.js');

      const result = execSync(`node ${mcpPath}`, {
        input: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'get_signature_info',
            arguments: {}
          },
          id: 1
        }),
        encoding: 'utf-8'
      });

      const parsed = JSON.parse(result);
      const authInfo = parsed.result?.content?.[0]?.text
        ? JSON.parse(parsed.result.content[0].text)
        : {};

      spinner.succeed('Authentication status retrieved');

      console.log(chalk.bold('\n🔐 Authenticated Nodes:\n'));

      if (authInfo.authenticated_nodes?.length > 0) {
        authInfo.authenticated_nodes.forEach(node => {
          console.log(chalk.green(`✓ ${node.type}`));
          if (node.operations?.length > 0) {
            console.log(chalk.gray(`  Operations: ${node.operations.slice(0, 3).join(', ')}${node.operations.length > 3 ? '...' : ''}`));
          }
        });
      } else {
        console.log(chalk.yellow('No nodes authenticated yet'));
        console.log(chalk.gray('\nAuthenticate nodes with:'));
        console.log(chalk.cyan('  claude "add openai to signature with api_key=sk-..."'));
      }

    } catch (error) {
      spinner.fail('Failed to check authentication');
      console.error(chalk.red(`Error: ${error.message}`));
    }
  });

program.parse();
