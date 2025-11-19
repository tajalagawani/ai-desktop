'use client';

import { useState } from 'react';
import type { Message, ToolStatus } from '@/lib/flow-builder/types/chat';
import { formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useSessionStore } from '@/lib/stores/session-store';
import { TodoList } from './TodoList';
import { NodeApprovalPrompt } from './NodeApprovalPrompt';

interface ChatMessageProps {
  message: Message;
}

interface ToolItem {
  server?: string;
  tool: string;
  toolId?: string;
  input?: any;
  output?: any;
  status?: ToolStatus;
  duration?: number;
}

interface ExpandableToolItemProps {
  item: ToolItem;
  idx: number;
}

// Expandable Tool Item Component
function ExpandableToolItem({ item, idx }: ExpandableToolItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Status indicator
  const getStatusIndicator = (status?: ToolStatus) => {
    switch (status) {
      case 'completed':
        return <span className="text-green-600 dark:text-green-400">✓</span>;
      case 'failed':
        return <span className="text-red-600 dark:text-red-400">✗</span>;
      case 'running':
        return <span className="text-yellow-600 dark:text-yellow-400">⚠</span>;
      default:
        return <span className="text-zinc-400">○</span>;
    }
  };

  // Duration formatting
  const formatDuration = (duration?: number) => {
    if (!duration) return null;
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(1)}s`;
  };

  return (
    <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors w-full text-left"
      >
        <span className="text-zinc-400">{isExpanded ? '▼' : '▶'}</span>
        {item.server && <Badge variant="mcp">{item.server}</Badge>}
        <span className="font-medium">{item.tool}</span>
        {getStatusIndicator(item.status)}
        {item.duration && !isExpanded && (
          <span className="text-zinc-500 text-[10px]">
            {formatDuration(item.duration)}
          </span>
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 ml-4 space-y-1 text-xs text-zinc-600 dark:text-zinc-400">
          {/* Status */}
          <div className="flex items-center gap-2">
            <span className="font-medium">Status:</span>
            <span className="flex items-center gap-1">
              {getStatusIndicator(item.status)}
              <span className="capitalize">{item.status || 'pending'}</span>
              {item.duration && (
                <span className="text-zinc-500">({formatDuration(item.duration)})</span>
              )}
            </span>
          </div>

          {/* Tool ID */}
          {item.toolId && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Tool ID:</span>
              <span className="font-mono text-[10px] text-zinc-500">
                {item.toolId.substring(0, 16)}
              </span>
            </div>
          )}

          {/* Input */}
          {item.input && (
            <div className="space-y-1">
              <span className="font-medium">Input:</span>
              <pre className="text-[10px] bg-zinc-100 dark:bg-zinc-900 p-2 rounded overflow-x-auto max-h-32">
                {JSON.stringify(item.input, null, 2)}
              </pre>
            </div>
          )}

          {/* Output / Result */}
          {item.output && (
            <div className="space-y-1">
              <span className="font-medium">Result:</span>
              <pre className="text-[10px] bg-green-50 dark:bg-green-950 text-green-900 dark:text-green-100 p-2 rounded overflow-auto max-h-64 border border-green-200 dark:border-green-800">
                {(() => {
                  const outputStr = typeof item.output === 'string'
                    ? item.output
                    : JSON.stringify(item.output, null, 2);

                  // Truncate very long outputs
                  if (outputStr.length > 5000) {
                    return outputStr.substring(0, 5000) + '\n\n... (truncated, ' + outputStr.length + ' chars total)';
                  }
                  return outputStr;
                })()}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Helper to parse and render message content with badges
function renderMessageContent(
  content: string,
  message: Message,
  isExpanded: boolean,
  onToggleExpand: () => void,
  sessionData: any,
  resultData: any
) {
  const metadata = message.metadata;
  const toolHistory = metadata?.toolHistory || [];
  const mcpToolHistory = metadata?.mcpToolHistory || [];
  const globalSessionData = sessionData;
  const globalResultData = resultData;

  // Determine if we should show expandable section
  const hasExpandableContent =
    toolHistory.length > 0 ||
    mcpToolHistory.length > 0 ||
    (metadata?.tokens?.total && metadata.tokens.total > 0) ||
    metadata?.cacheStats ||
    (metadata?.cost && metadata.cost > 0) ||
    (globalSessionData?.skills && globalSessionData.skills.length > 0) ||
    (globalSessionData?.tools && globalSessionData.tools.length > 0) ||
    (globalSessionData?.mcpServers && globalSessionData.mcpServers.length > 0) ||
    (globalSessionData?.agents && globalSessionData.agents.length > 0) ||
    (globalSessionData?.slashCommands && globalSessionData.slashCommands.length > 0) ||
    globalSessionData?.model ||
    metadata?.messageId ||
    metadata?.messageModel ||
    (metadata?.resultData || globalResultData);

  // ============================================================================
  // TODO LIST - Inline todo progress display
  // ============================================================================
  if (message.type === 'todo') {
    // TodoList component will read the todos from message metadata
    return (
      <div className="flex flex-col gap-2">
        <TodoList message={message} />
      </div>
    );
  }

  // ============================================================================
  // NODE APPROVAL - User permission for unauthenticated nodes
  // ============================================================================
  if (metadata?._meta?.type === 'node_approval_request' && metadata._meta.awaiting_response) {
    const metaData = metadata._meta;
    const nodeType = metaData.node_type || '';
    const nodeName = metaData.node_name || '';
    const reason = metaData.reason || '';
    const requiredFields = metaData.required_fields || [];

    const handleApprove = async () => {
      console.log('[ChatMessage] User approved node:', nodeType);
      // Call MCP tool to add unauthenticated node
      try {
        const response = await fetch('/api/mcp/add-unauthenticated-node', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            node_type: nodeType,
          }),
        });
        const result = await response.json();
        console.log('[ChatMessage] Node added:', result);
      } catch (error) {
        console.error('[ChatMessage] Failed to add node:', error);
      }
    };

    const handleReject = () => {
      console.log('[ChatMessage] User rejected node:', nodeType);
      // User declined - agent should handle this
    };

    return (
      <div className="flex flex-col gap-2">
        <NodeApprovalPrompt
          nodeType={nodeType}
          nodeName={nodeName}
          reason={reason}
          requiredFields={requiredFields}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      </div>
    );
  }

  // ============================================================================
  // THINKING MESSAGES - Badge style with expand
  // ============================================================================
  if (message.type === 'thinking' || (message.role === 'assistant' && !metadata?.mcpServer && !metadata?.toolName)) {
    const tokens = metadata?.tokens;
    const cacheStats = metadata?.cacheStats;
    const model = metadata?.messageModel || globalSessionData?.model;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onToggleExpand}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Badge variant="tool">💭 Thinking</Badge>
          </button>

          {model && (
            <>
              <span className="text-zinc-400">|</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">{model}</span>
            </>
          )}

          {/* Token info inline */}
          {tokens?.total && tokens.total > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {tokens.total.toLocaleString()} tokens
              </span>
            </>
          )}

          {/* Cache indicator */}
          {cacheStats?.cacheRead && cacheStats.cacheRead > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <Badge variant="success">
                ⚡ {(cacheStats.cacheRead / 1000).toFixed(0)}K cached
              </Badge>
            </>
          )}
        </div>

        {/* Thinking content */}
        <div className="whitespace-pre-wrap break-words text-zinc-700 dark:text-zinc-300">
          {content}
        </div>

        {/* Expanded details */}
        {isExpanded && hasExpandableContent && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          tokens,
          cacheStats,
          metadata?.cost,
          metadata?.resultData || globalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  // ============================================================================
  // MCP TOOL MESSAGES - Badge style with expand
  // ============================================================================
  if (metadata?.mcpServer && metadata?.mcpToolName) {
    const tokens = metadata.tokens;
    const cacheStats = metadata.cacheStats;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onToggleExpand}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Badge variant="mcp">
              {metadata.mcpServer} {mcpToolHistory.length > 1 && `(${mcpToolHistory.length})`}
            </Badge>
          </button>
          <span className="text-zinc-400">|</span>
          <span className="font-medium">{metadata.mcpToolName}</span>

          {/* Token info inline */}
          {tokens?.total && tokens.total > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {tokens.total.toLocaleString()} tokens
              </span>
            </>
          )}

          {/* Cache indicator */}
          {cacheStats?.cacheRead && cacheStats.cacheRead > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <Badge variant="success">
                ⚡ {(cacheStats.cacheRead / 1000).toFixed(0)}K cached
              </Badge>
            </>
          )}
        </div>

        {/* Expanded details */}
        {isExpanded && hasExpandableContent && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          tokens,
          cacheStats,
          metadata?.cost,
          metadata?.resultData || globalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  // ============================================================================
  // STANDARD TOOL MESSAGES - Badge style with expand
  // ============================================================================
  if (metadata?.toolName && !metadata?.mcpServer) {
    const tokens = metadata.tokens;
    const cacheStats = metadata.cacheStats;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onToggleExpand}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Badge variant="tool">
              🔧 Tool {toolHistory.length > 1 && `(${toolHistory.length})`}
            </Badge>
          </button>
          <span className="text-zinc-400">|</span>
          <span className="font-medium">{metadata.toolName}</span>

          {/* Token info inline */}
          {tokens?.total && tokens.total > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {tokens.total.toLocaleString()} tokens
              </span>
            </>
          )}

          {/* Cache indicator */}
          {cacheStats?.cacheRead && cacheStats.cacheRead > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <Badge variant="success">
                ⚡ {(cacheStats.cacheRead / 1000).toFixed(0)}K cached
              </Badge>
            </>
          )}
        </div>

        {/* Expanded details */}
        {isExpanded && hasExpandableContent && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          tokens,
          cacheStats,
          metadata?.cost,
          metadata?.resultData || globalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  // ============================================================================
  // FLOW MESSAGES - Badge style with expand
  // ============================================================================
  if (message.type === 'flow' || metadata?.flowName) {
    const tokens = metadata?.tokens;
    const cacheStats = metadata?.cacheStats;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onToggleExpand}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Badge variant="success">💾 Flow Generated</Badge>
          </button>
          <span className="text-zinc-400">|</span>
          <span className="font-medium">{metadata.flowName || 'Workflow'}</span>

          {/* Token info inline */}
          {tokens?.total && tokens.total > 0 && (
            <>
              <span className="text-zinc-400">•</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {tokens.total.toLocaleString()} tokens
              </span>
            </>
          )}
        </div>

        {/* Flow content preview */}
        {metadata?.flowContent && (
          <pre className="text-xs bg-zinc-900 dark:bg-zinc-950 text-zinc-100 p-3 rounded overflow-x-auto max-h-60">
            {metadata.flowContent}
          </pre>
        )}

        {/* Flow path */}
        {metadata?.flowPath && (
          <div className="text-xs text-zinc-500 dark:text-zinc-400">
            📁 {metadata.flowPath}
          </div>
        )}

        {/* Expanded details */}
        {isExpanded && hasExpandableContent && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          tokens,
          cacheStats,
          metadata?.cost,
          metadata?.resultData || globalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  // ============================================================================
  // STATUS MESSAGES - Badge style with expand
  // ============================================================================
  if (message.type === 'status') {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="tool">📊 Status</Badge>
          <span className="text-zinc-400">|</span>
          <span className="text-zinc-700 dark:text-zinc-300">{content}</span>
        </div>
      </div>
    );
  }

  // ============================================================================
  // COMPLETION MESSAGES - Badge style with expand
  // ============================================================================
  if (message.type === 'completion') {
    const finalResultData = metadata?.resultData || globalResultData;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onToggleExpand}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Badge variant="success">✅ Completed</Badge>
          </button>

          {finalResultData && (
            <>
              <span className="text-zinc-400">|</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {finalResultData.numTurns} turns
              </span>
              <span className="text-zinc-400">•</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {(finalResultData.durationMs / 1000).toFixed(1)}s
              </span>
              <span className="text-zinc-400">•</span>
              <span className="text-xs font-medium text-green-600 dark:text-green-400">
                ${finalResultData.totalCostUsd.toFixed(4)}
              </span>
            </>
          )}
        </div>

        {/* Expanded details */}
        {isExpanded && finalResultData && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          null,
          null,
          finalResultData.totalCostUsd,
          finalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  // ============================================================================
  // ERROR MESSAGES - Badge style
  // ============================================================================
  if (message.type === 'error' || message.error) {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="error">❌ Error</Badge>
          <span className="text-zinc-400">|</span>
          <span className="text-red-600 dark:text-red-400">{content || message.error}</span>
        </div>
      </div>
    );
  }

  // ============================================================================
  // DEFAULT - Plain text with optional expand
  // ============================================================================
  if (hasExpandableContent) {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-start gap-2">
          <div className="flex-1 whitespace-pre-wrap break-words">{content}</div>
          <button
            onClick={onToggleExpand}
            className="flex-shrink-0 text-xs text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 transition-colors"
            title="Show details"
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>

        {isExpanded && renderExpandedDetails(
          toolHistory,
          mcpToolHistory,
          metadata?.tokens,
          metadata?.cacheStats,
          metadata?.cost,
          metadata?.resultData || globalResultData,
          globalSessionData,
          metadata
        )}
      </div>
    );
  }

  return content;
}

// Helper function to render expanded details section
function renderExpandedDetails(
  toolHistory: any[],
  mcpToolHistory: any[],
  tokens: any,
  cacheStats: any,
  cost: any,
  finalResultData: any,
  globalSessionData: any,
  metadata: any
) {
  return (
    <div className="mt-2 pl-4 border-l-2 border-zinc-300 dark:border-zinc-700 space-y-3">
      {/* 1. Standard Tool History */}
      {toolHistory.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Tool History ({toolHistory.length})
          </div>
          {toolHistory.map((item: any, idx: number) => (
            <ExpandableToolItem key={idx} item={item} idx={idx} />
          ))}
        </div>
      )}

      {/* 2. MCP Tool History */}
      {mcpToolHistory.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            MCP Tool History ({mcpToolHistory.length})
          </div>
          {mcpToolHistory.map((item: any, idx: number) => (
            <ExpandableToolItem key={idx} item={item} idx={idx} />
          ))}
        </div>
      )}

      {/* 3. Token Breakdown */}
      {tokens && tokens.total > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Tokens</div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
            <div className="flex justify-between">
              <span>Input:</span>
              <span className="font-medium">{tokens.input?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Output:</span>
              <span className="font-medium">{tokens.output?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Total:</span>
              <span className="font-medium">{tokens.total?.toLocaleString() || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* 4. Cache Statistics */}
      {cacheStats && (cacheStats.cacheRead > 0 || cacheStats.cacheCreation > 0) && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Cache Statistics</div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
            {cacheStats.cacheRead > 0 && (
              <div className="flex justify-between">
                <span>Cache Read:</span>
                <span className="font-medium text-green-600 dark:text-green-400">
                  ⚡ {cacheStats.cacheRead.toLocaleString()}
                </span>
              </div>
            )}
            {cacheStats.cacheCreation > 0 && (
              <div className="flex justify-between">
                <span>Cache Created:</span>
                <span className="font-medium">{cacheStats.cacheCreation.toLocaleString()}</span>
              </div>
            )}
            {cacheStats.ephemeral5m > 0 && (
              <div className="flex justify-between">
                <span>Ephemeral 5m:</span>
                <span className="font-medium">{cacheStats.ephemeral5m.toLocaleString()}</span>
              </div>
            )}
            {cacheStats.ephemeral1h > 0 && (
              <div className="flex justify-between">
                <span>Ephemeral 1h:</span>
                <span className="font-medium">{cacheStats.ephemeral1h.toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 5. Cost Information */}
      {cost && cost > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Cost</div>
          <div className="text-sm font-medium text-green-600 dark:text-green-400">
            ${cost.toFixed(4)}
          </div>
        </div>
      )}

      {/* 6. Message Metadata */}
      {(metadata?.messageId || metadata?.messageModel || metadata?.sessionId) && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Message Info</div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
            {metadata.messageModel && (
              <div className="flex justify-between">
                <span>Model:</span>
                <span className="font-medium">{metadata.messageModel}</span>
              </div>
            )}
            {metadata.messageId && (
              <div className="flex justify-between">
                <span>ID:</span>
                <span className="font-mono text-[10px]">{metadata.messageId.substring(0, 12)}...</span>
              </div>
            )}
            {metadata.sessionId && (
              <div className="flex justify-between">
                <span>Session:</span>
                <span className="font-mono text-[10px]">{metadata.sessionId.substring(0, 12)}...</span>
              </div>
            )}
            {metadata.uuid && (
              <div className="flex justify-between">
                <span>UUID:</span>
                <span className="font-mono text-[10px]">{metadata.uuid.substring(0, 12)}...</span>
              </div>
            )}
            {metadata.serviceTier && (
              <div className="flex justify-between">
                <span>Tier:</span>
                <span className="font-medium">{metadata.serviceTier}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. Skills */}
      {globalSessionData?.skills && globalSessionData.skills.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Skills ({globalSessionData.skills.length})
          </div>
          <div className="flex flex-wrap gap-1">
            {globalSessionData.skills.map((skill: string, idx: number) => (
              <Badge key={idx} variant="tool">
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* 8. Available Tools */}
      {globalSessionData?.tools && globalSessionData.tools.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Available Tools ({globalSessionData.tools.length})
          </div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 flex flex-wrap gap-1">
            {globalSessionData.tools.slice(0, 15).map((tool: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 bg-zinc-100 dark:bg-zinc-800 rounded">
                {tool}
              </span>
            ))}
            {globalSessionData.tools.length > 15 && (
              <span className="px-2 py-0.5">+{globalSessionData.tools.length - 15} more</span>
            )}
          </div>
        </div>
      )}

      {/* 9. MCP Servers */}
      {globalSessionData?.mcpServers && globalSessionData.mcpServers.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            MCP Servers ({globalSessionData.mcpServers.length})
          </div>
          <div className="flex flex-wrap gap-1">
            {globalSessionData.mcpServers.map((server: any, idx: number) => (
              <Badge key={idx} variant="mcp">
                {server.name}{' '}
                {server.status === 'connected' && '✓'}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* 10. Agents */}
      {globalSessionData?.agents && globalSessionData.agents.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Agents ({globalSessionData.agents.length})
          </div>
          <div className="flex flex-wrap gap-1">
            {globalSessionData.agents.map((agent: string, idx: number) => (
              <Badge key={idx} variant="tool">
                {agent}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* 11. Slash Commands */}
      {globalSessionData?.slashCommands && globalSessionData.slashCommands.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Slash Commands ({globalSessionData.slashCommands.length})
          </div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 flex flex-wrap gap-1">
            {globalSessionData.slashCommands.slice(0, 10).map((cmd: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 bg-zinc-100 dark:bg-zinc-800 rounded">
                /{cmd}
              </span>
            ))}
            {globalSessionData.slashCommands.length > 10 && (
              <span>+{globalSessionData.slashCommands.length - 10} more</span>
            )}
          </div>
        </div>
      )}

      {/* 12. Session Details */}
      {globalSessionData && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Session</div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
            {globalSessionData.model && (
              <div className="flex justify-between">
                <span>Model:</span>
                <span className="font-medium">{globalSessionData.model}</span>
              </div>
            )}
            {globalSessionData.permissionMode && (
              <div className="flex justify-between">
                <span>Permission:</span>
                <span className="font-medium">{globalSessionData.permissionMode}</span>
              </div>
            )}
            {globalSessionData.claudeCodeVersion && (
              <div className="flex justify-between">
                <span>Version:</span>
                <span className="font-medium">{globalSessionData.claudeCodeVersion}</span>
              </div>
            )}
            {globalSessionData.apiKeySource && (
              <div className="flex justify-between">
                <span>API Key:</span>
                <span className="font-medium">{globalSessionData.apiKeySource}</span>
              </div>
            )}
            {globalSessionData.outputStyle && (
              <div className="flex justify-between">
                <span>Output Style:</span>
                <span className="font-medium">{globalSessionData.outputStyle}</span>
              </div>
            )}
            {globalSessionData.cwd && (
              <div className="flex flex-col gap-0.5">
                <span>Working Dir:</span>
                <span className="font-mono text-[10px] text-zinc-500 dark:text-zinc-500 break-all">
                  {globalSessionData.cwd}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 13. Result Data (Session Complete) */}
      {finalResultData && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Session Results</div>
          <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
            <div className="flex justify-between">
              <span>Duration:</span>
              <span className="font-medium">{(finalResultData.durationMs / 1000).toFixed(1)}s</span>
            </div>
            <div className="flex justify-between">
              <span>API Time:</span>
              <span className="font-medium">{(finalResultData.durationApiMs / 1000).toFixed(1)}s</span>
            </div>
            <div className="flex justify-between">
              <span>Turns:</span>
              <span className="font-medium">{finalResultData.numTurns}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Cost:</span>
              <span className="font-medium text-green-600 dark:text-green-400">
                ${finalResultData.totalCostUsd.toFixed(4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Input Tokens:</span>
              <span className="font-medium">{finalResultData.usage.inputTokens.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Output Tokens:</span>
              <span className="font-medium">{finalResultData.usage.outputTokens.toLocaleString()}</span>
            </div>
            {finalResultData.usage.cacheReadInputTokens > 0 && (
              <div className="flex justify-between">
                <span>Cache Read:</span>
                <span className="font-medium text-green-600 dark:text-green-400">
                  ⚡ {finalResultData.usage.cacheReadInputTokens.toLocaleString()}
                </span>
              </div>
            )}
            {finalResultData.usage.cacheCreationInputTokens > 0 && (
              <div className="flex justify-between">
                <span>Cache Created:</span>
                <span className="font-medium">{finalResultData.usage.cacheCreationInputTokens.toLocaleString()}</span>
              </div>
            )}
            {finalResultData.usage.webSearchRequests > 0 && (
              <div className="flex justify-between">
                <span>Web Searches:</span>
                <span className="font-medium">{finalResultData.usage.webSearchRequests}</span>
              </div>
            )}
          </div>

          {/* Model Usage Breakdown */}
          {finalResultData.modelUsage && Object.keys(finalResultData.modelUsage).length > 0 && (
            <div className="mt-2 space-y-1">
              <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Model Usage</div>
              {Object.entries(finalResultData.modelUsage).map(([model, usage]: [string, any]) => (
                <div key={model} className="p-2 bg-zinc-50 dark:bg-zinc-900 rounded space-y-0.5">
                  <div className="font-medium text-zinc-700 dark:text-zinc-300">{model}</div>
                  <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-0.5">
                    <div className="flex justify-between">
                      <span>Tokens:</span>
                      <span>{(usage.inputTokens + usage.outputTokens).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Cost:</span>
                      <span className="text-green-600 dark:text-green-400">${usage.costUSD.toFixed(4)}</span>
                    </div>
                    {usage.cacheReadInputTokens > 0 && (
                      <div className="flex justify-between">
                        <span>Cache:</span>
                        <span className="text-green-600 dark:text-green-400">
                          ⚡ {usage.cacheReadInputTokens.toLocaleString()}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span>Context:</span>
                      <span>{(usage.contextWindow / 1000).toFixed(0)}K</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { sessionData, resultData } = useSessionStore();
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isSystem = message.role === 'system';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          isUser
            ? 'bg-zinc-200 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-400'
            : isAssistant
            ? 'bg-zinc-200 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-400'
            : 'bg-zinc-500 text-white'
        }`}
      >
        {isUser ? (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
          </svg>
        ) : isAssistant ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Message Header */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            {isUser ? 'You' : isAssistant ? 'Assistant' : 'System'}
          </span>
          <span className="text-[10px] text-zinc-400 dark:text-zinc-500">{formatDate(message.createdAt)}</span>
        </div>

        {/* Message Bubble */}
        <div
          className={`rounded-lg inline-block ${
            isUser
              ? 'px-4 py-2 text-sm bg-zinc-200 dark:bg-zinc-700'
              : isAssistant
              ? 'px-4 py-2 text-sm bg-zinc-100 dark:bg-zinc-800'
              : 'px-4 py-2 text-sm bg-zinc-100 dark:bg-zinc-800'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {renderMessageContent(
              message.content,
              message,
              isExpanded,
              () => setIsExpanded(!isExpanded),
              sessionData,
              resultData
            )}
          </div>

          {/* Streaming Indicator */}
          {message.streaming && (
            <div className="mt-2 flex items-center gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
              <span className="text-xs opacity-70">Streaming...</span>
            </div>
          )}

          {/* Tool Uses (Legacy support) */}
          {message.toolUses && message.toolUses.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.toolUses.map((toolUse) => (
                <div
                  key={toolUse.id}
                  className="text-xs p-2 rounded border border-zinc-300 dark:border-zinc-600 bg-zinc-50 dark:bg-zinc-900"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">Tool: {toolUse.toolName}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                        toolUse.status === 'completed'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : toolUse.status === 'running'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                          : toolUse.status === 'failed'
                          ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                          : 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300'
                      }`}
                    >
                      {toolUse.status}
                    </span>
                  </div>
                  {toolUse.duration && (
                    <div className="text-zinc-500 dark:text-zinc-400">Duration: {toolUse.duration}ms</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Error (Legacy support) */}
          {message.error && (
            <div className="mt-2 text-xs p-2 rounded bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800">
              Error: {message.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
