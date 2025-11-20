'use client';

import { useEffect, useState } from 'react';
import { SessionItem } from './SessionItem';
import type { ChatSession } from '@prisma/client';
import { apiFetch } from "@/lib/utils/api"

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

interface SessionListProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
}

export function SessionList({ currentSessionId, onSelectSession, onNewSession }: SessionListProps) {
  const [sessions, setSessions] = useState<SessionWithMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load sessions from API
  useEffect(() => {
    loadSessions();
  }, []);

  // Reload sessions when current session changes (new session created)
  useEffect(() => {
    if (currentSessionId) {
      loadSessions();
    }
  }, [currentSessionId]);

  async function loadSessions() {
    try {
      setLoading(true);
      setError(null);

      const response = await apiFetch('/api/flow-builder/sessions?userId=default-user&limit=50');
      if (!response.ok) throw new Error('Failed to fetch sessions');

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('[SessionList] Error loading sessions:', err);
      setError('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(sessionId: string) {
    try {
      const response = await fetch(`/api/flow-builder/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete session');

      // Remove from local state
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));

      // If deleted session was current, trigger new session
      if (sessionId === currentSessionId) {
        onNewSession();
      }
    } catch (err) {
      console.error('[SessionList] Error deleting session:', err);
    }
  }

  async function handleRename(sessionId: string, newTitle: string) {
    try {
      const response = await fetch(`/api/flow-builder/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle }),
      });

      if (!response.ok) throw new Error('Failed to rename session');

      // Update local state
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, title: newTitle } : s))
      );
    } catch (err) {
      console.error('[SessionList] Error renaming session:', err);
    }
  }

  async function handleArchive(sessionId: string) {
    try {
      const response = await fetch(`/api/flow-builder/sessions/${sessionId}/archive`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to archive session');

      // Remove from local state
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));

      // If archived session was current, trigger new session
      if (sessionId === currentSessionId) {
        onNewSession();
      }
    } catch (err) {
      console.error('[SessionList] Error archiving session:', err);
    }
  }

  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-16 bg-zinc-100 dark:bg-zinc-900 rounded animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 overflow-y-auto p-4">
        <div className="text-xs text-zinc-700 dark:text-zinc-300">{error}</div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {sessions.length === 0 ? (
        <div className="p-4 text-xs text-zinc-600 dark:text-zinc-400 text-center">
          No sessions yet. Start a new conversation!
        </div>
      ) : (
        <div className="space-y-1 p-2">
          {sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === currentSessionId}
              onSelect={() => onSelectSession(session.id)}
              onDelete={() => handleDelete(session.id)}
              onRename={(newTitle) => handleRename(session.id, newTitle)}
              onArchive={() => handleArchive(session.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
