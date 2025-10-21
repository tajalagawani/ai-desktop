/**
 * Centralized TypeScript type exports
 * Import types from here instead of individual files
 */

// Export types from app.types.ts
export type * from "./app.types"

// Re-export commonly used types from data files
export type { AppConfig, WindowConfig, DesktopFolder } from "@/data/desktop-apps"

// Action Builder types
export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'error' | 'tool-use' | 'tool-result';
  content: string;
  timestamp: number;
  isToolUse?: boolean;
  toolName?: string;
  toolInput?: string;
  toolResult?: string;
  sessionId?: string;
}

export interface Session {
  id: string;
  summary?: string;
  lastMessage?: string;
  messageCount?: number;
  created?: string;
  updated?: string;
  lastActivity: string;
  topic?: {
    id: string;
    name: string;
    context: string;
  };
}

export interface Action {
  id: string;
  name: string;
  path: string;
  metadata?: {
    id: string;
    name: string;
    description?: string;
    created: string;
    tags?: string[];
    requiredServices?: string[];
    author?: string;
    sessionId?: string;
  };
}

export interface Project {
  name: string;
  displayName?: string;
  path?: string;
  fullPath?: string;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  sessionId?: string;
  error?: string;
  topic?: string;
  prompt?: string;
  resume?: boolean;
}

export interface ChatState {
  messages: Message[];
  sessions: Session[];
  actions: Action[];
  currentSession: Session | null;
  isConnected: boolean;
  isLoading: boolean;
}

// Future: Add more type exports as needed
// export type * from "./user.types"
// export type * from "./workflow.types"
// export type * from "./api.types"
