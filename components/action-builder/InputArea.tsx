'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { Send } from 'lucide-react';

export default function InputArea() {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isConnected = useChatStore(state => state.isConnected);
  const isLoading = useChatStore(state => state.isLoading);
  const sendMessage = useChatStore(state => state.sendMessage);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || !isConnected || isLoading) return;

    // Send message
    sendMessage(trimmedInput);

    // Clear input
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleStopGeneration = () => {
    // TODO: Implement stop generation via WebSocket
    console.log('Stop generation requested');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex-shrink-0 border-t border-border bg-background p-4">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                !isConnected
                  ? 'Connecting to Action Builder...'
                  : isLoading
                  ? 'Action Builder is working...'
                  : 'Ask Action Builder to create an action...'
              }
              disabled={!isConnected || isLoading}
              rows={1}
              className="w-full resize-none rounded-xl border border-border bg-background px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed max-h-40 overflow-y-auto"
            />
            {!isConnected && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>

          <button
            type={isLoading ? "button" : "submit"}
            onClick={isLoading ? handleStopGeneration : undefined}
            disabled={!isConnected || (!isLoading && !input.trim())}
            className={`flex-shrink-0 h-12 w-12 rounded-xl flex items-center justify-center transition-colors ${
              isLoading
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : input.trim()
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <rect x="6" y="6" width="8" height="8" />
              </svg>
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Connection status */}
        {!isConnected && (
          <div className="mt-2 text-xs text-muted-foreground flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
            Connecting to backend...
          </div>
        )}
      </form>
    </div>
  );
}
