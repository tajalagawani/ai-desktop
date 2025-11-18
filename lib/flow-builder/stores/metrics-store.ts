import { create } from 'zustand';
import type { Metrics } from '@/lib/flow-builder/types/chat';

interface MetricsState {
  metrics: Metrics;

  updateMetrics: (updates: Partial<Metrics>) => void;
  incrementMetrics: (increments: Partial<Metrics>) => void;
  resetMetrics: () => void;
}

const initialMetrics: Metrics = {
  inputTokens: 0,
  outputTokens: 0,
  cacheReadTokens: 0,
  cacheCreationTokens: 0,
  totalCost: 0,
  duration: 0,
  turnCount: 0,
  toolCallCount: 0,
};

export const useMetricsStore = create<MetricsState>((set) => ({
  metrics: initialMetrics,

  updateMetrics: (updates) =>
    set((state) => ({
      metrics: { ...state.metrics, ...updates },
    })),

  incrementMetrics: (increments) =>
    set((state) => ({
      metrics: {
        inputTokens: state.metrics.inputTokens + (increments.inputTokens || 0),
        outputTokens: state.metrics.outputTokens + (increments.outputTokens || 0),
        cacheReadTokens: state.metrics.cacheReadTokens + (increments.cacheReadTokens || 0),
        cacheCreationTokens: state.metrics.cacheCreationTokens + (increments.cacheCreationTokens || 0),
        totalCost: state.metrics.totalCost + (increments.totalCost || 0),
        duration: state.metrics.duration + (increments.duration || 0),
        turnCount: state.metrics.turnCount + (increments.turnCount || 0),
        toolCallCount: state.metrics.toolCallCount + (increments.toolCallCount || 0),
      },
    })),

  resetMetrics: () =>
    set({
      metrics: initialMetrics,
    }),
}));
