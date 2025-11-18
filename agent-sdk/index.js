#!/usr/bin/env node
/**
 * ACT Flow Architect Agent
 *
 * An autonomous AI agent that generates complete ACT workflow files
 * using Claude Agent SDK and your existing MCP infrastructure.
 *
 * Usage:
 *   node index.js "Build a flow that sends GitHub issues to Slack daily"
 */

import { query } from '@anthropic-ai/claude-agent-sdk';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment from agent-sdk directory first (has ANTHROPIC_API_KEY)
const __dirname = dirname(fileURLToPath(import.meta.url));
const agentEnvPath = join(__dirname, '.env');
const parentEnvPath = join(__dirname, '../.env');

console.log('[Agent SDK] Loading environment from:', agentEnvPath);
dotenv.config({ path: agentEnvPath }); // Load agent-sdk/.env first

// Log API key status for debugging
if (process.env.ANTHROPIC_API_KEY) {
  console.log('[Agent SDK] API Key loaded from .env:', process.env.ANTHROPIC_API_KEY.substring(0, 20) + '...');
} else {
  console.warn('[Agent SDK] WARNING: No API key found in', agentEnvPath);
  console.log('[Agent SDK] Trying parent .env:', parentEnvPath);
  dotenv.config({ path: parentEnvPath }); // Fallback to parent .env
  if (process.env.ANTHROPIC_API_KEY) {
    console.log('[Agent SDK] API Key loaded from parent .env:', process.env.ANTHROPIC_API_KEY.substring(0, 20) + '...');
  } else {
    console.error('[Agent SDK] ERROR: No API key found in either location!');
  }
}

const ACT_ROOT = join(__dirname, '..');
const MCP_SERVER_PATH = join(ACT_ROOT, 'mcp/index.js');
const FLOWS_DIR = join(ACT_ROOT, 'flows');
const SIGNATURE_PATH = join(ACT_ROOT, 'mcp/signatures/user.act.sig');

/**
 * Parse ACT flow file using custom INI-like format (NOT TOML)
 * ACT uses Python's configparser which accepts colons in section names: [node:Name]
 */
function parseActFlow(content) {
  const flow = { workflow: {}, parameters: {}, edges: {}, settings: {}, configuration: {} };
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
      } else if (value.startsWith('"""') || value.startsWith("'''")) {
        // Multi-line string - just keep as is for now
        value = value;
      } else if (value === 'true') {
        value = true;
      } else if (value === 'false') {
        value = false;
      } else if (!isNaN(value) && value !== '') {
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
    } else if (sectionName === 'settings') {
      flow.settings = sectionData;
    } else if (sectionName === 'configuration') {
      flow.configuration = sectionData;
    } else if (sectionName === 'env') {
      flow.env = sectionData;
    } else if (sectionName === 'deployment') {
      flow.deployment = sectionData;
    } else if (sectionName.startsWith('node:')) {
      flow[sectionName] = sectionData;
    }
  }

  return flow;
}

/**
 * Flow Architect Agent
 * Generates complete ACT workflow files autonomously
 */
export class FlowArchitectAgent {
  constructor(options = {}) {
    this.mcpServerPath = options.mcpServerPath || MCP_SERVER_PATH;
    this.flowsDir = options.flowsDir || FLOWS_DIR;
    this.signaturePath = options.signaturePath || SIGNATURE_PATH;
    this.model = options.model || process.env.ACT_AGENT_MODEL || process.env.DEFAULT_MODEL || 'claude-sonnet-4-5-20250929';
    this.verbose = options.verbose !== undefined ? options.verbose : (process.env.VERBOSE === 'true');
    this.streamMode = process.env.STREAM_MODE === 'true';
  }


  /**
   * Generate a flow from natural language description
   */
  async generateFlow(userRequest, options = {}) {
    const {
      outputPath = null,
      validate = true,
      dryRun = false
    } = options;

    console.log('🤖 Flow Architect Agent Starting...\n');
    console.log(`📝 Request: ${userRequest}\n`);

    // Build the agent prompt
    // Read conversation context from environment variable
    let conversationHistory = [];
    if (process.env.CONVERSATION_CONTEXT) {
      try {
        const contextData = JSON.parse(process.env.CONVERSATION_CONTEXT);
        conversationHistory = contextData.conversationHistory || [];
        console.log(`📚 Loaded ${conversationHistory.length} previous messages from conversation history\n`);
      } catch (error) {
        console.warn("⚠️  Failed to parse conversation context:", error.message);
      }
    }

    const agentPrompt = this.buildAgentPrompt(userRequest, conversationHistory);

    // SECURITY: Check if sandbox bypass is allowed
    // This should ONLY be true on trusted VPS servers running as root
    const allowSandboxBypass = process.env.ALLOW_SANDBOX_BYPASS === 'true';

    if (allowSandboxBypass) {
      console.log('⚠️  [SECURITY] Sandbox bypass enabled - running with unrestricted access\n');
    } else {
      console.log('🔒 [SECURITY] Sandbox enabled - running with normal security restrictions\n');
    }

    // Configure Agent SDK with ACT MCP server
    const agentConfig = {
      model: this.model,
      apiKey: process.env.ANTHROPIC_API_KEY,  // CRITICAL: Must provide API key to avoid OAuth
      // NO maxTokens limit - allow flows of any size
      mcpServers: {
        'act-workflow': {
          type: 'stdio',
          command: 'node',
          args: [this.mcpServerPath]
        }
      },
      allowedTools: [
        // MCP tools for discovering ACT capabilities
        'list_available_nodes',
        'get_node_info',
        'list_node_operations',
        'get_operation_details',
        'search_operations',
        'get_signature_info',
        'validate_params',
        // Built-in tools for file operations
        'Write',
        'Read',
        'Bash',
        // MANDATORY: Todo tracking (agent MUST use this)
        'TodoWrite',
        // Enable Agent Skills
        'Skill'
      ],
      permissionMode: 'bypassPermissions',  // Auto-approve MCP tools
      dangerouslyDisableSandbox: allowSandboxBypass,  // Only true if ALLOW_SANDBOX_BYPASS=true in .env
      settingSources: ['user', 'project'],  // Enable loading from user and project .claude directories
      cwd: __dirname  // Set working directory to agent-sdk directory for project-level settings
    };

    let generatedFlow = null;
    let flowMetadata = {};

    console.log('🔍 Agent analyzing requirements...\n');

    // Run the agent
    const result = query({
      prompt: agentPrompt,
      options: agentConfig
    });

    // Stream agent execution
    for await (const message of result) {
      if (this.verbose) {
        console.log('\n[DEBUG] Message:', JSON.stringify(message, null, 2));
      }

      if (message.type === 'assistant') {
        // Agent thinking/planning - stream the assistant's response
        const content = message.message?.content;
        if (content && Array.isArray(content)) {
          for (const block of content) {
            if (block.type === 'text' && block.text) {
              console.log(`💭 ${block.text}`);
            }
          }
        }
      }

      if (message.type === 'tool_use') {
        // Agent using tools
        const toolName = message.message?.name || message.name || 'unknown';
        const toolInput = message.message?.input || message.input || {};
        console.log(`\n🔧 Tool: ${toolName}`);
        console.log(`   Input: ${JSON.stringify(toolInput, null, 2)}`);
      }

      if (message.type === 'tool_result') {
        // Tool execution result
        const output = message.output || message.message?.output || 'success';
        const preview = typeof output === 'string' ? output.substring(0, 200) : JSON.stringify(output).substring(0, 200);
        console.log(`\n✓ Tool result: ${preview}...`);
      }

      if (message.type === 'result') {
        // Get the result - save it EXACTLY as is
        let resultText = typeof message.result === 'string' ? message.result : JSON.stringify(message.result);

        // Clean up: Remove markdown code fences if present
        resultText = resultText.trim();
        if (resultText.startsWith('```')) {
          resultText = resultText.replace(/^```[a-z]*\n?/, '');
          resultText = resultText.replace(/\n?```$/, '');
          resultText = resultText.trim();
        }

        // If Claude added text before [workflow], strip it
        const workflowStart = resultText.indexOf('[workflow]');
        if (workflowStart > 0) {
          resultText = resultText.substring(workflowStart);
          console.log('⚠️  Removed explanatory text before [workflow]');
        }

        // Save it as-is without any parsing or validation
        generatedFlow = resultText;

        // Set default metadata
        flowMetadata = {
          nodes_used: [],
          authenticated_nodes: [],
          needs_auth: [],
          estimated_complexity: 'unknown',
          description: 'Generated flow'
        };

        console.log('\n✅ Flow generation complete!\n');
      }
    }

    if (!generatedFlow) {
      throw new Error('Agent failed to generate flow');
    }

    // NO PARSING - NO VALIDATION - Just save the flow as-is!
    // The flow format is custom and should be saved exactly as Claude generates it

    // Save flow file directly
    if (!dryRun) {
      const savedPath = await this.saveFlowRaw(generatedFlow, outputPath);
      console.log(`\n💾 Flow saved to: ${savedPath}`);
      console.log(`\n🎉 Success! Flow is ready to use.`);
      console.log(`\nRun it with:`);
      console.log(`  python act/miniact_executor.py ${savedPath}\n`);
      return { flow: generatedFlow, path: savedPath };
    }

    return { flow: generatedFlow };
  }

  /**
   * Build the agent prompt with context and instructions
   */
  buildAgentPrompt(userRequest, conversationHistory = []) {
    return `You are the ACT Flow Architect - an expert at building workflow automation files.

ACT (Universal Task Agent) is a workflow automation system with 150+ pre-built nodes for integrations.

USER REQUEST:
${userRequest}

## CONVERSATION HISTORY:
${conversationHistory.length > 0 ?
  "Previous conversation:\n" + conversationHistory.map((msg, i) =>
    `${i + 1}. ${msg.role.toUpperCase()}: ${msg.content}`
  ).join("\n\n") + "\n\nContinue the conversation above based on the user's new message in USER REQUEST." :
  "This is the start of a new conversation."}

YOUR MISSION:
Generate a complete, production-ready ACT workflow file (.flow) that fulfills the user's request.

## ⚠️ DYNAMIC TODO SYSTEM ⚠️

**YOU MUST CREATE TASK-SPECIFIC TODOS - NOT THE SAME GENERIC LIST FOR EVERYTHING!**

### The Three Commandments:

1. **Match Complexity** - Simple task = 4-7 todos | Medium = 8-12 | Complex = 12-20
2. **Use User's Words** - If they say "GitHub", your todos must say "GitHub"
3. **Show Real Work** - Each todo = specific action they can track

### Quick Decision Guide:

**SIMPLE (4-7 todos):** Basic API, single integration, straightforward flow
Example: "Build weather API" → 5 todos covering fetch + serve

**MEDIUM (8-12 todos):** 2-3 integrations, some logic, moderate complexity
Example: "GitHub to Slack" → 10 todos covering research + build + connect

**COMPLEX (12-20 todos):** Multiple services, filtering, auth, scheduling, data transforms
Example: "Multi-stage data pipeline" → 18 todos with detailed breakdown

### Required Phases (Scale Based on Complexity):

**Phase 1: Discovery** (1-3 todos)
- Analyze [USER'S EXACT REQUEST using their words]
- Check signature + discover relevant nodes

**Phase 2: Research** (Group for simple, separate for complex)
- Research [SpecificNodeType] node (get_node_info + list_operations + get_operation_details)
- Do this for EVERY node type you'll use

**Phase 3: Build** (2-12 todos - MOST SCALING HAPPENS HERE)
- Design [their specific architecture]
- Create [node:SpecificName] for [their feature]
- One todo per major component

**Phase 4: Finalize** (1-2 todos)
- Generate complete .flow file

### Examples:

**Simple: "Build basic weather API"** (5 todos)
  1. Analyze weather API requirements
  2. Check signature and research py/aci nodes
  3. Design weather fetch + API serve architecture
  4. Create weather data fetch and API server nodes
  5. Generate weather-api.flow file

**Medium: "GitHub to Slack sync"** (10 todos)
  1. Analyze GitHub to Slack sync requirements
  2. Check signature for GitHub and Slack nodes
  3. Discover and identify relevant integration nodes
  4. Research GitHub node operations
  5. Research Slack node operations
  6. Design GitHub → Slack workflow architecture
  7. Create GitHub issues fetch node
  8. Create Slack message formatting node
  9. Create Slack send message node
  10. Generate github-slack-sync.flow file

**Complex: "Scheduled GitHub issues filter to Slack"** (14 todos)
  1. Analyze GitHub to Slack sync with filtering and scheduling
  2. Check signature for GitHub, Slack, scheduler nodes
  3. Discover available nodes for all integrations
  4. Research GitHub node (list_issues, get_details)
  5. Research Slack node (send_message, format)
  6. Research scheduler node for daily triggers
  7. Research filter/if node for criteria logic
  8. Design scheduled GitHub → Filter → Slack pipeline
  9. Create scheduler node for daily trigger
  10. Create GitHub issues fetch node
  11. Create filter node for issue criteria
  12. Create Slack message formatter node
  13. Create Slack send message node
  14. Generate complete scheduled-github-slack.flow

### Strict Rules:

1. **TodoWrite FIRST** - Before any other tool
2. **Use their EXACT terminology** - "PostgreSQL" not "database", "Slack" not "messaging"
3. **Cover ALL features** they requested
4. **Update in real-time**: Mark "in_progress" when starting, "completed" when done
5. **Research EVERY node**: get_node_info + list_node_operations + get_operation_details
6. **Scale appropriately**: Don't use 15 todos for "simple API"

### Update Pattern:

When starting a task, call TodoWrite marking it "in_progress":
  TodoWrite({ todos: [..., { content: "Task X", status: "in_progress", activeForm: "..." }, ...] })

When completing, mark it "completed" and start the next:
  TodoWrite({ todos: [..., { content: "Task X", status: "completed", activeForm: "..." }, { content: "Task Y", status: "in_progress", activeForm: "..." }, ...] })

**NOW: Analyze the user's request and create YOUR SPECIFIC todo list with TodoWrite!**

CRITICAL RULES - READ CAREFULLY:

1. MANDATORY Sections:
   - [workflow] section with start_node is REQUIRED
   - start_node MUST be QUOTED string: start_node = "NodeName"
   - start_node value must reference an existing node name exactly
   - Every node MUST have a type field
   - Node names use format [node:NodeName] with COLON (PascalCase preferred)

2. Node Type Syntax:
   - ALL types MUST be quoted: type = "py", type = "neon", type = "aci"
   - Node sections use colon: [node:NodeName] NOT [node.NodeName]
   - String values: Use quotes: label = "Description"

3. NO HTTP Node:
   - There is NO 'http' or 'request' node type
   - Use py node with requests library for ALL HTTP calls

4. Python Node for HTTP (MANDATORY for HTTP requests):
   [node:FetchData]
   type = "py"
   label = "Fetch data from API"
   code = """
   import requests

   def fetch(**kwargs):
       response = requests.get('https://api.example.com/data', timeout=10)
       response.raise_for_status()
       return {'result': response.json()}
   """
   function = fetch

5. Placeholder Syntax (MUST BE QUOTED):
   - Parameters: "{{.Parameter.param_name}}" (ALWAYS use quotes around placeholders)
   - Node results: "{{NodeName.result.field}}" or "{{NodeName.result.result.field}}"
   - Environment vars: "\${ENV_VAR_NAME}"
   - Examples:
     * port = "{{.Parameter.port}}" ✅ CORRECT
     * port = {{.Parameter.port}} ❌ WRONG - missing quotes
     * message = "{{PreviousNode.result.data}}" ✅ CORRECT

6. Special Node Types:
   - if nodes: MUST return {"result": boolean}, edge order [0]=true, [1]=false
   - switch nodes: MUST return {"selected_node": "target_name"}
   - set nodes: MUST return {"key": "name", "value": data}
   - aci nodes: MUST have mode = server for API routes

7. TOML SYNTAX RULES:
   - NO multi-line inline tables/dictionaries
   - NO multi-line arrays - arrays MUST be on ONE line
   - Inline tables MUST be on ONE line: config = { key = "value", num = 123 }
   - Arrays MUST be on ONE line: items = ["a", "b", "c"]
   - For complex data, use string values or separate sections
   - AVOID: response = {\n  "key": "value"\n}  ❌ INVALID
   - AVOID: routes = [\n  item1,\n  item2\n]  ❌ INVALID
   - USE: response_message = "Hello World"  ✅ VALID
   - USE: routes = ["/hello", "/world"]  ✅ VALID

8. PARAMETERS SECTION RULES:
   - Parameters are SIMPLE key-value pairs ONLY
   - NO type definitions, NO schema, NO { type = "..." } syntax
   - CORRECT: port = 8080, message = "Hello"
   - WRONG: port = { type = "number", default = 8080 }  ❌ INVALID

EXAMPLE WORKFLOW STRUCTURE:
[workflow]
name = "Flow Name"
description = "Description"
start_node = "FirstNode"    # MUST BE QUOTED

[parameters]
# Simple key-value pairs ONLY - no type definitions
port = 8080
message = "Hello World"

[node:FirstNode]
type = "py"                 # ALL types MUST be quoted
label = "Description"       # Quotes for strings
param = "{{.Parameter.port}}"  # Reference parameters with quotes

[edges]
FirstNode = SecondNode      # NO quotes for node references in edges

[configuration]
agent_enabled = true

WORKFLOW PROCESS:
1. **Discover Available Nodes**
   - Use list_available_nodes() to see all 150+ node types
   - Use search_operations() to find relevant nodes for the task
   - Use get_node_info() and get_operation_details() for specific nodes

2. **Check Authentication**
   - Use get_signature_info() to see which nodes are already authenticated
   - For authenticated nodes, you can use them directly
   - For non-authenticated nodes, include them but add a comment about authentication

3. **Design the Workflow**
   - Identify the logical steps needed
   - Map each step to appropriate ACT nodes
   - Design the graph flow (edges between nodes)
   - Consider error handling and retries

4. **Generate Complete TOML Flow**
   Create a .flow file with:

   [workflow]
   name = "Descriptive Name"
   description = "What this flow does"
   start_node = "FirstNode"

   [parameters]
   # Any user inputs needed

   [node:NodeName]
   type = "node_type"
   operation = "operation_name"
   # All required parameters

   [edges]
   # Graph connections

   [configuration]
   # If it's an API, add agent config

5. **Best Practices**
   - Use meaningful node names (e.g., "FetchGitHubIssues" not "Node1")
   - Add descriptive comments
   - Include parameter validation
   - Use placeholders correctly: {{NodeName.result.field}}
   - For HTTP requests, use py node with requests library
   - Include error handling where appropriate
   - Add [settings] for retry/timeout configuration

6. **CRITICAL: Return Format**
   You MUST return the raw ACT workflow file content ONLY.

   RULES:
   - NO explanations before the flow
   - NO explanations after the flow
   - NO markdown code fences
   - NO JSON wrapping
   - The FIRST character of your response MUST be the opening bracket: [
   - The FIRST line MUST be: [workflow]

   Your response should look EXACTLY like this:
   [workflow]
   name = "Example Flow"
   description = "This is an example"
   start_node = "FirstNode"

   [node:FirstNode]
   type = "py"
   ...

   CRITICAL: Start your response with [workflow] - nothing before it!

IMPORTANT NOTES:
- Use ONLY nodes that exist in the catalog (check with list_available_nodes)
- Verify parameter names with get_operation_details()
- For authenticated nodes, you can use them immediately
- For non-authenticated nodes, include them but note they need authentication
- The flow must be syntactically valid TOML
- Use realistic, working examples

## 🚨 MANDATORY WORKFLOW - MUST FOLLOW THIS ORDER 🚨

**CRITICAL: You MUST follow these steps IN ORDER. Do NOT skip to flow generation!**

### Step 1: CREATE DYNAMIC TODO LIST (FIRST ACTION!)
- Call TodoWrite with task-specific todos (4-7 simple, 8-12 medium, 12-20 complex)
- Use user's exact terminology
- Mark first task "in_progress"

### Step 2: CHECK SIGNATURE (MANDATORY!)
- Call get_signature_info() to see authenticated nodes
- Include this in your todos - NEVER skip

### Step 3: DISCOVER NODES (MANDATORY!)
- Call list_available_nodes() to see all 150+ node types
- Call search_operations() with relevant keywords
- Identify which nodes you'll use
- Include in your todos - NEVER skip

### Step 4: RESEARCH EVERY NODE (MANDATORY - NO EXCEPTIONS!)
**For EACH AND EVERY node type you decide to use, you MUST call ALL 3 tools:**
  a) get_node_info(node_type) - Get basic info
  b) list_node_operations(node_type) - Get all operations
  c) get_operation_details(node_type, operation_name) - For EACH operation you'll use

Example: If using github and slack nodes:
  - get_node_info("github")
  - list_node_operations("github")
  - get_operation_details("github", "list_issues")
  - get_node_info("slack")
  - list_node_operations("slack")
  - get_operation_details("slack", "post_message")

**CRITICAL: NO node should be used in the flow without ALL 3 research calls!**

### Step 5: DESIGN ARCHITECTURE
- Plan workflow structure based on research
- Map data flow and placeholders
- Design edges (node connections)

### Step 6: GENERATE FLOW
- Only AFTER all research is complete
- Return ONLY raw .flow content starting with [workflow]
- Mark all todos completed

**ENFORCEMENT: If you generate a flow without calling ALL 3 MCP tools for EVERY node, the flow WILL fail!**

**NOW BEGIN: Call TodoWrite to create your dynamic, task-specific todo list!**`;
  }

  /**
   * Validate flow structure
   */
  async validateFlow(parsedFlow) {
    const errors = [];

    // Check required sections
    if (!parsedFlow.workflow) {
      errors.push('Missing [workflow] section');
    } else {
      if (!parsedFlow.workflow.name) errors.push('Missing workflow.name');
      if (!parsedFlow.workflow.start_node) errors.push('Missing workflow.start_node');
    }

    // Check nodes exist
    const nodeNames = Object.keys(parsedFlow).filter(key => key.startsWith('node:'));
    if (nodeNames.length === 0) {
      errors.push('No nodes defined in workflow');
    }

    // Check start node exists
    if (parsedFlow.workflow?.start_node) {
      const startNodeKey = `node:${parsedFlow.workflow.start_node}`;
      if (!parsedFlow[startNodeKey]) {
        errors.push(`Start node "${parsedFlow.workflow.start_node}" not found in nodes`);
      }
    }

    // Check each node has required fields
    for (const key of nodeNames) {
      const node = parsedFlow[key];
      const nodeName = key.replace('node:', '');

      if (!node.type) {
        errors.push(`Node "${nodeName}" missing type`);
      }
    }

    if (errors.length > 0) {
      throw new Error(`Flow validation failed:\n${errors.map(e => `  - ${e}`).join('\n')}`);
    }
  }

  /**
   * Display flow summary
   */
  displayFlowSummary(parsedFlow, metadata) {
    console.log('\n📊 Flow Summary:');
    console.log('─'.repeat(50));
    console.log(`Name: ${parsedFlow.workflow?.name || 'Unnamed'}`);
    console.log(`Description: ${parsedFlow.workflow?.description || 'No description'}`);

    const nodeNames = Object.keys(parsedFlow).filter(key => key.startsWith('node:'));
    console.log(`Nodes: ${nodeNames.length}`);

    if (metadata.nodes_used) {
      console.log(`Node types: ${metadata.nodes_used.join(', ')}`);
    }

    if (metadata.authenticated_nodes?.length > 0) {
      console.log(`✓ Authenticated: ${metadata.authenticated_nodes.join(', ')}`);
    }

    if (metadata.needs_auth?.length > 0) {
      console.log(`⚠ Needs auth: ${metadata.needs_auth.join(', ')}`);
    }

    console.log('─'.repeat(50));
  }

  /**
   * Save flow to file RAW - no parsing, no validation
   */
  async saveFlowRaw(flowContent, outputPath) {
    // Determine output path
    let finalPath = outputPath;

    if (!finalPath) {
      // Try to extract workflow name from the flow content
      const nameMatch = flowContent.match(/name\s*=\s*["']([^"']+)["']/);
      const flowName = nameMatch ? nameMatch[1] : 'generated-flow';

      const filename = flowName
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
      finalPath = join(this.flowsDir, `${filename}.flow`);
    }

    // Ensure flows directory exists
    await mkdir(dirname(finalPath), { recursive: true });

    // Save flow file EXACTLY as generated - no modifications!
    await writeFile(finalPath, flowContent, 'utf-8');

    return finalPath;
  }

  /**
   * Save flow to file (DEPRECATED - kept for backwards compatibility)
   */
  async saveFlow(flowContent, outputPath) {
    return this.saveFlowRaw(flowContent, outputPath);
  }
}

/**
 * CLI Entry Point
 */
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const userRequest = process.argv[2];

  if (!userRequest) {
    console.error('Usage: node index.js "Your flow request here"');
    console.error('\nExamples:');
    console.error('  node index.js "Build a flow that sends GitHub issues to Slack daily"');
    console.error('  node index.js "Create an API that fetches weather data and stores in PostgreSQL"');
    process.exit(1);
  }

  const agent = new FlowArchitectAgent({
    // verbose and model will be read from environment variables if not specified
  });

  agent.generateFlow(userRequest)
    .then(result => {
      console.log('\n🎉 Success! Flow is ready to use.');
      console.log(`\nRun it with:`);
      console.log(`  python act/miniact_executor.py ${result.path}`);
    })
    .catch(error => {
      console.error('\n❌ Error:', error.message);
      process.exit(1);
    });
}

export default FlowArchitectAgent;
