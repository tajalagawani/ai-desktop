'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useChatStore } from '@/lib/flow-builder/stores/chat-store';
import { useMetricsStore } from '@/lib/flow-builder/stores/metrics-store';
import { useSessionStore } from '@/lib/flow-builder/stores/session-store';
import { useFlowSettingsStore } from '@/lib/flow-builder/stores/settings-store';
import { parseAgentLog, groupLogs, type ParsedLogData } from '@/lib/flow-builder/utils/log-parser';
import { generateUUID } from '@/lib/utils';

// Helper to save message to database
async function saveMessageToDatabase(sessionId: string, message: any) {
  try {
    await fetch('/api/flow-builder/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: message.id, // CRITICAL: Include client-side UUID so server uses same ID
        sessionId,
        role: message.role.toUpperCase(),
        content: message.content,
        type: message.type?.toUpperCase() || 'TEXT',
        streaming: message.streaming,
        error: message.error,
        metadata: message.metadata, // Save full metadata including toolHistory, mcpToolHistory, etc.
        inputTokens: message.metadata?.tokens?.input,
        outputTokens: message.metadata?.tokens?.output,
      }),
    });
  } catch (error) {
    console.error('[useAgent] Error saving message to database:', error);
  }
}

// Helper to update existing message in database
async function updateMessageInDatabase(messageId: string, message: any) {
  try {
    await fetch(`/api/flow-builder/messages/${messageId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: message.content,
        type: message.type?.toUpperCase() || 'TEXT',
        streaming: message.streaming,
        error: message.error,
        metadata: message.metadata, // Update full metadata
        inputTokens: message.metadata?.tokens?.input,
        outputTokens: message.metadata?.tokens?.output,
      }),
    });
  } catch (error) {
    console.error('[useAgent] Error updating message in database:', error);
  }
}

/**
 * Enhanced useAgent Hook
 * 
 * Handles WebSocket communication with the agent server and processes all log types
 * using the comprehensive enhanced parser.
 * 
 * Server Emission Pattern:
 * ========================
 * The server emits logs line-by-line through the 'stream:chunk' event:
 * 
 * socket.emit('stream:chunk', { chunk: logLine });
 * 
 * Each chunk can be:
 * - Plain text status messages (🔍, ✅, 💾, etc.)
 * - JSON structured logs ([DEBUG] Message: {...})
 * - DEBUG logs ([DEBUG] MCP server..., [DEBUG] Tool..., etc.)
 * - Thinking messages (💭 ...)
 * - Flow content ([workflow], [node:...], etc.)
 * - Session boundaries (====...)
 * 
 * This hook parses each chunk, extracts structured data, and updates the appropriate stores.
 */

export function useAgent(sessionId: string) {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const currentMessageIdRef = useRef<string | null>(null);
  const flowContentBufferRef = useRef<string[]>([]);
  const thinkingBufferRef = useRef<string[]>([]);

  // JSON buffering for multiline JSON logs
  const jsonBufferRef = useRef<string[]>([]);
  const isBufferingJsonRef = useRef<boolean>(false);
  const jsonBraceCountRef = useRef<number>(0);

  // Chat store actions
  const addMessage = useChatStore((state) => state.addMessage);
  const messages = useChatStore((state) => state.messages);
  const updateMessage = useChatStore((state) => state.updateMessage);
  const removeMessage = useChatStore((state) => state.removeMessage);
  const appendToStreamingMessage = useChatStore((state) => state.appendToStreamingMessage);
  const completeStreamingMessage = useChatStore((state) => state.completeStreamingMessage);
  const addToolUse = useChatStore((state) => state.addToolUse);
  const updateToolUse = useChatStore((state) => state.updateToolUse);
  const setAgentRunning = useChatStore((state) => state.setAgentRunning);

  // Metrics store actions
  const updateMetrics = useMetricsStore((state) => state.updateMetrics);
  const incrementMetrics = useMetricsStore((state) => state.incrementMetrics);

  // Session store
  const { setSessionData, setResultData, sessionData } = useSessionStore();

  // Track which messages have been saved to avoid duplicates
  const savedMessageIds = useRef<Set<string>>(new Set());
  const savingMessageIds = useRef<Set<string>>(new Set());

  // Track messages loaded from DB to prevent re-saving them on first render
  const loadedFromDbIds = useRef<Set<string>>(new Set());

  // Debounce timer for todo updates
  const todoUpdateTimerRef = useRef<NodeJS.Timeout | null>(null);
  const pendingTodoUpdateRef = useRef<{ id: string; message: any } | null>(null);

  // Auto-save all new messages to database
  useEffect(() => {
    messages.forEach((message) => {
      // Skip messages loaded from database (first time only)
      if ((message as any)._loadedFromDb && !loadedFromDbIds.current.has(message.id)) {
        // This message was loaded from DB, mark as saved but don't re-save
        savedMessageIds.current.add(message.id);
        loadedFromDbIds.current.add(message.id);
        return;
      }

      // Skip if streaming
      if (message.streaming) {
        return;
      }

      // Skip if currently saving
      if (savingMessageIds.current.has(message.id)) {
        return;
      }

      // Check if already saved
      const alreadySaved = savedMessageIds.current.has(message.id);
      const currentlySaving = savingMessageIds.current.has(message.id);

      if (alreadySaved) {
        // For TODO messages, debounce updates to save the latest state
        if (message.type === 'todo') {
          // Clear existing timer
          if (todoUpdateTimerRef.current) {
            clearTimeout(todoUpdateTimerRef.current);
          }

          // Store the pending update
          pendingTodoUpdateRef.current = { id: message.id, message };

          // Set new timer to save after 100ms of no updates (reduced from 500ms)
          todoUpdateTimerRef.current = setTimeout(() => {
            const pending = pendingTodoUpdateRef.current;
            if (pending) {
              const todos = pending.message.metadata?.todos;
              const completedCount = todos?.filter((t: any) => t.status === 'completed').length || 0;
              console.log('[useAgent] 💾 Debounced save of todo message:', pending.id, `${completedCount}/${todos?.length || 0} completed`);
              console.log('[useAgent] Todo states:', todos?.map((t: any) => `${t.content.substring(0, 20)}... = ${t.status}`));
              updateMessageInDatabase(pending.id, pending.message)
                .then(() => {
                  console.log('[useAgent] ✅ Todo message saved successfully to DB');
                })
                .catch((error) => {
                  console.error('[useAgent] ❌ Failed to update todo message:', pending.id, error);
                });
              pendingTodoUpdateRef.current = null;
            }
          }, 100);
        }
        // Skip other already-saved messages
        return;
      }

      // Skip if currently being saved (prevent duplicate POSTs and premature PATCHes)
      if (currentlySaving) {
        console.log('[useAgent] Skipping save - message already being saved:', message.id);
        return;
      }

      // Mark as saving and save new message to database
      savingMessageIds.current.add(message.id);
      console.log('[useAgent] Auto-saving new message:', message.id, message.type);
      saveMessageToDatabase(sessionId, message)
        .then(() => {
          // Mark as saved and remove from saving set
          savedMessageIds.current.add(message.id);
          savingMessageIds.current.delete(message.id);
          console.log('[useAgent] ✅ Message saved to DB:', message.id);
        })
        .catch((error) => {
          console.error('[useAgent] Failed to save message:', message.id, error);
          // Remove from saving set so we can retry
          savingMessageIds.current.delete(message.id);
        });
    });

    // Cleanup: flush pending todo updates on unmount
    return () => {
      if (todoUpdateTimerRef.current) {
        clearTimeout(todoUpdateTimerRef.current);
        const pending = pendingTodoUpdateRef.current;
        if (pending) {
          console.log('[useAgent] Flushing pending todo on unmount');
          updateMessageInDatabase(pending.id, pending.message).catch(console.error);
        }
      }
    };
  }, [messages, sessionId]);

  // ============================================================================
  // HELPER: Merge session data from multiple sources
  // ============================================================================
  const mergeSessionData = useCallback((newData: any) => {
    const existingData = sessionData || ({} as any);

    const mergedData = {
      sessionId: newData.sessionId || existingData.sessionId || '',
      cwd: newData.cwd || existingData.cwd || '',
      model: newData.model || existingData.model || '',
      permissionMode: newData.permissionMode || existingData.permissionMode || '',
      apiKeySource: newData.apiKeySource || existingData.apiKeySource || '',
      claudeCodeVersion: newData.claudeCodeVersion || existingData.claudeCodeVersion || '',
      outputStyle: newData.outputStyle || existingData.outputStyle || '',
      uuid: newData.uuid || existingData.uuid || '',
      skills: [...new Set([...(existingData.skills || []), ...(newData.skills || [])])],
      tools: newData.tools && newData.tools.length > 0 ? newData.tools : existingData.tools || [],
      mcpServers:
        newData.mcpServers && newData.mcpServers.length > 0 ? newData.mcpServers : existingData.mcpServers || [],
      agents: [...new Set([...(existingData.agents || []), ...(newData.agents || [])])],
      slashCommands: [...new Set([...(existingData.slashCommands || []), ...(newData.slashCommands || [])])],
    };

    setSessionData(mergedData);
    return mergedData;
  }, [sessionData, setSessionData]);

  // ============================================================================
  // HELPER: Update current message with metadata
  // ============================================================================
  const updateCurrentMessage = useCallback((updates: any) => {
    if (!currentMessageIdRef.current) return;

    const messages = useChatStore.getState().messages;
    const existingMessage = messages.find((m) => m.id === currentMessageIdRef.current);
    if (!existingMessage) return;

    updateMessage(currentMessageIdRef.current, {
      ...updates,
      metadata: {
        ...existingMessage.metadata,
        ...updates.metadata,
      },
    } as any);
  }, [updateMessage]);

  // ============================================================================
  // HELPER: Create or update tool message
  // ============================================================================
  const handleToolMessage = useCallback((parsed: ParsedLogData) => {
    // ===== SPECIAL HANDLING FOR TodoWrite =====
    // TodoWrite updates the existing todo message (or creates if first time)
    if (parsed.metadata?.toolName === 'TodoWrite' && parsed.metadata?.toolInput?.todos) {
      const messages = useChatStore.getState().messages;

      // Find existing todo message
      const existingTodoMessage = messages.find(m => m.type === 'todo');

      if (existingTodoMessage) {
        // UPDATE existing todo message - MOVE IT TO BOTTOM by removing and re-adding
        console.log('[useAgent] Updating existing todo message:', existingTodoMessage.id, 'with todos:', parsed.metadata.toolInput.todos);

        // Remove old todo message
        removeMessage(existingTodoMessage.id);

        // Add updated todo as new message at bottom (keeps same ID for database consistency)
        addMessage({
          id: existingTodoMessage.id, // Keep same ID so database updates work
          role: 'system',
          content: 'Workflow Progress',
          type: 'todo',
          streaming: false,
          createdAt: new Date(), // New timestamp = moves to bottom
          metadata: {
            todos: parsed.metadata.toolInput.todos,
          },
        } as any);
      } else {
        // CREATE new todo message (first time)
        const todoMessageId = generateUUID();
        console.log('[useAgent] Creating new todo message:', todoMessageId, 'with todos:', parsed.metadata.toolInput.todos);

        addMessage({
          id: todoMessageId,
          role: 'system',
          content: 'Workflow Progress',
          type: 'todo',
          streaming: false,
          createdAt: new Date(),
          metadata: {
            todos: parsed.metadata.toolInput.todos,
          },
        } as any);
      }

      // Don't continue with regular tool handling
      return;
    }

    // ===== REGULAR TOOL HANDLING =====
    if (currentMessageIdRef.current) {
      // Get existing message to accumulate tool history
      const messages = useChatStore.getState().messages;
      const existingMessage = messages.find((m) => m.id === currentMessageIdRef.current);
      const existingHistory = existingMessage?.metadata?.toolHistory || [];
      const existingMcpHistory = existingMessage?.metadata?.mcpToolHistory || [];

      // Build new history entries
      let newToolHistory = existingHistory;
      let newMcpHistory = existingMcpHistory;

      if (parsed.type === 'mcp_tool_use' && parsed.metadata?.mcpServer) {
        // Check if this tool is already in history to prevent duplicates
        const toolId = parsed.metadata.toolId;
        const alreadyExists = existingMcpHistory.some((item) => item.toolId === toolId);

        if (!alreadyExists) {
          newMcpHistory = [
            ...existingMcpHistory,
            {
              server: parsed.metadata.mcpServer,
              tool: parsed.metadata.mcpToolName || '',
              toolId: parsed.metadata.toolId,
              input: parsed.metadata.toolInput,
              status: 'running' as const,
            },
          ];
          console.log('[useAgent] Adding MCP tool to history:', parsed.metadata.mcpToolName, toolId);
        } else {
          console.warn('[useAgent] Duplicate MCP tool_use event ignored:', parsed.metadata.mcpToolName, toolId);
        }
      } else if (parsed.type === 'tool_use') {
        // Check if this tool is already in history to prevent duplicates
        const toolId = parsed.metadata?.toolId;
        const alreadyExists = existingHistory.some((item) => item.toolId === toolId);

        if (!alreadyExists) {
          newToolHistory = [
            ...existingHistory,
            {
              tool: parsed.metadata?.toolName || '',
              toolId: parsed.metadata?.toolId,
              input: parsed.metadata?.toolInput,
              status: 'running' as const,
            },
          ];
          console.log('[useAgent] Adding tool to history:', parsed.metadata?.toolName, toolId);
        } else {
          console.warn('[useAgent] Duplicate tool_use event ignored:', parsed.metadata?.toolName, toolId);
        }
      }

      // REPLACE current message with latest operation, but keep all history
      updateMessage(currentMessageIdRef.current, {
        content: parsed.content,
        metadata: {
          ...existingMessage?.metadata,
          ...parsed.metadata,
          toolHistory: newToolHistory,
          mcpToolHistory: newMcpHistory,
        },
      } as any);
    } else {
      // Create first tool message
      const messageId = generateUUID();
      currentMessageIdRef.current = messageId;

      const initialToolHistory =
        parsed.type === 'tool_use'
          ? [
              {
                tool: parsed.metadata?.toolName || '',
                toolId: parsed.metadata?.toolId,
                input: parsed.metadata?.toolInput,
                status: 'running' as const,
              },
            ]
          : [];

      const initialMcpHistory =
        parsed.type === 'mcp_tool_use' && parsed.metadata?.mcpServer
          ? [
              {
                server: parsed.metadata.mcpServer,
                tool: parsed.metadata.mcpToolName || '',
                toolId: parsed.metadata.toolId,
                input: parsed.metadata.toolInput,
                status: 'running' as const,
              },
            ]
          : [];

      addMessage({
        id: messageId,
        role: 'assistant',
        content: parsed.content,
        type: 'text',
        streaming: true,
        createdAt: new Date(),
        metadata: {
          ...parsed.metadata,
          toolHistory: initialToolHistory,
          mcpToolHistory: initialMcpHistory,
        },
      } as any);
    }
  }, [addMessage, updateMessage, removeMessage]);

  // ============================================================================
  // HELPER: Handle thinking messages (accumulate and display)
  // ============================================================================
  const handleThinkingMessage = useCallback(async (parsed: ParsedLogData) => {
    // Add to thinking buffer
    thinkingBufferRef.current.push(parsed.content);

    // Complete current tool message if any
    if (currentMessageIdRef.current) {
      completeStreamingMessage(currentMessageIdRef.current);
      currentMessageIdRef.current = null;
    }

    // Create or update thinking message
    const messageId = generateUUID();
    const message = {
      id: messageId,
      role: 'assistant',
      content: parsed.content,
      type: 'thinking',
      streaming: false,
      createdAt: new Date(),
      metadata: parsed.metadata,
    };

    addMessage(message as any);
  }, [addMessage, completeStreamingMessage, sessionId]);

  // ============================================================================
  // HELPER: Handle flow content (accumulate and display)
  // ============================================================================
  const handleFlowContent = useCallback((parsed: ParsedLogData) => {
    flowContentBufferRef.current.push(parsed.content);
  }, []);

  // ============================================================================
  // HELPER: Handle flow generation completion
  // ============================================================================
  const handleFlowGenerated = useCallback(async (parsed: ParsedLogData) => {
    // Complete current message
    if (currentMessageIdRef.current) {
      completeStreamingMessage(currentMessageIdRef.current);
      currentMessageIdRef.current = null;
    }

    // Combine buffered flow content
    const fullFlowContent = flowContentBufferRef.current.join('\n');
    flowContentBufferRef.current = [];

    // Add flow generated message with full content
    const message = {
      id: generateUUID(),
      role: 'system',
      content: parsed.content,
      type: 'flow',
      streaming: false,
      createdAt: new Date(),
      metadata: {
        ...parsed.metadata,
        flowContent: fullFlowContent,
      },
    };

    addMessage(message as any);
  }, [addMessage, completeStreamingMessage, sessionId]);

  // ============================================================================
  // HELPER: Handle MCP lifecycle events
  // ============================================================================
  const handleMcpLifecycle = useCallback((parsed: ParsedLogData) => {
    // Log MCP events but don't clutter the UI
    console.log('[MCP Lifecycle]', parsed.content, parsed.metadata);

    // Only show important MCP events (connection, disconnection)
    if (
      parsed.content.includes('connected') ||
      parsed.content.includes('disconnection') ||
      parsed.content.includes('exited')
    ) {
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: parsed.content,
        type: 'text',
        streaming: false,
        createdAt: new Date(),
        metadata: parsed.metadata,
      });
    }
  }, [addMessage]);

  // ============================================================================
  // HELPER: Handle status messages
  // ============================================================================
  const handleStatusMessage = useCallback((parsed: ParsedLogData) => {
    // Complete current message if any
    if (currentMessageIdRef.current) {
      completeStreamingMessage(currentMessageIdRef.current);
      currentMessageIdRef.current = null;
    }

    // Add status message
    addMessage({
      id: generateUUID(),
      role: 'system',
      content: parsed.content,
      type: 'status',
      streaming: false,
      createdAt: new Date(),
      metadata: parsed.metadata,
    } as any);
  }, [addMessage, completeStreamingMessage]);

  // ============================================================================
  // HELPER: Handle metrics updates
  // ============================================================================
  const handleMetrics = useCallback((parsed: ParsedLogData) => {
    // Update current message tokens
    if (currentMessageIdRef.current && parsed.metadata) {
      const messages = useChatStore.getState().messages;
      const existingMessage = messages.find((m) => m.id === currentMessageIdRef.current);
      const existingTokens = existingMessage?.metadata?.tokens || { input: 0, output: 0, total: 0 };

      updateCurrentMessage({
        metadata: {
          tokens: {
            input: (existingTokens.input || 0) + (parsed.metadata.inputTokens || 0),
            output: (existingTokens.output || 0) + (parsed.metadata.outputTokens || 0),
            total:
              (existingTokens.total || 0) +
              (parsed.metadata.inputTokens || 0) +
              (parsed.metadata.outputTokens || 0),
          },
          cacheStats: {
            cacheCreation: (parsed.metadata.cacheCreationInputTokens || 0),
            cacheRead: (parsed.metadata.cacheReadInputTokens || 0),
            ephemeral5m: (parsed.metadata.ephemeral5mTokens || 0),
            ephemeral1h: (parsed.metadata.ephemeral1hTokens || 0),
          },
        },
      });
    }

    // Update global metrics
    if (parsed.metadata) {
      incrementMetrics({
        inputTokens: parsed.metadata.inputTokens || 0,
        outputTokens: parsed.metadata.outputTokens || 0,
      });
    }
  }, [incrementMetrics, updateCurrentMessage]);

  // ============================================================================
  // HELPER: Handle session end (result data)
  // ============================================================================
  const handleSessionEnd = useCallback((parsed: ParsedLogData) => {
    if (parsed.metadata?.resultData) {
      // Store in session store
      setResultData(parsed.metadata.resultData);

      // Update current message with result data
      if (currentMessageIdRef.current) {
        updateCurrentMessage({
          metadata: {
            resultData: parsed.metadata.resultData,
          },
        });
      }

      // Update global metrics with final values
      const result = parsed.metadata.resultData;
      updateMetrics({
        inputTokens: result.usage.inputTokens,
        outputTokens: result.usage.outputTokens,
        totalCost: result.totalCostUsd,
        cacheCreationTokens: result.usage.cacheCreationInputTokens,
        cacheReadTokens: result.usage.cacheReadInputTokens,
      });

      // Add completion message
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Session completed - ${result.numTurns} turns, ${(result.durationMs / 1000).toFixed(1)}s, $${result.totalCostUsd.toFixed(4)}`,
        type: 'completion',
        streaming: false,
        createdAt: new Date(),
        metadata: {
          resultData: result,
        },
      } as any);
    }
  }, [setResultData, updateCurrentMessage, updateMetrics, addMessage]);

  // ============================================================================
  // HELPER: Handle agent lifecycle events
  // ============================================================================
  const handleAgentLifecycle = useCallback((parsed: ParsedLogData) => {
    // Complete any streaming message
    if (currentMessageIdRef.current) {
      completeStreamingMessage(currentMessageIdRef.current);
      currentMessageIdRef.current = null;
    }

    // Add lifecycle message
    addMessage({
      id: generateUUID(),
      role: 'system',
      content: parsed.content,
      type: 'status',
      streaming: false,
      createdAt: new Date(),
      metadata: parsed.metadata,
    });
  }, [addMessage, completeStreamingMessage]);

  // ============================================================================
  // ROUTE PARSED CHUNK TO HANDLERS
  // ============================================================================
  const routeParsedChunk = useCallback((parsed: ParsedLogData) => {

    // Route to appropriate handler based on type
    switch (parsed.type) {
      // ===== SESSION MANAGEMENT =====
      case 'session_init':
        if (parsed.metadata?.sessionData) {
          mergeSessionData(parsed.metadata.sessionData);
        }
        break;

      case 'session_end':
        handleSessionEnd(parsed);
        break;

      case 'session_header':
        // Log but don't display boundary markers
        console.log('[Session Header]', parsed.content);
        break;

      // ===== THINKING =====
      case 'thinking':
        handleThinkingMessage(parsed);
        break;

      // ===== TOOLS =====
      case 'tool_use':
      case 'mcp_tool_use':
        handleToolMessage(parsed);
        incrementMetrics({ toolCallCount: 1 });
        break;

      case 'tool_result':
      case 'mcp_tool_result':
        // Update tool status in history instead of creating separate message
        if (currentMessageIdRef.current) {
          const messages = useChatStore.getState().messages;
          const existingMessage = messages.find((m) => m.id === currentMessageIdRef.current);

          if (existingMessage) {
            const isMcp = parsed.type === 'mcp_tool_result';
            const historyKey = isMcp ? 'mcpToolHistory' : 'toolHistory';
            const history = existingMessage.metadata?.[historyKey] || [];

            // Find the tool to update (match by toolId, tool name, or update the last running tool)
            const toolId = parsed.metadata?.toolId;
            const toolName = isMcp ? parsed.metadata?.mcpToolName : parsed.metadata?.toolName;
            let matchFound = false;
            const updatedHistory = history.map((item, index: number) => {
              // Match by toolId if available, or by tool name if it's the last running one with that name
              let isMatch = false;
              if (toolId && item.toolId === toolId) {
                isMatch = true;
              } else if (toolName && item.tool === toolName && item.status === 'running') {
                // Match by tool name for the most recent running tool with that name
                const laterRunningToolWithSameName = history.slice(index + 1).some(
                  (laterItem) => laterItem.tool === toolName && laterItem.status === 'running'
                );
                isMatch = !laterRunningToolWithSameName;
              } else if (!toolId && !toolName && index === history.length - 1 && item.status === 'running') {
                // Fallback: update last running tool
                isMatch = true;
              }

              if (isMatch) {
                matchFound = true;
                console.log('[useAgent] Updating tool in history:', { toolId, tool: item.tool, status: 'completed', hasOutput: !!parsed.metadata?.toolOutput });
                return {
                  ...item,
                  status: parsed.metadata?.duration ? 'completed' as const : item.status, // Only mark completed if we have duration
                  duration: parsed.metadata?.duration || item.duration, // Keep existing duration if not provided
                  output: parsed.metadata?.toolOutput || item.output || parsed.content, // Keep existing output if not provided, fallback to content
                };
              }
              return item;
            });

            // If no match found, this might be a race condition - log it
            if (!matchFound) {
              console.warn('[useAgent] Tool result received but no matching running tool found:', {
                toolId,
                parsed: parsed.metadata,
                existingHistory: history.map(h => ({ tool: h.tool, toolId: h.toolId, status: h.status })),
              });
            }

            // Build updated message
            const updatedMetadata = {
              ...existingMessage.metadata,
              [historyKey]: updatedHistory,
            };

            // Update message in store
            updateMessage(currentMessageIdRef.current, {
              metadata: updatedMetadata,
            });

            // Save updated message to database (only if already saved)
            if (savedMessageIds.current.has(currentMessageIdRef.current)) {
              const updatedMessage = {
                ...existingMessage,
                metadata: updatedMetadata,
              };
              updateMessageInDatabase(currentMessageIdRef.current, updatedMessage).catch((error) => {
                console.error('[useAgent] Failed to update message in database:', error);
              });
            }
          }
        }
        break;

      // ===== MCP LIFECYCLE =====
      case 'mcp_connection':
      case 'mcp_lifecycle':
        handleMcpLifecycle(parsed);
        break;

      // ===== FLOWS =====
      case 'flow_content':
        handleFlowContent(parsed);
        break;

      case 'flow_generated':
        handleFlowGenerated(parsed);
        break;

      // ===== STATUS & AGENT LIFECYCLE =====
      case 'status':
        handleStatusMessage(parsed);
        break;

      case 'agent_lifecycle':
        handleAgentLifecycle(parsed);
        break;

      // ===== METRICS =====
      case 'metrics':
        handleMetrics(parsed);
        break;

      // ===== ERRORS =====
      case 'error':
        addMessage({
          id: generateUUID(),
          role: 'system',
          content: `Error: ${parsed.content}`,
          type: 'error',
          error: parsed.metadata?.errorMessage || parsed.content,
          createdAt: new Date(),
          metadata: parsed.metadata,
        });
        break;

      // ===== DEBUG LOGS =====
      case 'debug_file_ops':
      case 'debug_shell':
      case 'debug_plugin':
      case 'debug_hooks':
      case 'debug_settings':
      case 'debug_misc':
      case 'stream_event':
        // Log debug info but don't show in UI (clutters the interface)
        console.log(`[Debug ${parsed.type}]`, parsed.content);
        break;

      // ===== MESSAGES & CACHE =====
      case 'message_assistant':
      case 'message_user':
      case 'cache_stats':
      case 'model_usage':
        // These are handled as part of thinking/tool messages via metadata
        console.log(`[${parsed.type}]`, parsed.metadata);
        break;

      // ===== UNKNOWN =====
      default:
        console.log('[Unknown chunk type]', parsed.type, parsed.content.substring(0, 100));
    }
  }, [
    mergeSessionData,
    handleSessionEnd,
    handleThinkingMessage,
    handleToolMessage,
    handleFlowContent,
    handleFlowGenerated,
    handleMcpLifecycle,
    handleStatusMessage,
    handleAgentLifecycle,
    handleMetrics,
    incrementMetrics,
    addMessage,
    updateMessage,
  ]);

  // ============================================================================
  // MAIN CHUNK PROCESSOR
  // ============================================================================
  const processChunk = useCallback((chunk: string) => {
    const trimmedChunk = chunk.trim();

    // ===== JSON BUFFERING LOGIC =====
    // Check if we're starting JSON buffering
    if (!isBufferingJsonRef.current &&
        (trimmedChunk.startsWith('[DEBUG] Message: {') || trimmedChunk.startsWith('{"type"'))) {
      console.log('[Agent] Starting JSON buffer');
      isBufferingJsonRef.current = true;
      jsonBufferRef.current = [chunk];
      jsonBraceCountRef.current = 0;

      // Count braces in first line
      for (const char of chunk) {
        if (char === '{') jsonBraceCountRef.current++;
        if (char === '}') jsonBraceCountRef.current--;
      }

      // If balanced on first line, we have complete JSON
      if (jsonBraceCountRef.current === 0) {
        isBufferingJsonRef.current = false;
        const completeJson = jsonBufferRef.current.join('\n');
        jsonBufferRef.current = [];
        console.log('[Agent] Complete JSON on first line');
        // Parse and process the complete JSON
        const parsed = parseAgentLog(completeJson);
        if (parsed.type !== 'raw' || parsed.content || parsed.metadata) {
          console.log('[Agent] Parsed JSON chunk:', { type: parsed.type, content: parsed.content.substring(0, 100) });
          routeParsedChunk(parsed);
        }
      }
      return;
    }

    // Continue buffering JSON
    if (isBufferingJsonRef.current) {
      jsonBufferRef.current.push(chunk);

      // Count braces
      for (const char of chunk) {
        if (char === '{') jsonBraceCountRef.current++;
        if (char === '}') jsonBraceCountRef.current--;
      }

      // Check if JSON is complete (balanced braces)
      if (jsonBraceCountRef.current === 0) {
        console.log('[Agent] JSON buffer complete, lines:', jsonBufferRef.current.length);
        isBufferingJsonRef.current = false;
        const completeJson = jsonBufferRef.current.join('\n');
        jsonBufferRef.current = [];

        // Parse and process the complete JSON
        const parsed = parseAgentLog(completeJson);
        if (parsed.type !== 'raw' || parsed.content || parsed.metadata) {
          console.log('[Agent] Parsed buffered JSON:', { type: parsed.type, content: parsed.content.substring(0, 100) });
          routeParsedChunk(parsed);
        }
      }
      return;
    }

    // ===== NORMAL PARSING (non-JSON chunks) =====
    // Parse the chunk using enhanced parser
    const parsed = parseAgentLog(chunk);

    // Skip empty/raw logs with no useful content
    if ((parsed.type === 'raw' && !parsed.content) || (!parsed.content && !parsed.metadata)) {
      return;
    }

    // Log for debugging
    console.log('[Agent] Parsed chunk:', { type: parsed.type, content: parsed.content.substring(0, 100) });

    routeParsedChunk(parsed);
  }, [routeParsedChunk]);

  // ============================================================================
  // WEBSOCKET CONNECTION
  // ============================================================================
  useEffect(() => {
    const socket = io({
      path: '/socket.io',
    });

    socket.on('connect', () => {
      console.log('[Agent] Connected to WebSocket');
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('[Agent] Disconnected from WebSocket');
      setIsConnected(false);
      setAgentRunning(false);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [setAgentRunning]);

  // ============================================================================
  // EVENT LISTENERS
  // ============================================================================
  useEffect(() => {
    const socket = socketRef.current;
    if (!socket) return;

    // ===== AGENT LIFECYCLE =====
    socket.on('agent:started', () => {
      console.log('[Agent] Started');
      setAgentRunning(true);

      // Reset buffers
      flowContentBufferRef.current = [];
      thinkingBufferRef.current = [];
      jsonBufferRef.current = [];
      isBufferingJsonRef.current = false;
      jsonBraceCountRef.current = 0;
      currentMessageIdRef.current = null;
    });

    socket.on('agent:completed', ({ exitCode, duration }) => {
      console.log('[Agent] Completed', { exitCode, duration });
      setAgentRunning(false);

      // Flush any pending todo updates immediately
      if (todoUpdateTimerRef.current) {
        clearTimeout(todoUpdateTimerRef.current);
        const pending = pendingTodoUpdateRef.current;
        if (pending) {
          const todos = pending.message.metadata?.todos;
          const completedCount = todos?.filter((t: any) => t.status === 'completed').length || 0;
          console.log('[useAgent] 🚀 FLUSHING FINAL TODO STATE on completion');
          console.log('[useAgent] Final state:', `${completedCount}/${todos?.length || 0} completed`);
          console.log('[useAgent] Final todos:', JSON.stringify(todos, null, 2));
          updateMessageInDatabase(pending.id, pending.message)
            .then(() => console.log('[useAgent] ✅ FINAL TODO STATE SAVED TO DB'))
            .catch((error) => console.error('[useAgent] ❌ Failed to save final todo state:', error));
          pendingTodoUpdateRef.current = null;
        }
      }

      // Complete any streaming message
      if (currentMessageIdRef.current) {
        completeStreamingMessage(currentMessageIdRef.current);
        currentMessageIdRef.current = null;
      }

      // Add completion message
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Agent completed with exit code ${exitCode} (${(duration / 1000).toFixed(1)}s)`,
        type: 'completion',
        createdAt: new Date(),
      });
    });

    // ===== STREAM CHUNKS (MAIN LOG PROCESSING) =====
    socket.on('stream:chunk', ({ chunk }) => {
      processChunk(chunk);
    });

    // ===== TOOL EVENTS (Legacy support - can be removed if server only uses stream:chunk) =====
    socket.on('tool:start', ({ toolUseId, toolName, input }) => {
      console.log('[Agent] Tool started:', toolName);

      const messages = useChatStore.getState().messages;
      const lastMessage = messages[messages.length - 1];

      if (lastMessage && lastMessage.role === 'assistant') {
        // Add to legacy toolUses array
        addToolUse(lastMessage.id, {
          id: toolUseId,
          toolName,
          input,
          status: 'running',
        });

        // ALSO add to metadata.toolHistory for persistence
        const existingHistory = lastMessage.metadata?.toolHistory || [];
        updateMessage(lastMessage.id, {
          metadata: {
            ...lastMessage.metadata,
            toolHistory: [
              ...existingHistory,
              {
                tool: toolName,
                toolId: toolUseId,
                input,
                status: 'running' as const,
              },
            ],
          },
        });
      }

      incrementMetrics({ toolCallCount: 1 });
    });

    socket.on('tool:complete', ({ toolUseId, output, duration, success }) => {
      console.log('[Agent] Tool completed:', toolUseId);

      const messages = useChatStore.getState().messages;
      const lastMessage = messages[messages.length - 1];

      if (lastMessage && lastMessage.role === 'assistant') {
        // Update legacy toolUses array
        updateToolUse(lastMessage.id, toolUseId, {
          output,
          duration,
          status: success ? 'completed' : 'failed',
        });

        // ALSO update metadata.toolHistory for persistence
        const existingHistory = lastMessage.metadata?.toolHistory || [];
        const newStatus: 'completed' | 'failed' = success ? 'completed' : 'failed';
        const updatedHistory = existingHistory.map((item) =>
          item.toolId === toolUseId
            ? {
                ...item,
                status: newStatus,
                duration,
                output,
              }
            : item
        );

        updateMessage(lastMessage.id, {
          metadata: {
            ...lastMessage.metadata,
            toolHistory: updatedHistory,
          },
        });

        // Save to database (only if already saved)
        if (savedMessageIds.current.has(lastMessage.id)) {
          const updatedMessage = {
            ...lastMessage,
            metadata: {
              ...lastMessage.metadata,
              toolHistory: updatedHistory,
            },
          };
          updateMessageInDatabase(lastMessage.id, updatedMessage).catch((error) => {
            console.error('[useAgent] Failed to update message in database:', error);
          });
        }
      }
    });

    // ===== METRICS (Legacy support) =====
    socket.on('metrics:update', (data) => {
      console.log('[Agent] Metrics update:', data);
      updateMetrics(data);
    });

    // ===== FLOW EVENTS (Legacy support) =====
    socket.on('flow:generated', ({ name, content }) => {
      console.log('[Agent] Flow generated:', name);

      // Complete the streaming message
      const messages = useChatStore.getState().messages;
      const streamingMessage = messages.find((m) => m.streaming);
      if (streamingMessage) {
        completeStreamingMessage(streamingMessage.id);
      }

      // Add flow generated message
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Flow generated: ${name}\n\n\`\`\`toml\n${content}\n\`\`\``,
        type: 'flow',
        createdAt: new Date(),
      });
    });

    socket.on('flow:saved', ({ path }) => {
      console.log('[Agent] Flow saved:', path);

      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Flow saved to: ${path}`,
        type: 'text',
        createdAt: new Date(),
      });
    });

    // ===== ERROR HANDLING =====
    socket.on('error', ({ message, code }) => {
      console.error('[Agent] Error:', code, message);

      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Error: ${message}`,
        type: 'error',
        error: message,
        createdAt: new Date(),
      });

      setAgentRunning(false);
    });

    // ===== GENERIC LOGS =====
    socket.on('log', ({ level, message, data }) => {
      console.log(`[Agent] Log [${level}]:`, message, data);

      // Only show important logs as messages
      if (level === 'error' || level === 'warn') {
        addMessage({
          id: generateUUID(),
          role: 'system',
          content: `[${level.toUpperCase()}] ${message}`,
          type: 'text',
          createdAt: new Date(),
        });
      }
    });

    return () => {
      socket.off('agent:started');
      socket.off('agent:completed');
      socket.off('stream:chunk');
      socket.off('tool:start');
      socket.off('tool:complete');
      socket.off('metrics:update');
      socket.off('flow:generated');
      socket.off('flow:saved');
      socket.off('error');
      socket.off('log');
    };
  }, [
    addMessage,
    updateMessage,
    appendToStreamingMessage,
    completeStreamingMessage,
    addToolUse,
    updateToolUse,
    setAgentRunning,
    updateMetrics,
    incrementMetrics,
    processChunk,
  ]);

  // ============================================================================
  // AGENT CONTROL
  // ============================================================================

  // Start agent
  const startAgent = useCallback(
    (request: string) => {
      const socket = socketRef.current;
      if (!socket) {
        console.error('[Agent] Socket not connected');
        return;
      }

      // Format conversation history for the agent
      const conversationHistory = messages.map((msg) => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content,
      }));

      // Get API key from settings
      const settings = useFlowSettingsStore.getState().settings;
      const apiKey = settings.anthropicApiKey;

      console.log('[Agent] Starting agent with request:', request);
      console.log('[Agent] Conversation history length:', conversationHistory.length);
      console.log('[Agent] API key from settings:', apiKey ? apiKey.substring(0, 20) + '...' : 'NOT SET');

      socket.emit('agent:start', {
        sessionId,
        request,
        conversationHistory,
        apiKey, // Pass API key from settings
      });
    },
    [sessionId, messages]
  );

  // Stop agent
  const stopAgent = useCallback(() => {
    const socket = socketRef.current;
    if (!socket) return;

    console.log('[Agent] Stopping agent');
    socket.emit('agent:stop', { sessionId });
    setAgentRunning(false);
  }, [sessionId, setAgentRunning]);

  return {
    startAgent,
    stopAgent,
    isConnected,
  };
}