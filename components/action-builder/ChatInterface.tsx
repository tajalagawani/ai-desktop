'use client';

import MessageList from './MessageList';
import InputArea from './InputArea';
import ActionsList from './ActionsList';
import ClaudeStatus from './ClaudeStatus';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { MessageSquare, Settings, Plus, Menu } from 'lucide-react';
import { useState } from 'react';

export default function ChatInterface() {
  const [showActions, setShowActions] = useState(true);
  const currentSession = useChatStore(state => state.currentSession);
  const isDevMode = useChatStore(state => state.isDevMode);
  const toggleDevMode = useChatStore(state => state.toggleDevMode);
  const createNewSession = useChatStore(state => state.createNewSession);
  const showSettings = useChatStore(state => state.showSettings);
  const setShowSettings = useChatStore(state => state.setShowSettings);
  const isMobile = useChatStore(state => state.isMobile);
  const setSidebarOpen = useChatStore(state => state.setSidebarOpen);
  const toggleDarkMode = useChatStore(state => state.toggleDarkMode);
  const isDarkMode = useChatStore(state => state.isDarkMode);
  const isLoading = useChatStore(state => state.isLoading);
  const isConnected = useChatStore(state => state.isConnected);

  return (
    <div className="h-full flex flex-col bg-background text-foreground">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-border bg-background">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-2">
            {/* Mobile Menu Button */}
            {isMobile && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-1.5 rounded-lg hover:bg-muted transition-colors md:hidden"
                title="Open Menu"
              >
                <Menu className="w-4 h-4" />
              </button>
            )}

            <div className="w-8 h-8 bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h1 className="text-sm font-semibold">
                {currentSession?.summary || 'New Session'}
              </h1>
              <p className="text-xs text-muted-foreground">Action Builder</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* New Session Button */}
            <button
              onClick={createNewSession}
              className="p-1.5 rounded-lg hover:bg-muted transition-colors"
              title="New Session"
            >
              <Plus className="w-4 h-4" />
            </button>

            {/* Dev Mode Toggle */}
            <button
              onClick={toggleDevMode}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                !isDevMode
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-foreground border border-border'
              }`}
              title={isDevMode ? 'Switch to Normal Mode' : 'Switch to Dev Mode'}
            >
              {!isDevMode ? '✨ Normal' : '🔧 Dev'}
            </button>

            {/* Settings Button */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-1.5 rounded-lg hover:bg-muted transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <MessageList />
          {/* Show status only in Dev Mode */}
          {isDevMode && <ClaudeStatus />}
          <InputArea />
        </div>

        {/* Actions Sidebar - Desktop only */}
        {!isMobile && showActions && (
          <div className="w-80 border-l border-border bg-muted/30 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 p-4 border-b border-border">
              <h2 className="text-sm font-semibold">Actions</h2>
            </div>
            <div className="flex-1 overflow-y-auto">
              <ActionsList />
            </div>
          </div>
        )}
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowSettings(false)}
        >
          <div
            className="bg-background border border-border rounded-xl shadow-2xl w-full max-w-md m-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-lg font-semibold">Settings</h2>
              <button
                onClick={() => setShowSettings(false)}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Dark Mode */}
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Dark Mode</div>
                  <div className="text-sm text-muted-foreground">
                    Toggle between light and dark themes
                  </div>
                </div>
                <button
                  onClick={toggleDarkMode}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    isDarkMode ? 'bg-primary' : 'bg-muted'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      isDarkMode ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>

              {/* Show Actions */}
              {!isMobile && (
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Actions Sidebar</div>
                    <div className="text-sm text-muted-foreground">
                      Show generated actions in sidebar
                    </div>
                  </div>
                  <button
                    onClick={() => setShowActions(!showActions)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      showActions ? 'bg-primary' : 'bg-muted'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full transition-transform ${
                        showActions ? 'translate-x-6' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
              )}

              {/* About */}
              <div className="pt-4 border-t border-border">
                <div className="text-sm text-muted-foreground space-y-1">
                  <div className="font-medium text-foreground mb-2">
                    About Action Builder
                  </div>
                  <div>Version: 1.0.0</div>
                  <div>A specialized AI that creates executable actions</div>
                  <div className="pt-2">
                    <a
                      href="https://github.com/tajalagawani/actcahtapp"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      View on GitHub
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
