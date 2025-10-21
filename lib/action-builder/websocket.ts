// WebSocket client for Action Builder backend

import { Message, WebSocketMessage } from '@/types';

export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Set<(message: WebSocketMessage) => void> = new Set();
  private connectionHandlers: Set<(connected: boolean) => void> = new Set();
  private sessionId: string | null = null;

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        console.log('[WebSocket Client] ========================================');
        console.log('[WebSocket Client] Connecting to:', this.url);
        console.log('[WebSocket Client] ========================================');

        // Connect without authentication
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket Client] ========================================');
          console.log('[WebSocket Client] ✅ WebSocket connected successfully!');
          console.log('[WebSocket Client] ReadyState:', this.ws?.readyState);
          console.log('[WebSocket Client] ========================================');
          this.reconnectAttempts = 0;
          this.notifyConnectionHandlers(true);
          resolve();
        };

        this.ws.onmessage = (event) => {
          console.log('[WebSocket Client] ----------------------------------------');
          console.log('[WebSocket Client] Message received:', event.data.substring(0, 200));
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            console.log('[WebSocket Client] Parsed message type:', message.type);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket Client] ❌ Failed to parse message:', error);
          }
          console.log('[WebSocket Client] ----------------------------------------');
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket Client] ========================================');
          console.error('[WebSocket Client] ❌ WebSocket error:', error);
          console.error('[WebSocket Client] URL:', this.url);
          console.error('[WebSocket Client] ReadyState:', this.ws?.readyState);
          console.error('[WebSocket Client] ========================================');
          // Silently handle connection errors - will retry automatically
          reject(new Error('WebSocket connection failed'));
        };

        this.ws.onclose = (event) => {
          console.log('[WebSocket Client] ========================================');
          console.log('[WebSocket Client] WebSocket closed');
          console.log('[WebSocket Client]   - Code:', event.code);
          console.log('[WebSocket Client]   - Reason:', event.reason);
          console.log('[WebSocket Client]   - Clean:', event.wasClean);
          console.log('[WebSocket Client] ========================================');
          this.notifyConnectionHandlers(false);
          this.attemptReconnect();
        };
      } catch (error) {
        console.error('[WebSocket Client] ❌ Exception during connect:', error);
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    // Capture session ID from responses
    if (message.sessionId) {
      this.sessionId = message.sessionId;
    }

    // Notify all handlers
    this.messageHandlers.forEach(handler => handler(message));
  }

  private notifyConnectionHandlers(connected: boolean) {
    this.connectionHandlers.forEach(handler => handler(connected));
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(message: WebSocketMessage) {
    console.log('[WebSocket Client] ----------------------------------------');
    console.log('[WebSocket Client] Sending message type:', message.type);
    console.log('[WebSocket Client] ReadyState:', this.ws?.readyState);

    if (this.ws?.readyState === WebSocket.OPEN) {
      const messageStr = JSON.stringify(message);
      console.log('[WebSocket Client] Message:', messageStr.substring(0, 200));
      this.ws.send(messageStr);
      console.log('[WebSocket Client] ✅ Message sent');
    } else {
      console.error('[WebSocket Client] ❌ WebSocket not connected, state:', this.ws?.readyState);
    }
    console.log('[WebSocket Client] ----------------------------------------');
  }

  sendUserMessage(content: string, sessionId?: string, topicId?: string) {
    console.log('[WebSocket Client] sendUserMessage called');
    console.log('[WebSocket Client]   - Content:', content.substring(0, 100));
    console.log('[WebSocket Client]   - Session ID:', sessionId || this.sessionId || 'NONE');
    console.log('[WebSocket Client]   - Topic ID:', topicId || 'NONE');

    // Desktop server expects 'start_chat' type
    this.send({
      type: 'start_chat',
      prompt: content,
      sessionId: sessionId || this.sessionId || undefined,
      resume: !!(sessionId || this.sessionId),
      topic: topicId // NEW: Include topic ID
    });
  }

  createSession(projectName: string) {
    // Not needed for desktop server - sessions are created automatically
    console.log('[WebSocket Client] createSession called (no-op for desktop server)');
  }

  abortSession(sessionId: string) {
    this.send({
      type: 'stop_chat',
      sessionId
    });
  }

  onMessage(handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onConnectionChange(handler: (connected: boolean) => void) {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getCurrentSessionId(): string | null {
    return this.sessionId;
  }
}

// Singleton instance
let wsInstance: ChatWebSocket | null = null;

export function getWebSocketClient(): ChatWebSocket {
  if (!wsInstance) {
    // Desktop app WebSocket endpoint
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3000/api/action-builder/ws';
    console.log('[WebSocket Client] Connecting to:', wsUrl);
    wsInstance = new ChatWebSocket(wsUrl);
  }
  return wsInstance;
}
