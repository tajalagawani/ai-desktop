'use client';

import React from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { MessageSquare, FileText, Terminal, GitBranch, ListTodo } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function MobileNav() {
  const activeTab = useChatStore(state => state.activeTab);
  const setActiveTab = useChatStore(state => state.setActiveTab);
  const isInputFocused = useChatStore(state => state.isInputFocused);
  const selectedProject = useChatStore(state => state.selectedProject);
  const tasksEnabled = useChatStore(state => state.tasksEnabled);
  const isTaskMasterInstalled = useChatStore(state => state.isTaskMasterInstalled);

  const shouldShowTasksTab = tasksEnabled && isTaskMasterInstalled;

  // Mobile nav items
  const navItems = [
    { id: 'chat' as const, label: 'Chat', icon: MessageSquare, show: true },
    { id: 'files' as const, label: 'Files', icon: FileText, show: !!selectedProject },
    { id: 'shell' as const, label: 'Shell', icon: Terminal, show: !!selectedProject },
    { id: 'git' as const, label: 'Git', icon: GitBranch, show: !!selectedProject },
    { id: 'tasks' as const, label: 'Tasks', icon: ListTodo, show: shouldShowTasksTab },
  ].filter(item => item.show);

  // Hide mobile nav when input is focused
  if (isInputFocused) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-background md:hidden">
      <div className="flex items-center justify-around h-16 px-2 safe-area-bottom">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                'flex flex-col items-center justify-center flex-1 h-full gap-1 text-xs font-medium transition-colors',
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground'
              )}
            >
              <Icon className={cn('w-5 h-5', isActive && 'text-primary')} />
              <span className={cn(isActive && 'font-semibold')}>{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
