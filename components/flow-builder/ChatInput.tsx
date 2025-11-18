'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/lib/flow-builder/stores/chat-store';
import { useMetricsStore } from '@/lib/flow-builder/stores/metrics-store';
import { useAgent } from '@/lib/flow-builder/hooks/use-agent';
import { generateUUID } from '@/lib/utils';

interface ChatInputProps {
  examplePrompt?: string | null;
  onPromptSent?: () => void;
}

export function ChatInput({ examplePrompt, onPromptSent }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const addMessage = useChatStore((state) => state.addMessage);
  const isAgentRunning = useChatStore((state) => state.isAgentRunning);
  const sessionId = useChatStore((state) => state.sessionId);
  const setSessionId = useChatStore((state) => state.setSessionId);
  const incrementMetrics = useMetricsStore((state) => state.incrementMetrics);

  const { startAgent, isConnected } = useAgent(sessionId || 'temp');

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  // Handle example prompts
  useEffect(() => {
    if (examplePrompt && !isAgentRunning && isConnected) {
      // Submit example prompt
      handleMessageSubmit(examplePrompt);
      onPromptSent?.();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [examplePrompt, isAgentRunning, isConnected]);

  // Generate a title from the first user message
  function generateTitle(userMessage: string): string {
    // Use first 50 chars of message as title
    return userMessage.slice(0, 50) + (userMessage.length > 50 ? '...' : '');
  }

  // Create a new session with generated title
  async function createSessionWithTitle(userMessage: string): Promise<string> {
    try {
      console.log('[ChatInput] Creating new session');

      // Generate title from user message
      const title = generateTitle(userMessage);

      // Create session in database
      const response = await fetch('/api/flow-builder/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'default-user',
          title: title,
        }),
      });

      if (!response.ok) throw new Error('Failed to create session');

      const { session } = await response.json();
      console.log('[ChatInput] Session created:', session.id, 'with title:', title);

      return session.id;
    } catch (error) {
      console.error('[ChatInput] Error creating session:', error);
      throw error;
    }
  }

  async function handleMessageSubmit(messageText: string) {
    if (!messageText.trim() || isAgentRunning || !isConnected) return;

    console.log('[ChatInput] Submitting message:', messageText);

    // If no session exists, create one with AI-generated title
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      console.log('[ChatInput] No session - creating new session with AI title');
      currentSessionId = await createSessionWithTitle(messageText);
      setSessionId(currentSessionId);
    }

    // Add user message to UI
    const message = {
      id: generateUUID(),
      role: 'user' as const,
      content: messageText,
      type: 'text' as const,
      createdAt: new Date(),
    };

    addMessage(message);

    // Save user message to database
    try {
      await fetch('/api/flow-builder/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: message.id,
          sessionId: currentSessionId,
          role: 'USER',
          content: messageText,
          type: 'TEXT',
          streaming: false,
        }),
      });
    } catch (error) {
      console.error('[ChatInput] Error saving message:', error);
    }

    console.log('[ChatInput] Starting agent with request:', messageText);

    // Start agent - it will handle streaming and assistant message creation
    startAgent(messageText);

    // Increment turn count
    incrementMetrics({ turnCount: 1 });
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const messageText = input;
    setInput('');

    await handleMessageSubmit(messageText);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Describe the flow you want to generate..."
        disabled={isAgentRunning}
        rows={1}
        className="flex-1 resize-none rounded-lg bg-white dark:bg-zinc-900 px-4 py-3 text-sm focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed max-h-32"
      />
      <button
        type="submit"
        disabled={!input.trim() || isAgentRunning || !isConnected}
        className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed flex items-center gap-2"
      >
        {!isConnected ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Connecting...</span>
          </>
        ) : isAgentRunning ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Running...</span>
          </>
        ) : (
          <>
            <span>Send</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </>
        )}
      </button>
    </form>
  );
}
