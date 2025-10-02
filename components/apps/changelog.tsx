"use client"

import { useEffect, useState } from "react"
import { GitCommit, Clock, User, ExternalLink, RefreshCw, Download, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface ChangelogEntry {
  sha: string
  message: string
  author: string
  date: string
  url: string
}

export function Changelog() {
  const [changelog, setChangelog] = useState<ChangelogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentVersion, setCurrentVersion] = useState<string>("")
  const [buildDate, setBuildDate] = useState<string>("")
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [latestSHA, setLatestSHA] = useState<string>("")
  const [currentSHA, setCurrentSHA] = useState<string>("")
  const [updating, setUpdating] = useState(false)
  const [updateMessage, setUpdateMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchChangelog()
  }, [])

  const fetchChangelog = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/changelog')
      const data = await response.json()

      if (data.success) {
        setChangelog(data.changelog)
        setCurrentVersion(data.currentVersion)
        setBuildDate(data.buildDate)
        setUpdateAvailable(data.updateAvailable)
        setLatestSHA(data.latestSHA)
        setCurrentSHA(data.currentSHA)
      } else {
        setError('Failed to load changelog')
      }
    } catch (err) {
      setError('Failed to fetch changelog')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    setUpdating(true)
    setUpdateMessage(null)
    try {
      const response = await fetch('/api/update', { method: 'POST' })
      const data = await response.json()

      if (data.success) {
        setUpdateMessage('✅ Update completed successfully! The app will reload in 3 seconds...')
        setTimeout(() => {
          window.location.reload()
        }, 3000)
      } else {
        setUpdateMessage(`❌ Update failed: ${data.error}`)
      }
    } catch (err) {
      setUpdateMessage('❌ Failed to trigger update')
    } finally {
      setUpdating(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 7) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    } else if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} ago`
    } else if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ago`
    } else {
      return 'Just now'
    }
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header with Version Info */}
      <div className="border-b border-border bg-card/50">
        <div className="flex items-center justify-between p-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <GitCommit className="w-5 h-5 text-foreground" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-semibold text-foreground">Recent Updates</h2>
                <Badge variant="secondary" className="font-mono text-xs">
                  v{currentVersion}
                </Badge>
                {updateAvailable && (
                  <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20">
                    Update Available
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                Build: {buildDate} • Commit: {currentSHA || 'Unknown'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {updateAvailable && !updating && (
              <Button
                onClick={handleUpdate}
                variant="default"
                size="sm"
                className="gap-2 bg-green-600 hover:bg-green-700 text-white"
              >
                <Download className="w-4 h-4" />
                Update Now
              </Button>
            )}
            <Button
              onClick={fetchChangelog}
              variant="outline"
              size="sm"
              disabled={loading}
              className="gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Update Status Banner */}
        {updateMessage && (
          <div className={`px-6 py-3 border-t border-border ${
            updateMessage.startsWith('✅') ? 'bg-green-500/10' : 'bg-red-500/10'
          }`}>
            <p className={`text-sm ${
              updateMessage.startsWith('✅') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
              {updateMessage}
            </p>
          </div>
        )}

        {/* Updating Progress */}
        {updating && (
          <div className="px-6 py-4 bg-muted/50 border-t border-border">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground">Updating application...</p>
                <p className="text-xs text-muted-foreground">Please wait while we update to the latest version</p>
              </div>
            </div>
          </div>
        )}

        {/* Version Comparison */}
        {updateAvailable && !updating && (
          <div className="px-6 py-4 bg-muted/30 border-t border-border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground mb-1">New Version Available!</p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    Current: <code className="font-mono bg-muted px-1 rounded">{currentSHA}</code>
                  </span>
                  <span>→</span>
                  <span className="flex items-center gap-1">
                    Latest: <code className="font-mono bg-muted px-1 rounded text-green-600">{latestSHA}</code>
                  </span>
                </div>
              </div>
              <AlertCircle className="w-5 h-5 text-green-600" />
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-border border-t-foreground rounded-full animate-spin" />
              <p className="text-sm text-muted-foreground">Loading changelog...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-destructive mb-2">{error}</p>
              <Button onClick={fetchChangelog} variant="outline" size="sm">
                Retry
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl mx-auto">
            {changelog.map((entry, index) => (
              <div
                key={entry.sha}
                className="group relative p-6 rounded-lg bg-card border border-border hover:border-foreground/20 hover:bg-card/80 transition-all duration-200"
              >
                {/* Commit Info */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="mt-1 p-2 rounded-md bg-muted">
                        <GitCommit className="w-4 h-4 text-muted-foreground" />
                      </div>
                      <div className="flex-1">
                        <p className="text-foreground font-medium mb-2 leading-relaxed">
                          {entry.message}
                        </p>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1.5">
                            <User className="w-3.5 h-3.5" />
                            <span className="font-medium">{entry.author}</span>
                          </span>
                          <span className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5" />
                            {formatDate(entry.date)}
                          </span>
                          <span className="font-mono text-xs bg-muted px-2.5 py-1 rounded-md border border-border">
                            {entry.sha}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <a
                    href={entry.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-muted rounded-lg"
                    title="View on GitHub"
                  >
                    <ExternalLink className="w-4 h-4 text-muted-foreground" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border bg-card/50">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Showing last {changelog.length} commits</span>
          <span className="flex items-center gap-2">
            {!updateAvailable ? (
              <>
                <CheckCircle className="w-3 h-3 text-green-600" />
                <span>You're up to date</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3 text-yellow-600" />
                <span>{changelog.length} new updates available</span>
              </>
            )}
          </span>
        </div>
      </div>
    </div>
  )
}
