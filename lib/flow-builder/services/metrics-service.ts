import { prisma } from '@/lib/db/prisma';
import type { SessionMetrics } from '@prisma/client';

export interface UpdateMetricsInput {
  inputTokens?: number;
  outputTokens?: number;
  cacheReadTokens?: number;
  cacheCreationTokens?: number;
  totalCost?: number;
  totalDuration?: number;
  turnCount?: number;
  toolCallCount?: number;
  successfulTools?: number;
  failedTools?: number;
}

export class MetricsService {
  /**
   * Create or update session metrics
   */
  static async upsertMetrics(sessionId: string, updates: UpdateMetricsInput): Promise<SessionMetrics> {
    // Try to find existing metrics
    const existing = await prisma.sessionMetrics.findUnique({
      where: { sessionId },
    });

    if (existing) {
      // Update existing metrics (increment)
      return await prisma.sessionMetrics.update({
        where: { sessionId },
        data: {
          inputTokens: existing.inputTokens + (updates.inputTokens || 0),
          outputTokens: existing.outputTokens + (updates.outputTokens || 0),
          cacheReadTokens: existing.cacheReadTokens + (updates.cacheReadTokens || 0),
          cacheCreationTokens: existing.cacheCreationTokens + (updates.cacheCreationTokens || 0),
          totalTokens:
            existing.totalTokens +
            (updates.inputTokens || 0) +
            (updates.outputTokens || 0) +
            (updates.cacheReadTokens || 0) +
            (updates.cacheCreationTokens || 0),
          totalCost: existing.totalCost + (updates.totalCost || 0),
          totalDuration: existing.totalDuration + (updates.totalDuration || 0),
          turnCount: existing.turnCount + (updates.turnCount || 0),
          toolCallCount: existing.toolCallCount + (updates.toolCallCount || 0),
          successfulTools: existing.successfulTools + (updates.successfulTools || 0),
          failedTools: existing.failedTools + (updates.failedTools || 0),
        },
      });
    } else {
      // Create new metrics
      return await prisma.sessionMetrics.create({
        data: {
          sessionId,
          inputTokens: updates.inputTokens || 0,
          outputTokens: updates.outputTokens || 0,
          cacheReadTokens: updates.cacheReadTokens || 0,
          cacheCreationTokens: updates.cacheCreationTokens || 0,
          totalTokens:
            (updates.inputTokens || 0) +
            (updates.outputTokens || 0) +
            (updates.cacheReadTokens || 0) +
            (updates.cacheCreationTokens || 0),
          totalCost: updates.totalCost || 0,
          totalDuration: updates.totalDuration || 0,
          turnCount: updates.turnCount || 0,
          toolCallCount: updates.toolCallCount || 0,
          successfulTools: updates.successfulTools || 0,
          failedTools: updates.failedTools || 0,
        },
      });
    }
  }

  /**
   * Get session metrics
   */
  static async getMetrics(sessionId: string): Promise<SessionMetrics | null> {
    return await prisma.sessionMetrics.findUnique({
      where: { sessionId },
      include: {
        snapshots: {
          orderBy: { timestamp: 'desc' },
          take: 10,
        },
      },
    });
  }

  /**
   * Create a metrics snapshot
   */
  static async createSnapshot(sessionId: string): Promise<void> {
    const metrics = await prisma.sessionMetrics.findUnique({
      where: { sessionId },
    });

    if (!metrics) return;

    await prisma.metricsSnapshot.create({
      data: {
        metricsId: metrics.id,
        inputTokens: metrics.inputTokens,
        outputTokens: metrics.outputTokens,
        cacheReadTokens: metrics.cacheReadTokens,
        cacheCreationTokens: metrics.cacheCreationTokens,
        totalCost: metrics.totalCost,
        turnCount: metrics.turnCount,
      },
    });
  }
}
