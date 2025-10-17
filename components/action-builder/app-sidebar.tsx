'use client';

import { useRouter } from 'next/navigation';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar';
import { Bot, MessageSquare, Plus, Settings, Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function AppSidebar() {
  const router = useRouter();
  const sessions = useChatStore(state => state.sessions);
  const currentSession = useChatStore(state => state.currentSession);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);
  const isDarkMode = useChatStore(state => state.isDarkMode);
  const toggleDarkMode = useChatStore(state => state.toggleDarkMode);

  const handleNewSession = () => {
    setCurrentSession(null);
    router.push('/');
  };

  const handleSessionClick = (session: any) => {
    router.push(`/session/${session.id}`);
  };

  const formatTimeAgo = (lastActivity: string) => {
    const now = new Date();
    const activityDate = new Date(lastActivity);
    const diffInMinutes = Math.floor((now.getTime() - activityDate.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <div className="flex items-center gap-3">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Bot className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Action Builder</span>
                  <span className="truncate text-xs text-muted-foreground">AI Assistant</span>
                </div>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <div className="px-3 py-2">
            <Button onClick={handleNewSession} className="w-full" size="sm">
              <Plus className="mr-2 h-4 w-4" />
              New Session
            </Button>
          </div>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Recent Sessions</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {sessions.map((session) => (
                <SidebarMenuItem key={session.id}>
                  <SidebarMenuButton
                    onClick={() => handleSessionClick(session)}
                    isActive={currentSession?.id === session.id}
                    tooltip={session.summary || 'New Session'}
                  >
                    <MessageSquare className="h-4 w-4" />
                    <div className="flex flex-col flex-1 overflow-hidden">
                      <span className="truncate text-sm font-medium">
                        {session.summary || 'New Session'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatTimeAgo(session.lastActivity)}
                        {session.messageCount && ` • ${session.messageCount} messages`}
                      </span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
              {sessions.length === 0 && (
                <div className="px-3 py-8 text-center text-sm text-muted-foreground">
                  No sessions yet
                </div>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={toggleDarkMode}>
              {isDarkMode ? (
                <>
                  <Sun className="h-4 w-4" />
                  <span>Light Mode</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4" />
                  <span>Dark Mode</span>
                </>
              )}
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton>
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
