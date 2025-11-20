"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { GitCommit, User, Calendar, Loader2, FileText, Plus, Minus, ChevronDown, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/utils/api"

interface HistoryViewProps {
  currentRepo: string
}

interface Commit {
  hash: string
  author: string
  date: string
  message: string
}

interface CommitStats {
  filesChanged: number
  insertions: number
  deletions: number
  files: {
    path: string
    additions: number
    deletions: number
  }[]
}

export function HistoryView({ currentRepo }: HistoryViewProps) {
  const [commits, setCommits] = useState<Commit[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedCommit, setExpandedCommit] = useState<string | null>(null)
  const [commitStats, setCommitStats] = useState<Record<string, CommitStats>>({})

  useEffect(() => {
    loadHistory()
  }, [currentRepo])

  const loadHistory = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      const response = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: 'git log --pretty=format:"%H|||%an|||%ar|||%s" -n 50',
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const parsedCommits = output.split('\n').filter((line: string) => line.trim()).map((line: string) => {
          const [hash, author, date, message] = line.split('|||')
          return { hash, author, date, message }
        })
        setCommits(parsedCommits)
      }
    } catch (error) {
      console.error("Failed to load history:", error)
    } finally {
      setLoading(false)
    }
  }

  const loadCommitStats = async (hash: string) => {
    if (commitStats[hash]) return

    try {
      // Get commit stats
      const response = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git show ${hash} --stat --format=""`,
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const lines = output.trim().split('\n')
        const files: CommitStats['files'] = []
        let totalInsertions = 0
        let totalDeletions = 0

        // Parse each file line
        for (const line of lines) {
          if (!line.trim()) continue

          // Match pattern like: "file.ts | 10 +++++-----"
          const match = line.match(/^\s*(.+?)\s+\|\s+(\d+)\s+([+-]+)/)
          if (match) {
            const [, path, changes, symbols] = match
            const additions = (symbols.match(/\+/g) || []).length
            const deletions = (symbols.match(/-/g) || []).length

            files.push({
              path: path.trim(),
              additions,
              deletions
            })

            totalInsertions += additions
            totalDeletions += deletions
          }
        }

        setCommitStats(prev => ({
          ...prev,
          [hash]: {
            filesChanged: files.length,
            insertions: totalInsertions,
            deletions: totalDeletions,
            files
          }
        }))
      }
    } catch (error) {
      console.error("Failed to load commit stats:", error)
    }
  }

  const toggleCommitExpand = (hash: string) => {
    if (expandedCommit === hash) {
      setExpandedCommit(null)
    } else {
      setExpandedCommit(hash)
      loadCommitStats(hash)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        {commits.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">No commit history found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {commits.map((commit) => {
              const isExpanded = expandedCommit === commit.hash
              const stats = commitStats[commit.hash]

              return (
                <div
                  key={commit.hash}
                  className="border border-border rounded-lg overflow-hidden hover:bg-muted/50 transition-colors"
                >
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => toggleCommitExpand(commit.hash)}
                  >
                    <div className="flex items-start gap-3">
                      {isExpanded ? (
                        <ChevronDown className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                      )}
                      <GitCommit className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                      <div className="flex-1 space-y-2">
                        <p className="text-sm font-medium">{commit.message}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {commit.author}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {commit.date}
                          </div>
                          <div className="font-mono">{commit.hash.substring(0, 7)}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="border-t border-border bg-muted/30 p-4">
                      {stats ? (
                        <div className="space-y-3">
                          {/* Summary Stats */}
                          <div className="flex items-center gap-4 text-sm">
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 text-muted-foreground" />
                              <span className="font-medium">{stats.filesChanged}</span>
                              <span className="text-muted-foreground">
                                {stats.filesChanged === 1 ? 'file' : 'files'} changed
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Plus className="h-4 w-4 text-green-500" />
                              <span className="font-medium text-green-500">{stats.insertions}</span>
                              <span className="text-muted-foreground">additions</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Minus className="h-4 w-4 text-red-500" />
                              <span className="font-medium text-red-500">{stats.deletions}</span>
                              <span className="text-muted-foreground">deletions</span>
                            </div>
                          </div>

                          {/* File List */}
                          <div className="space-y-1">
                            {stats.files.map((file, idx) => (
                              <div
                                key={idx}
                                className="flex items-center gap-2 text-xs p-2 rounded hover:bg-background/50"
                              >
                                <FileText className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                                <span className="flex-1 font-mono">{file.path}</span>
                                <div className="flex items-center gap-2">
                                  {file.additions > 0 && (
                                    <span className="text-green-500">+{file.additions}</span>
                                  )}
                                  {file.deletions > 0 && (
                                    <span className="text-red-500">-{file.deletions}</span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center py-4">
                          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </ScrollArea>
  )
}
