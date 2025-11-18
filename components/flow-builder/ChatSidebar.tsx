'use client';

import { useState } from 'react';
import { SessionList } from './SessionList';

interface ChatSidebarProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
}

export function ChatSidebar({ currentSessionId, onSelectSession, onNewSession }: ChatSidebarProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="w-12 border-r border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 flex items-center justify-center text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
        title="Open sidebar"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    );
  }

  return (
    <div className="w-80 border-r border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 flex flex-col">
      {/* Sidebar Header - TodoList style */}
      <div className="border-b border-zinc-200 dark:border-zinc-700 flex items-center justify-between px-4 py-3">
        <h2 className="text-xs text-zinc-700 dark:text-zinc-300 font-medium">Chat Sessions</h2>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1 text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors rounded"
          title="Close sidebar"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* New Session Button - TodoList button style */}
      <div className="p-3 border-b border-zinc-200 dark:border-zinc-700">
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-medium transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Session
        </button>
      </div>

      {/* Search Bar - TodoList style */}
      <div className="p-3 border-b border-zinc-200 dark:border-zinc-700">
        <div className="relative">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs text-zinc-700 dark:text-zinc-300 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded focus:outline-none focus:border-zinc-300 dark:focus:border-zinc-600"
          />
        </div>
      </div>

      {/* Session List */}
      <SessionList
        currentSessionId={currentSessionId}
        onSelectSession={onSelectSession}
        onNewSession={onNewSession}
      />

      {/* Footer with stats - TodoList style */}
      <div className="border-t border-zinc-200 dark:border-zinc-700 p-3">
        <div className="text-xs text-zinc-500 dark:text-zinc-400 space-y-1">
          <div className="flex items-center justify-between">
            <span>ACT Agent</span>
            <span>v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
