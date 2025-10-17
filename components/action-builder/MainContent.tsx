'use client';

import React, { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { MessageSquare, FileText, Terminal, GitBranch, ListTodo, Eye } from 'lucide-react';

export default function MainContent() {
  const activeTab = useChatStore(state => state.activeTab);
  const setActiveTab = useChatStore(state => state.setActiveTab);
  const isMobile = useChatStore(state => state.isMobile);
  const setIsMobile = useChatStore(state => state.setIsMobile);
  const isInputFocused = useChatStore(state => state.isInputFocused);
  const sidebarOpen = useChatStore(state => state.sidebarOpen);
  const setSidebarOpen = useChatStore(state => state.setSidebarOpen);
  const selectedProject = useChatStore(state => state.selectedProject);
  const selectedSession = useChatStore(state => state.currentSession);
  const tasksEnabled = useChatStore(state => state.tasksEnabled);
  const isTaskMasterInstalled = useChatStore(state => state.isTaskMasterInstalled);

  // Check mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, [setIsMobile]);

  // Only show tasks tab if TaskMaster is installed and enabled
  const shouldShowTasksTab = tasksEnabled && isTaskMasterInstalled;

  // Switch away from tasks tab when tasks are disabled or TaskMaster is not installed
  useEffect(() => {
    if (!shouldShowTasksTab && activeTab === 'tasks') {
      setActiveTab('chat');
    }
  }, [shouldShowTasksTab, activeTab, setActiveTab]);

  // Tabs configuration
  const tabs = [
    { id: 'chat' as const, label: 'Chat', icon: MessageSquare, show: true },
    { id: 'files' as const, label: 'Files', icon: FileText, show: !!selectedProject },
    { id: 'shell' as const, label: 'Shell', icon: Terminal, show: !!selectedProject },
    { id: 'git' as const, label: 'Git', icon: GitBranch, show: !!selectedProject },
    { id: 'tasks' as const, label: 'Tasks', icon: ListTodo, show: shouldShowTasksTab },
    { id: 'preview' as const, label: 'Preview', icon: Eye, show: !!selectedProject },
  ].filter(tab => tab.show);

  return (
    <div className={`flex-1 flex flex-col min-w-0 ${isMobile && !isInputFocused ? 'pb-16' : ''}`}>
      {/* Desktop Tabs */}
      {!isMobile && tabs.length > 1 && (
        <div className="flex-shrink-0 border-b border-border bg-background">
          <div className="flex items-center px-4 gap-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all
                    ${isActive
                      ? 'text-primary border-primary'
                      : 'text-muted-foreground border-transparent hover:text-foreground hover:border-border'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'files' && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <h3 className="text-lg font-semibold mb-2">File Browser</h3>
              <p className="text-sm">Coming soon - Browse and edit project files</p>
            </div>
          </div>
        )}
        {activeTab === 'shell' && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <Terminal className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <h3 className="text-lg font-semibold mb-2">Terminal</h3>
              <p className="text-sm">Coming soon - Interactive terminal shell</p>
            </div>
          </div>
        )}
        {activeTab === 'git' && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <GitBranch className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <h3 className="text-lg font-semibold mb-2">Git Panel</h3>
              <p className="text-sm">Coming soon - Git operations and history</p>
            </div>
          </div>
        )}
        {activeTab === 'tasks' && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <ListTodo className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <h3 className="text-lg font-semibold mb-2">Task Management</h3>
              <p className="text-sm">Coming soon - TaskMaster integration</p>
            </div>
          </div>
        )}
        {activeTab === 'preview' && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <Eye className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <h3 className="text-lg font-semibold mb-2">Preview</h3>
              <p className="text-sm">Coming soon - Preview web apps and content</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
