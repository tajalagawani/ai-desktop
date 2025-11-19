'use client';

import { useMetricsStore } from '@/lib/stores/metrics-store';

export function ChatHeader() {
  const { metrics } = useMetricsStore();
  const {
    inputTokens = 0,
    outputTokens = 0,
    cacheReadTokens = 0,
    cacheCreationTokens = 0,
    totalCost = 0,
    turnCount = 0,
    toolCallCount = 0,
  } = metrics;

  return (
    <div className="border-b border-zinc-200 dark:border-zinc-800 px-4 py-3">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-medium">ACT Agent</h1>

        <div className="flex items-center gap-6 text-sm">
          {/* Tokens */}
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Input:</span>
            <span className="font-medium">{inputTokens.toLocaleString()}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Output:</span>
            <span className="font-medium">{outputTokens.toLocaleString()}</span>
          </div>

          {/* Cache */}
          {(cacheReadTokens > 0 || cacheCreationTokens > 0) && (
            <div className="flex items-center gap-2">
              <span className="text-zinc-600 dark:text-zinc-400">Cache:</span>
              <span className="font-medium">{cacheReadTokens.toLocaleString()}</span>
            </div>
          )}

          {/* Cost */}
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Cost:</span>
            <span className="font-medium text-green-600 dark:text-green-400">
              ${totalCost.toFixed(4)}
            </span>
          </div>

          {/* Model */}
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Model:</span>
            <span className="text-xs px-2 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-md">
              claude-sonnet-4
            </span>
          </div>

          {/* Turns */}
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Turns:</span>
            <span className="font-medium">{turnCount}</span>
          </div>

          {/* Tools */}
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400">Tools:</span>
            <span className="font-medium">{toolCallCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
