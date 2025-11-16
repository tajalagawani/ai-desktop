"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Loader2, FolderOpen, Play, Square, RefreshCw, ExternalLink, Terminal } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export function CodeEditorApp() {
  const [serverUrl, setServerUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [folder, setFolder] = useState("/var/www")
  const [showInstallDialog, setShowInstallDialog] = useState(false)
  const [serverRunning, setServerRunning] = useState(false)

  useEffect(() => {
    checkServerStatus()
  }, [])

  const checkServerStatus = async () => {
    try {
      const response = await fetch("/api/code-server")
      const data = await response.json()

      if (data.success && data.servers.length > 0) {
        const server = data.servers[0]
        const hostname = window.location.hostname
        const serverUrl = `http://${hostname}:${server.port}`
        setServerUrl(serverUrl)
        setFolder(server.folder)
        setServerRunning(true)
      }
    } catch (error) {
      console.error("Failed to check server status:", error)
    }
  }

  const startServer = async () => {
    setLoading(true)
    try {
      const response = await fetch("/api/code-server", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "start",
          folder: folder,
          port: 8080
        })
      })

      const data = await response.json()

      if (data.success) {
        // Use current hostname instead of hardcoded localhost
        const hostname = window.location.hostname
        const serverUrl = `http://${hostname}:${data.port || 8080}`
        setServerUrl(serverUrl)
        setServerRunning(true)
        toast.success("VS Code started successfully!")
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
    try {
      const response = await fetch("/api/code-server", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "stop",
          folder: folder
        })
      })

      const data = await response.json()

      if (data.success) {
        setServerUrl(null)
        setServerRunning(false)
        toast.success("VS Code stopped")
      }
    } catch (error: any) {
      toast.error(`Failed to stop VS Code: ${error.message}`)
    }
  }

  const refreshServer = () => {
    if (serverUrl) {
      const iframe = document.getElementById('code-editor-iframe') as HTMLIFrameElement
      if (iframe) {
        iframe.src = iframe.src
      }
    }
  }

  if (!serverUrl) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background">
        <div className="max-w-md w-full p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="mx-auto w-16 h-16 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
              <Terminal className="h-8 w-8 text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold">VS Code Editor</h2>
            <p className="text-sm text-muted-foreground">
              Run a full VS Code instance in your browser
            </p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Folder to Open</label>
              <div className="flex gap-2">
                <Input
                  value={folder}
                  onChange={(e) => setFolder(e.target.value)}
                  placeholder="/path/to/folder"
                  className="flex-1"
                />
                <Button variant="outline" size="icon">
                  <FolderOpen className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <Button
              onClick={startServer}
              disabled={loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Starting VS Code...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-5 w-5" />
                  Start VS Code
                </>
              )}
            </Button>

            <div className="pt-4 border-t">
              <p className="text-xs text-muted-foreground text-center mb-2">
                Features included:
              </p>
              <ul className="text-xs text-muted-foreground space-y-1">
                <li>✅ Full VS Code UI and features</li>
                <li>✅ Integrated terminal</li>
                <li>✅ Git integration</li>
                <li>✅ Extensions support</li>
                <li>✅ IntelliSense & debugging</li>
                <li>✅ Multiple themes</li>
              </ul>
            </div>
          </div>
        </div>

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
                <h3 className="font-semibold">Installation Instructions:</h3>

                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium mb-2">Option 1: Install Script (Recommended)</p>
                    <div className="bg-muted p-3 rounded-lg font-mono text-sm">
                      curl -fsSL https://code-server.dev/install.sh | sh
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">Option 2: Homebrew (macOS)</p>
                    <div className="bg-muted p-3 rounded-lg font-mono text-sm">
                      brew install code-server
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">Option 3: npm (Global)</p>
                    <div className="bg-muted p-3 rounded-lg font-mono text-sm">
                      npm install -g code-server
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  After installation, restart this app and click "Start VS Code" again.
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
                <Button onClick={() => setShowInstallDialog(false)}>
                  Got it
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    )
  }

  return (
    <div className="h-full w-full flex flex-col bg-background">
      {/* Control Bar */}
      <div className="border-b border-border bg-muted/30 p-2 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 rounded-md text-sm">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
            Running
          </div>
          <span className="text-sm text-muted-foreground">
            {folder}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshServer}
            title="Refresh"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.open(serverUrl, '_blank')}
            title="Open in new window"
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={stopServer}
            className="text-destructive"
            title="Stop server"
          >
            <Square className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* VS Code iframe */}
      <iframe
        id="code-editor-iframe"
        src={serverUrl}
        className="flex-1 w-full border-0"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-downloads"
        title="VS Code Editor"
      />
    </div>
  )
}
