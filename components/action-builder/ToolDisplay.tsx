'use client';

import { Message } from '@/types';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface ToolDisplayProps {
  message: Message;
  autoExpandTools?: boolean;
  showRawParameters?: boolean;
}

// Create diff lines for displaying code changes
function createDiff(oldStr: string, newStr: string) {
  const oldLines = oldStr.split('\n');
  const newLines = newStr.split('\n');
  const diff: { type: 'removed' | 'added'; content: string }[] = [];

  // Simple diff - mark all old as removed, all new as added
  oldLines.forEach(line => {
    diff.push({ type: 'removed', content: line });
  });
  newLines.forEach(line => {
    diff.push({ type: 'added', content: line });
  });

  return diff;
}

export default function ToolDisplay({ message, autoExpandTools = false, showRawParameters = false }: ToolDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(autoExpandTools);

  if (!message.isToolUse || !message.toolName) {
    return null;
  }

  // Parse tool input
  let input: any = {};
  try {
    input = message.toolInput ? JSON.parse(message.toolInput) : {};
  } catch (e) {
    input = {};
  }

  // Read tool - hidden (no display)
  if (message.toolName === 'Read') {
    return null;
  }

  // Write tool - show file creation with diff
  if (message.toolName === 'Write' && input.file_path && input.content !== undefined) {
    return (
      <div className="mb-2">
        <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <div className="flex items-center justify-between px-3 py-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <span className="text-xs font-mono text-gray-700 dark:text-gray-300 truncate">
              {input.file_path}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
              New File
            </span>
          </div>
          <div className="text-xs font-mono max-h-96 overflow-y-auto overscroll-contain">
            {createDiff('', input.content).map((diffLine, i) => (
              <div key={i} className="flex">
                <span className={`w-8 text-center border-r flex-shrink-0 ${
                  diffLine.type === 'removed'
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800'
                    : 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-800'
                }`}>
                  {diffLine.type === 'removed' ? '-' : '+'}
                </span>
                <span className={`px-2 py-0.5 flex-1 whitespace-pre-wrap ${
                  diffLine.type === 'removed'
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                    : 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                }`}>
                  {diffLine.content}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // TodoWrite - show formatted todo list
  if (message.toolName === 'TodoWrite' && input.todos && Array.isArray(input.todos)) {
    return (
      <div className="bg-blue-50 dark:bg-blue-900/20 border-l-2 border-blue-300 dark:border-blue-600 pl-3 py-2 mb-2">
        <div className="text-sm text-blue-700 dark:text-blue-300 mb-2 font-medium">
          📝 Updated todo list
        </div>
        <div className="space-y-1">
          {input.todos.map((todo: any, idx: number) => (
            <div key={idx} className="flex items-start gap-2 text-sm">
              <span className={`${
                todo.status === 'completed' ? 'text-green-600 dark:text-green-400' :
                todo.status === 'in_progress' ? 'text-blue-600 dark:text-blue-400' :
                'text-gray-500 dark:text-gray-400'
              }`}>
                {todo.status === 'completed' ? '✓' :
                 todo.status === 'in_progress' ? '⋯' : '○'}
              </span>
              <span className={`flex-1 ${
                todo.status === 'completed' ? 'line-through text-gray-500 dark:text-gray-400' :
                'text-gray-700 dark:text-gray-300'
              }`}>
                {todo.content}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // TodoRead - simple indicator
  if (message.toolName === 'TodoRead') {
    return (
      <div className="bg-blue-50 dark:bg-blue-900/20 border-l-2 border-blue-300 dark:border-blue-600 pl-3 py-1 mb-2 text-sm text-blue-700 dark:text-blue-300">
        📋 Read todo list
      </div>
    );
  }

  // Bash tool - simple green command text
  if (message.toolName === 'Bash') {
    return (
      <div className="text-sm font-mono text-green-600 dark:text-green-400 py-1">
        $ {input.command}
      </div>
    );
  }

  // Edit tool - show diff
  if (message.toolName === 'Edit' && input.file_path && input.old_string && input.new_string) {
    return (
      <div className="mb-2">
        <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <div className="flex items-center justify-between px-3 py-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <span className="text-xs font-mono text-gray-700 dark:text-gray-300 truncate">
              {input.file_path}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Diff
            </span>
          </div>
          <div className="text-xs font-mono max-h-96 overflow-y-auto overscroll-contain">
            {createDiff(input.old_string, input.new_string).map((diffLine, i) => (
              <div key={i} className="flex">
                <span className={`w-8 text-center border-r flex-shrink-0 ${
                  diffLine.type === 'removed'
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800'
                    : 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-800'
                }`}>
                  {diffLine.type === 'removed' ? '-' : '+'}
                </span>
                <span className={`px-2 py-0.5 flex-1 whitespace-pre-wrap ${
                  diffLine.type === 'removed'
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                    : 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                }`}>
                  {diffLine.content}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Default tool display for other tools
  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-2">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 bg-blue-600 rounded flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span className="font-medium text-blue-900 dark:text-blue-100">
            Using {message.toolName}
          </span>
        </div>
      </div>

      {message.toolInput && (
        <details open={isExpanded} onToggle={(e) => setIsExpanded((e.target as HTMLDetailsElement).open)}>
          <summary className="text-sm text-blue-700 dark:text-blue-300 cursor-pointer hover:text-blue-800 dark:hover:text-blue-200 flex items-center gap-2">
            <svg className="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            View input parameters
          </summary>
          <pre className="mt-2 text-xs bg-blue-100 dark:bg-blue-800/30 p-2 rounded whitespace-pre-wrap break-words overflow-hidden text-blue-900 dark:text-blue-100">
            {message.toolInput}
          </pre>
        </details>
      )}
    </div>
  );
}
