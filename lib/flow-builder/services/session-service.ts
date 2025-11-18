import { prisma } from '@/lib/db/prisma';
import type { ChatSession, SessionStatus, Message } from '@prisma/client';

export interface CreateSessionInput {
  userId: string;
  title?: string;
  agentModel?: string;
}

export interface UpdateSessionInput {
  title?: string;
  status?: SessionStatus;
  exitCode?: number;
  errorMessage?: string;
  completedAt?: Date;
}

export class SessionService {
  /**
   * Create a new chat session
   */
  static async createSession(input: CreateSessionInput): Promise<ChatSession> {
    try {
      console.log('[SessionService] Creating session with input:', input);

      const session = await prisma.chatSession.create({
        data: {
          userId: input.userId,
          title: input.title || 'New Flow',
          agentModel: input.agentModel || 'claude-sonnet-4-20250514',
          status: 'ACTIVE',
          lastActivityAt: new Date(),
        },
      });

      console.log('[SessionService] Session created successfully:', session.id);
      return session;
    } catch (error) {
      console.error('[SessionService] Error creating session:', error);
      console.error('[SessionService] Error details:', error instanceof Error ? error.message : String(error));
      throw error;
    }
  }

  /**
   * Get session by ID with messages
   */
  static async getSession(sessionId: string) {
    try {
      console.log('[SessionService] Getting session:', sessionId);

      const session = await prisma.chatSession.findUnique({
        where: { id: sessionId },
        include: {
          messages: {
            orderBy: { createdAt: 'asc' },
          },
          metrics: true,
          flows: {
            orderBy: { createdAt: 'desc' },
            take: 10,
          },
        },
      });

      console.log('[SessionService] Session query completed. Found:', !!session);
      return session;
    } catch (error) {
      console.error('[SessionService] Error getting session:', error);
      console.error('[SessionService] Error details:', error instanceof Error ? error.message : String(error));
      throw error;
    }
  }

  /**
   * Get all sessions for a user
   */
  static async getUserSessions(userId: string, options?: {
    limit?: number;
    offset?: number;
    status?: SessionStatus;
  }) {
    const { limit = 50, offset = 0, status } = options || {};

    return await prisma.chatSession.findMany({
      where: {
        userId,
        ...(status && { status }),
      },
      orderBy: { lastActivityAt: 'desc' },
      take: limit,
      skip: offset,
      include: {
        _count: {
          select: { messages: true },
        },
        metrics: {
          select: {
            totalTokens: true,
            totalCost: true,
            turnCount: true,
          },
        },
      },
    });
  }

  /**
   * Update session
   */
  static async updateSession(sessionId: string, updates: UpdateSessionInput): Promise<ChatSession> {
    return await prisma.chatSession.update({
      where: { id: sessionId },
      data: {
        ...updates,
        lastActivityAt: new Date(),
      },
    });
  }

  /**
   * Update session activity timestamp
   */
  static async touchSession(sessionId: string): Promise<void> {
    await prisma.chatSession.update({
      where: { id: sessionId },
      data: { lastActivityAt: new Date() },
    });
  }

  /**
   * Delete session (cascade deletes messages, metrics, etc.)
   */
  static async deleteSession(sessionId: string): Promise<void> {
    await prisma.chatSession.delete({
      where: { id: sessionId },
    });
  }

  /**
   * Archive session
   */
  static async archiveSession(sessionId: string): Promise<ChatSession> {
    return await prisma.chatSession.update({
      where: { id: sessionId },
      data: {
        status: 'ARCHIVED',
        lastActivityAt: new Date(),
      },
    });
  }

  /**
   * Search sessions by title or content
   */
  static async searchSessions(userId: string, query: string) {
    return await prisma.chatSession.findMany({
      where: {
        userId,
        OR: [
          { title: { contains: query, mode: 'insensitive' } },
          {
            messages: {
              some: {
                content: {
                  string_contains: query,
                },
              },
            },
          },
        ],
      },
      orderBy: { lastActivityAt: 'desc' },
      take: 20,
      include: {
        _count: {
          select: { messages: true },
        },
      },
    });
  }

  /**
   * Get session count for user
   */
  static async getSessionCount(userId: string, status?: SessionStatus): Promise<number> {
    return await prisma.chatSession.count({
      where: {
        userId,
        ...(status && { status }),
      },
    });
  }

  /**
   * Auto-generate session title from first message
   */
  static async generateTitle(sessionId: string): Promise<string> {
    const session = await prisma.chatSession.findUnique({
      where: { id: sessionId },
      include: {
        messages: {
          where: { role: 'USER' },
          orderBy: { createdAt: 'asc' },
          take: 1,
        },
      },
    });

    if (!session || !session.messages[0]) {
      return 'New Flow';
    }

    // Get first user message content
    const firstMessage = session.messages[0];
    const content = typeof firstMessage.content === 'string'
      ? firstMessage.content
      : JSON.stringify(firstMessage.content);

    // Generate title (first 50 chars)
    const title = content.substring(0, 50).trim() + (content.length > 50 ? '...' : '');

    // Update session title
    await this.updateSession(sessionId, { title });

    return title;
  }
}
