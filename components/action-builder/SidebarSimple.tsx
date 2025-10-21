import React, { useState, useEffect, memo } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Plus, MessageSquare, Clock, ChevronDown, Trash2, Search, X, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import ClaudeLogo from '@/components/action-builder/ClaudeLogo';
import { api } from '@/lib/action-builder/api';
import CatalogViewer from '@/components/action-builder/CatalogViewer';
import ActionsList from '@/components/action-builder/ActionsList';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { TOPICS } from '@/components/action-builder/TopicSelector';

interface Session {
  id: string;
  summary?: string;
  lastActivity: string;
  messageCount?: number;
  topic?: {
    id: string;
    name: string;
    context: string;
  };
}

interface Project {
  name: string;
  displayName?: string;
  fullPath?: string;
}

interface SessionsResponse {
  sessions: Session[];
  hasMore: boolean;
}

interface SidebarSimpleProps {
  selectedSession: Session | null;
  onSessionSelect: (session: Session) => void;
  onNewSession: (project: { name: string }) => void;
  onSessionDelete?: (projectName: string, sessionId: string) => void;
  onShowSettings: () => void;
  updateAvailable?: boolean;
  onShowVersionModal?: () => void;
  isMobile?: boolean;
}

const formatTimeAgo = (dateString: string, currentTime: Date): string => {
  const date = new Date(dateString);
  const now = currentTime;

  if (isNaN(date.getTime())) return 'Unknown';

  const diffInMs = now.getTime() - date.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInSeconds < 60) return 'Just now';
  if (diffInMinutes === 1) return '1 min ago';
  if (diffInMinutes < 60) return `${diffInMinutes} mins ago`;
  if (diffInHours === 1) return '1 hour ago';
  if (diffInHours < 24) return `${diffInHours} hours ago`;
  if (diffInDays === 1) return '1 day ago';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  return date.toLocaleDateString();
};

function SidebarSimple({
  selectedSession,
  onSessionSelect,
  onNewSession,
  onSessionDelete,
  onShowSettings,
  updateAvailable,
  onShowVersionModal,
  isMobile
}: SidebarSimpleProps) {
  const sessions = useChatStore(state => state.sessions);
  const currentProject = useChatStore(state => state.currentProject);
  const loadSessions = useChatStore(state => state.loadSessions);

  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchFilter, setSearchFilter] = useState('');

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  // Load sessions when project is available
  useEffect(() => {
    if (currentProject && sessions.length === 0) {
      loadSessions();
    }
  }, [currentProject, sessions.length, loadSessions]);

  const deleteSession = async (sessionId: string) => {
    if (!currentProject) return;
    if (!confirm('Delete this session?')) return;

    try {
      await api.deleteSession(currentProject.name, sessionId);
      if (onSessionDelete) {
        onSessionDelete(currentProject.name, sessionId);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
      alert('Failed to delete session');
    }
  };

  // Filter sessions
  const filteredSessions = sessions.filter(session => {
    if (!searchFilter.trim()) return true;
    const searchLower = searchFilter.toLowerCase();
    const sessionName = (session.summary || 'New Session').toLowerCase();
    return sessionName.includes(searchLower);
  });

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-border/60">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl flex items-center justify-center border border-primary/10">
              <MessageSquare className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-base font-medium text-foreground">Action Builder</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Define executable actions</p>
            </div>
          </div>
          <button
            onClick={onShowSettings}
            className="p-2 hover:bg-muted/70 rounded-lg transition-colors"
          >
            <Settings className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        {/* New Session Button - not full width */}
        <button
          onClick={() => currentProject && onNewSession({ name: currentProject.name })}
          disabled={!currentProject}
          className="w-full h-10 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-primary-foreground rounded-lg flex items-center justify-center gap-2 font-medium text-sm transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>

        {/* Search */}
        <div className="mt-3 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            type="text"
            placeholder="Search sessions..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="pl-9 pr-8 h-9 text-sm"
          />
          {searchFilter && (
            <button
              onClick={() => setSearchFilter('')}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 hover:bg-muted rounded transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Sessions List */}
      <ScrollArea className="flex-1">
        <div className="px-3 py-2 space-y-1.5">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-16 px-4">
              <MessageSquare className="w-14 h-14 text-muted-foreground mx-auto mb-4 opacity-40" />
              <h3 className="text-sm font-semibold text-foreground mb-2">
                {searchFilter ? 'No matching sessions' : 'No sessions yet'}
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {searchFilter ? 'Try adjusting your search' : 'Start chatting to create your first session'}
              </p>
            </div>
          ) : (
            filteredSessions.map((session) => {
              const sessionDate = new Date(session.lastActivity);
              const diffInMinutes = Math.floor((currentTime.getTime() - sessionDate.getTime()) / (1000 * 60));
              const isActive = diffInMinutes < 10;
              const messageCount = session.messageCount || 0;

              // Show topic icon + name if no messages yet, otherwise show summary
              let sessionName = session.summary || 'New Session';
              if (session.topic && messageCount === 0) {
                const topicInfo = TOPICS.find(t => t.id === session.topic?.id);
                sessionName = topicInfo ? `${topicInfo.icon} ${topicInfo.name}` : session.topic.name;
              }

              const isSelected = selectedSession?.id === session.id;

              return (
                <div key={session.id} className="relative group">
                  {/* Active indicator - bigger and more prominent */}
                  {isActive && (
                    <div className="absolute -left-1 top-1/2 transform -translate-y-1/2 z-10">
                      <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
                    </div>
                  )}

                  <button
                    className={cn(
                      "w-full text-left rounded-xl px-4 py-3 transition-all duration-200 relative block group",
                      isSelected
                        ? "bg-primary/10 border border-primary/20"
                        : "hover:bg-muted/50 border border-transparent"
                    )}
                    onClick={() => {
                      onSessionSelect(session);
                    }}
                  >
                    <div className="flex items-start min-w-0 w-full pr-8">
                      <div className="flex-1 min-w-0">
                        {/* Session name - 2 lines with ellipsis */}
                        <div className={cn(
                          "text-sm font-medium leading-relaxed mb-2 line-clamp-2",
                          isSelected ? "text-primary" : "text-foreground"
                        )}>
                          {sessionName}
                        </div>

                        {/* Time only - clean and simple */}
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(session.lastActivity, currentTime)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Delete button - positioned absolutely, shows on hover */}
                  <div className="absolute top-1/2 right-2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      className="h-8 w-8 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center justify-center transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                      title="Delete session"
                    >
                      <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </ScrollArea>

      {/* Actions & Catalog - with visual separation */}
      <div className="flex-shrink-0 border-t border-border/60 mt-auto">
        <ActionsList currentSessionId={selectedSession?.id} />
        <CatalogViewer />
      </div>

      {/* Version Update */}
      {updateAvailable && (
        <div className="px-3 py-3 border-t border-border/60 flex-shrink-0">
          <button
            onClick={onShowVersionModal}
            className="w-full p-3 text-left hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg transition-colors flex items-start gap-3"
          >
            <div className="relative flex-shrink-0">
              <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-blue-600 dark:text-blue-400">Update Available</div>
              <div className="text-xs text-muted-foreground mt-0.5">Click to view details</div>
            </div>
          </button>
        </div>
      )}
    </div>
  );
}

export default SidebarSimple;
