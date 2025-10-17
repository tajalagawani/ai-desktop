'use client';

import ChatInterface from '@/components/action-builder/ChatInterface';
import SidebarSimple from '@/components/action-builder/SidebarSimple';
import { useEffect } from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';

export function ActionBuilder() {
  const initWebSocket = useChatStore(state => state.initWebSocket);
  const loadProjects = useChatStore(state => state.loadProjects);
  const isConnected = useChatStore(state => state.isConnected);
  const sessions = useChatStore(state => state.sessions);
  const currentSession = useChatStore(state => state.currentSession);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);

  // Initialize WebSocket and load projects on mount
  useEffect(() => {
    console.log('[Action Builder] ========================================');
    console.log('[Action Builder] Component mounted');
    console.log('[Action Builder] Initializing WebSocket connection...');
    console.log('[Action Builder] ========================================');

    const init = async () => {
      try {
        console.log('[Action Builder] Calling initWebSocket()...');
        await initWebSocket();
        console.log('[Action Builder] ✅ WebSocket initialized');

        console.log('[Action Builder] Loading projects...');
        await loadProjects();
        console.log('[Action Builder] ✅ Projects loaded');
      } catch (error) {
        console.error('[Action Builder] ❌ Initialization error:', error);
      }
    };

    init();
  }, [initWebSocket, loadProjects]);

  // Log sessions changes
  useEffect(() => {
    console.log('[Action Builder] Sessions updated:', sessions.length);
  }, [sessions]);

  // Log connection status changes
  useEffect(() => {
    console.log('[Action Builder] Connection status:', isConnected ? '✅ Connected' : '❌ Disconnected');
  }, [isConnected]);

  const handleSessionSelect = async (session: any) => {
    console.log('[Action Builder] ========================================');
    console.log('[Action Builder] Session selected:', session.id);
    console.log('[Action Builder] Session summary:', session.summary);
    console.log('[Action Builder] ========================================');

    setCurrentSession(session);

    // Load messages for this session
    const currentProject = useChatStore.getState().currentProject;
    if (currentProject) {
      console.log('[Action Builder] Loading messages for session:', session.id);
      try {
        const response = await fetch(`/api/projects/${currentProject.name}/sessions/${session.id}/messages`);
        if (response.ok) {
          const data = await response.json();
          console.log('[Action Builder] Loaded', data.messages?.length || 0, 'messages');

          // Transform and set messages
          const loadMessages = useChatStore.getState().loadSessionMessages;
          loadMessages(currentProject.name, session.id);
        } else {
          console.error('[Action Builder] Failed to load messages:', response.status);
        }
      } catch (error) {
        console.error('[Action Builder] Error loading messages:', error);
      }
    }
  };

  const handleNewSession = () => {
    console.log('[Action Builder] New session requested');
    setCurrentSession(null);
  };

  return (
    <div className="w-full h-full flex bg-background">
      {/* Sidebar - 25% width */}
      <div className="w-1/4 min-w-[250px] max-w-[350px] border-r border-border overflow-hidden">
        <SidebarSimple
          selectedSession={currentSession}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          onSessionDelete={() => {}}
          onShowSettings={() => {}}
          isMobile={false}
        />
      </div>

      {/* Chat Interface - 75% width */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
