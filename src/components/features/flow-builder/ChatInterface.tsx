'use client';

import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '@/lib/stores/chat-store';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatSidebar } from './ChatSidebar';
import { FlowBuilderSettings } from './FlowBuilderSettings';
import { Settings, MessageSquare } from 'lucide-react';

export function ChatInterface() {

  const messages = useChatStore((state) => state.messages);
  const isAgentRunning = useChatStore((state) => state.isAgentRunning);
  const sessionId = useChatStore((state) => state.sessionId);
  const setSessionId = useChatStore((state) => state.setSessionId);
  const clearMessages = useChatStore((state) => state.clearMessages);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [promptText, setPromptText] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'settings'>('chat');

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize - no session creation on mount, wait for user's first message
  useEffect(() => {
    if (initialized) return;
    console.log('[ChatInterface] Initialized - waiting for user input');
    setInitialized(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle new session creation
  async function handleNewSession() {
    try {
      setLoading(true);
      clearMessages();

      // Create new session via API
      const response = await fetch('/api/flow-builder/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'default-user', // TODO: Get from auth
          title: 'New Flow',
        }),
      });

      if (!response.ok) throw new Error('Failed to create session');

      const { session } = await response.json();
      setSessionId(session.id);
    } catch (error) {
      console.error('[ChatInterface] Error creating new session:', error);
    } finally {
      setLoading(false);
    }
  }

  // Handle session selection from sidebar
  async function handleSelectSession(selectedSessionId: string) {
    try {
      setLoading(true);
      clearMessages();

      // Load session with messages from API
      const response = await fetch(`/api/flow-builder/sessions/${selectedSessionId}`);
      if (!response.ok) throw new Error('Failed to load session');

      const { session } = await response.json();
      setSessionId(session.id);

      // Convert database messages to chat store format and load them
      const loadedMessages = session.messages.map((dbMsg: {
        id: string;
        role: string;
        content: string | object;
        type?: string;
        streaming?: boolean;
        createdAt: string;
        error?: string;
        metadata?: any;
        toolUses?: any[];
        inputTokens?: number;
        outputTokens?: number;
      }) => ({
        id: dbMsg.id,
        role: dbMsg.role.toLowerCase(),
        content: typeof dbMsg.content === 'string' ? dbMsg.content : JSON.stringify(dbMsg.content),
        type: dbMsg.type?.toLowerCase() || 'text',
        streaming: dbMsg.streaming || false,
        createdAt: new Date(dbMsg.createdAt),
        error: dbMsg.error,
        // Include toolUses from database (legacy tool tracking)
        toolUses: dbMsg.toolUses || [],
        // Use metadata from database, or fallback to constructing from tokens
        metadata: dbMsg.metadata || {
          tokens: {
            input: dbMsg.inputTokens,
            output: dbMsg.outputTokens,
            total: (dbMsg.inputTokens || 0) + (dbMsg.outputTokens || 0),
          },
        },
      }));

      // Add messages to store and mark them as loaded from DB
      const addMessage = useChatStore.getState().addMessage;
      loadedMessages.forEach((msg: any) => {
        // Add a flag to indicate this was loaded from DB
        addMessage({ ...msg, _loadedFromDb: true });
      });

    } catch (error) {
      console.error('[ChatInterface] Error loading session:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <ChatSidebar
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      {/* Main Area */}
      <div className="flex flex-col flex-1">
        {/* Tab Navigation */}
        <div className="flex items-center border-b border-zinc-200 dark:border-zinc-800 px-4">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'chat'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'settings'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
            }`}
          >
            <Settings className="h-4 w-4" />
            Settings
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'chat' ? (
          <>
            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-full border-4 border-zinc-200 dark:border-zinc-700 border-t-blue-600 animate-spin" />
                <p className="text-zinc-600 dark:text-zinc-400">Loading session...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-semibold">ACT Flow Architect</h2>
                <p className="text-zinc-600 dark:text-zinc-400 max-w-md">
                  Generate ACT workflows using natural language. Describe what you want to build, and I&apos;ll create a complete
                  .flow file for you.
                </p>
                <div className="flex flex-wrap gap-2 justify-center mt-6">
                  <ExamplePrompt onSelect={setPromptText}>Build a GitHub to Slack sync</ExamplePrompt>
                  <ExamplePrompt onSelect={setPromptText}>Create a weather tracking API</ExamplePrompt>
                  <ExamplePrompt onSelect={setPromptText}>Generate daily reports with AI</ExamplePrompt>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isAgentRunning && <StreamingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

            {/* Chat Input */}
            <div className="border-t border-zinc-200 dark:border-zinc-800 p-4">
              <ChatInput examplePrompt={promptText} onPromptSent={() => setPromptText(null)} />
            </div>
          </>
        ) : (
          /* Settings Tab */
          <FlowBuilderSettings />
        )}
      </div>
    </div>
  );
}

function ExamplePrompt({ children, onSelect }: { children: React.ReactNode; onSelect?: (text: string) => void }) {
  const handleClick = () => {
    if (onSelect) {
      onSelect(children as string);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="px-4 py-2 text-sm bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-lg transition-colors"
    >
      {children}
    </button>
  );
}

function StreamingIndicator() {
  return (
    <div className="flex items-center gap-2 text-zinc-500 dark:text-zinc-400">
      <div className="flex gap-1">
        <div className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm">Agent is thinking...</span>
    </div>
  );
}
