'use client';

import MessageList from './MessageList';
import InputArea from './InputArea';
import ActionsList from './ActionsList';
import ClaudeStatus from './ClaudeStatus';
import FlowStatusView from './FlowStatusView';
import ExecutionHistoryTab from './ExecutionHistoryTab';
import TopicSelector, { type Topic } from './TopicSelector';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';
import { MessageSquare, Settings, Plus, Menu, Zap, History } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

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

  // NEW: Flow-related state
  const selectedFlow = useChatStore(state => state.selectedFlow);
  const mainContentTab = useChatStore(state => state.mainContentTab);
  const setMainContentTab = useChatStore(state => state.setMainContentTab);
  const loadFlows = useChatStore(state => state.loadFlows);

  // NEW: Topic selector state
  const selectedTopic = useChatStore(state => state.selectedTopic);
  const setSelectedTopic = useChatStore(state => state.setSelectedTopic);
  const sessions = useChatStore(state => state.sessions);
  const setSessions = useChatStore(state => state.setSessions);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);
  const messages = useChatStore(state => state.messages);

  const handleSelectTopic = (topic: Topic) => {
    console.log('Topic selected:', topic);
    setSelectedTopic(topic);

    // Create new session immediately with topic info
    const newSession = {
      id: crypto.randomUUID(), // Temporary UUID until backend creates real one
      summary: `${topic.icon} ${topic.name}`,
      messageCount: 0,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
      topic: {
        id: topic.id,
        name: topic.name,
        context: topic.context
      }
    };

    // Add to sessions list at the top
    setSessions([newSession, ...sessions]);

    // Set as current session
    setCurrentSession(newSession);

    // Auto-focus input after topic selection
    setTimeout(() => {
      const input = document.querySelector('textarea');
      if (input) {
        input.focus();
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  return (
    <div className="h-full flex flex-col bg-background text-foreground">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-border bg-background">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-3">
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
                {currentSession?.topic && (currentSession?.messageCount || 0) === 0
                  ? `${currentSession.topic.name}`
                  : currentSession?.summary || 'New Session'}
              </h1>
              <p className="text-xs text-muted-foreground">
                {currentSession?.topic ? 'Topic-based chat' : 'Action Builder'}
              </p>
            </div>

            {/* Tabs - Only show when session exists */}
            {currentSession && (
              <div className="flex items-center gap-1 ml-4">
                <button
                  onClick={() => setMainContentTab('messages')}
                  className={cn(
                    "px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5",
                    mainContentTab === 'messages'
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted text-muted-foreground"
                  )}
                >
                  <MessageSquare className="h-3.5 w-3.5" />
                  Messages
                </button>

                {selectedFlow && (
                  <button
                    onClick={() => setMainContentTab('flow-status')}
                    className={cn(
                      "px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5",
                      mainContentTab === 'flow-status'
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted text-muted-foreground"
                    )}
                  >
                    <Zap className="h-3.5 w-3.5" />
                    Flow Status
                  </button>
                )}

                <button
                  onClick={() => setMainContentTab('executions')}
                  className={cn(
                    "px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5",
                    mainContentTab === 'executions'
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted text-muted-foreground"
                  )}
                >
                  <History className="h-3.5 w-3.5" />
                  Executions
                </button>
              </div>
            )}
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
          {/* Tab Content */}
          {currentSession ? (
            <>
              {mainContentTab === 'messages' ? (
                <>
                  <MessageList />
                  {isDevMode && <ClaudeStatus />}
                  <InputArea />
                </>
              ) : mainContentTab === 'flow-status' && selectedFlow ? (
                <FlowStatusView flow={selectedFlow} onFlowUpdate={loadFlows} />
              ) : mainContentTab === 'executions' ? (
                <ExecutionHistoryTab />
              ) : (
                /* Fallback to messages if invalid state */
                <>
                  <MessageList />
                  {isDevMode && <ClaudeStatus />}
                  <InputArea />
                </>
              )}
            </>
          ) : (
            /* No session view - Show topic selector OR welcome message OR message list */
            <>
              {!currentSession ? (
                /* Topic selector - no session yet */
                <div className="flex-1 overflow-y-auto p-6">
                  <div className="max-w-4xl mx-auto space-y-6">
                    <div className="text-center">
                      <h2 className="text-2xl font-semibold mb-2">Choose a Topic</h2>
                      <p className="text-sm text-muted-foreground">
                        Select what you want to build or ask about
                      </p>
                    </div>
                    <TopicSelector
                      onSelectTopic={handleSelectTopic}
                      onCancel={() => {}}
                      selectedTopicId={selectedTopic?.id}
                    />
                  </div>
                </div>
              ) : messages.length === 0 && currentSession.topic ? (
                /* Welcome message - session exists but no messages yet */
                <div className="flex-1 overflow-y-auto flex items-center justify-center p-6">
                  <div className="max-w-2xl text-center space-y-4">
                    <div className="text-6xl mb-4">{selectedTopic?.icon || '💬'}</div>
                    <h2 className="text-2xl font-semibold">{currentSession.topic.name}</h2>
                    <p className="text-sm text-muted-foreground">
                      {selectedTopic?.description || 'Start your conversation'}
                    </p>
                    {selectedTopic && (
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-2">Example queries:</p>
                        <p className="text-sm italic">{selectedTopic.example}</p>
                      </div>
                    )}
                    <p className="text-sm text-primary font-medium">
                      Start typing your message below ↓
                    </p>
                    <button
                      onClick={() => {
                        setSelectedTopic(null);
                        setCurrentSession(null);
                      }}
                      className="text-xs text-muted-foreground hover:text-foreground underline mt-4"
                    >
                      Change topic
                    </button>
                  </div>
                </div>
              ) : (
                /* Messages view - session exists and has messages */
                <>
                  <MessageList />
                  {isDevMode && <ClaudeStatus />}
                </>
              )}
              <InputArea />
            </>
          )}
        </div>

        {/* Actions Sidebar - Desktop only, hide when flow status or executions is shown */}
        {!isMobile && showActions && mainContentTab === 'messages' && (
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
