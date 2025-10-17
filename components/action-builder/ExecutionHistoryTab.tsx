'use client'

import { useEffect, useState } from 'react'
import { useChatStore } from '@/lib/action-builder/stores/chatStore'
import { CheckCircle2, XCircle, Clock, Zap, ChevronDown, ChevronRight } from 'lucide-react'

export default function ExecutionHistoryTab() {
  const executions = useChatStore(state => state.executions)
  const isLoadingExecutions = useChatStore(state => state.isLoadingExecutions)
  const loadExecutions = useChatStore(state => state.loadExecutions)
  const currentSession = useChatStore(state => state.currentSession)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  // Load executions on mount and when session changes
  useEffect(() => {
    if (currentSession) {
      loadExecutions()
    }
  }, [currentSession?.id])

  const toggleExpand = (executionId: string) => {
    setExpandedIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(executionId)) {
        newSet.delete(executionId)
      } else {
        newSet.add(executionId)
      }
      return newSet
    })
  }

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${(ms / 60000).toFixed(1)}m`
  }

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (diffSec < 60) return `${diffSec}s ago`
    if (diffMin < 60) return `${diffMin}m ago`
    if (diffHour < 24) return `${diffHour}h ago`
    return `${diffDay}d ago`
  }

  if (!currentSession) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground">
          <p>Select a session to view execution history</p>
        </div>
      </div>
    )
  }

  if (isLoadingExecutions) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading executions...</p>
        </div>
      </div>
    )
  }

  if (executions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground">
          <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">No Executions Yet</p>
          <p className="text-sm">
            Flow executions will appear here once you run workflows in this session
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-1">Execution History</h3>
        <p className="text-sm text-muted-foreground">
          {executions.length} execution{executions.length !== 1 ? 's' : ''} in this session
        </p>
      </div>

      {executions.map((execution) => {
        const isExpanded = expandedIds.has(execution.executionId)

        return (
          <div
            key={execution.executionId}
            className="border border-border rounded-lg overflow-hidden bg-card hover:shadow-md transition-shadow"
          >
            {/* Execution Header */}
            <button
              onClick={() => toggleExpand(execution.executionId)}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-muted/50 transition-colors text-left"
            >
              {/* Expand Icon */}
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
              )}

              {/* Status Icon */}
              {execution.success ? (
                <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 flex-shrink-0 text-red-500" />
              )}

              {/* Flow Info */}
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{execution.flowName}</div>
                <div className="text-xs text-muted-foreground flex items-center gap-2">
                  <span className="uppercase">{execution.mode}</span>
                  <span>•</span>
                  <span>{formatTimeAgo(execution.timestamp)}</span>
                </div>
              </div>

              {/* Duration Badge */}
              <div className="flex items-center gap-1 text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                <Clock className="w-3 h-3" />
                <span>{formatDuration(execution.duration)}</span>
              </div>
            </button>

            {/* Execution Details (Expanded) */}
            {isExpanded && (
              <div className="border-t border-border p-4 space-y-3 bg-muted/30">
                {/* Execution ID */}
                <div>
                  <div className="text-xs font-medium text-muted-foreground mb-1">
                    Execution ID
                  </div>
                  <div className="text-xs font-mono bg-background px-2 py-1 rounded border border-border">
                    {execution.executionId}
                  </div>
                </div>

                {/* Timestamp */}
                <div>
                  <div className="text-xs font-medium text-muted-foreground mb-1">
                    Executed At
                  </div>
                  <div className="text-xs">
                    {new Date(execution.timestamp).toLocaleString()}
                  </div>
                </div>

                {/* Result or Error */}
                {execution.success ? (
                  <div>
                    <div className="text-xs font-medium text-muted-foreground mb-1">
                      Result
                    </div>
                    <div className="text-xs font-mono bg-background px-3 py-2 rounded border border-border overflow-x-auto max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(execution.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="text-xs font-medium text-red-500 mb-1">
                      Error: {execution.errorType || 'Unknown Error'}
                    </div>
                    <div className="text-xs bg-red-500/10 border border-red-500/20 px-3 py-2 rounded">
                      {execution.error || 'No error details available'}
                    </div>
                    {execution.traceback && (
                      <div className="mt-2">
                        <div className="text-xs font-medium text-muted-foreground mb-1">
                          Traceback
                        </div>
                        <div className="text-xs font-mono bg-background px-3 py-2 rounded border border-border overflow-x-auto max-h-48 overflow-y-auto">
                          <pre className="whitespace-pre-wrap text-red-400">
                            {execution.traceback}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Deployment Info (for agent mode) */}
                {execution.deployment && (
                  <div>
                    <div className="text-xs font-medium text-muted-foreground mb-1">
                      Deployment
                    </div>
                    <div className="text-xs bg-blue-500/10 border border-blue-500/20 px-3 py-2 rounded space-y-1">
                      {execution.deployment.deployed && (
                        <>
                          <div>✅ Deployed successfully</div>
                          <div>
                            <span className="font-medium">Flow:</span> {execution.deployment.flow_name}
                          </div>
                          <div>
                            <span className="font-medium">Port:</span> {execution.deployment.port}
                          </div>
                          {execution.deployment.url && (
                            <div>
                              <span className="font-medium">URL:</span>{' '}
                              <a
                                href={execution.deployment.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:underline"
                              >
                                {execution.deployment.url}
                              </a>
                            </div>
                          )}
                        </>
                      )}
                      {!execution.deployment.deployed && execution.deployment.error && (
                        <div className="text-red-400">
                          ❌ Deployment failed: {execution.deployment.error}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
