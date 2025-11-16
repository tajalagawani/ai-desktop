"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { GitCommit, User, Calendar, Loader2 } from "lucide-react"

interface HistoryViewProps {
  currentRepo: string
}

interface Commit {
  hash: string
  author: string
  date: string
  message: string
}

export function HistoryView({ currentRepo }: HistoryViewProps) {
  const [commits, setCommits] = useState<Commit[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [currentRepo])

  const loadHistory = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: 'git log --pretty=format:"%H|||%an|||%ar|||%s" -n 50',
        }),
      })

      const result = await response.json()
      if (result.success && result.output) {
        const parsedCommits = result.output.split('\n').filter((line: string) => line.trim()).map((line: string) => {
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
            {commits.map((commit) => (
              <div
                key={commit.hash}
                className="border border-border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
              >
                <div className="flex items-start gap-3">
                  <GitCommit className="h-5 w-5 text-muted-foreground mt-0.5" />
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
            ))}
          </div>
        )}
      </div>
    </ScrollArea>
  )
}
