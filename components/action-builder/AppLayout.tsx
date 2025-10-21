'use client';

import { useEffect } from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { useStoreHydration } from '@/lib/action-builder/stores/useStoreHydration';
import SidebarSimple from '@/components/action-builder/SidebarSimple';
import MobileNav from '@/components/action-builder/MobileNav';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  useStoreHydration();

  const initWebSocket = useChatStore(state => state.initWebSocket);
  const isMobile = useChatStore(state => state.isMobile);
  const sidebarOpen = useChatStore(state => state.sidebarOpen);
  const setSidebarOpen = useChatStore(state => state.setSidebarOpen);
  const currentSession = useChatStore(state => state.currentSession);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);
  const projects = useChatStore(state => state.projects);
  const loadProjects = useChatStore(state => state.loadProjects);
  const setCurrentProject = useChatStore(state => state.setCurrentProject);

  // Initialize ONCE on mount - this layout persists across navigation
  useEffect(() => {
    const init = async () => {
      await initWebSocket();
      await loadProjects();
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-select flow-architect project if available
  useEffect(() => {
    if (projects.length > 0 && !useChatStore.getState().currentProject) {
      const flowArchitect = projects.find(p => p.name === 'flow-architect' || p.displayName === 'Action Builder');
      if (flowArchitect) {
        setCurrentProject(flowArchitect);
      }
    }
  }, [projects, setCurrentProject]);

  const handleSessionSelect = async (session: any) => {
    const loadMessages = useChatStore.getState().loadMessages;
    const currentProject = useChatStore.getState().currentProject;

    // Set as current session
    setCurrentSession(session);

    // Load messages for this session
    if (currentProject) {
      await loadMessages(session.id);
    }

    // Close mobile sidebar
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const handleNewSession = () => {
    const createNewSession = useChatStore.getState().createNewSession;
    createNewSession();

    // Close mobile sidebar
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className="fixed inset-0 flex bg-background">
      {/* Desktop Sidebar - PERSISTS across navigation */}
      {!isMobile && (
        <div className="w-80 flex-shrink-0 border-r border-border bg-card">
          <div className="h-full overflow-hidden">
            <SidebarSimple
              selectedSession={currentSession}
              onSessionSelect={handleSessionSelect}
              onNewSession={handleNewSession}
              onSessionDelete={() => {}}
              onShowSettings={() => {}}
              isMobile={false}
            />
          </div>
        </div>
      )}

      {/* Mobile Sidebar Overlay - PERSISTS across navigation */}
      {isMobile && (
        <div
          className={`fixed inset-0 z-50 flex transition-all duration-150 ease-out ${
            sidebarOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
          }`}
        >
          <button
            className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity duration-150 ease-out"
            onClick={(e) => {
              e.stopPropagation();
              setSidebarOpen(false);
            }}
            onTouchStart={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setSidebarOpen(false);
            }}
            aria-label="Close sidebar"
          />
          <div
            className={`relative w-[85vw] max-w-sm sm:w-80 bg-card border-r border-border transform transition-transform duration-150 ease-out ${
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            }`}
            style={{ height: 'calc(100vh - 80px)' }}
            onClick={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
          >
            <SidebarSimple
              selectedSession={currentSession}
              onSessionSelect={handleSessionSelect}
              onNewSession={handleNewSession}
              onSessionDelete={() => {}}
              onShowSettings={() => {}}
              isMobile={true}
            />
          </div>
        </div>
      )}

      {/* Main Content Area - CHANGES on navigation */}
      {children}

      {/* Mobile Bottom Navigation - PERSISTS across navigation */}
      {isMobile && <MobileNav />}
    </div>
  );
}
