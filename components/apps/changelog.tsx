"use client"

import { useEffect, useState } from "react"
import { Clock, User, ExternalLink, RefreshCw, Download, CheckCircle, Loader2 } from "lucide-react"
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
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [latestSHA, setLatestSHA] = useState<string>("")
  const [currentSHA, setCurrentSHA] = useState<string>("")
  const [lastUpdated, setLastUpdated] = useState<string>("")
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
        setUpdateAvailable(data.updateAvailable)
        setLatestSHA(data.latestSHA)
        setCurrentSHA(data.currentSHA)
        setLastUpdated(data.lastUpdated)
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
        setUpdateMessage('Update completed successfully! Reloading in 3 seconds...')
        setTimeout(() => {
          window.location.reload()
        }, 3000)
      } else {
        setUpdateMessage(`Update failed: ${data.error}`)
      }
    } catch (err) {
      setUpdateMessage('Failed to trigger update')
    } finally {
      setUpdating(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 7) {
      return formatDate(dateString)
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
      {/* Simple Header */}
      <div className="border-b border-border">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">Changelog</h1>
              <p className="text-muted-foreground">
                {currentSHA ? `Currently on ${currentSHA}` : 'Not deployed'} • v{currentVersion}
              </p>
            </div>
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

          {/* Version Status Banner */}
          {!updating && currentSHA && (
            <div className={`p-4 border rounded-lg ${
              updateAvailable
                ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900'
                : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {updateAvailable ? (
                      <Download className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                    )}
                    <p className={`font-medium ${
                      updateAvailable
                        ? 'text-blue-900 dark:text-blue-100'
                        : 'text-green-900 dark:text-green-100'
                    }`}>
                      {updateAvailable ? 'Update Available' : 'Up to Date'}
                    </p>
                  </div>
                  <p className={`text-sm ${
                    updateAvailable
                      ? 'text-blue-700 dark:text-blue-300'
                      : 'text-green-700 dark:text-green-300'
                  }`}>
                    {updateAvailable ? (
                      <>New version {latestSHA} is available</>
                    ) : (
                      <>You're running the latest version {currentSHA}</>
                    )}
                    {lastUpdated && ` • Last updated ${lastUpdated}`}
                  </p>
                </div>
                {updateAvailable && (
                  <Button
                    onClick={handleUpdate}
                    size="sm"
                    className="gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Update Now
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Not Deployed Banner */}
          {!updating && !currentSHA && (
            <div className="p-4 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-900 rounded-lg">
              <div className="flex items-center gap-2">
                <ExternalLink className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                  Not deployed yet • Latest version {latestSHA} is available
                </p>
              </div>
            </div>
          )}

          {/* Updating State */}
          {updating && (
            <div className="p-4 bg-muted/50 border border-border rounded-lg">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-foreground">Updating application...</p>
                  <p className="text-xs text-muted-foreground">This may take a few moments</p>
                </div>
              </div>
            </div>
          )}

          {/* Update Message */}
          {updateMessage && (
            <div className={`p-4 border rounded-lg ${
              updateMessage.includes('success')
                ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900'
                : 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900'
            }`}>
              <p className={`text-sm ${
                updateMessage.includes('success')
                  ? 'text-green-900 dark:text-green-100'
                  : 'text-red-900 dark:text-red-100'
              }`}>
                {updateMessage}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Loading changelog...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <p className="text-destructive mb-4">{error}</p>
                <Button onClick={fetchChangelog} variant="outline" size="sm">
                  Try Again
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-12">
              {changelog.map((entry, index) => (
                <article key={entry.sha} className="relative">
                  {/* Timeline connector */}
                  {index !== changelog.length - 1 && (
                    <div className="absolute left-[7px] top-10 bottom-0 w-[2px] bg-border" />
                  )}

                  <div className="relative flex gap-6">
                    {/* Timeline dot */}
                    <div className="relative flex-shrink-0">
                      <div className="w-4 h-4 rounded-full border-2 border-border bg-background mt-2" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0 pb-2">
                      {/* Date */}
                      <time className="text-sm text-muted-foreground mb-2 block">
                        {formatDate(entry.date)}
                      </time>

                      {/* Title/Message */}
                      <h2 className="text-2xl font-bold text-foreground mb-3 leading-snug">
                        {entry.message}
                      </h2>

                      {/* Meta Info */}
                      <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                        <span className="flex items-center gap-1.5">
                          <User className="w-3.5 h-3.5" />
                          {entry.author}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5" />
                          {formatRelativeTime(entry.date)}
                        </span>
                        <Badge variant="outline" className="font-mono text-xs">
                          {entry.sha}
                        </Badge>
                      </div>

                      {/* GitHub Link */}
                      <a
                        href={entry.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        View on GitHub
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      {!loading && !error && (
        <div className="border-t border-border">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Showing {changelog.length} recent updates</span>
              {!updateAvailable && currentSHA && (
                <span className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  You're up to date
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
