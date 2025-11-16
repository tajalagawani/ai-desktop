"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { X, Loader2 } from "lucide-react"

interface GitHubDiffPanelProps {
  file: string
  currentRepo: string | null
  onClose: () => void
}

export function GitHubDiffPanel({ file, currentRepo, onClose }: GitHubDiffPanelProps) {
  const [diff, setDiff] = useState<string>("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDiff()
  }, [file, currentRepo])

  const loadDiff = async () => {
    if (!currentRepo || !file) return

    setLoading(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git diff HEAD -- "${file}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        setDiff(result.output || "No changes")
      }
    } catch (error) {
      console.error("Failed to load diff:", error)
      setDiff("Error loading diff")
    } finally {
      setLoading(false)
    }
  }

  const renderDiffLine = (line: string, index: number) => {
    let className = "font-mono text-xs px-3 py-0.5"

    if (line.startsWith('+') && !line.startsWith('+++')) {
      className += " bg-green-500/10 text-green-600 dark:text-green-400"
    } else if (line.startsWith('-') && !line.startsWith('---')) {
      className += " bg-red-500/10 text-red-600 dark:text-red-400"
    } else if (line.startsWith('@@')) {
      className += " bg-blue-500/10 text-blue-600 dark:text-blue-400 font-semibold"
    } else if (line.startsWith('diff') || line.startsWith('index') || line.startsWith('---') || line.startsWith('+++')) {
      className += " text-muted-foreground"
    }

    return (
      <div key={index} className={className}>
        {line || ' '}
      </div>
    )
  }

  return (
    <div className="w-[500px] border-l border-border bg-background flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold truncate">{file}</h3>
          <p className="text-xs text-muted-foreground">Diff</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Diff Content */}
      <ScrollArea className="flex-1">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : diff === "No changes" ? (
          <div className="p-4 text-center text-muted-foreground">
            <p className="text-sm">No changes to display</p>
          </div>
        ) : (
          <div className="py-2">
            {diff.split('\n').map((line, index) => renderDiffLine(line, index))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
