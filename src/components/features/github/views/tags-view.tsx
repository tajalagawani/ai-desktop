"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tag, Plus, Trash2, Loader2, Upload } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface TagsViewProps {
  currentRepo: string
}

interface GitTag {
  name: string
  commit: string
}

export function TagsView({ currentRepo }: TagsViewProps) {
  const [tags, setTags] = useState<GitTag[]>([])
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newTagName, setNewTagName] = useState("")
  const [tagMessage, setTagMessage] = useState("")

  useEffect(() => {
    loadTags()
  }, [currentRepo])

  const loadTags = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git tag -l --format='%(refname:short)|||%(objectname:short)'",
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const parsedTags = output.split('\n')
          .filter((line: string) => line.trim())
          .map((line: string) => {
            const [name, commit] = line.split('|||')
            return { name, commit }
          })
        setTags(parsedTags)
      }
    } catch (error) {
      console.error("Failed to load tags:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      toast.error("Please enter a tag name")
      return
    }

    try {
      const command = tagMessage.trim()
        ? `git tag -a "${newTagName}" -m "${tagMessage}"`
        : `git tag "${newTagName}"`

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
        setNewTagName("")
        setTagMessage("")
        setCreateDialogOpen(false)
        loadTags()
        toast.success(`Tag ${newTagName} created!`)
      } else {
        toast.error(`Failed to create tag: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to create tag: ${error.message}`)
    }
  }

  const handleDeleteTag = async (tagName: string) => {
    if (!confirm(`Are you sure you want to delete tag "${tagName}"?`)) {
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git tag -d "${tagName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadTags()
        toast.success(`Tag ${tagName} deleted!`)
      } else {
        toast.error(`Failed to delete tag: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to delete tag: ${error.message}`)
    }
  }

  const handlePushTag = async (tagName: string) => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git push origin "${tagName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success(`Tag ${tagName} pushed to remote!`)
      } else {
        toast.error(`Failed to push tag: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to push tag: ${error.message}`)
    }
  }

  const handlePushAllTags = async () => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git push origin --tags",
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success("All tags pushed to remote!")
      } else {
        toast.error(`Failed to push tags: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to push tags: ${error.message}`)
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
    <>
      <ScrollArea className="h-full">
        <div className="p-4 space-y-4">
          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={() => setCreateDialogOpen(true)} className="flex-1">
              <Plus className="mr-2 h-4 w-4" />
              Create Tag
            </Button>
            <Button
              variant="outline"
              onClick={handlePushAllTags}
              disabled={tags.length === 0}
            >
              <Upload className="h-4 w-4" />
            </Button>
          </div>

          {/* Tags List */}
          <div className="space-y-2">
            {tags.map((tag) => (
              <div
                key={tag.name}
                className="border border-border rounded-lg p-3 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Tag className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">{tag.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground font-mono">{tag.commit}</p>
                  </div>

                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePushTag(tag.name)}
                      title="Push tag to remote"
                    >
                      <Upload className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteTag(tag.name)}
                      title="Delete tag"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {tags.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No tags found</p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Create Tag Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Tag</DialogTitle>
            <DialogDescription>
              Create a new tag at the current commit
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Tag Name</label>
              <Input
                placeholder="v1.0.0"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !tagMessage && handleCreateTag()}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Message (optional)</label>
              <Input
                placeholder="Release version 1.0.0"
                value={tagMessage}
                onChange={(e) => setTagMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreateTag()}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateTag}>
              Create Tag
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
