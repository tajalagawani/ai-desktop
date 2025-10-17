'use client';

import { useState, useEffect } from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { MessageSquare, Network, Zap, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EnhancedSidebarProps {
  isMobile: boolean;
}

export default function EnhancedSidebar({ isMobile }: EnhancedSidebarProps) {
  const sidebarView = useChatStore(state => state.sidebarView);
  const setSidebarView = useChatStore(state => state.setSidebarView);
  const sessions = useChatStore(state => state.sessions);
  const flows = useChatStore(state => state.flows);
  const currentSession = useChatStore(state => state.currentSession);
  const selectedFlow = useChatStore(state => state.selectedFlow);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);
  const setSelectedFlow = useChatStore(state => state.setSelectedFlow);
  const selectFlowAndLoadSession = useChatStore(state => state.selectFlowAndLoadSession);
  const loadFlows = useChatStore(state => state.loadFlows);
  const loadSessionMessages = useChatStore(state => state.loadSessionMessages);
  const currentProject = useChatStore(state => state.currentProject);
  const isLoadingFlows = useChatStore(state => state.isLoadingFlows);

  // Load flows when sidebar switches to flows view
  useEffect(() => {
    if (sidebarView === 'flows') {
      loadFlows();
    }
  }, [sidebarView, loadFlows]);

  // Load flows when there's a current session (for auto-selecting linked flows)
  useEffect(() => {
    if (currentSession && flows.length === 0) {
      console.log('[Sidebar] Loading flows for session:', currentSession.id);
      loadFlows(true); // Silent load
    }
  }, [currentSession, flows.length, loadFlows]);

  // Auto-refresh flows status every 3 seconds when on flows view
  useEffect(() => {
    if (sidebarView !== 'flows') return;

    // Initial load (show loading state)
    loadFlows(false);

    // Set up polling interval (silent refreshes)
    const intervalId = setInterval(() => {
      loadFlows(true); // Silent refresh to prevent flashing
    }, 3000); // Refresh every 3 seconds

    // Cleanup on unmount or view change
    return () => clearInterval(intervalId);
  }, [sidebarView, loadFlows]);

  // Auto-select flow when flows are loaded and current session has a linked flow
  useEffect(() => {
    if (!currentSession || flows.length === 0) return;

    // Find flow linked to current session
    const linkedFlow = flows.find(f => f.metadata?.sessionId === currentSession.id);

    // Only update if different from current selection
    if (linkedFlow && selectedFlow?.name !== linkedFlow.name) {
      console.log('[Sidebar] Auto-selecting linked flow:', linkedFlow.name);
      setSelectedFlow(linkedFlow);
    } else if (!linkedFlow && selectedFlow) {
      // Clear selection if no linked flow exists
      console.log('[Sidebar] Clearing flow selection - no linked flow found');
      setSelectedFlow(null);
    }
  }, [currentSession, flows, selectedFlow, setSelectedFlow]);

  const handleSessionSelect = async (session: any) => {
    setCurrentSession(session);

    // Load messages for this session
    if (currentProject) {
      try {
        await loadSessionMessages(currentProject.name, session.id);
      } catch (error) {
        console.error('[Sidebar] Error loading messages:', error);
      }
    }

    // Load flows if not already loaded (useEffect will handle flow selection)
    if (flows.length === 0) {
      await loadFlows(false);
    }
  };

  const handleFlowSelect = async (flow: any) => {
    await selectFlowAndLoadSession(flow);
  };

  const handleNewSession = () => {
    setCurrentSession(null);
  };

  return (
    <div className="h-full flex flex-col bg-background border-r border-border">
      {/* Tabs Header */}
      <div className="flex-shrink-0 border-b border-border">
        <div className="flex">
          <button
            onClick={() => setSidebarView('chats')}
            className={cn(
              "flex-1 px-4 py-3 text-sm font-medium transition-colors relative",
              sidebarView === 'chats'
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
            )}
          >
            <div className="flex items-center justify-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span>Chats</span>
            </div>
            {sidebarView === 'chats' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>

          <button
            onClick={() => setSidebarView('flows')}
            className={cn(
              "flex-1 px-4 py-3 text-sm font-medium transition-colors relative",
              sidebarView === 'flows'
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
            )}
          >
            <div className="flex items-center justify-center gap-2">
              <Zap className="h-4 w-4" />
              <span>Flows</span>
            </div>
            {sidebarView === 'flows' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {sidebarView === 'chats' ? (
          /* Chats View */
          <div className="p-3 space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase">Sessions</h3>
              <button
                onClick={handleNewSession}
                className="text-xs text-primary hover:underline"
              >
                + New
              </button>
            </div>

            {sessions.length === 0 ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No sessions yet
              </div>
            ) : (
              sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => handleSessionSelect(session)}
                  className={cn(
                    "w-full text-left px-3 py-2 rounded-lg transition-colors",
                    currentSession?.id === session.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  )}
                >
                  <div className="text-sm font-medium truncate">
                    {session.summary || 'New Session'}
                  </div>
                  <div className="text-xs opacity-70 mt-0.5">
                    {session.messageCount || 0} messages
                  </div>
                </button>
              ))
            )}
          </div>
        ) : (
          /* Flows View */
          <div className="p-3 space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase">
                Deployed Flows
              </h3>
              {flows.length > 0 && (
                <span className="text-xs text-muted-foreground">
                  {flows.length}
                </span>
              )}
            </div>

            {isLoadingFlows ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                Loading flows...
              </div>
            ) : flows.length === 0 ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No flows deployed yet
              </div>
            ) : (
              flows.map((flow) => (
                <button
                  key={flow.name}
                  onClick={() => handleFlowSelect(flow)}
                  className={cn(
                    "w-full text-left px-3 py-2.5 rounded-lg transition-colors border",
                    selectedFlow?.name === flow.name
                      ? "bg-primary text-primary-foreground border-primary"
                      : "hover:bg-muted border-transparent"
                  )}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-shrink-0 mt-0.5">
                      {flow.mode === 'agent' ? (
                        <Network className="h-4 w-4" />
                      ) : (
                        <Zap className="h-4 w-4" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {flow.agent_name || flow.name}
                      </div>
                      {flow.description && (
                        <div className="text-xs opacity-70 mt-0.5 line-clamp-2">
                          {flow.description}
                        </div>
                      )}
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs opacity-70">
                          Port {flow.port}
                        </span>
                        {flow.container?.running ? (
                          flow.health?.status === 'healthy' ? (
                            <span className="flex items-center gap-1 text-xs text-green-500">
                              <Circle className="h-2 w-2 fill-current" />
                              Running
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-xs text-red-500">
                              <Circle className="h-2 w-2 fill-current" />
                              Unhealthy
                            </span>
                          )
                        ) : (
                          <span className="flex items-center gap-1 text-xs opacity-50">
                            <Circle className="h-2 w-2 fill-current" />
                            Stopped
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
