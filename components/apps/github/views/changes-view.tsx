"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { FileEdit, FilePlus, FileX, Loader2 } from "lucide-react"

interface ChangesViewProps {
  currentRepo: string
  onFileSelect?: (file: string) => void
}

interface GitFile {
  path: string
  status: "modified" | "added" | "deleted" | "untracked"
  staged: boolean
}

export function ChangesView({ currentRepo, onFileSelect }: ChangesViewProps) {
  const [files, setFiles] = useState<GitFile[]>([])
  const [loading, setLoading] = useState(true)
  const [commitMessage, setCommitMessage] = useState("")
  const [committing, setCommitting] = useState(false)

  useEffect(() => {
    loadChanges()
  }, [currentRepo])

  const loadChanges = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      // Get status
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git status --porcelain",
        }),
      })

      const result = await response.json()
      if (result.success) {
        const parsedFiles = parseGitStatus(result.output)
        setFiles(parsedFiles)
      }
    } catch (error) {
      console.error("Failed to load changes:", error)
    } finally {
      setLoading(false)
    }
  }

  const parseGitStatus = (output: string): GitFile[] => {
    if (!output.trim()) return []

    return output.split('\n').filter(line => line.trim()).map(line => {
      const status = line.substring(0, 2)
      const path = line.substring(3)

      let fileStatus: GitFile['status'] = 'modified'
      let staged = false

      if (status[0] === 'M' || status[1] === 'M') fileStatus = 'modified'
      if (status[0] === 'A' || status[1] === 'A') fileStatus = 'added'
      if (status[0] === 'D' || status[1] === 'D') fileStatus = 'deleted'
      if (status === '??') fileStatus = 'untracked'

      if (status[0] !== ' ' && status[0] !== '?') staged = true

      return { path, status: fileStatus, staged }
    })
  }

  const toggleStageFile = async (file: GitFile) => {
    try {
      const command = file.staged
        ? `git restore --staged "${file.path}"`
        : `git add "${file.path}"`

      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command,
        }),
      })

      if (response.ok) {
        loadChanges()
      }
    } catch (error) {
      console.error("Failed to stage/unstage file:", error)
    }
  }

  const stageAll = async () => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git add -A",
        }),
      })

      if (response.ok) {
        loadChanges()
      }
    } catch (error) {
      console.error("Failed to stage all:", error)
    }
  }

  const handleCommit = async () => {
    if (!commitMessage.trim()) {
      alert("Please enter a commit message")
      return
    }

    setCommitting(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git commit -m "${commitMessage.replace(/"/g, '\\"')}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        setCommitMessage("")
        loadChanges()
        alert("Commit successful!")
      } else {
        alert(`Commit failed: ${result.error}`)
      }
    } catch (error: any) {
      alert(`Commit failed: ${error.message}`)
    } finally {
      setCommitting(false)
    }
  }

  const getFileIcon = (status: GitFile['status']) => {
    switch (status) {
      case 'added':
        return <FilePlus className="h-4 w-4 text-green-500" />
      case 'deleted':
        return <FileX className="h-4 w-4 text-red-500" />
      case 'modified':
      case 'untracked':
        return <FileEdit className="h-4 w-4 text-yellow-500" />
    }
  }

  const stagedFiles = files.filter(f => f.staged)
  const unstagedFiles = files.filter(f => !f.staged)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Changes List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* Staged Changes */}
          {stagedFiles.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">Staged Changes ({stagedFiles.length})</h3>
              </div>
              <div className="space-y-1">
                {stagedFiles.map((file) => (
                  <div
                    key={file.path}
                    className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer group"
                    onClick={() => onFileSelect?.(file.path)}
                  >
                    <Checkbox
                      checked={file.staged}
                      onCheckedChange={() => toggleStageFile(file)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    {getFileIcon(file.status)}
                    <span className="text-sm flex-1">{file.path}</span>
                    <span className="text-xs text-muted-foreground capitalize">{file.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Unstaged Changes */}
          {unstagedFiles.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">Changes ({unstagedFiles.length})</h3>
                <Button variant="ghost" size="sm" onClick={stageAll}>
                  Stage All
                </Button>
              </div>
              <div className="space-y-1">
                {unstagedFiles.map((file) => (
                  <div
                    key={file.path}
                    className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer group"
                    onClick={() => onFileSelect?.(file.path)}
                  >
                    <Checkbox
                      checked={file.staged}
                      onCheckedChange={() => toggleStageFile(file)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    {getFileIcon(file.status)}
                    <span className="text-sm flex-1">{file.path}</span>
                    <span className="text-xs text-muted-foreground capitalize">{file.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {files.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No changes detected</p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Commit Panel */}
      <div className="border-t border-border p-4 space-y-3">
        <Textarea
          placeholder="Commit message..."
          value={commitMessage}
          onChange={(e) => setCommitMessage(e.target.value)}
          rows={3}
          className="resize-none"
        />
        <Button
          className="w-full"
          onClick={handleCommit}
          disabled={stagedFiles.length === 0 || committing}
        >
          {committing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Commit to {currentRepo ? 'main' : 'branch'}
        </Button>
      </div>
    </div>
  )
}
