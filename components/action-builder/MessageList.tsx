'use client';

import { Message } from '@/types';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { useEffect, useRef, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Components } from 'react-markdown';
import LoadingSkeleton from './LoadingSkeleton';
import ToolDisplay from './ToolDisplay';

function MessageList() {
  const messages = useChatStore(state => state.messages);
  const isDevMode = useChatStore(state => state.isDevMode);
  const autoScrollToBottom = useChatStore(state => state.autoScrollToBottom);
  const isDarkMode = useChatStore(state => state.isDarkMode);
  const isLoading = useChatStore(state => state.isLoading);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debug logging
  useEffect(() => {
    console.log('💬 MessageList render:', {
      messagesCount: messages.length,
      isDevMode,
      firstMessage: messages[0],
      lastMessage: messages[messages.length - 1]
    });
  }, [messages, isDevMode]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScrollToBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScrollToBottom]);

  // Filter messages - always hide catalog content in both modes
  const visibleMessages = messages.filter(msg => {
    // Always show user messages and errors
    if (msg.type === 'user') return true;
    if (msg.type === 'error') return true;

    // For assistant text messages, check if content contains catalog/technical data
    if (msg.type === 'assistant' && msg.content) {
      const content = msg.content.toLowerCase();

      // ALWAYS hide messages that are primarily catalog/service definitions (in both modes)
      if (
        content.includes('"type":"service"') ||
        content.includes('"type":"tool"') ||
        (content.includes('"category":') && content.includes('"parameters":')) ||
        content.includes('requires_service') ||
        (content.includes('catalog') && content.includes('parameters')) ||
        (content.startsWith('{"') && content.includes('"name":') && content.includes('"description":') && content.length > 500) ||
        (content.includes('[{') && content.includes('"type":') && content.includes('"name":') && content.length > 1000)
      ) {
        return false;
      }

      // ALWAYS hide Read/Write tool results
      if (msg.toolName === 'Read' || msg.toolName === 'Write') {
        return false;
      }

      // ALWAYS hide catalog file operations
      if (msg.toolInput) {
        const input = String(msg.toolInput);
        if (
          input.includes('/catalogs/') ||
          input.includes('-catalog.json')
        ) {
          return false;
        }
      }

      // In normal mode, hide .act file operations (Edit/Write)
      // In dev mode, show them with diffs
      if (!isDevMode && msg.toolInput) {
        const input = String(msg.toolInput);
        if (input.includes('/actions/') && input.includes('.act')) {
          return false;
        }
      }

      // If not catalog content, show in both modes if not a tool use
      if (!msg.isToolUse) {
        return true;
      }
    }

    // In dev mode, show tool usage (but not catalog content which is already filtered above)
    if (isDevMode && msg.isToolUse) {
      return true;
    }

    // In normal mode, hide all remaining tool usage
    return false;
  });

  console.log('👁️ Visible messages after filter:', {
    total: messages.length,
    visible: visibleMessages.length,
    filtered: messages.length - visibleMessages.length
  });

  // Show loading skeleton while fetching initial messages
  if (isLoading && visibleMessages.length === 0) {
    return <LoadingSkeleton />;
  }

  if (visibleMessages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 bg-muted rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">Start a Conversation</h3>
          <p className="text-sm">
            Ask Action Builder to create executable actions for your tasks.
            Every request becomes a deterministic, traceable action.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {visibleMessages.map((msg, index) => {
        // Detect if this message contains an action file reference
        let actionFilename = null;
        if (msg.type === 'assistant' && msg.content) {
          // Try folder pattern first: actions/folder-name/ or actions/folder-name/action.act
          const folderMatch = msg.content.match(/actions?\/([a-z0-9-_]+)\//i);
          if (folderMatch) {
            actionFilename = folderMatch[1]; // Just the folder name
          } else {
            // Fall back to legacy file pattern: actions/filename.act
            const fileMatch = msg.content.match(/actions?\/([a-z0-9-_]+\.act)/i);
            if (fileMatch) {
              actionFilename = fileMatch[1]; // Filename with .act extension
            }
          }
        }

        return (
          <div key={`${msg.id}-${index}`}>
            <MessageBubble message={msg} />

            {/* Show action banner in normal mode only */}
            {actionFilename && !isDevMode && (
              <div className="mt-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xl">✓</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900 dark:text-green-100 text-lg mb-1">
                      Action Created Successfully
                    </h3>
                    <p className="text-sm text-green-700 dark:text-green-300 mb-2">
                      Your action is ready to execute.
                    </p>
                    <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400">
                      <span className="font-mono bg-green-100 dark:bg-green-900/40 px-2 py-1 rounded">
                        {actionFilename}
                      </span>
                      <span>•</span>
                      <span>📁 actions/{actionFilename}/</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Thinking indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="flex items-center gap-2 text-muted-foreground">
            <div className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

const MessageBubble = memo(function MessageBubble({ message }: { message: Message }) {
  const isDarkMode = useChatStore(state => state.isDarkMode);

  // Custom markdown components with syntax highlighting
  const markdownComponents: Components = {
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';

      return !inline && language ? (
        <SyntaxHighlighter
          style={isDarkMode ? oneDark : oneLight}
          language={language}
          PreTag="div"
          className="rounded-md my-2"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-3">
          <div className="text-sm whitespace-pre-wrap break-words">{message.content}</div>
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="flex justify-start">
        <div className="max-w-[80%] bg-destructive/10 border border-destructive/20 rounded-2xl rounded-tl-sm px-4 py-3">
          <div className="flex items-start gap-2">
            <svg
              className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="text-sm text-destructive whitespace-pre-wrap break-words">{message.content}</div>
          </div>
        </div>
      </div>
    );
  }

  if (message.isToolUse) {
    return (
      <div className="flex justify-start">
        <div className="max-w-[90%]">
          <ToolDisplay message={message} autoExpandTools={true} />
        </div>
      </div>
    );
  }

  // Assistant message with enhanced markdown
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] bg-muted rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="prose prose-sm dark:prose-invert max-w-none prose-pre:p-0 prose-pre:bg-transparent">
          <ReactMarkdown components={markdownComponents}>
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
});

export default memo(MessageList);
