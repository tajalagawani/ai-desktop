'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Play,
  Square,
  RotateCw,
  Circle,
  Globe,
  Copy,
  ExternalLink,
  Terminal as TerminalIcon,
  Network,
  Zap,
  History,
  CheckCircle2,
  XCircle,
  Clock,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FlowStatusViewProps {
  flow: any;
  onFlowUpdate?: () => void;
}

interface RouteInfo {
  path: string;
  method: string;
  node?: string;
  description?: string;
}

// ACI Routes Tab Component
function ACIRoutesTab({ flow }: { flow: any }) {
  const [routes, setRoutes] = useState<RouteInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRoutes = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:${flow.port}/api/routes`);
        if (response.ok) {
          const data = await response.json();

          if (data.routes && typeof data.routes === 'object') {
            const parsedRoutes: RouteInfo[] = Object.entries(data.routes).map(([key, value]: [string, any]) => {
              const [method, ...pathParts] = key.split(' ');
              const path = pathParts.join(' ');

              return {
                path: path || key,
                method: method || 'GET',
                node: value.aci_node_id || value.handler_name,
                description: value.description
              };
            });
            setRoutes(parsedRoutes);
          }
        }
      } catch (error) {
        console.error('Failed to fetch routes:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRoutes();
  }, [flow.port]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET':
        return 'bg-blue-600 text-white';
      case 'POST':
        return 'bg-green-600 text-white';
      case 'PUT':
        return 'bg-yellow-600 text-white';
      case 'DELETE':
        return 'bg-red-600 text-white';
      case 'PATCH':
        return 'bg-purple-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  return (
    <TabsContent value="aci" className="flex-1 overflow-auto mt-0 min-h-0">
      <Card className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-normal text-sm">ACI Routes</h3>
          <Badge variant="outline" className="text-xs">
            {routes.length} {routes.length === 1 ? 'route' : 'routes'}
          </Badge>
        </div>

        {loading ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            Loading routes...
          </div>
        ) : routes.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No ACI routes found for this flow
          </div>
        ) : (
          <div className="space-y-2">
            {routes.map((route, index) => (
              <div
                key={index}
                className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Badge className={cn("text-xs font-mono", getMethodColor(route.method))}>
                    {route.method}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono">
                        {route.path}
                      </code>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => copyToClipboard(`http://localhost:${flow.port}${route.path}`)}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => window.open(`http://localhost:${flow.port}${route.path}`, '_blank')}
                      >
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                    {route.node && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Node: {route.node}
                      </p>
                    )}
                    {route.description && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {route.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </TabsContent>
  );
}

// Container Execution History Tab Component
function ContainerExecutionHistoryTab({ flow }: { flow: any }) {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchExecutions = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:${flow.port}/api/executions`);
        if (response.ok) {
          const data = await response.json();
          if (data.executions && Array.isArray(data.executions)) {
            setExecutions(data.executions);
          }
        }
      } catch (error) {
        console.error('Failed to fetch container executions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchExecutions();

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchExecutions, 5000);
    return () => clearInterval(interval);
  }, [flow.port]);

  const toggleExpand = (executionId: string) => {
    setExpandedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(executionId)) {
        newSet.delete(executionId);
      } else {
        newSet.add(executionId);
      }
      return newSet;
    });
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHour < 24) return `${diffHour}h ago`;
    return `${diffDay}d ago`;
  };

  return (
    <TabsContent value="executions" className="flex-1 overflow-auto mt-0 min-h-0">
      <Card className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-normal text-sm">Container Execution History</h3>
          <Badge variant="outline" className="text-xs">
            {executions.length} {executions.length === 1 ? 'execution' : 'executions'}
          </Badge>
        </div>

        {loading ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            Loading executions...
          </div>
        ) : executions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No executions recorded yet. Execution history will appear here when API requests are made to this flow.
          </div>
        ) : (
          <div className="space-y-2">
            {executions.map((execution) => {
              const isExpanded = expandedIds.has(execution.executionId || execution.id);

              return (
                <div
                  key={execution.executionId || execution.id}
                  className="border border-border rounded-lg overflow-hidden bg-card hover:shadow-md transition-shadow"
                >
                  {/* Execution Header */}
                  <button
                    onClick={() => toggleExpand(execution.executionId || execution.id)}
                    className="w-full px-3 py-2 flex items-center gap-2 hover:bg-muted/50 transition-colors text-left"
                  >
                    {/* Expand Icon */}
                    {isExpanded ? (
                      <ChevronDown className="w-3 h-3 flex-shrink-0 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="w-3 h-3 flex-shrink-0 text-muted-foreground" />
                    )}

                    {/* Status Icon */}
                    {execution.success !== false ? (
                      <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 flex-shrink-0 text-red-500" />
                    )}

                    {/* Execution Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <code className="text-xs font-mono">
                          {execution.method || 'GET'} {execution.path || execution.route}
                        </code>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatTimeAgo(execution.timestamp)}
                      </div>
                    </div>

                    {/* Duration Badge */}
                    {execution.duration !== undefined && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                        <Clock className="w-3 h-3" />
                        <span>{formatDuration(execution.duration)}</span>
                      </div>
                    )}
                  </button>

                  {/* Execution Details (Expanded) */}
                  {isExpanded && (
                    <div className="border-t border-border p-3 space-y-2 bg-muted/30 text-xs">
                      {/* Execution ID */}
                      {execution.executionId && (
                        <div>
                          <div className="font-medium text-muted-foreground mb-1">
                            Execution ID
                          </div>
                          <div className="font-mono bg-background px-2 py-1 rounded border border-border">
                            {execution.executionId}
                          </div>
                        </div>
                      )}

                      {/* Request Details */}
                      {execution.request && (
                        <div>
                          <div className="font-medium text-muted-foreground mb-1">
                            Request
                          </div>
                          <div className="font-mono bg-background px-2 py-1 rounded border border-border overflow-x-auto max-h-48 overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-xs">
                              {JSON.stringify(execution.request, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* Response/Result */}
                      {execution.response !== undefined && (
                        <div>
                          <div className="font-medium text-muted-foreground mb-1">
                            Response
                          </div>
                          <div className="font-mono bg-background px-2 py-1 rounded border border-border overflow-x-auto max-h-64 overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-xs">
                              {typeof execution.response === 'string'
                                ? execution.response
                                : JSON.stringify(execution.response, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* Error Details */}
                      {execution.error && (
                        <div>
                          <div className="font-medium text-red-500 mb-1">
                            Error
                          </div>
                          <div className="bg-red-500/10 border border-red-500/20 px-2 py-1 rounded">
                            {execution.error}
                          </div>
                        </div>
                      )}

                      {/* Timestamp */}
                      <div>
                        <div className="font-medium text-muted-foreground mb-1">
                          Executed At
                        </div>
                        <div>
                          {new Date(execution.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </TabsContent>
  );
}

export default function FlowStatusView({ flow, onFlowUpdate }: FlowStatusViewProps) {
  const [actionLoading, setActionLoading] = useState(false);
  const [logs, setLogs] = useState<string>('');
  const [logsLoading, setLogsLoading] = useState(false);

  // Debug: Log flow status
  useEffect(() => {
    console.log('[FlowStatusView] Flow data updated:', {
      name: flow.name,
      mode: flow.mode,
      port: flow.port,
      running: flow.container?.running,
      status: flow.container?.status,
      hasContainer: !!flow.container,
      fullFlow: flow
    });
  }, [flow]);

  const handleFlowAction = async (action: string) => {
    setActionLoading(true);
    try {
      const response = await fetch('/api/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, flowName: flow.name })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Flow action failed');
      }

      if (onFlowUpdate) {
        onFlowUpdate();
      }

      setTimeout(() => {
        setActionLoading(false);
      }, 1000);
    } catch (error: any) {
      console.error('Flow action error:', error);
      alert(error.message || 'Failed to perform action');
      setActionLoading(false);
    }
  };

  const loadLogs = useCallback(async (silent = false) => {
    if (!silent) {
      setLogsLoading(true);
    }
    try {
      const response = await fetch(`/api/flows?flowName=${flow.name}&action=logs&lines=100`);
      const data = await response.json();

      if (response.ok && data.logs) {
        setLogs(data.logs);
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      if (!silent) {
        setLogsLoading(false);
      }
    }
  }, [flow.name]);

  useEffect(() => {
    if (flow.container?.running) {
      loadLogs(false);
      const interval = setInterval(() => {
        loadLogs(true);
      }, 5000);
      return () => clearInterval(interval);
    } else {
      setLogs('');
    }
  }, [flow.container?.running, loadLogs]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getAccessUrl = () => {
    if (typeof window !== 'undefined') {
      return `http://${window.location.hostname}:${flow.port}`;
    }
    return null;
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 p-6">
      {/* Flow Header */}
      <div className="mb-4 flex items-start gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
          {flow.mode === 'agent' ? (
            <Network className="h-8 w-8 text-primary" />
          ) : (
            <Zap className="h-8 w-8 text-primary" />
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-normal">{flow.agent_name || flow.name}</h2>
            {flow.container?.running ? (
              flow.health?.status === 'healthy' ? (
                <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                  <Circle className="mr-1 h-2 w-2 fill-green-500 text-green-500" />
                  Running
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <Circle className="mr-1 h-2 w-2 fill-red-500 text-red-500" />
                  Unhealthy
                </Badge>
              )
            ) : (
              <Badge variant="secondary">
                <Circle className="mr-1 h-2 w-2 fill-gray-400 text-gray-400" />
                Stopped
              </Badge>
            )}
          </div>
          {flow.description && (
            <p className="text-base text-muted-foreground mb-2 max-w-2xl">
              {flow.description}
            </p>
          )}
          <div className="flex items-center gap-2">
            <Badge className="text-[10px] font-normal bg-foreground text-background border-0 px-1.5 py-0.5">
              {flow.mode === 'agent' ? 'Agent Mode' : flow.mode === 'miniact' ? 'MiniACT Mode' : 'Waiting'}
            </Badge>
            <Badge className="text-[10px] font-normal bg-foreground text-background border-0 px-1.5 py-0.5">
              Port {flow.port}
            </Badge>
          </div>
        </div>

        <div className="flex gap-2 items-center flex-shrink-0">
          {flow.container?.running ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleFlowAction('stop')}
              disabled={actionLoading}
              title="Stop flow"
            >
              {actionLoading ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Square className="h-3.5 w-3.5" />
              )}
            </Button>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleFlowAction('start')}
              disabled={actionLoading}
              title="Start flow"
            >
              {actionLoading ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleFlowAction('restart')}
            disabled={actionLoading}
            title="Restart flow"
          >
            <RotateCw className={cn("h-3.5 w-3.5", actionLoading && "animate-spin")} />
          </Button>
        </div>
      </div>

      {/* Access Details */}
      <div className="space-y-3 flex-shrink-0">
        <div className="p-3 bg-muted/50 rounded-lg space-y-2.5">
          <h3 className="font-normal text-sm flex items-center gap-2">
            <Globe className="h-3.5 w-3.5" />
            Access Details
          </h3>
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Port:</span>
              <div className="flex items-center gap-1.5">
                <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                  {flow.port}
                </code>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={() => copyToClipboard(flow.port.toString())}
                >
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Mode:</span>
              <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                {flow.mode}
              </code>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">File:</span>
              <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                {flow.file}
              </code>
            </div>
          </div>

          {flow.container?.running && (
            <>
              <div className="border-t pt-2.5" />
              <h3 className="font-normal text-sm flex items-center gap-2">
                <TerminalIcon className="h-3.5 w-3.5" />
                API Endpoints
              </h3>
              <div className="flex items-center gap-1.5">
                <input
                  type="text"
                  value={getAccessUrl()!}
                  readOnly
                  className="flex-1 px-2 py-1 bg-background rounded text-xs"
                />
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={() => copyToClipboard(getAccessUrl()!)}
                >
                  <Copy className="h-3 w-3" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={() => window.open(getAccessUrl()! + '/health', '_blank')}
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Debug Info */}
      <div className="px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 rounded text-xs mb-2">
        <strong>DEBUG:</strong> Running: {String(flow.container?.running)} | Status: {flow.container?.status || 'N/A'} | Port: {flow.port}
      </div>

      {/* Tabs Section */}
      {flow.container?.running ? (
        <Tabs defaultValue="logs" className="flex-1 flex flex-col mt-2 min-h-0">
          <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="info">Flow Info</TabsTrigger>
            {flow.mode === 'agent' && (
              <TabsTrigger value="aci">ACI Routes</TabsTrigger>
            )}
            <TabsTrigger value="executions">
              <History className="h-3.5 w-3.5 mr-1.5" />
              Executions
            </TabsTrigger>
          </TabsList>

          <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
            <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
              <div className="flex items-center justify-between mb-2 flex-shrink-0">
                <h3 className="font-normal text-sm">Container Logs (Live)</h3>
                <Button size="sm" onClick={() => loadLogs(false)} disabled={logsLoading}>
                  <RotateCw className={cn("h-3 w-3 mr-1.5", logsLoading && "animate-spin")} />
                  Refresh
                </Button>
              </div>
              <div className="flex-1 min-h-0 bg-black rounded overflow-hidden">
                <pre className="h-full w-full p-3 text-green-400 font-mono text-xs overflow-y-scroll overflow-x-hidden whitespace-pre-wrap break-words scrollbar-thin will-change-scroll">
                  {logs || 'Loading logs...'}
                </pre>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="info" className="flex-1 overflow-auto mt-0 min-h-0">
            <Card className="p-3">
              <h3 className="font-normal mb-2 text-sm">Flow Configuration</h3>
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between py-1.5 border-b">
                  <span className="text-muted-foreground">Container Name:</span>
                  <code className="text-xs">act-{flow.name}</code>
                </div>
                <div className="flex justify-between py-1.5 border-b">
                  <span className="text-muted-foreground">Status:</span>
                  <code className="text-xs">{flow.container?.status || 'unknown'}</code>
                </div>
                {flow.container?.started_at && (
                  <div className="flex justify-between py-1.5 border-b">
                    <span className="text-muted-foreground">Started At:</span>
                    <code className="text-xs">{new Date(flow.container.started_at).toLocaleString()}</code>
                  </div>
                )}
                <div className="flex justify-between py-1.5">
                  <span className="text-muted-foreground">Auto-assigned Port:</span>
                  <code className="text-xs">{flow.auto_assigned ? 'Yes' : 'No'}</code>
                </div>
              </div>
            </Card>
          </TabsContent>

          {flow.mode === 'agent' && (
            <ACIRoutesTab flow={flow} />
          )}

          <ContainerExecutionHistoryTab flow={flow} />
        </Tabs>
      ) : (
        <div className="flex-1 flex items-center justify-center p-8">
          <Card className="p-6 text-center max-w-md">
            <div className="text-muted-foreground mb-4">
              <Circle className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <h3 className="font-medium text-lg mb-2">Flow is Stopped</h3>
              <p className="text-sm">
                Start the flow to view logs, routes, and execution history.
              </p>
            </div>
            <Button
              onClick={() => handleFlowAction('start')}
              disabled={actionLoading}
              className="mt-2"
            >
              {actionLoading ? (
                <RotateCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Start Flow
            </Button>
          </Card>
        </div>
      )}
    </div>
  );
}
