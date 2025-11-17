"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { getIcon } from "@/utils/icon-mapper"
import {
  Play,
  Square,
  RotateCw,
  ArrowLeft,
  AlertCircle,
  Check,
  ExternalLink,
  FolderGit2,
  Folder,
  Copy,
  Search,
  Code,
  GitBranch,
  FileEdit,
  FilePlus,
  FileX
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { VSCodeRepository } from "@/lib/vscode/types"

interface VSCodeManagerProps {
  // Props for future use
}

interface GitChange {
  path: string
  status: 'modified' | 'added' | 'deleted' | 'renamed'
  additions?: number
  deletions?: number
}

export function VSCodeManager(_props: VSCodeManagerProps) {
  const [repositories, setRepositories] = useState<VSCodeRepository[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRepo, setSelectedRepo] = useState<VSCodeRepository | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [gitChanges, setGitChanges] = useState<GitChange[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileDiff, setFileDiff] = useState<string>("")
  const { toast} = useToast()

  // Store last data to compare
  const lastDataRef = React.useRef<string>("")

  const loadRepositories = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }
    try {
      const response = await fetch('/api/vscode/list', {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache'
        }
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load repositories')
      }

      // Only update if data actually changed
      const newDataString = JSON.stringify(data.repositories)
      const hasChanged = newDataString !== lastDataRef.current

      if (hasChanged || !silent) {
        lastDataRef.current = newDataString
        setRepositories(data.repositories || [])
        if (!silent) {
          setLoading(false)
        }
      }
    } catch (error) {
      console.error('Failed to load repositories:', error)
      if (!silent) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    // Run cleanup on first mount
    fetch('/api/vscode/cleanup', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.cleaned > 0) {
          console.log(`[VSCode] Cleaned up ${data.cleaned} orphaned processes`)
        }
      })
      .catch(err => console.error('[VSCode] Cleanup failed:', err))

    loadRepositories(false)
    // Silent background refresh
    const interval = setInterval(() => {
      loadRepositories(true)
    }, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [loadRepositories])

  const handleStart = async (repoId: string) => {
    setActionLoading(repoId)
    const repo = repositories.find(r => r.id === repoId)

    try {
      const response = await fetch('/api/vscode/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoId })
      })
      const data = await response.json()

      if (data.success) {
        toast({
          title: "VS Code Started",
          description: `${repo?.name || repoId} is now running on port ${data.port}`,
        })
        await loadRepositories(false)
        // Open in new tab
        if (data.url) {
          const hostname = window.location.hostname
          window.open(`http://${hostname}${data.url}`, '_blank')
        }
      } else {
        toast({
          title: "Failed to Start",
          description: data.error || "Could not start VS Code instance",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error starting VS Code",
        variant: "destructive"
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleStop = async (repoId: string) => {
    setActionLoading(repoId)
    const repo = repositories.find(r => r.id === repoId)

    try {
      const response = await fetch('/api/vscode/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoId })
      })
      const data = await response.json()

      if (data.success) {
        toast({
          title: "VS Code Stopped",
          description: `${repo?.name || repoId} has been stopped`,
        })
        await loadRepositories(false)
      } else {
        toast({
          title: "Failed to Stop",
          description: data.error || "Could not stop VS Code instance",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error stopping VS Code",
        variant: "destructive"
      })
    } finally {
      setActionLoading(null)
    }
  }

  const loadGitChanges = useCallback(async (repoId: string) => {
    try {
      const response = await fetch(`/api/vscode/changes/${repoId}`)
      const data = await response.json()
      if (data.success) {
        setGitChanges(data.changes || [])
      }
    } catch (error) {
      console.error('Failed to load git changes:', error)
    }
  }, [])

  const loadFileDiff = useCallback(async (repoId: string, filePath: string) => {
    try {
      const response = await fetch('/api/vscode/diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoId, filePath })
      })
      const data = await response.json()
      if (data.success) {
        setFileDiff(data.diff || '')
      }
    } catch (error) {
      console.error('Failed to load file diff:', error)
    }
  }, [])

  // Load git changes when a repository is selected
  useEffect(() => {
    if (selectedRepo && selectedRepo.type === 'git') {
      loadGitChanges(selectedRepo.id)
      const interval = setInterval(() => loadGitChanges(selectedRepo.id), 3000)
      return () => clearInterval(interval)
    } else {
      setGitChanges([])
    }
  }, [selectedRepo, loadGitChanges])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  // Filtered repositories
  const filteredRepos = useMemo(() => {
    let filtered = selectedCategory === 'all'
      ? repositories
      : repositories.filter(r => r.type === selectedCategory)

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(query) ||
        r.path.toLowerCase().includes(query) ||
        (r.branch && r.branch.toLowerCase().includes(query))
      )
    }

    return filtered
  }, [repositories, selectedCategory, searchQuery])

  // Statistics
  const stats = useMemo(() => {
    return {
      total: repositories.length,
      running: repositories.filter(r => r.running).length,
      stopped: repositories.filter(r => !r.running).length,
      git: repositories.filter(r => r.type === 'git').length,
    }
  }, [repositories])

  if (loading) {
    return (
      <div className="h-full bg-background">
        <div className="grid h-full grid-cols-[320px_1fr]">
          {/* Left side skeleton */}
          <div className="border-r p-6 flex flex-col">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
          {/* Right side skeleton */}
          <div className="p-8">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-background">
      <div className="grid h-full grid-cols-[320px_1fr]">
        {/* Left Panel - Sidebar */}
        <div className="border-r p-6 flex flex-col bg-muted/30">
          <div className="mb-6">
            <h1 className="text-2xl font-normal mb-1">VS Code Manager</h1>
            <p className="text-sm text-muted-foreground">Manage code editors for repositories</p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.running}</div>
              <div className="text-xs text-muted-foreground">Running</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.stopped}</div>
              <div className="text-xs text-muted-foreground">Stopped</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.git}</div>
              <div className="text-xs text-muted-foreground">Git Repos</div>
            </Card>
          </div>

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search repositories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Categories */}
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-3 text-muted-foreground">Filter by Type</h3>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedCategory('all')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'all'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                All ({repositories.length})
              </button>
              <button
                onClick={() => setSelectedCategory('git')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'git'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Git Repositories ({stats.git})
              </button>
              <button
                onClick={() => setSelectedCategory('folder')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'folder'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Folders ({repositories.length - stats.git})
              </button>
            </div>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => loadRepositories(false)} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <span>→</span>
            </Button>
          </div>
        </div>

        {/* Right Panel - Main Content */}
        <div className="bg-background p-8 h-full overflow-auto">
          {selectedRepo ? (
            // Repository Detail View
            <div className="flex flex-col flex-1">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2 w-fit"
                onClick={() => setSelectedRepo(null)}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to repositories
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
                  {selectedRepo.type === 'git' ? (
                    <FolderGit2 className="h-8 w-8 text-primary" />
                  ) : (
                    <Folder className="h-8 w-8 text-primary" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-2xl font-normal">{selectedRepo.name}</h2>
                    {selectedRepo.running ? (
                      <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                        <Check className="mr-1 h-3 w-3" />
                        Running
                      </Badge>
                    ) : (
                      <Badge variant="secondary">Stopped</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {selectedRepo.type === 'git' ? 'Git Repository' : 'Folder'}
                    {selectedRepo.branch && ` • ${selectedRepo.branch} branch`}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 items-center flex-shrink-0">
                  {selectedRepo.running ? (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const hostname = window.location.hostname
                          window.open(`http://${hostname}${selectedRepo.url}`, '_blank')
                        }}
                        title="Open in new tab"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleStop(selectedRepo.id)}
                        disabled={actionLoading === selectedRepo.id}
                        title="Stop code-server"
                      >
                        {actionLoading === selectedRepo.id ? (
                          <RotateCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Square className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleStart(selectedRepo.id)}
                      disabled={actionLoading === selectedRepo.id}
                      title="Start code-server"
                    >
                      {actionLoading === selectedRepo.id ? (
                        <RotateCw className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Play className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  )}
                </div>
              </div>

              {/* Connection Info */}
              {selectedRepo.running && (
                <div className="p-4 bg-muted/50 rounded-lg space-y-3 mb-4">
                  <h3 className="font-normal text-sm flex items-center gap-2">
                    <Code className="h-3.5 w-3.5" />
                    Access Information
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Editor URL:</span>
                      <div className="flex items-center gap-2">
                        <code className="font-mono bg-background px-2 py-1 rounded text-xs">
                          {selectedRepo.url}
                        </code>
                        <Button size="sm" variant="ghost" onClick={() => copyToClipboard(selectedRepo.url!)}>
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Port:</span>
                      <div className="flex items-center gap-2">
                        <code className="font-mono bg-background px-2 py-1 rounded text-xs">
                          {selectedRepo.port}
                        </code>
                        <Button size="sm" variant="ghost" onClick={() => copyToClipboard(String(selectedRepo.port))}>
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Uptime:</span>
                      <span className="text-xs">{selectedRepo.uptime}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Repository Info */}
              <div className="p-4 bg-muted/50 rounded-lg space-y-3">
                <h3 className="font-normal text-sm flex items-center gap-2">
                  <FolderGit2 className="h-3.5 w-3.5" />
                  Repository Information
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Path:</span>
                    <div className="flex items-center gap-2">
                      <code className="font-mono bg-background px-2 py-1 rounded text-xs max-w-md truncate">
                        {selectedRepo.path}
                      </code>
                      <Button size="sm" variant="ghost" onClick={() => copyToClipboard(selectedRepo.path)}>
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="text-xs">{selectedRepo.type === 'git' ? 'Git Repository' : 'Folder'}</span>
                  </div>
                  {selectedRepo.branch && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Branch:</span>
                      <div className="flex items-center gap-1">
                        <GitBranch className="h-3 w-3" />
                        <span className="text-xs">{selectedRepo.branch}</span>
                      </div>
                    </div>
                  )}
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Added:</span>
                    <span className="text-xs">{new Date(selectedRepo.addedAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Live Git Changes */}
              {selectedRepo.type === 'git' && (
                <div className="p-4 bg-muted/50 rounded-lg space-y-3 mt-4">
                  <h3 className="font-normal text-sm flex items-center gap-2">
                    <FileEdit className="h-3.5 w-3.5" />
                    Live Changes ({gitChanges.length})
                  </h3>
                  {gitChanges.length > 0 ? (
                    <div className="space-y-2">
                      {gitChanges.map((change) => {
                        const Icon = change.status === 'added' ? FilePlus :
                                   change.status === 'deleted' ? FileX :
                                   FileEdit
                        const statusColor = change.status === 'added' ? 'text-green-600' :
                                          change.status === 'deleted' ? 'text-red-600' :
                                          'text-amber-600'

                        return (
                          <div
                            key={change.path}
                            className="flex items-center justify-between text-sm p-2 rounded hover:bg-background cursor-pointer transition-colors"
                            onClick={() => {
                              setSelectedFile(change.path)
                              loadFileDiff(selectedRepo.id, change.path)
                            }}
                          >
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <Icon className={cn("h-3.5 w-3.5 flex-shrink-0", statusColor)} />
                              <span className="font-mono text-xs truncate">{change.path}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground flex-shrink-0">
                              {change.additions !== undefined && change.additions > 0 && (
                                <span className="text-green-600">+{change.additions}</span>
                              )}
                              {change.deletions !== undefined && change.deletions > 0 && (
                                <span className="text-red-600">-{change.deletions}</span>
                              )}
                            </div>
                          </div>
                        )
                      })}

                      {/* Diff Viewer */}
                      {selectedFile && fileDiff && (
                        <div className="mt-4 border-t pt-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-mono text-muted-foreground">{selectedFile}</span>
                            <Button size="sm" variant="ghost" onClick={() => setSelectedFile(null)}>
                              <span className="text-xs">Close</span>
                            </Button>
                          </div>
                          <ScrollArea className="h-64 w-full rounded border bg-background p-3">
                            <pre className="text-xs font-mono">
                              {fileDiff.split('\n').map((line, i) => (
                                <div
                                  key={i}
                                  className={cn(
                                    "px-2 py-0.5",
                                    line.startsWith('+') && !line.startsWith('+++') ? "bg-green-500/10 text-green-600" :
                                    line.startsWith('-') && !line.startsWith('---') ? "bg-red-500/10 text-red-600" :
                                    line.startsWith('@@') ? "bg-blue-500/10 text-blue-600" :
                                    "text-muted-foreground"
                                  )}
                                >
                                  {line || ' '}
                                </div>
                              ))}
                            </pre>
                          </ScrollArea>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">No uncommitted changes</p>
                  )}
                </div>
              )}
            </div>
          ) : (
            // Repository List View
            <>
              <h2 className="text-xl font-normal mb-6">Repositories</h2>

              {filteredRepos.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No repositories found. Clone a repository in GitHub Desktop to get started.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-3">
                  {filteredRepos.map((repo) => (
                    <div
                      key={repo.id}
                      className="border rounded-lg p-4 hover:border-primary/50 transition-colors bg-card cursor-pointer"
                      onClick={() => setSelectedRepo(repo)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                          {repo.type === 'git' ? (
                            <FolderGit2 className="h-6 w-6 text-primary" />
                          ) : (
                            <Folder className="h-6 w-6 text-primary" />
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium truncate">{repo.name}</h3>
                            {repo.running && (
                              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs">
                                Running
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground truncate">
                            {repo.path}
                            {repo.branch && ` • ${repo.branch}`}
                          </p>
                          {repo.running && repo.port && (
                            <div className="flex items-center gap-2 mt-1">
                              <p className="text-xs text-muted-foreground">
                                Port {repo.port} • {repo.uptime}
                              </p>
                              {(repo.added !== undefined && repo.added > 0) && (
                                <span className="text-xs text-green-600 flex items-center gap-0.5">
                                  <FilePlus className="h-3 w-3" />
                                  {repo.added}
                                </span>
                              )}
                              {(repo.modified !== undefined && repo.modified > 0) && (
                                <span className="text-xs text-amber-600 flex items-center gap-0.5">
                                  <FileEdit className="h-3 w-3" />
                                  {repo.modified}
                                </span>
                              )}
                              {(repo.deleted !== undefined && repo.deleted > 0) && (
                                <span className="text-xs text-red-600 flex items-center gap-0.5">
                                  <FileX className="h-3 w-3" />
                                  {repo.deleted}
                                </span>
                              )}
                              {repo.ahead !== undefined && repo.ahead > 0 && (
                                <span className="text-xs text-primary">↑{repo.ahead}</span>
                              )}
                              {repo.behind !== undefined && repo.behind > 0 && (
                                <span className="text-xs text-destructive">↓{repo.behind}</span>
                              )}
                            </div>
                          )}
                        </div>

                        <div className="flex gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                          {repo.running ? (
                            <>
                              <Button
                                size="sm"
                                onClick={() => {
                                  const hostname = window.location.hostname
                                  window.open(`http://${hostname}${repo.url}`, '_blank')
                                }}
                              >
                                <ExternalLink className="mr-2 h-3.5 w-3.5" />
                                Open
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleStop(repo.id)}
                                disabled={actionLoading === repo.id}
                              >
                                {actionLoading === repo.id ? (
                                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                ) : (
                                  <Square className="h-3.5 w-3.5" />
                                )}
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleStart(repo.id)}
                              disabled={actionLoading === repo.id}
                            >
                              {actionLoading === repo.id ? (
                                <>
                                  <RotateCw className="mr-2 h-3.5 w-3.5 animate-spin" />
                                  Starting...
                                </>
                              ) : (
                                <>
                                  <Play className="mr-2 h-3.5 w-3.5" />
                                  Start
                                </>
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
