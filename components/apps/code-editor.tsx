"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Loader2, Play, Square, RefreshCw, ExternalLink, Terminal, FolderGit2, Trash2, Activity, XCircle } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface Repository {
  id: string
  name: string
  path: string
  type: 'git' | 'folder'
  vscodeRunning: boolean
  vscodePort?: number
  lastOpened?: string
}

export function CodeEditorApp() {
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingRepos, setLoadingRepos] = useState(true)
  const [showInstallDialog, setShowInstallDialog] = useState(false)
  const [installing, setInstalling] = useState(false)
  const [installMethod, setInstallMethod] = useState<'script' | 'homebrew' | 'npm'>('script')
  const [allProcesses, setAllProcesses] = useState<any[]>([])
  const [showProcessManager, setShowProcessManager] = useState(false)
  const [loadingProcesses, setLoadingProcesses] = useState(false)

  useEffect(() => {
    loadRepositories()
  }, [])

  const loadRepositories = async () => {
    setLoadingRepos(true)
    try {
      const response = await fetch("/api/repositories")
      const data = await response.json()

      if (data.success) {
        setRepositories(data.repositories || [])
      }
    } catch (error) {
      console.error("Failed to load repositories:", error)
      toast.error("Failed to load repositories")
    } finally {
      setLoadingRepos(false)
    }
  }

  const startServer = async () => {
    if (!selectedRepo) {
      toast.error("Please select a repository")
      return
    }

    setLoading(true)
    try {
      const response = await fetch("/api/code-server/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repoId: selectedRepo })
      })

      const data = await response.json()

      if (data.success) {
        const hostname = window.location.hostname
        const fullUrl = `http://${hostname}${data.url}`
        toast.success("VS Code started! Opening in new window...")

        // Reload repositories to update status
        await loadRepositories()

        // Open in new window immediately
        window.open(fullUrl, '_blank', 'width=1600,height=1000')
      } else {
        if (data.error?.includes('not installed')) {
          setShowInstallDialog(true)
          toast.error("code-server not installed")
        } else {
          toast.error(data.error || "Failed to start VS Code")
        }
      }
    } catch (error: any) {
      toast.error(`Failed to start VS Code: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const stopServer = async () => {
    if (!selectedRepo) return

    try {
      const response = await fetch("/api/code-server/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repoId: selectedRepo })
      })

      const data = await response.json()

      if (data.success) {
        toast.success("VS Code stopped")

        // Reload repositories to update status
        await loadRepositories()
      } else {
        toast.error(data.error || "Failed to stop VS Code")
      }
    } catch (error: any) {
      toast.error(`Failed to stop VS Code: ${error.message}`)
    }
  }

  const handleInstall = async (method: 'script' | 'homebrew' | 'npm') => {
    setInstalling(true)
    setInstallMethod(method)

    try {
      const response = await fetch("/api/code-server/install", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method })
      })

      const data = await response.json()

      if (data.success) {
        toast.success("code-server installed successfully!")
        setShowInstallDialog(false)
        // Try to start server automatically
        setTimeout(() => startServer(), 1000)
      } else {
        toast.error(data.error || "Installation failed")
      }
    } catch (error: any) {
      toast.error(`Installation failed: ${error.message}`)
    } finally {
      setInstalling(false)
    }
  }

  const selectedRepoData = repositories.find(r => r.id === selectedRepo)

  const loadProcesses = async () => {
    setLoadingProcesses(true)
    try {
      const response = await fetch("/api/code-server/cleanup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "list-processes" })
      })
      const data = await response.json()
      if (data.success) {
        setAllProcesses(data.processes || [])
      }
    } catch (error) {
      console.error("Failed to load processes:", error)
      toast.error("Failed to load processes")
    } finally {
      setLoadingProcesses(false)
    }
  }

  const killProcess = async (pid: number) => {
    try {
      const response = await fetch("/api/code-server/cleanup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "kill-pid", pid })
      })
      const data = await response.json()

      if (data.success) {
        toast.success(`Process ${pid} killed`)
        await loadProcesses()
        await loadRepositories()
      } else {
        toast.error(data.error || "Failed to kill process")
      }
    } catch (error: any) {
      toast.error(`Failed to kill process: ${error.message}`)
    }
  }

  const killAllProcesses = async () => {
    try {
      const response = await fetch("/api/code-server/cleanup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "kill-all" })
      })
      const data = await response.json()

      if (data.success) {
        toast.success("All code-server processes killed")
        await loadProcesses()
        await loadRepositories()
      } else {
        toast.error(data.error || "Failed to kill processes")
      }
    } catch (error: any) {
      toast.error(`Failed to kill processes: ${error.message}`)
    }
  }

  if (loadingRepos) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Loading repositories...</p>
        </div>
      </div>
    )
  }

  // Always show the card grid view - no embedded iframe
  return (
      <div className="h-full w-full bg-background overflow-auto">
        <div className="max-w-6xl mx-auto p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h2 className="text-2xl font-bold">VS Code Editor</h2>
              <p className="text-sm text-muted-foreground">
                Select a repository to open in VS Code
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowProcessManager(true)
                  loadProcesses()
                }}
              >
                <Activity className="mr-2 h-4 w-4" />
                Process Manager
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={loadRepositories}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>
          </div>

          {/* Repositories Grid */}
          {repositories.length === 0 ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center space-y-4">
                <div className="mx-auto w-20 h-20 bg-muted rounded-full flex items-center justify-center">
                  <FolderGit2 className="h-10 w-10 text-muted-foreground" />
                </div>
                <div className="space-y-2">
                  <p className="text-lg font-medium">No repositories found</p>
                  <p className="text-sm text-muted-foreground max-w-sm">
                    Clone a repository in GitHub Desktop to get started with VS Code
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {repositories.map((repo) => (
                <div
                  key={repo.id}
                  className="border rounded-lg p-4 hover:border-primary/50 transition-colors bg-card"
                >
                  <div className="space-y-3">
                    {/* Repository Header */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-3 flex-1 min-w-0">
                        <div className="mt-1">
                          <FolderGit2 className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold truncate">{repo.name}</h3>
                          <p className="text-xs text-muted-foreground truncate" title={repo.path}>
                            {repo.path}
                          </p>
                        </div>
                      </div>
                      {repo.vscodeRunning && (
                        <div className="flex items-center gap-1 text-xs text-green-500 bg-green-500/10 px-2 py-1 rounded">
                          <div className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
                          Running
                        </div>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Terminal className="h-3 w-3" />
                        {repo.type}
                      </div>
                      {repo.vscodePort && (
                        <div className="flex items-center gap-1">
                          Port {repo.vscodePort}
                        </div>
                      )}
                      {repo.lastOpened && (
                        <div className="flex items-center gap-1">
                          Opened {new Date(repo.lastOpened).toLocaleDateString()}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-2">
                      {repo.vscodeRunning ? (
                        <>
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => {
                              const hostname = window.location.hostname
                              window.open(`http://${hostname}/vscode/${repo.id}/`, '_blank', 'width=1600,height=1000')
                            }}
                          >
                            <ExternalLink className="mr-2 h-4 w-4" />
                            Open VS Code
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={async () => {
                              setSelectedRepo(repo.id)
                              await stopServer()
                            }}
                          >
                            <Square className="h-4 w-4" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          className="w-full"
                          disabled={loading && selectedRepo === repo.id}
                          onClick={async () => {
                            setSelectedRepo(repo.id)
                            await startServer()
                          }}
                        >
                          {loading && selectedRepo === repo.id ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Starting...
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              Start VS Code
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
        </div>

        {/* Process Manager Dialog */}
        <Dialog open={showProcessManager} onOpenChange={setShowProcessManager}>
          <DialogContent className="max-w-4xl max-h-[80vh]">
            <DialogHeader>
              <DialogTitle>Code-Server Process Manager</DialogTitle>
              <DialogDescription>
                View and manage all running code-server processes
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={loadProcesses}
                  disabled={loadingProcesses}
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${loadingProcesses ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={async () => {
                    if (confirm('Are you sure you want to kill ALL code-server processes? This will stop all running VS Code instances.')) {
                      await killAllProcesses()
                    }
                  }}
                  disabled={loadingProcesses || allProcesses.length === 0}
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Kill All Processes
                </Button>
              </div>

              {/* Process List */}
              {loadingProcesses ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : allProcesses.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No code-server processes running
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-muted sticky top-0">
                        <tr>
                          <th className="text-left p-3 font-medium">PID</th>
                          <th className="text-left p-3 font-medium">CPU %</th>
                          <th className="text-left p-3 font-medium">Memory %</th>
                          <th className="text-left p-3 font-medium">Port</th>
                          <th className="text-left p-3 font-medium">Command</th>
                          <th className="text-left p-3 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {allProcesses.map((proc, idx) => (
                          <tr key={idx} className="border-t hover:bg-muted/50">
                            <td className="p-3 font-mono text-xs">{proc.pid}</td>
                            <td className="p-3">{proc.cpu}</td>
                            <td className="p-3">{proc.mem}</td>
                            <td className="p-3 font-mono text-xs">
                              {proc.port || <span className="text-muted-foreground">-</span>}
                            </td>
                            <td className="p-3 max-w-md truncate" title={proc.command}>
                              <code className="text-xs">{proc.command}</code>
                            </td>
                            <td className="p-3">
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={async () => {
                                  if (confirm(`Kill process ${proc.pid}?`)) {
                                    await killProcess(proc.pid)
                                  }
                                }}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Info */}
              <div className="pt-4 border-t text-sm text-muted-foreground">
                <p>
                  This manager shows all running code-server processes on the system, including old or orphaned processes.
                  Use this to clean up any stuck or unwanted VS Code instances.
                </p>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Install Instructions Dialog */}
        <Dialog open={showInstallDialog} onOpenChange={setShowInstallDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Install code-server</DialogTitle>
              <DialogDescription>
                code-server is required to run VS Code in your browser
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <h3 className="font-semibold">Choose Installation Method:</h3>

                <div className="space-y-3">
                  {/* Option 1: Install Script */}
                  <div className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <p className="text-sm font-medium mb-1">Install Script (Recommended)</p>
                        <p className="text-xs text-muted-foreground mb-2">
                          Official installer - works on all Linux systems
                        </p>
                        <div className="bg-muted p-2 rounded font-mono text-xs">
                          curl -fsSL https://code-server.dev/install.sh | sh
                        </div>
                      </div>
                      <Button
                        onClick={() => handleInstall('script')}
                        disabled={installing}
                        size="sm"
                      >
                        {installing && installMethod === 'script' ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Installing...
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-4 w-4" />
                            Install
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Option 2: npm */}
                  <div className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <p className="text-sm font-medium mb-1">npm (Global)</p>
                        <p className="text-xs text-muted-foreground mb-2">
                          Install via npm package manager
                        </p>
                        <div className="bg-muted p-2 rounded font-mono text-xs">
                          npm install -g code-server
                        </div>
                      </div>
                      <Button
                        onClick={() => handleInstall('npm')}
                        disabled={installing}
                        size="sm"
                        variant="outline"
                      >
                        {installing && installMethod === 'npm' ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Installing...
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-4 w-4" />
                            Install
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Click "Install" to run the installation automatically in the background.
                  The app will start VS Code once installation completes.
                </p>
              </div>

              <div className="flex justify-between items-center">
                <a
                  href="https://github.com/coder/code-server"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-500 hover:underline flex items-center gap-1"
                >
                  View documentation
                  <ExternalLink className="h-3 w-3" />
                </a>
                <Button onClick={() => setShowInstallDialog(false)} variant="outline">
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    )
}
