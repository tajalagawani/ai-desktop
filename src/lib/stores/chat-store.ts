import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type { Message, ToolUse } from '@/lib/flow-builder/types/chat';

interface ChatState {
  // Messages
  messages: Message[];
  streamingMessageId: string | null;

  // Session
  sessionId: string | null;
  sessionTitle: string;

  // Agent Status
  isAgentRunning: boolean;

  // Actions
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  removeMessage: (id: string) => void;
  appendToStreamingMessage: (id: string, chunk: string) => void;
  completeStreamingMessage: (id: string) => void;

  addToolUse: (messageId: string, toolUse: ToolUse) => void;
  updateToolUse: (messageId: string, toolUseId: string, updates: Partial<ToolUse>) => void;

  setAgentRunning: (running: boolean) => void;
  setSessionId: (id: string) => void;
  setSessionTitle: (title: string) => void;

  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  immer((set) => ({
    messages: [],
    streamingMessageId: null,
    sessionId: null,
    sessionTitle: 'New Flow',
    isAgentRunning: false,

    addMessage: (message) =>
      set((state) => {
        state.messages.push(message);
      }),

    updateMessage: (id, updates) =>
      set((state) => {
        const message = state.messages.find((m) => m.id === id);
        if (message) {
          Object.assign(message, updates);
        }
      }),

    removeMessage: (id) =>
      set((state) => {
        const index = state.messages.findIndex((m) => m.id === id);
        if (index !== -1) {
          state.messages.splice(index, 1);
        }
      }),

    appendToStreamingMessage: (id, chunk) =>
      set((state) => {
        const message = state.messages.find((m) => m.id === id);
        if (message) {
          message.content += chunk;
        }
      }),

    completeStreamingMessage: (id) =>
      set((state) => {
        const message = state.messages.find((m) => m.id === id);
        if (message) {
          message.streaming = false;
        }
        state.streamingMessageId = null;
      }),

    addToolUse: (messageId, toolUse) =>
      set((state) => {
        const message = state.messages.find((m) => m.id === messageId);
        if (message) {
          if (!message.toolUses) message.toolUses = [];
          message.toolUses.push(toolUse);
        }
      }),

    updateToolUse: (messageId, toolUseId, updates) =>
      set((state) => {
        const message = state.messages.find((m) => m.id === messageId);
        if (message?.toolUses) {
          const toolUse = message.toolUses.find((t) => t.id === toolUseId);
          if (toolUse) {
            Object.assign(toolUse, updates);
          }
        }
      }),

    setAgentRunning: (running) =>
      set((state) => {
        state.isAgentRunning = running;
      }),

    setSessionId: (id) =>
      set((state) => {
        state.sessionId = id;
      }),

    setSessionTitle: (title) =>
      set((state) => {
        state.sessionTitle = title;
      }),

    clearMessages: () =>
      set((state) => {
        state.messages = [];
        state.streamingMessageId = null;
      }),
  }))
);
