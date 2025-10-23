'use client';

import { Message } from '@/types';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChevronDownIcon } from 'lucide-react';
import {
  Item,
  ItemContent,
  ItemTitle,
  ItemMedia,
} from '@/components/ui/item';
import { NodeAuthRequest } from './NodeAuthRequest';
import { ParameterCollectionForm } from './ParameterCollectionForm';

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

  // Parse tool result (for UI components)
  let result: any = {};
  try {
    result = message.toolResult ? JSON.parse(message.toolResult) : {};

    // MCP tools return content array with text, need to parse that too
    if (result.content && Array.isArray(result.content) && result.content[0]?.text) {
      const innerResult = JSON.parse(result.content[0].text);
      if (innerResult.ui_component) {
        result = innerResult;
      }
    }
  } catch (e) {
    result = {};
  }

  // Check if this is a UI component from MCP tool result

  if (result.ui_component === 'NodeAuthRequest' && result.data) {
    return (
      <NodeAuthRequest
        nodeType={result.data.nodeType}
        nodeName={result.data.nodeName}
        requiredAuth={result.data.requiredAuth}
        reason={result.data.reason}
      />
    );
  }

  if (result.ui_component === 'ParameterCollectionForm' && result.data) {
    return (
      <ParameterCollectionForm
        title={result.data.title}
        description={result.data.description}
        fields={result.data.fields}
        onSubmit={(values) => {
          window.dispatchEvent(new CustomEvent('parameter-submitted', {
            detail: { values, messageId: message.id }
          }));
        }}
        submitLabel={result.data.submitLabel}
      />
    );
  }

  // Also check by tool name for MCP tools
  if (message.toolName?.includes('request_node_auth')) {
    // Parse from input if result doesn't have ui_component
    if (input.node_type && input.node_name) {
      return (
        <NodeAuthRequest
          nodeType={input.node_type}
          nodeName={input.node_name}
          requiredAuth={input.required_auth}
          reason={input.reason}
        />
      );
    }
  }

  if (message.toolName?.includes('request_parameters')) {
    // Parse from input if result doesn't have ui_component
    if (input.fields && Array.isArray(input.fields)) {
      return (
        <ParameterCollectionForm
          title={input.title || 'Additional Information Required'}
          description={input.description}
          fields={input.fields}
          onSubmit={(values) => {
            window.dispatchEvent(new CustomEvent('parameter-submitted', {
              detail: { values, messageId: message.id }
            }));
          }}
          submitLabel={input.submit_label}
        />
      );
    }
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

  // NodeAuthRequest - interactive auth request
  if (message.toolName === 'RequestNodeAuth' && input.node_type && input.node_name) {
    return (
      <NodeAuthRequest
        nodeType={input.node_type}
        nodeName={input.node_name}
        requiredAuth={input.required_auth}
        reason={input.reason}
      />
    );
  }

  // ParameterCollectionForm - collect params from user
  if (message.toolName === 'RequestParameters' && input.fields && Array.isArray(input.fields)) {
    return (
      <ParameterCollectionForm
        title={input.title || 'Additional Information Required'}
        description={input.description}
        fields={input.fields}
        onSubmit={(values) => {
          // Send collected values back to chat
          window.dispatchEvent(new CustomEvent('parameter-submitted', {
            detail: { values, messageId: message.id }
          }));
        }}
        submitLabel={input.submit_label}
      />
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

  // Hide UI-only MCP tools (they're already rendered above)
  if (message.toolName?.includes('request_node_auth') || message.toolName?.includes('request_parameters')) {
    return null;
  }

  // Default tool display for other tools
  return (
    <div className="mb-2">
      <Item variant="outline" size="sm">
        <ItemMedia>
          <div className="w-5 h-5 bg-primary/10 rounded flex items-center justify-center">
            <svg className="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Using {message.toolName}</ItemTitle>
          {message.toolInput && (
            <details open={isExpanded} onToggle={(e) => setIsExpanded((e.target as HTMLDetailsElement).open)} className="mt-1">
              <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground flex items-center gap-1">
                <ChevronDownIcon className="w-3 h-3 transition-transform" />
                View input parameters
              </summary>
              <pre className="mt-2 text-xs bg-muted p-2 rounded whitespace-pre-wrap break-words overflow-hidden">
                {message.toolInput}
              </pre>
            </details>
          )}
        </ItemContent>
      </Item>
    </div>
  );
}
