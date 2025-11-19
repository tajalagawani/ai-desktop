'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import type { Message } from '@/lib/flow-builder/types/chat';

interface Todo {
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
  activeForm: string;
}

interface TodoListProps {
  message: Message;
}

interface ExpandableTodoItemProps {
  todo: Todo;
  idx: number;
}

// Expandable Todo Item Component - EXACT same structure as ExpandableToolItem
function ExpandableTodoItem({ todo, idx }: ExpandableTodoItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Status indicator - EXACT same as MCP tools
  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="text-green-600 dark:text-green-400">●</span>;
      case 'in_progress':
        return <span className="text-yellow-600 dark:text-yellow-400">⚠</span>;
      default:
        return <span className="text-zinc-400">○</span>;
    }
  };

  return (
    <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors w-full text-left"
      >
        <span className="text-zinc-400">⊢</span>
        <Badge variant="mcp">
          <span className="flex items-center gap-1.5">
            {getStatusIndicator(todo.status)}
            {todo.content}
          </span>
        </Badge>
      </button>

      {isExpanded && (
        <div className="mt-2 ml-4 space-y-1 text-xs text-zinc-600 dark:text-zinc-400">
          {/* Status */}
          <div className="flex items-center gap-2">
            <span className="font-medium">Status:</span>
            <span className="flex items-center gap-1">
              {getStatusIndicator(todo.status)}
              <span className="capitalize">{todo.status.replace('_', ' ')}</span>
            </span>
          </div>

          {/* Task Number */}
          <div className="flex items-center gap-2">
            <span className="font-medium">Task:</span>
            <Badge variant="tool">#{idx + 1}</Badge>
          </div>

          {/* Active Form */}
          {todo.activeForm && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Active Form:</span>
              <span className="text-[10px] bg-zinc-100 dark:bg-zinc-900 px-2 py-1 rounded inline-block">
                {todo.activeForm}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function TodoList({ message }: TodoListProps) {
  // Extract todos from message metadata
  const todoState = message.metadata?.todos as Todo[] | null;

  // Don't render if no todos
  if (!todoState || todoState.length === 0) {
    return null;
  }

  // Count completed/total
  const completedCount = todoState.filter(t => t.status === 'completed').length;
  const totalCount = todoState.length;

  return (
    <div className="flex flex-col gap-2">
      {/* Header with Badge - EXACT same as MCP Tool History header */}
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="tool">Workflow Progress</Badge>
        <span className="text-zinc-400">|</span>
        <span className="text-xs text-zinc-500 dark:text-zinc-400">
          {completedCount}/{totalCount} tasks
        </span>
        {completedCount === totalCount && (
          <>
            <span className="text-zinc-400">•</span>
            <Badge variant="success">Complete</Badge>
          </>
        )}
      </div>

      {/* Task items - EXACT same structure as MCP Tool History items */}
      <div className="space-y-1">
        {todoState.map((todo, index) => (
          <ExpandableTodoItem key={index} todo={todo} idx={index} />
        ))}
      </div>
    </div>
  );
}
