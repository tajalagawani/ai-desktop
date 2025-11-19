// Chat Types for the ACT Agent UI

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';
export type MessageType = 'text' | 'tool_use' | 'tool_result' | 'stream_start' | 'stream_end' | 'error' | 'status' | 'completion' | 'flow' | 'thinking' | 'todo' | 'mcp_call';
export type ToolStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  type: MessageType;
  streaming?: boolean;
  createdAt: Date;
  toolUses?: ToolUse[];
  error?: string;
  metadata?: {
    // Special metadata for UI rendering
    _meta?: {
      type?: string;
      awaiting_response?: boolean;
      node_type?: string;
      node_name?: string;
      reason?: string;
      required_fields?: string[];
    };

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
    mcpCapabilities?: any;
    mcpServerInfo?: any;

    // Tool history arrays
    mcpToolHistory?: Array<{ server: string; tool: string; toolId?: string; input?: any; output?: any; status?: ToolStatus; duration?: number }>;
    toolHistory?: Array<{ tool: string; toolId?: string; input?: any; output?: any; status?: ToolStatus; duration?: number }>;

    // Todo list
    todos?: Array<{ content: string; status: 'pending' | 'in_progress' | 'completed'; activeForm: string }>;

    // Flow/Workflow
    flowName?: string;
    flowPath?: string;
    flowContent?: string;

    // Tokens and cost
    tokens?: {
      input?: number;
      output?: number;
      total?: number;
      cacheRead?: number;
      cacheCreation?: number;
    };
    cacheStats?: {
      cacheCreation?: number;
      cacheRead?: number;
      ephemeral5m?: number;
      ephemeral1h?: number;
    };
    inputTokens?: number;
    outputTokens?: number;
    cacheCreationInputTokens?: number;
    cacheReadInputTokens?: number;
    ephemeral5mTokens?: number;
    ephemeral1hTokens?: number;
    cost?: number;

    // Session data
    sessionData?: any;
    resultData?: {
      durationMs: number;
      durationApiMs?: number;
      numTurns: number;
      totalCostUsd: number;
      usage: {
        inputTokens: number;
        outputTokens: number;
        cacheReadInputTokens: number;
        cacheCreationInputTokens: number;
        webSearchRequests?: number;
      };
      modelUsage?: Record<string, any>;
    };

    // Message metadata
    messageId?: string;
    messageRole?: string;
    messageModel?: string;
    parentToolUseId?: string;
    sessionId?: string;
    uuid?: string;
    stopReason?: string;
    serviceTier?: string;

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

    // Debug info
    filePath?: string;
    fileSize?: number;
    shellType?: string;
    shellConfig?: string;
    pluginCount?: number;
    hookType?: string;
    hookQuery?: string;
  };
}

export interface ToolUse {
  id: string;
  toolName: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: ToolStatus;
  duration?: number;
  error?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  lastActivityAt: Date;
  messageCount: number;
}

export interface Metrics {
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens: number;
  cacheCreationTokens: number;
  totalCost: number;
  duration: number;
  turnCount: number;
  toolCallCount: number;
}
