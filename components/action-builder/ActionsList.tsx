import { useState, useEffect } from 'react';
import { authenticatedFetch } from '@/lib/action-builder/api';

// TypeScript interfaces
interface ActionMetadata {
  name?: string;
  description?: string;
  tags?: string[];
  id?: string;
  sessionId?: string;
}

interface Action {
  name: string;
  type: string;
  metadata?: ActionMetadata;
}

interface ActionsListProps {
  currentSessionId?: string | null;
}

export default function ActionsList({ currentSessionId }: ActionsListProps) {
  const [actions, setActions] = useState<Action[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadActions();

    // Refresh actions list every 15 seconds to show newly created actions
    // Increased from 5s to reduce UI flashing
    const interval = setInterval(loadActions, 15000);
    return () => clearInterval(interval);
  }, []);

  async function loadActions() {
    setIsLoading(true);
    setError(null);
    try {
      // Try flow-architect specific endpoint first, fall back to general actions endpoint
      let res = await authenticatedFetch('/api/flow-architect/actions');

      if (!res.ok) {
        // Try general actions endpoint as fallback
        res = await authenticatedFetch('/api/actions');
      }

      if (!res.ok) {
        // If both fail, silently set empty actions (endpoint might not be implemented yet)
        setActions([]);
        return;
      }

      const data = await res.json();
      const newActions = data.actions || [];

      // Only update state if data has changed (prevents unnecessary re-renders)
      setActions(prevActions => {
        if (JSON.stringify(prevActions) === JSON.stringify(newActions)) {
          return prevActions; // Return same reference if no changes
        }
        return newActions;
      });
    } catch (err: any) {
      console.error('Error loading actions:', err);
      // Don't show error to user, just log it (endpoint might not be implemented yet)
      setActions([]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="actions-list border-t border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
          📁 Generated Actions
        </h3>
        <button
          onClick={loadActions}
          className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          title="Refresh"
        >
          🔄
        </button>
      </div>

      {isLoading && actions.length === 0 ? (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400 mx-auto mb-2"></div>
          <p className="text-xs">Loading...</p>
        </div>
      ) : error ? (
        <div className="text-center py-4 text-red-500 dark:text-red-400">
          <p className="text-xs">Error: {error}</p>
          <button
            onClick={loadActions}
            className="mt-2 text-xs px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            Retry
          </button>
        </div>
      ) : actions.length > 0 ? (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {actions
            .filter(action => {
              // Filter by current session if sessionId is provided
              if (!currentSessionId) return true; // Show all if no session
              const isObject = typeof action === 'object';
              const metadata = isObject ? action.metadata : null;

              // Show actions that:
              // 1. Match the current session
              // 2. Have the placeholder sessionId (newly created, not yet updated)
              // 3. Have no sessionId (very new or legacy)
              return metadata?.sessionId === currentSessionId ||
                     metadata?.sessionId === 'current-session-id-here' ||
                     !metadata?.sessionId;
            })
            .map(action => {
            // Handle both old string format and new object format
            const isObject = typeof action === 'object';
            const actionName = isObject ? action.name : action as any;
            const actionType = isObject ? action.type : 'file';
            const metadata = isObject ? action.metadata : null;

            return (
              <div
                key={actionName}
                className={`p-2 rounded transition-colors ${
                  actionType === 'folder'
                    ? 'bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-800'
                    : 'bg-gray-100 dark:bg-gray-800'
                }`}
                title={metadata?.description || `View ${actionName}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    {metadata ? (
                      <>
                        <div className="flex items-center gap-2">
                          <span className="text-xs">📦</span>
                          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">
                            {metadata.name}
                          </span>
                        </div>
                        {metadata.description && (
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                            {metadata.description}
                          </p>
                        )}
                        {metadata.tags && metadata.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {metadata.tags.slice(0, 3).map(tag => (
                              <span
                                key={tag}
                                className="text-xs px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                            {metadata.tags.length > 3 && (
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                +{metadata.tags.length - 3}
                              </span>
                            )}
                          </div>
                        )}
                        {metadata.id && (
                          <div className="mt-1.5 text-xs font-mono text-gray-500 dark:text-gray-500 truncate" title={`ID: ${metadata.id}`}>
                            ID: {metadata.id.substring(0, 8)}...
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="text-xs">📄</span>
                        <span className="text-xs font-mono text-gray-900 dark:text-gray-100 break-all">
                          {actionName}
                        </span>
                      </div>
                    )}
                  </div>
                  {actionType === 'folder' && (
                    <span className="text-xs text-purple-600 dark:text-purple-400 font-medium shrink-0">
                      v2
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-gray-500 dark:text-gray-400 py-2">
          No actions created yet. Start chatting to create your first action!
        </p>
      )}
    </div>
  );
}
