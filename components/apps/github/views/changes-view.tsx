"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { FileEdit, FilePlus, FileX, Loader2, RotateCcw, History } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

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
  const [amendMode, setAmendMode] = useState(false)

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
      toast.error("Please enter a commit message")
      return
    }

    setCommitting(true)
    try {
      const command = amendMode
        ? `git commit --amend -m "${commitMessage.replace(/"/g, '\\"')}"`
        : `git commit -m "${commitMessage.replace(/"/g, '\\"')}"`

      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command,
        }),
      })

      const result = await response.json()
      if (result.success) {
        setCommitMessage("")
        setAmendMode(false)
        loadChanges()
        toast.success(amendMode ? "Commit amended successfully!" : "Commit successful!")
      } else {
        toast.error(`Commit failed: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Commit failed: ${error.message}`)
    } finally {
      setCommitting(false)
    }
  }

  const handleDiscardChanges = async (file: GitFile) => {
    if (!confirm(`Are you sure you want to discard changes in "${file.path}"? This cannot be undone.`)) {
      return
    }

    try {
      const command = file.status === 'untracked'
        ? `rm "${file.path}"`
        : `git restore "${file.path}"`

      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadChanges()
        toast.success("Changes discarded")
      } else {
        toast.error(`Failed to discard changes: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to discard changes: ${error.message}`)
    }
  }

  const handleDiscardAll = async () => {
    if (!confirm("Are you sure you want to discard ALL changes? This cannot be undone.")) {
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git restore .",
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadChanges()
        toast.success("All changes discarded")
      } else {
        toast.error(`Failed to discard changes: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to discard changes: ${error.message}`)
    }
  }

  const handleAmendLastCommit = async () => {
    try {
      // Get last commit message
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git log -1 --pretty=%B",
        }),
      })

      const result = await response.json()
      if (result.success) {
        setCommitMessage(result.output.trim())
        setAmendMode(true)
        toast.success("Ready to amend last commit")
      }
    } catch (error: any) {
      toast.error(`Failed to load commit message: ${error.message}`)
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
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={handleDiscardAll} className="text-destructive">
                    <RotateCcw className="h-4 w-4 mr-1" />
                    Discard All
                  </Button>
                  <Button variant="ghost" size="sm" onClick={stageAll}>
                    Stage All
                  </Button>
                </div>
              </div>
              <div className="space-y-1">
                {unstagedFiles.map((file) => (
                  <div
                    key={file.path}
                    className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer group"
                  >
                    <Checkbox
                      checked={file.staged}
                      onCheckedChange={() => toggleStageFile(file)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div className="flex-1 flex items-center gap-2" onClick={() => onFileSelect?.(file.path)}>
                      {getFileIcon(file.status)}
                      <span className="text-sm flex-1">{file.path}</span>
                      <span className="text-xs text-muted-foreground capitalize">{file.status}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDiscardChanges(file)
                      }}
                      className="opacity-0 group-hover:opacity-100 text-destructive"
                    >
                      <RotateCcw className="h-4 w-4" />
                    </Button>
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
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium">
            {amendMode ? "Amend Commit Message" : "Commit Message"}
          </label>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleAmendLastCommit}
            disabled={amendMode}
          >
            <History className="h-4 w-4 mr-1" />
            Amend Last
          </Button>
        </div>
        <Textarea
          placeholder="Commit message..."
          value={commitMessage}
          onChange={(e) => setCommitMessage(e.target.value)}
          rows={3}
          className="resize-none"
        />
        <div className="flex gap-2">
          {amendMode && (
            <Button
              variant="outline"
              onClick={() => {
                setAmendMode(false)
                setCommitMessage("")
              }}
            >
              Cancel Amend
            </Button>
          )}
          <Button
            className="flex-1"
            onClick={handleCommit}
            disabled={stagedFiles.length === 0 || committing}
          >
            {committing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {amendMode ? "Amend Commit" : "Commit"}
          </Button>
        </div>
      </div>
    </div>
  )
}
