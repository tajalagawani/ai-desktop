'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import type { ChatSession } from '@prisma/client';

interface SessionWithMetrics extends ChatSession {
  _count?: {
    messages: number;
  };
  metrics?: {
    totalTokens: number;
    totalCost: number;
    turnCount: number;
  } | null;
}

interface SessionItemProps {
  session: SessionWithMetrics;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (newTitle: string) => void;
  onArchive: () => void;
}

export function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
  onRename,
  onArchive,
}: SessionItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(session.title);
  const [showMenu, setShowMenu] = useState(false);

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== session.title) {
      onRename(editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setEditTitle(session.title);
      setIsEditing(false);
    }
  };

  return (
    <div
      className={`group relative rounded transition-colors border-l-2 ${
        isActive
          ? 'border-zinc-200 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-900'
          : 'border-transparent hover:border-zinc-200 hover:dark:border-zinc-700'
      }`}
    >
      <button
        onClick={onSelect}
        className="w-full text-left p-2 flex flex-col gap-1"
      >
        {/* Title */}
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleRename}
            onKeyDown={handleKeyDown}
            className="w-full px-2 py-1 text-xs text-zinc-700 dark:text-zinc-300 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded focus:outline-none focus:border-zinc-300 dark:focus:border-zinc-600"
            autoFocus
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <div className="text-xs text-zinc-700 dark:text-zinc-300 font-medium line-clamp-2">{session.title}</div>
        )}

        {/* Metadata */}
        <div className="flex items-center gap-2 text-[10px] text-zinc-600 dark:text-zinc-400">
          {/* Message count */}
          {session._count && (
            <span>{session._count.messages} msgs</span>
          )}

          {/* Separator */}
          {session._count && session.lastActivityAt && <span>•</span>}

          {/* Last activity */}
          {session.lastActivityAt && (
            <span>
              {formatDistanceToNow(new Date(session.lastActivityAt), { addSuffix: true })}
            </span>
          )}
        </div>

        {/* Cost/Tokens (if available) */}
        {session.metrics && (
          <div className="flex items-center gap-1 text-[10px] text-zinc-600 dark:text-zinc-400">
            <span className="bg-zinc-100 dark:bg-zinc-900 px-1.5 py-0.5 rounded inline-block">
              {session.metrics.totalTokens.toLocaleString()} tokens
            </span>
            <span className="bg-zinc-100 dark:bg-zinc-900 px-1.5 py-0.5 rounded inline-block">
              ${session.metrics.totalCost.toFixed(4)}
            </span>
          </div>
        )}
      </button>

      {/* Actions Menu */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-1 rounded text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>

        {showMenu && (
          <div className="absolute right-0 mt-1 w-40 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded shadow-lg z-10">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
                setShowMenu(false);
              }}
              className="w-full px-3 py-1.5 text-left text-xs text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors rounded-t"
            >
              Rename
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onArchive();
                setShowMenu(false);
              }}
              className="w-full px-3 py-1.5 text-left text-xs text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors"
            >
              Archive
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm('Delete this session? This cannot be undone.')) {
                  onDelete();
                }
                setShowMenu(false);
              }}
              className="w-full px-3 py-1.5 text-left text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors rounded-b"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
