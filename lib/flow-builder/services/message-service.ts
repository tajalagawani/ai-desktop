import { prisma } from '@/lib/db/prisma';
import type { Message, MessageRole, MessageType } from '@prisma/client';

export interface CreateMessageInput {
  id?: string; // Optional client-side UUID
  sessionId: string;
  role: MessageRole;
  content: any; // JSON content
  type?: MessageType;
  streaming?: boolean;
  error?: string;
  metadata?: any; // Full message metadata
  inputTokens?: number;
  outputTokens?: number;
}

export class MessageService {
  /**
   * Create a new message
   */
  static async createMessage(input: CreateMessageInput): Promise<Message> {
    return await prisma.message.create({
      data: {
        ...(input.id && { id: input.id }), // Use client ID if provided
        sessionId: input.sessionId,
        role: input.role,
        content: input.content,
        type: input.type || 'TEXT',
        streaming: input.streaming || false,
        error: input.error,
        metadata: input.metadata,
        inputTokens: input.inputTokens,
        outputTokens: input.outputTokens,
      },
    });
  }

  /**
   * Get messages for a session
   */
  static async getSessionMessages(sessionId: string) {
    return await prisma.message.findMany({
      where: { sessionId },
      orderBy: { createdAt: 'asc' },
      include: {
        toolUses: true,
        attachments: true,
      },
    });
  }

  /**
   * Update message
   */
  static async updateMessage(messageId: string, updates: Partial<CreateMessageInput>): Promise<Message> {
    return await prisma.message.update({
      where: { id: messageId },
      data: updates,
    });
  }

  /**
   * Complete streaming message
   */
  static async completeStreamingMessage(messageId: string): Promise<Message> {
    return await prisma.message.update({
      where: { id: messageId },
      data: { streaming: false },
    });
  }

  /**
   * Append to message content
   */
  static async appendToMessage(messageId: string, chunk: string): Promise<Message> {
    const message = await prisma.message.findUnique({
      where: { id: messageId },
    });

    if (!message) {
      throw new Error(`Message ${messageId} not found`);
    }

    const currentContent = typeof message.content === 'string' ? message.content : '';
    const newContent = currentContent + chunk;

    return await prisma.message.update({
      where: { id: messageId },
      data: { content: newContent },
    });
  }

  /**
   * Delete message
   */
  static async deleteMessage(messageId: string): Promise<void> {
    await prisma.message.delete({
      where: { id: messageId },
    });
  }

  /**
   * Get message count for session
   */
  static async getMessageCount(sessionId: string): Promise<number> {
    return await prisma.message.count({
      where: { sessionId },
    });
  }

  /**
   * Bulk create messages (for initial session load)
   */
  static async bulkCreateMessages(messages: CreateMessageInput[]): Promise<number> {
    const result = await prisma.message.createMany({
      data: messages,
    });
    return result.count;
  }
}
