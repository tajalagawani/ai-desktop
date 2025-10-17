// Zustand store for chat state management - Expanded to match React app contexts

import { create } from 'zustand';
import { Message, Session, Action, Project } from '@/types';
import { getWebSocketClient } from '@/lib/action-builder/websocket';
import { api } from '@/lib/action-builder/api';

// Transform JSONL format messages to app format
function transformMessages(rawMessages: any[]): Message[] {
  const converted: Message[] = [];
  const toolResults = new Map(); // Map tool_use_id to tool result

  // First pass: collect all tool results
  for (const msg of rawMessages) {
    if (msg.message?.role === 'user' && Array.isArray(msg.message?.content)) {
      for (const part of msg.message.content) {
        if (part.type === 'tool_result') {
          toolResults.set(part.tool_use_id, {
            content: part.content,
            isError: part.is_error,
            timestamp: new Date(msg.timestamp || Date.now())
          });
        }
      }
    }
  }

  // Second pass: process messages
  for (const msg of rawMessages) {
    // Handle user messages
    if (msg.message?.role === 'user' && msg.message?.content) {
      let content = '';

      if (Array.isArray(msg.message.content)) {
        const textParts = [];
        for (const part of msg.message.content) {
          if (part.type === 'text') {
            textParts.push(part.text);
          }
        }
        content = textParts.join('\n');
      } else if (typeof msg.message.content === 'string') {
        content = msg.message.content;
      } else {
        content = String(msg.message.content);
      }

      // Skip command messages and empty content
      if (content && !content.startsWith('<command-name>') && !content.startsWith('[Request interrupted')) {
        converted.push({
          id: msg.uuid || msg.id || String(Date.now()),
          type: 'user',
          content: content,
          timestamp: new Date(msg.timestamp || Date.now()).getTime(),
          sessionId: msg.sessionId
        });
      }
    }
    // Handle assistant messages
    else if (msg.message?.role === 'assistant' && Array.isArray(msg.message?.content)) {
      for (const part of msg.message.content) {
        if (part.type === 'text' && part.text) {
          converted.push({
            id: msg.uuid || msg.id || String(Date.now()),
            type: 'assistant',
            content: part.text,
            timestamp: new Date(msg.timestamp || Date.now()).getTime(),
            sessionId: msg.sessionId
          });
        } else if (part.type === 'tool_use') {
          const toolResult = toolResults.get(part.id);
          converted.push({
            id: msg.uuid || msg.id || String(Date.now()),
            type: 'assistant',
            content: '',
            timestamp: new Date(msg.timestamp || Date.now()).getTime(),
            isToolUse: true,
            toolName: part.name,
            toolInput: JSON.stringify(part.input, null, 2),
            toolResult: toolResult?.content || '',
            sessionId: msg.sessionId
          });
        }
      }
    }
  }

  return converted;
}

interface User {
  id: string;
  username: string;
}

interface ChatStore {
  // === Messages & Sessions ===
  messages: Message[];
  sessions: Session[];
  actions: Action[];
  currentSession: Session | null;
  streamingMessageId: string | null;

  // === Projects ===
  projects: Project[];
  currentProject: Project | null;
  selectedProject: Project | null;
  isLoadingProjects: boolean;

  // === Auth State ===
  user: User | null;
  token: string | null;
  isAuthLoading: boolean;
  needsSetup: boolean;
  authError: string | null;

  // === WebSocket State ===
  isConnected: boolean;
  isLoading: boolean;
  isInitialLoading: boolean;
  claudeStatus: { text?: string; tokens?: number; can_interrupt?: boolean } | null;

  // === UI State ===
  isDarkMode: boolean;
  isDevMode: boolean;
  activeTab: 'chat' | 'files' | 'shell' | 'git' | 'tasks' | 'preview';
  isMobile: boolean;
  sidebarOpen: boolean;
  showSettings: boolean;
  showQuickSettings: boolean;
  isInputFocused: boolean;

  // === Settings ===
  autoExpandTools: boolean;
  showRawParameters: boolean;
  autoScrollToBottom: boolean;
  sendByCtrlEnter: boolean;

  // === TaskMaster State ===
  tasks: any[];
  nextTask: any | null;
  projectTaskMaster: any | null;
  mcpServerStatus: any | null;
  isLoadingTasks: boolean;
  isLoadingMCP: boolean;
  tasksEnabled: boolean;
  isTaskMasterInstalled: boolean;
  isTaskMasterReady: boolean;

  // === Session Protection ===
  activeSessions: Set<string>;

  // === File/Editor State ===
  editingFile: any | null;
  selectedTask: any | null;

  // === PWA State ===
  isPWA: boolean;
  updateAvailable: boolean;

  // === Actions - Messages & Sessions ===
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateStreamingMessage: (messageId: string, content: string) => void;
  setSessions: (sessions: Session[]) => void;
  setActions: (actions: Action[]) => void;
  setCurrentSession: (session: Session | null) => void;

  // === Actions - Projects ===
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  setSelectedProject: (project: Project | null) => void;
  setIsLoadingProjects: (loading: boolean) => void;

  // === Actions - Auth ===
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (username: string, password: string) => Promise<{success: boolean; error?: string}>;
  register: (username: string, password: string) => Promise<{success: boolean; error?: string}>;
  logout: () => void;
  checkAuthStatus: () => Promise<void>;

  // === Actions - WebSocket ===
  setIsConnected: (connected: boolean) => void;
  setIsLoading: (loading: boolean) => void;
  setIsInitialLoading: (loading: boolean) => void;
  setClaudeStatus: (status: { text?: string; tokens?: number; can_interrupt?: boolean } | null) => void;
  initWebSocket: () => void;

  // === Actions - UI ===
  toggleDarkMode: () => void;
  toggleDevMode: () => void;
  setActiveTab: (tab: 'chat' | 'files' | 'shell' | 'git' | 'tasks' | 'preview') => void;
  setIsMobile: (mobile: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setShowSettings: (show: boolean) => void;
  setShowQuickSettings: (show: boolean) => void;
  setIsInputFocused: (focused: boolean) => void;

  // === Actions - Settings ===
  setAutoExpandTools: (value: boolean) => void;
  setShowRawParameters: (value: boolean) => void;
  setAutoScrollToBottom: (value: boolean) => void;
  setSendByCtrlEnter: (value: boolean) => void;

  // === Actions - TaskMaster ===
  setTasks: (tasks: any[]) => void;
  setNextTask: (task: any | null) => void;
  refreshTasks: () => Promise<void>;
  refreshMCPStatus: () => Promise<void>;
  setTasksEnabled: (enabled: boolean) => void;
  toggleTasksEnabled: () => void;

  // === Actions - Session Protection ===
  markSessionAsActive: (sessionId: string) => void;
  markSessionAsInactive: (sessionId: string) => void;
  replaceTemporarySession: (realSessionId: string) => void;

  // === Actions - File/Editor ===
  setEditingFile: (file: any | null) => void;
  setSelectedTask: (task: any | null) => void;

  // === Async operations ===
  loadProjects: () => Promise<void>;
  loadSessions: () => Promise<void>;
  loadSessionMessages: (projectName: string, sessionId: string) => Promise<void>;
  loadActions: () => Promise<void>;
  loadMessages: (sessionId: string) => Promise<void>;
  sendMessage: (content: string) => void;
  createNewSession: () => void;
  deleteSession: (sessionId: string) => Promise<void>;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // === Initial State - Messages & Sessions ===
  messages: [],
  sessions: [],
  actions: [],
  currentSession: null,
  streamingMessageId: null,

  // === Initial State - Projects ===
  projects: [],
  currentProject: null,
  selectedProject: null,
  isLoadingProjects: false,

  // === Initial State - Auth ===
  user: null,
  token: null,
  isAuthLoading: true,
  needsSetup: false,
  authError: null,

  // === Initial State - WebSocket ===
  isConnected: false,
  isLoading: false,
  isInitialLoading: true,
  claudeStatus: null,

  // === Initial State - UI ===
  isDarkMode: false,
  isDevMode: false,
  activeTab: 'chat',
  isMobile: false,
  sidebarOpen: false,
  showSettings: false,
  showQuickSettings: false,
  isInputFocused: false,

  // === Initial State - Settings ===
  autoExpandTools: false,
  showRawParameters: false,
  autoScrollToBottom: true,
  sendByCtrlEnter: false,

  // === Initial State - TaskMaster ===
  tasks: [],
  nextTask: null,
  projectTaskMaster: null,
  mcpServerStatus: null,
  isLoadingTasks: false,
  isLoadingMCP: false,
  tasksEnabled: true,
  isTaskMasterInstalled: false,
  isTaskMasterReady: false,

  // === Initial State - Session Protection ===
  activeSessions: new Set<string>(),

  // === Initial State - File/Editor ===
  editingFile: null,
  selectedTask: null,

  // === Initial State - PWA ===
  isPWA: false,
  updateAvailable: false,

  // === Setters - Messages & Sessions ===
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  updateStreamingMessage: (messageId, content) => set((state) => ({
    messages: state.messages.map(msg =>
      msg.id === messageId ? { ...msg, content } : msg
    )
  })),
  setSessions: (sessions) => set({ sessions }),
  setActions: (actions) => set({ actions }),
  setCurrentSession: (session) => set({ currentSession: session }),

  // === Setters - Projects ===
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  setSelectedProject: (project) => set({ selectedProject: project }),
  setIsLoadingProjects: (loading) => set({ isLoadingProjects: loading }),

  // === Setters - Auth ===
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),

  // === Setters - WebSocket ===
  setIsConnected: (connected) => set({ isConnected: connected }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setIsInitialLoading: (loading) => set({ isInitialLoading: loading }),
  setClaudeStatus: (status) => set({ claudeStatus: status }),

  // === Setters - UI ===
  setActiveTab: (tab) => set({ activeTab: tab }),
  setIsMobile: (mobile) => set({ isMobile: mobile }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setShowSettings: (show) => set({ showSettings: show }),
  setShowQuickSettings: (show) => set({ showQuickSettings: show }),
  setIsInputFocused: (focused) => set({ isInputFocused: focused }),

  toggleDarkMode: () => set((state) => {
    const newMode = !state.isDarkMode;
    if (typeof window !== 'undefined') {
      localStorage.setItem('darkMode', String(newMode));
      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
    return { isDarkMode: newMode };
  }),

  toggleDevMode: () => set((state) => {
    const newMode = !state.isDevMode;
    if (typeof window !== 'undefined') {
      localStorage.setItem('dev_mode', String(newMode));
    }
    return { isDevMode: newMode };
  }),

  // === Setters - Settings ===
  setAutoExpandTools: (value) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('autoExpandTools', String(value));
    }
    set({ autoExpandTools: value });
  },
  setShowRawParameters: (value) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('showRawParameters', String(value));
    }
    set({ showRawParameters: value });
  },
  setAutoScrollToBottom: (value) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('autoScrollToBottom', String(value));
    }
    set({ autoScrollToBottom: value });
  },
  setSendByCtrlEnter: (value) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('sendByCtrlEnter', String(value));
    }
    set({ sendByCtrlEnter: value });
  },

  // === Setters - TaskMaster ===
  setTasks: (tasks) => set({ tasks }),
  setNextTask: (task) => set({ nextTask: task }),
  setTasksEnabled: (enabled) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('tasks-enabled', String(enabled));
    }
    set({ tasksEnabled: enabled });
  },
  toggleTasksEnabled: () => set((state) => {
    const newValue = !state.tasksEnabled;
    if (typeof window !== 'undefined') {
      localStorage.setItem('tasks-enabled', String(newValue));
    }
    return { tasksEnabled: newValue };
  }),

  // === Setters - File/Editor ===
  setEditingFile: (file) => set({ editingFile: file }),
  setSelectedTask: (task) => set({ selectedTask: task }),

  // === Session Protection ===
  markSessionAsActive: (sessionId) => {
    if (sessionId) {
      set((state) => ({
        activeSessions: new Set([...state.activeSessions, sessionId])
      }));
    }
  },

  markSessionAsInactive: (sessionId) => {
    if (sessionId) {
      set((state) => {
        const newSet = new Set(state.activeSessions);
        newSet.delete(sessionId);
        return { activeSessions: newSet };
      });
    }
  },

  replaceTemporarySession: (realSessionId) => {
    if (realSessionId) {
      set((state) => {
        const newSet = new Set<string>();
        for (const sessionId of state.activeSessions) {
          if (!sessionId.startsWith('new-session-')) {
            newSet.add(sessionId);
          }
        }
        newSet.add(realSessionId);
        return { activeSessions: newSet };
      });
    }
  },

  // === Auth Operations ===
  checkAuthStatus: async () => {
    try {
      set({ isAuthLoading: true, authError: null });

      const statusResponse = await api.auth.status();
      const statusData = await statusResponse.json();

      if (statusData.needsSetup) {
        set({ needsSetup: true, isAuthLoading: false });
        return;
      }

      const { token } = get();
      if (token) {
        try {
          const userResponse = await api.auth.user();

          if (userResponse.ok) {
            const userData = await userResponse.json();
            set({ user: userData.user, needsSetup: false });
          } else {
            if (typeof window !== 'undefined') {
              localStorage.removeItem('auth-token');
            }
            set({ token: null, user: null });
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth-token');
          }
          set({ token: null, user: null });
        }
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      set({ authError: 'Failed to check authentication status' });
    } finally {
      set({ isAuthLoading: false });
    }
  },

  login: async (username, password) => {
    try {
      set({ authError: null });
      const response = await api.auth.login(username, password);
      const data = await response.json();

      if (response.ok) {
        set({ token: data.token, user: data.user });
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth-token', data.token);
        }
        return { success: true };
      } else {
        set({ authError: data.error || 'Login failed' });
        return { success: false, error: data.error || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = 'Network error. Please try again.';
      set({ authError: errorMessage });
      return { success: false, error: errorMessage };
    }
  },

  register: async (username, password) => {
    try {
      set({ authError: null });
      const response = await api.auth.register(username, password);
      const data = await response.json();

      if (response.ok) {
        set({ token: data.token, user: data.user, needsSetup: false });
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth-token', data.token);
        }
        return { success: true };
      } else {
        set({ authError: data.error || 'Registration failed' });
        return { success: false, error: data.error || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = 'Network error. Please try again.';
      set({ authError: errorMessage });
      return { success: false, error: errorMessage };
    }
  },

  logout: () => {
    const { token } = get();
    set({ token: null, user: null });
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-token');
    }

    if (token) {
      api.auth.logout().catch(error => {
        console.error('Logout endpoint error:', error);
      });
    }
  },

  // Initialize WebSocket connection
  initWebSocket: async () => {
    if (typeof window === 'undefined') return;

    console.log('[ChatStore] ========================================');
    console.log('[ChatStore] initWebSocket called');
    console.log('[ChatStore] ========================================');

    try {
      console.log('[ChatStore] Getting WebSocket client...');
      const ws = getWebSocketClient();
      console.log('[ChatStore] WebSocket client obtained');

      ws.onMessage((message) => {
        const store = useChatStore.getState();
        console.log('📨 WebSocket message received:', message.type, message);

        switch (message.type) {
          case 'connected':
            console.log('✅ WebSocket connected message received');
            break;

          case 'claude_output':
          case 'claude-response':
            // Desktop server sends claude_output, standalone sends claude-response
            const data = message.data;
            console.log('🔍 [DEBUG] Message type:', message.type);
            console.log('🔍 [DEBUG] Data exists:', !!data);
            console.log('🔍 [DEBUG] Full data:', JSON.stringify(data, null, 2));

            if (data) {
              console.log('💬 Claude response data:', data);
              console.log('🔍 [DEBUG] data.message exists:', !!data.message);
              console.log('🔍 [DEBUG] data.message.role:', data.message?.role);
              console.log('🔍 [DEBUG] data.message.content type:', Array.isArray(data.message?.content) ? 'array' : typeof data.message?.content);

              // Handle assistant messages with content array
              if (data.message?.role === 'assistant' && Array.isArray(data.message?.content)) {
                let hasTextContent = false;
                let textContent = '';

                for (const part of data.message.content) {
                  // Handle text content - accumulate it
                  if (part.type === 'text' && part.text) {
                    console.log('✍️ Text content:', part.text.substring(0, 100));
                    hasTextContent = true;
                    textContent += part.text;
                  }

                  // Handle tool use
                  if (part.type === 'tool_use') {
                    console.log('🔧 Tool use:', part.name);
                    // Clear streaming message when tool use starts
                    if (store.streamingMessageId) {
                      set({ streamingMessageId: null });
                    }

                    store.addMessage({
                      id: `tool-${data.uuid || Date.now()}`,
                      type: 'assistant',
                      content: '',
                      timestamp: Date.now(),
                      isToolUse: true,
                      toolName: part.name,
                      toolInput: JSON.stringify(part.input, null, 2),
                    });
                  }
                }

                // Add or update text content if we found any
                if (hasTextContent && textContent) {
                  const currentStreamingId = store.streamingMessageId;

                  if (currentStreamingId) {
                    // Update existing streaming message
                    const currentMsg = store.messages.find(m => m.id === currentStreamingId);
                    if (currentMsg) {
                      console.log('📝 Updating streaming message');
                      // stream-json sends FULL message each time, not deltas - replace content
                      store.updateStreamingMessage(currentStreamingId, textContent);
                    }
                  } else {
                    // Create new streaming message
                    const newId = data.uuid || `msg-${Date.now()}`;
                    console.log('➕ Adding new assistant message:', newId);
                    store.addMessage({
                      id: newId,
                      type: 'assistant',
                      content: textContent,
                      timestamp: Date.now(),
                    });

                    // Only set as streaming if message doesn't have stop_reason
                    if (!data.message.stop_reason) {
                      set({ streamingMessageId: newId });
                    }
                  }
                }
              }

              // Handle user messages with tool results
              if (data.message?.role === 'user' && Array.isArray(data.message?.content)) {
                for (const part of data.message.content) {
                  if (part.type === 'tool_result') {
                    console.log('📋 Tool result');
                    // Find the corresponding tool use message and update it
                    const toolUseMsg = store.messages.find(m =>
                      m.isToolUse && m.toolName && !m.toolResult
                    );
                    if (toolUseMsg) {
                      store.updateStreamingMessage(toolUseMsg.id, toolUseMsg.content);
                      // Update with result
                      set({
                        messages: store.messages.map(m =>
                          m.id === toolUseMsg.id
                            ? { ...m, toolResult: part.content }
                            : m
                        )
                      });
                    }
                  }
                }
              }
            }
            break;

          case 'claude-output':
            const currentStreamingId = get().streamingMessageId;

            if (currentStreamingId) {
              // Update existing streaming message
              const currentMsg = get().messages.find(m => m.id === currentStreamingId);
              if (currentMsg) {
                get().updateStreamingMessage(currentStreamingId, currentMsg.content + (message.data || ''));
              }
            } else {
              // Create new streaming message
              const newId = `msg-${Date.now()}`;
              get().addMessage({
                id: newId,
                type: 'assistant',
                content: message.data || '',
                timestamp: Date.now(),
              });
              set({ streamingMessageId: newId });
            }
            break;

          case 'session-created':
            if (message.sessionId) {
              const newSession = {
                id: message.sessionId,
                summary: 'New Session',
                messageCount: 0,
                lastActivity: new Date().toISOString(),
                created: new Date().toISOString(),
                updated: new Date().toISOString(),
              };

              // Set as current session and add to list
              set({
                currentSession: newSession,
                sessions: [newSession, ...get().sessions]
              });

              // Navigate to new session
              if (typeof window !== 'undefined') {
                window.history.pushState({}, '', `/session/${message.sessionId}`);
              }
            }
            break;

          case 'session-ready':
            console.log('Session ready:', message.message);
            break;

          case 'claude-status':
            // Handle status updates with token count
            if (message.data) {
              const statusData = message.data;
              const statusInfo = {
                text: statusData.message || statusData.status || 'Working...',
                tokens: statusData.tokens || statusData.token_count || 0,
                can_interrupt: statusData.can_interrupt !== false
              };
              store.setClaudeStatus(statusInfo);
              store.setIsLoading(true);
            }
            break;

          case 'complete':
          case 'claude-complete':
            console.log('✅ Session completed');
            set({ streamingMessageId: null, claudeStatus: null });
            store.setIsLoading(false);
            break;

          case 'claude-error':
          case 'error':
            set({ streamingMessageId: null, claudeStatus: null });
            store.addMessage({
              id: `msg-${Date.now()}`,
              type: 'error',
              content: message.error || 'An error occurred',
              timestamp: Date.now(),
            });
            store.setIsLoading(false);
            break;
        }
      });

    console.log('[ChatStore] Setting up connection change handler...');
    ws.onConnectionChange((connected) => {
      console.log('[ChatStore] Connection state changed:', connected);
      const state = useChatStore.getState();
      state.setIsConnected(connected);

      // On first successful connection, mark initial loading as complete
      if (connected && state.isInitialLoading) {
        console.log('[ChatStore] First connection successful, clearing initial loading');
        state.setIsInitialLoading(false);
      }
    });

    console.log('[ChatStore] Calling ws.connect()...');
    await ws.connect();
    console.log('[ChatStore] ✅ WebSocket connected successfully!');
  } catch (error) {
    console.error('[ChatStore] ❌ WebSocket initialization error:', error);
    // WebSocket initialization error, will retry
  }
},

  // === Async operations - Projects ===
  loadProjects: async () => {
    console.log('[ChatStore] ========================================');
    console.log('[ChatStore] Loading flow-architect project...');
    console.log('[ChatStore] ========================================');
    try {
      set({ isLoadingProjects: true });
      const response = await api.projects();
      const data = await response.json();

      console.log('[ChatStore] Projects loaded:', data.length, 'projects');

      // projects.js returns only flow-architect in Action Builder mode
      if (data.length > 0) {
        const flowArchitect = data[0];
        console.log('[ChatStore] Flow Architect project loaded with', flowArchitect.sessions?.length || 0, 'sessions');

        set({
          projects: data,
          currentProject: flowArchitect,
          sessions: flowArchitect.sessions || []
        });
      } else {
        console.warn('[ChatStore] No projects returned from API');
      }
    } catch (error) {
      console.error('[ChatStore] Error fetching projects:', error);
    } finally {
      set({ isLoadingProjects: false });
    }
  },

  // === Async operations - Sessions ===
  loadSessions: async () => {
    const { currentProject } = get();
    if (!currentProject) return;

    try {
      const response = await api.sessions(currentProject.name, 50, 0);
      if (response.ok) {
        const data = await response.json();
        set({ sessions: data.sessions || [] });
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  },

  loadSessionMessages: async (projectName: string, sessionId: string) => {
    console.log('[ChatStore] ========================================');
    console.log('[ChatStore] Loading messages for session:', sessionId);
    console.log('[ChatStore] Project:', projectName);
    console.log('[ChatStore] ========================================');

    try {
      const response = await api.sessionMessages(projectName, sessionId, null, 0);
      if (response.ok) {
        const data = await response.json();
        const messages = data.messages || [];
        console.log('[ChatStore] Loaded', messages.length, 'raw messages');

        // Transform JSONL messages to app format
        const transformed = transformMessages(messages);
        console.log('[ChatStore] Transformed to', transformed.length, 'messages');

        set({ messages: transformed });
      } else {
        console.error('[ChatStore] Failed to load messages:', response.status);
      }
    } catch (error) {
      console.error('[ChatStore] Error loading messages:', error);
    }
  },

  // === Async operations - Actions ===
  loadActions: async () => {
    try {
      const response = await api.get('/actions');
      if (response.ok) {
        const data = await response.json();
        set({ actions: data.actions || [] });
      }
    } catch (error) {
      console.error('Failed to load actions:', error);
    }
  },

  // === Async operations - TaskMaster ===
  refreshTasks: async () => {
    const { currentProject, user, token } = get();
    if (!currentProject || !user || !token) {
      set({ tasks: [], nextTask: null });
      return;
    }

    try {
      set({ isLoadingTasks: true });
      const response = await api.get(`/taskmaster/tasks/${encodeURIComponent(currentProject.name)}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to load tasks');
      }

      const data = await response.json();
      set({ tasks: data.tasks || [] });

      // Find next task (pending or in-progress)
      const nextTask = data.tasks?.find((task: any) =>
        task.status === 'pending' || task.status === 'in-progress'
      ) || null;
      set({ nextTask });
    } catch (err) {
      console.error('Error loading tasks:', err);
      set({ tasks: [], nextTask: null });
    } finally {
      set({ isLoadingTasks: false });
    }
  },

  refreshMCPStatus: async () => {
    const { user, token } = get();
    if (!user || !token) {
      set({ mcpServerStatus: null });
      return;
    }

    try {
      set({ isLoadingMCP: true });
      const response = await api.get('/mcp-utils/taskmaster-server');
      if (response.ok) {
        const data = await response.json();
        set({ mcpServerStatus: data });
      }
    } catch (err) {
      console.error('Error checking MCP server status:', err);
    } finally {
      set({ isLoadingMCP: false });
    }
  },

  loadMessages: async (sessionId: string) => {
    const { currentProject } = get();

    console.log('🔄 loadMessages called with:', { sessionId, currentProject });

    if (!currentProject) {
      console.error('❌ No current project selected');
      return;
    }

    try {
      set({ isLoading: true });
      console.log('📡 Fetching messages from:', `/api/projects/${currentProject.name}/sessions/${sessionId}/messages`);

      const response = await api.sessionMessages(currentProject.name, sessionId, null, 0);

      console.log('📥 Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        const rawMessages = data.messages || [];
        console.log('✅ Messages loaded:', rawMessages.length, 'messages');

        // Transform JSONL format to app format
        const transformed = transformMessages(rawMessages);
        console.log('🔄 Transformed messages:', transformed.length, 'messages');

        set({ messages: transformed });
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to load messages:', response.status, errorText);
        set({ messages: [] });
      }
    } catch (error) {
      console.error('❌ Error loading messages:', error);
      set({ messages: [] });
    } finally {
      set({ isLoading: false });
    }
  },

  sendMessage: (content: string) => {
    const ws = getWebSocketClient();
    const { currentSession } = get();

    // Add user message to UI immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content,
      timestamp: Date.now(),
    };

    get().addMessage(userMessage);

    // Set loading state and default status
    set({
      isLoading: true,
      claudeStatus: {
        text: 'Processing',
        tokens: 0,
        can_interrupt: true
      }
    });

    // Send to backend
    ws.sendUserMessage(content, currentSession?.id);
  },

  createNewSession: () => {
    // Simply clear the current session - don't create immediately
    // Session will be created when user sends first message
    set({ messages: [], currentSession: null });
  },

  deleteSession: async (sessionId: string) => {
    const { currentProject, sessions } = get();
    if (!currentProject) return;

    try {
      const response = await api.deleteSession(currentProject.name, sessionId);
      if (response.ok) {
        // Remove from local state
        set({
          sessions: sessions.filter(s => s.id !== sessionId),
          ...(get().currentSession?.id === sessionId && { currentSession: null, messages: [] })
        });
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  },
}));
