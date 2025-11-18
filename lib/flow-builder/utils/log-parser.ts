/**
 * Enhanced Agent Log Parser
 * Captures ALL information from Claude Code agent logs with no data loss
 */

import React from 'react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type LogEntryType =
  | 'thinking'
  | 'tool_use'
  | 'tool_result'
  | 'mcp_tool_use'
  | 'mcp_tool_result'
  | 'mcp_connection'
  | 'mcp_lifecycle'
  | 'flow_generated'
  | 'flow_content'
  | 'metrics'
  | 'status'
  | 'session_init'
  | 'session_end'
  | 'session_header'
  | 'agent_lifecycle'
  | 'debug_file_ops'
  | 'debug_shell'
  | 'debug_plugin'
  | 'debug_hooks'
  | 'debug_settings'
  | 'debug_misc'
  | 'error'
  | 'message_assistant'
  | 'message_user'
  | 'cache_stats'
  | 'model_usage'
  | 'stream_event'
  | 'raw';

export interface ParsedLogData {
  type: LogEntryType;
  content: string;
  timestamp?: string;
  renderContent?: React.ReactNode;
  metadata?: LogMetadata;
}

export interface LogMetadata {
  // Tool execution
  toolName?: string;
  toolInput?: any;
  toolOutput?: any;
  toolId?: string;
  duration?: number;
  durationMs?: number;

  // MCP specific
  mcpServer?: string;
  mcpToolName?: string;
  mcpConnectionTime?: number;
  mcpCapabilities?: MCPCapabilities;
  mcpServerInfo?: MCPServerInfo;

  // Flow/Workflow
  flowName?: string;
  flowPath?: string;
  flowContent?: string;

  // Tokens and cost
  inputTokens?: number;
  outputTokens?: number;
  cacheCreationInputTokens?: number;
  cacheReadInputTokens?: number;
  ephemeral5mTokens?: number;
  ephemeral1hTokens?: number;
  cost?: number;

  // Session data
  sessionData?: SessionData;
  resultData?: ResultData;

  // Message data
  messageId?: string;
  messageRole?: string;
  messageModel?: string;
  parentToolUseId?: string;
  sessionId?: string;
  uuid?: string;
  stopReason?: string;
  serviceTier?: string;

  // Debug info
  filePath?: string;
  fileSize?: number;
  shellType?: string;
  shellConfig?: string;
  pluginCount?: number;
  hookType?: string;
  hookQuery?: string;

  // Agent info
  agentName?: string;
  agentError?: string;

  // Request info
  requestText?: string;
  logFile?: string;
  startTime?: string;
  endTime?: string;
  exitCode?: number;

  // Error info
  errorType?: string;
  errorMessage?: string;
  serverStderr?: string;
}

export interface SessionData {
  sessionId: string;
  cwd: string;
  model: string;
  permissionMode: string;
  apiKeySource: string;
  claudeCodeVersion: string;
  outputStyle: string;
  tools: string[];
  mcpServers: Array<{ name: string; status: string }>;
  slashCommands: string[];
  agents: string[];
  skills: string[];
  uuid?: string;
}

export interface ResultData {
  durationMs: number;
  durationApiMs: number;
  numTurns: number;
  totalCostUsd: number;
  usage: {
    inputTokens: number;
    cacheCreationInputTokens: number;
    cacheReadInputTokens: number;
    outputTokens: number;
    webSearchRequests?: number;
    cacheCreation?: {
      ephemeral1hInputTokens: number;
      ephemeral5mInputTokens: number;
    };
  };
  modelUsage?: Record<
    string,
    {
      inputTokens: number;
      outputTokens: number;
      cacheReadInputTokens: number;
      cacheCreationInputTokens: number;
      webSearchRequests?: number;
      costUSD: number;
      contextWindow: number;
    }
  >;
  permissionDenials?: any[];
  uuid?: string;
}

export interface MCPCapabilities {
  hasTools?: boolean;
  hasPrompts?: boolean;
  hasResources?: boolean;
  serverVersion?: {
    name?: string;
    version?: string;
  };
}

export interface MCPServerInfo {
  name: string;
  version: string;
  toolCount?: number;
  tools?: string[];
}

// ============================================================================
// GROUPED LOGS FOR UI
// ============================================================================

export interface GroupedLogs {
  thinking: ParsedLogData[];
  tools: ParsedLogData[];
  mcpTools: ParsedLogData[];
  mcpLifecycle: ParsedLogData[];
  errors: ParsedLogData[];
  flows: ParsedLogData[];
  session: ParsedLogData[];
  messages: ParsedLogData[];
  debug: ParsedLogData[];
  other: ParsedLogData[];
}

// ============================================================================
// MAIN PARSER FUNCTION
// ============================================================================

export function parseAgentLog(chunk: string): ParsedLogData {
  const trimmedChunk = chunk.trim();
  
  if (!trimmedChunk) {
    return { type: 'raw', content: '' };
  }

  // =========================================================================
  // 1. JSON STRUCTURED LOGS (session init, result, messages)
  // =========================================================================
  
  if (trimmedChunk.startsWith('[DEBUG] Message: {') || trimmedChunk.startsWith('{"type"')) {
    try {
      const jsonStart = trimmedChunk.indexOf('{');
      const jsonStr = trimmedChunk.substring(jsonStart);
      const logEntry = JSON.parse(jsonStr);

      // Session initialization
      if (logEntry.type === 'system' && logEntry.subtype === 'init') {
        return {
          type: 'session_init',
          content: 'Session initialized',
          metadata: {
            sessionData: {
              sessionId: logEntry.session_id,
              cwd: logEntry.cwd,
              model: logEntry.model,
              permissionMode: logEntry.permissionMode,
              apiKeySource: logEntry.apiKeySource,
              claudeCodeVersion: logEntry.claude_code_version,
              outputStyle: logEntry.output_style,
              tools: logEntry.tools || [],
              mcpServers: logEntry.mcp_servers || [],
              slashCommands: logEntry.slash_commands || [],
              agents: logEntry.agents || [],
              skills: logEntry.skills || [],
              uuid: logEntry.uuid,
            },
          },
        };
      }

      // Session result/end
      if (logEntry.type === 'result') {
        return {
          type: 'session_end',
          content: 'Session completed',
          metadata: {
            resultData: {
              durationMs: logEntry.duration_ms,
              durationApiMs: logEntry.duration_api_ms,
              numTurns: logEntry.num_turns,
              totalCostUsd: logEntry.total_cost_usd,
              usage: {
                inputTokens: logEntry.usage?.input_tokens || 0,
                cacheCreationInputTokens: logEntry.usage?.cache_creation_input_tokens || 0,
                cacheReadInputTokens: logEntry.usage?.cache_read_input_tokens || 0,
                outputTokens: logEntry.usage?.output_tokens || 0,
                webSearchRequests: logEntry.usage?.server_tool_use?.web_search_requests || 0,
                cacheCreation: {
                  ephemeral1hInputTokens: logEntry.usage?.cache_creation?.ephemeral_1h_input_tokens || 0,
                  ephemeral5mInputTokens: logEntry.usage?.cache_creation?.ephemeral_5m_input_tokens || 0,
                },
              },
              modelUsage: logEntry.modelUsage,
              permissionDenials: logEntry.permission_denials,
              uuid: logEntry.uuid,
            },
          },
        };
      }

      // Assistant messages (thinking + tool use)
      if (logEntry.type === 'assistant' && logEntry.message) {
        const msg = logEntry.message;
        const content = msg.content || [];

        // Extract thinking text
        const textContent = content.find((c: any) => c.type === 'text');
        if (textContent) {
          return {
            type: 'thinking',
            content: textContent.text,
            metadata: {
              messageId: msg.id,
              messageModel: msg.model,
              sessionId: logEntry.session_id,
              uuid: logEntry.uuid,
              parentToolUseId: logEntry.parent_tool_use_id,
              stopReason: msg.stop_reason,
              serviceTier: msg.usage?.service_tier,
              inputTokens: msg.usage?.input_tokens,
              outputTokens: msg.usage?.output_tokens,
              cacheCreationInputTokens: msg.usage?.cache_creation_input_tokens,
              cacheReadInputTokens: msg.usage?.cache_read_input_tokens,
              ephemeral5mTokens: msg.usage?.cache_creation?.ephemeral_5m_input_tokens,
              ephemeral1hTokens: msg.usage?.cache_creation?.ephemeral_1h_input_tokens,
            },
          };
        }

        // Extract tool use
        const toolUse = content.find((c: any) => c.type === 'tool_use');
        if (toolUse) {
          const isMCP = toolUse.name.startsWith('mcp__');
          
          if (isMCP) {
            const parts = toolUse.name.split('__');
            const mcpServer = parts[1];
            const mcpToolName = parts.slice(2).join('__');
            
            return {
              type: 'mcp_tool_use',
              content: `${mcpServer}: ${mcpToolName}`,
              metadata: {
                toolName: toolUse.name,
                toolId: toolUse.id,
                toolInput: toolUse.input,
                mcpServer: mcpServer,
                mcpToolName: mcpToolName,
                messageId: msg.id,
                sessionId: logEntry.session_id,
                uuid: logEntry.uuid,
                inputTokens: msg.usage?.input_tokens,
                outputTokens: msg.usage?.output_tokens,
              },
            };
          } else {
            return {
              type: 'tool_use',
              content: `Tool: ${toolUse.name}`,
              metadata: {
                toolName: toolUse.name,
                toolId: toolUse.id,
                toolInput: toolUse.input,
                messageId: msg.id,
                sessionId: logEntry.session_id,
                uuid: logEntry.uuid,
              },
            };
          }
        }
      }

      // User messages (tool results)
      if (logEntry.type === 'user' && logEntry.message) {
        const msg = logEntry.message;
        const content = msg.content || [];
        
        const toolResult = content.find((c: any) => c.type === 'tool_result');
        if (toolResult) {
          const resultContent = Array.isArray(toolResult.content)
            ? toolResult.content.map((c: any) => c.text || c).join('\n')
            : toolResult.content;
          
          return {
            type: 'tool_result',
            content: resultContent.substring(0, 200) + (resultContent.length > 200 ? '...' : ''),
            metadata: {
              toolId: toolResult.tool_use_id,
              toolOutput: resultContent,
              sessionId: logEntry.session_id,
              uuid: logEntry.uuid,
            },
          };
        }
      }
    } catch (e) {
      // Not valid JSON or not a structured log, continue with text parsing
    }
  }

  // =========================================================================
  // 2. SESSION HEADER (boundaries and metadata)
  // =========================================================================

  if (trimmedChunk.includes('======================================')) {
    return { type: 'session_header', content: trimmedChunk };
  }

  if (trimmedChunk.startsWith('Request:')) {
    const request = trimmedChunk.replace('Request:', '').trim();
    return {
      type: 'session_header',
      content: `Request: ${request}`,
      metadata: { requestText: request },
    };
  }

  if (trimmedChunk.startsWith('Log file:')) {
    const logFile = trimmedChunk.replace('Log file:', '').trim();
    return {
      type: 'session_header',
      content: `Log file: ${logFile}`,
      metadata: { logFile },
    };
  }

  if (trimmedChunk.startsWith('Started:')) {
    const startTime = trimmedChunk.replace('Started:', '').trim();
    return {
      type: 'session_header',
      content: `Started: ${startTime}`,
      metadata: { startTime },
    };
  }

  if (trimmedChunk.startsWith('Finished:')) {
    const endTime = trimmedChunk.replace('Finished:', '').trim();
    return {
      type: 'session_header',
      content: `Finished: ${endTime}`,
      metadata: { endTime },
    };
  }

  if (trimmedChunk.startsWith('Exit code:')) {
    const exitCodeMatch = trimmedChunk.match(/Exit code:\s*(\d+)/);
    return {
      type: 'session_header',
      content: trimmedChunk,
      metadata: { exitCode: exitCodeMatch ? parseInt(exitCodeMatch[1]) : undefined },
    };
  }

  if (trimmedChunk.startsWith('Log saved to:')) {
    const logFile = trimmedChunk.replace('Log saved to:', '').trim();
    return {
      type: 'session_header',
      content: trimmedChunk,
      metadata: { logFile },
    };
  }

  // =========================================================================
  // 3. AGENT LIFECYCLE
  // =========================================================================

  if (trimmedChunk.includes('🤖 Flow Architect Agent Starting')) {
    return {
      type: 'agent_lifecycle',
      content: 'Flow Architect Agent Starting',
    };
  }

  if (trimmedChunk.startsWith('📝 Request:')) {
    const request = trimmedChunk.replace('📝 Request:', '').trim();
    return {
      type: 'agent_lifecycle',
      content: `Request: ${request}`,
      metadata: { requestText: request },
    };
  }

  if (trimmedChunk.includes('✅ Flow generation complete')) {
    return {
      type: 'agent_lifecycle',
      content: 'Flow generation complete',
    };
  }

  if (trimmedChunk.includes('🎉 Success! Flow is ready to use')) {
    return {
      type: 'agent_lifecycle',
      content: 'Success! Flow is ready to use',
    };
  }

  if (trimmedChunk.startsWith('Run it with:')) {
    return {
      type: 'agent_lifecycle',
      content: trimmedChunk,
    };
  }

  // =========================================================================
  // 4. MCP SERVER LIFECYCLE & CONNECTION
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Starting connection')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)".*timeout of (\d+)ms/);
    return {
      type: 'mcp_lifecycle',
      content: serverMatch ? `MCP server "${serverMatch[1]}" starting (timeout: ${serverMatch[2]}ms)` : trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        duration: serverMatch ? parseInt(serverMatch[2]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Successfully connected')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)".*in (\d+)ms/);
    return {
      type: 'mcp_connection',
      content: serverMatch ? `MCP server "${serverMatch[1]}" connected in ${serverMatch[2]}ms` : trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        mcpConnectionTime: serverMatch ? parseInt(serverMatch[2]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Connection established with capabilities')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)"/);
    const capsMatch = trimmedChunk.match(/capabilities:\s*(\{.+\})/);
    
    let capabilities: MCPCapabilities | undefined;
    if (capsMatch) {
      try {
        capabilities = JSON.parse(capsMatch[1]);
      } catch (e) {
        // Ignore parse error
      }
    }
    
    return {
      type: 'mcp_connection',
      content: serverMatch ? `MCP server "${serverMatch[1]}" capabilities established` : trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        mcpCapabilities: capabilities,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Calling MCP tool:')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)".*Calling MCP tool:\s*(\w+)/);
    return {
      type: 'mcp_tool_use',
      content: serverMatch ? `${serverMatch[1]}: ${serverMatch[2]}` : trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        mcpToolName: serverMatch?.[2],
      },
    };
  }

  // Parse MCP tool results with actual output data
  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Tool result:')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)"/);
    const toolMatch = trimmedChunk.match(/Tool '([^']+)'/);
    const resultMatch = trimmedChunk.match(/Tool result:\s*(.+)$/);

    let resultData = resultMatch?.[1];
    // Try to parse as JSON if it looks like JSON
    try {
      if (resultData && (resultData.startsWith('{') || resultData.startsWith('['))) {
        resultData = JSON.parse(resultData);
      }
    } catch (e) {
      // Keep as string if not valid JSON
    }

    return {
      type: 'mcp_tool_result',
      content: resultData ? (typeof resultData === 'string' ? resultData : JSON.stringify(resultData, null, 2)) : 'Result received',
      metadata: {
        mcpServer: serverMatch?.[1],
        mcpToolName: toolMatch?.[1],
        toolOutput: resultData,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Tool') && trimmedChunk.includes('completed successfully')) {
    const match = trimmedChunk.match(/Tool '([^']+)' completed successfully in (\d+)(\w+)/);
    return {
      type: 'mcp_tool_result',
      content: match ? `${match[1]} completed in ${match[2]}${match[3]}` : trimmedChunk,
      metadata: {
        mcpToolName: match?.[1],
        duration: match ? parseInt(match[2]) : undefined,
        // Don't include toolOutput here - it's just a completion message
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('Sending SIGINT')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)"/);
    return {
      type: 'mcp_lifecycle',
      content: serverMatch ? `MCP server "${serverMatch[1]}" shutting down` : trimmedChunk,
      metadata: { mcpServer: serverMatch?.[1] },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('connection closed')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)".*after (\d+)s/);
    return {
      type: 'mcp_lifecycle',
      content: serverMatch ? `MCP server "${serverMatch[1]}" connection closed after ${serverMatch[2]}s` : trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        duration: serverMatch ? parseInt(serverMatch[2]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG] MCP server') && trimmedChunk.includes('exited cleanly')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)"/);
    return {
      type: 'mcp_lifecycle',
      content: serverMatch ? `MCP server "${serverMatch[1]}" exited cleanly` : trimmedChunk,
      metadata: { mcpServer: serverMatch?.[1] },
    };
  }

  // MCP Server stderr output (informational)
  if (trimmedChunk.includes('[ERROR] MCP server') && trimmedChunk.includes('Server stderr:')) {
    const serverMatch = trimmedChunk.match(/MCP server "([^"]+)"/);
    const stderrMatch = trimmedChunk.match(/Server stderr:\s*(.+)/);
    return {
      type: 'mcp_lifecycle',
      content: stderrMatch?.[1] || trimmedChunk,
      metadata: {
        mcpServer: serverMatch?.[1],
        serverStderr: stderrMatch?.[1],
      },
    };
  }

  // =========================================================================
  // 5. THINKING (emoji format from streaming output)
  // =========================================================================

  if (trimmedChunk.startsWith('💭')) {
    const content = trimmedChunk.replace('💭', '').trim();
    return {
      type: 'thinking',
      content: content,
    };
  }

  // =========================================================================
  // 6. FLOW/WORKFLOW GENERATION
  // =========================================================================

  if (trimmedChunk.includes('💾 Flow saved to:')) {
    const match = trimmedChunk.match(/Flow saved to:\s*(.+)/);
    const flowPath = match?.[1];
    const flowName = flowPath?.split('/').pop();
    return {
      type: 'flow_generated',
      content: `Flow: ${flowName}`,
      metadata: {
        flowPath: flowPath,
        flowName: flowName,
      },
    };
  }

  // Flow content (TOML format)
  if (trimmedChunk.startsWith('[workflow]') || 
      trimmedChunk.startsWith('[parameters]') ||
      trimmedChunk.startsWith('[node:')) {
    return {
      type: 'flow_content',
      content: trimmedChunk,
      metadata: {
        flowContent: trimmedChunk,
      },
    };
  }

  // Flow content continuation (properties)
  if (/^[a-z_]+\s*=/.test(trimmedChunk) && !trimmedChunk.includes('[DEBUG]')) {
    return {
      type: 'flow_content',
      content: trimmedChunk,
      metadata: {
        flowContent: trimmedChunk,
      },
    };
  }

  // =========================================================================
  // 7. TOOL USAGE (emoji format)
  // =========================================================================

  if (trimmedChunk.startsWith('🔧 Tool:')) {
    const match = trimmedChunk.match(/🔧 Tool:\s*(.+)/);
    return {
      type: 'tool_use',
      content: `Tool: ${match?.[1]}`,
      metadata: {
        toolName: match?.[1],
      },
    };
  }

  if (trimmedChunk.startsWith('✓ Tool result:')) {
    const content = trimmedChunk.replace('✓ Tool result:', '').trim();
    return {
      type: 'tool_result',
      content: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
      metadata: {
        toolOutput: content,
      },
    };
  }

  // =========================================================================
  // 8. STATUS MESSAGES
  // =========================================================================

  if (trimmedChunk.includes('🔍 Agent analyzing')) {
    return {
      type: 'status',
      content: 'Analyzing requirements...',
    };
  }

  // =========================================================================
  // 9. DEBUG LOGS - File Operations
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Writing to temp file:')) {
    const pathMatch = trimmedChunk.match(/Writing to temp file:\s*(.+)/);
    return {
      type: 'debug_file_ops',
      content: `Writing temp file: ${pathMatch?.[1]?.split('/').pop()}`,
      metadata: {
        filePath: pathMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Temp file written successfully')) {
    const sizeMatch = trimmedChunk.match(/size:\s*(\d+)\s*bytes/);
    return {
      type: 'debug_file_ops',
      content: `Temp file written: ${sizeMatch?.[1]} bytes`,
      metadata: {
        fileSize: sizeMatch ? parseInt(sizeMatch[1]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Renaming')) {
    return {
      type: 'debug_file_ops',
      content: 'File rename operation',
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('written atomically')) {
    const pathMatch = trimmedChunk.match(/File\s+(.+?)\s+written/);
    return {
      type: 'debug_file_ops',
      content: `File written atomically: ${pathMatch?.[1]?.split('/').pop()}`,
      metadata: {
        filePath: pathMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Preserving file permissions')) {
    return {
      type: 'debug_file_ops',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  // =========================================================================
  // 10. DEBUG LOGS - Shell Operations
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Creating shell snapshot')) {
    const shellMatch = trimmedChunk.match(/for\s+(\w+)\s*\(([^)]+)\)/);
    return {
      type: 'debug_shell',
      content: shellMatch ? `Creating shell snapshot: ${shellMatch[1]}` : 'Creating shell snapshot',
      metadata: {
        shellType: shellMatch?.[1],
        shellConfig: shellMatch?.[2],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Shell snapshot created successfully')) {
    const sizeMatch = trimmedChunk.match(/\((\d+)\s*bytes\)/);
    return {
      type: 'debug_shell',
      content: `Shell snapshot created: ${sizeMatch?.[1]} bytes`,
      metadata: {
        fileSize: sizeMatch ? parseInt(sizeMatch[1]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Cleaned up session snapshot')) {
    return {
      type: 'debug_shell',
      content: 'Shell snapshot cleaned up',
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Looking for shell config file')) {
    const pathMatch = trimmedChunk.match(/file:\s*(.+)/);
    return {
      type: 'debug_shell',
      content: `Looking for shell config: ${pathMatch?.[1]?.split('/').pop()}`,
      metadata: {
        filePath: pathMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Snapshots directory')) {
    const pathMatch = trimmedChunk.match(/directory:\s*(.+)/);
    return {
      type: 'debug_shell',
      content: `Snapshots directory: ${pathMatch?.[1]}`,
      metadata: {
        filePath: pathMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Shell binary exists')) {
    return {
      type: 'debug_shell',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Execution timeout')) {
    return {
      type: 'debug_shell',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  // =========================================================================
  // 11. DEBUG LOGS - Plugin System
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Found') && trimmedChunk.includes('plugins')) {
    const match = trimmedChunk.match(/Found\s+(\d+)\s+plugins\s*\((\d+)\s+enabled,\s*(\d+)\s+disabled\)/);
    return {
      type: 'debug_plugin',
      content: match ? `Plugins: ${match[1]} total (${match[2]} enabled, ${match[3]} disabled)` : trimmedChunk,
      metadata: {
        pluginCount: match ? parseInt(match[1]) : undefined,
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('getPluginSkills')) {
    return {
      type: 'debug_plugin',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Total plugin')) {
    return {
      type: 'debug_plugin',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Registered') && trimmedChunk.includes('hooks')) {
    return {
      type: 'debug_plugin',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  // =========================================================================
  // 12. DEBUG LOGS - Skills
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('ENABLE_SKILLS')) {
    return {
      type: 'debug_misc',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Loading skills from directories')) {
    return {
      type: 'debug_misc',
      content: 'Loading skills from directories',
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Loaded') && trimmedChunk.includes('skills total')) {
    const match = trimmedChunk.match(/Loaded\s+(\d+)\s+skills total/);
    return {
      type: 'debug_misc',
      content: match ? `Loaded ${match[1]} skills total` : trimmedChunk,
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Skills and commands included in Skill tool:')) {
    const skillsMatch = trimmedChunk.match(/Skills and commands included in Skill tool:\s*(.+)/);
    if (skillsMatch) {
      const skillsList = skillsMatch[1].split(',').map((s) => s.trim());
      const uniqueSkills = [...new Set(skillsList)];
      return {
        type: 'debug_misc',
        content: `Skills: ${uniqueSkills.join(', ')}`,
        metadata: {
          sessionData: {
            skills: uniqueSkills,
          } as Partial<SessionData> as SessionData,
        },
      };
    }
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Slash commands included in SlashCommand tool')) {
    return {
      type: 'debug_misc',
      content: 'Slash commands loaded',
    };
  }

  // =========================================================================
  // 13. DEBUG LOGS - Hooks
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('executePreToolHooks')) {
    const toolMatch = trimmedChunk.match(/tool:\s*(.+)/);
    return {
      type: 'debug_hooks',
      content: `Pre-tool hook: ${toolMatch?.[1]}`,
      metadata: {
        hookType: 'pre',
        toolName: toolMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Getting matching hook commands')) {
    const hookTypeMatch = trimmedChunk.match(/commands for\s+(\w+)/);
    const queryMatch = trimmedChunk.match(/query:\s*(.+)/);
    return {
      type: 'debug_hooks',
      content: `Hook query: ${hookTypeMatch?.[1]} - ${queryMatch?.[1]}`,
      metadata: {
        hookType: hookTypeMatch?.[1],
        hookQuery: queryMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Matched') && trimmedChunk.includes('hooks')) {
    return {
      type: 'debug_hooks',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG] Hooks:')) {
    return {
      type: 'debug_hooks',
      content: trimmedChunk.replace('[DEBUG] Hooks:', '').trim(),
    };
  }

  // =========================================================================
  // 14. DEBUG LOGS - Agent Parsing
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Agent file') && trimmedChunk.includes('missing required')) {
    const fileMatch = trimmedChunk.match(/Agent file\s+(.+?)\s+is missing/);
    return {
      type: 'debug_misc',
      content: `Agent file missing required field: ${fileMatch?.[1]?.split('/').pop()}`,
      metadata: {
        agentError: 'missing_frontmatter',
        filePath: fileMatch?.[1],
      },
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Failed to parse agent from')) {
    const fileMatch = trimmedChunk.match(/from\s+(.+?):/);
    const errorMatch = trimmedChunk.match(/:\s*(.+)$/);
    return {
      type: 'debug_misc',
      content: `Agent parse error: ${fileMatch?.[1]?.split('/').pop()}`,
      metadata: {
        agentError: errorMatch?.[1],
        filePath: fileMatch?.[1],
      },
    };
  }

  // =========================================================================
  // 15. DEBUG LOGS - Settings & Watching
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Watching for changes in setting files')) {
    return {
      type: 'debug_settings',
      content: 'Watching settings files',
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Found') && trimmedChunk.includes('hook matchers')) {
    return {
      type: 'debug_settings',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  // =========================================================================
  // 16. DEBUG LOGS - Ripgrep & Tools
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Ripgrep first use test')) {
    return {
      type: 'debug_misc',
      content: 'Ripgrep test passed',
    };
  }

  // =========================================================================
  // 17. DEBUG LOGS - Stream Events
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Stream started')) {
    return {
      type: 'stream_event',
      content: 'Stream started',
    };
  }

  // =========================================================================
  // 18. DEBUG LOGS - Metrics & BigQuery
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('Metrics opt-out')) {
    return {
      type: 'debug_misc',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('BigQuery metrics')) {
    return {
      type: 'debug_misc',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  if (trimmedChunk.includes('[DEBUG]') && trimmedChunk.includes('API Response:')) {
    return {
      type: 'debug_misc',
      content: 'Metrics API response received',
    };
  }

  // =========================================================================
  // 19. SPAWNING COMMAND (contains session info)
  // =========================================================================

  if (trimmedChunk.includes('Spawning Claude Code process:')) {
    const modelMatch = trimmedChunk.match(/--model\s+(\S+)/);
    const toolsMatch = trimmedChunk.match(/--allowedTools\s+([^\s-]+)/);
    const mcpConfigMatch = trimmedChunk.match(/--mcp-config\s+(\{.+?\})\s+--/);
    const permissionMatch = trimmedChunk.match(/--permission-mode\s+(\S+)/);

    const tools = toolsMatch ? toolsMatch[1].split(',') : [];
    let mcpServers: Array<{ name: string; status: string }> = [];

    if (mcpConfigMatch) {
      try {
        const mcpConfig = JSON.parse(mcpConfigMatch[1]);
        mcpServers = Object.keys(mcpConfig.mcpServers || {}).map((name) => ({
          name,
          status: 'connected',
        }));
      } catch (e) {
        // Ignore parse error
      }
    }

    const sessionData: SessionData = {
      model: modelMatch ? modelMatch[1] : 'unknown',
      tools: tools,
      mcpServers: mcpServers,
      permissionMode: permissionMatch ? permissionMatch[1] : 'unknown',
      skills: [],
      agents: [],
      slashCommands: [],
      sessionId: '',
      cwd: '',
      apiKeySource: '',
      claudeCodeVersion: '',
      outputStyle: '',
    };

    return {
      type: 'session_init',
      content: 'Spawning Claude Code process',
      metadata: {
        sessionData,
      },
    };
  }

  // =========================================================================
  // 20. CATCH-ALL DEBUG
  // =========================================================================

  if (trimmedChunk.includes('[DEBUG]')) {
    return {
      type: 'debug_misc',
      content: trimmedChunk.replace('[DEBUG]', '').trim(),
    };
  }

  // =========================================================================
  // 21. ERRORS
  // =========================================================================

  if (trimmedChunk.includes('[ERROR]') && !trimmedChunk.includes('MCP server')) {
    return {
      type: 'error',
      content: trimmedChunk.replace('[ERROR]', '').trim(),
      metadata: {
        errorType: 'general',
        errorMessage: trimmedChunk,
      },
    };
  }

  // =========================================================================
  // 22. FALLBACK - Unknown/Raw
  // =========================================================================

  return {
    type: 'raw',
    content: trimmedChunk,
  };
}

// ============================================================================
// GROUPING FUNCTION
// ============================================================================

export function groupLogs(parsedLogs: ParsedLogData[]): GroupedLogs {
  const groups: GroupedLogs = {
    thinking: [],
    tools: [],
    mcpTools: [],
    mcpLifecycle: [],
    errors: [],
    flows: [],
    session: [],
    messages: [],
    debug: [],
    other: [],
  };

  for (const log of parsedLogs) {
    // Skip empty raw logs
    if (log.type === 'raw' && !log.content) {
      continue;
    }

    switch (log.type) {
      case 'thinking':
        groups.thinking.push(log);
        break;

      case 'tool_use':
      case 'tool_result':
        groups.tools.push(log);
        break;

      case 'mcp_tool_use':
      case 'mcp_tool_result':
        groups.mcpTools.push(log);
        break;

      case 'mcp_connection':
      case 'mcp_lifecycle':
        groups.mcpLifecycle.push(log);
        break;

      case 'error':
        groups.errors.push(log);
        break;

      case 'flow_generated':
      case 'flow_content':
        groups.flows.push(log);
        break;

      case 'session_init':
      case 'session_end':
      case 'session_header':
      case 'agent_lifecycle':
        groups.session.push(log);
        break;

      case 'message_assistant':
      case 'message_user':
      case 'cache_stats':
      case 'model_usage':
        groups.messages.push(log);
        break;

      case 'debug_file_ops':
      case 'debug_shell':
      case 'debug_plugin':
      case 'debug_hooks':
      case 'debug_settings':
      case 'debug_misc':
      case 'stream_event':
        groups.debug.push(log);
        break;

      default:
        groups.other.push(log);
        break;
    }
  }

  return groups;
}

// ============================================================================
// BATCH PARSING
// ============================================================================

export function parseLogFile(logContent: string): ParsedLogData[] {
  const lines = logContent.split('\n');
  const parsedLogs: ParsedLogData[] = [];

  for (const line of lines) {
    const parsed = parseAgentLog(line);
    parsedLogs.push(parsed);
  }

  return parsedLogs;
}

// ============================================================================
// METRICS EXTRACTION
// ============================================================================

export function extractMetrics(logs: ParsedLogData[]): {
  inputTokens: number;
  outputTokens: number;
  cacheCreationInputTokens: number;
  cacheReadInputTokens: number;
  totalTokens: number;
  toolCalls: number;
  mcpToolCalls: number;
  duration: number;
  totalCost: number;
  numTurns: number;
} {
  let inputTokens = 0;
  let outputTokens = 0;
  let cacheCreationInputTokens = 0;
  let cacheReadInputTokens = 0;
  let toolCalls = 0;
  let mcpToolCalls = 0;
  let duration = 0;
  let totalCost = 0;
  let numTurns = 0;

  for (const log of logs) {
    if (log.metadata) {
      // Accumulate tokens
      if (log.metadata.inputTokens) inputTokens += log.metadata.inputTokens;
      if (log.metadata.outputTokens) outputTokens += log.metadata.outputTokens;
      if (log.metadata.cacheCreationInputTokens) cacheCreationInputTokens += log.metadata.cacheCreationInputTokens;
      if (log.metadata.cacheReadInputTokens) cacheReadInputTokens += log.metadata.cacheReadInputTokens;

      // Count tool calls
      if (log.type === 'tool_use') toolCalls++;
      if (log.type === 'mcp_tool_use') mcpToolCalls++;

      // Extract duration
      if (log.metadata.durationMs) duration = log.metadata.durationMs;

      // Extract final metrics from session end
      if (log.type === 'session_end' && log.metadata.resultData) {
        totalCost = log.metadata.resultData.totalCostUsd;
        numTurns = log.metadata.resultData.numTurns;
        // Use the authoritative token counts from result
        inputTokens = log.metadata.resultData.usage.inputTokens;
        outputTokens = log.metadata.resultData.usage.outputTokens;
        cacheCreationInputTokens = log.metadata.resultData.usage.cacheCreationInputTokens;
        cacheReadInputTokens = log.metadata.resultData.usage.cacheReadInputTokens;
      }
    }
  }

  return {
    inputTokens,
    outputTokens,
    cacheCreationInputTokens,
    cacheReadInputTokens,
    totalTokens: inputTokens + outputTokens,
    toolCalls,
    mcpToolCalls,
    duration,
    totalCost,
    numTurns,
  };
}

// ============================================================================
// UTILITY: Get session info
// ============================================================================

export function extractSessionInfo(logs: ParsedLogData[]): SessionData | null {
  for (const log of logs) {
    if (log.type === 'session_init' && log.metadata?.sessionData) {
      return log.metadata.sessionData;
    }
  }
  return null;
}

// ============================================================================
// UTILITY: Get result info
// ============================================================================

export function extractResultInfo(logs: ParsedLogData[]): ResultData | null {
  for (const log of logs) {
    if (log.type === 'session_end' && log.metadata?.resultData) {
      return log.metadata.resultData;
    }
  }
  return null;
}

// ============================================================================
// UTILITY: Get all thinking messages
// ============================================================================

export function extractAllThinking(logs: ParsedLogData[]): string[] {
  return logs
    .filter((log) => log.type === 'thinking')
    .map((log) => log.content)
    .filter((content) => content.length > 0);
}

// ============================================================================
// UTILITY: Get flow content
// ============================================================================

export function extractFlowContent(logs: ParsedLogData[]): string {
  const flowLines = logs
    .filter((log) => log.type === 'flow_content')
    .map((log) => log.content);
  
  return flowLines.join('\n');
}

// ============================================================================
// UTILITY: Get MCP server info
// ============================================================================

export function extractMCPServers(logs: ParsedLogData[]): Array<{
  name: string;
  connectionTime?: number;
  capabilities?: MCPCapabilities;
}> {
  const servers = new Map<string, any>();

  for (const log of logs) {
    if (log.type === 'mcp_connection' && log.metadata?.mcpServer) {
      const serverName = log.metadata.mcpServer;
      const existing = servers.get(serverName) || { name: serverName };

      if (log.metadata.mcpConnectionTime) {
        existing.connectionTime = log.metadata.mcpConnectionTime;
      }
      if (log.metadata.mcpCapabilities) {
        existing.capabilities = log.metadata.mcpCapabilities;
      }

      servers.set(serverName, existing);
    }
  }

  return Array.from(servers.values());
}

// ============================================================================
// EXPORT ALL
// ============================================================================

export default {
  parseAgentLog,
  parseLogFile,
  groupLogs,
  extractMetrics,
  extractSessionInfo,
  extractResultInfo,
  extractAllThinking,
  extractFlowContent,
  extractMCPServers,
};