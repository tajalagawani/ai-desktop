"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Archive, Play, Trash2, Loader2 } from "lucide-react"

interface StashesViewProps {
  currentRepo: string
}

interface Stash {
  index: number
  name: string
  message: string
}

export function StashesView({ currentRepo }: StashesViewProps) {
  const [stashes, setStashes] = useState<Stash[]>([])
  const [loading, setLoading] = useState(true)
  const [stashMessage, setStashMessage] = useState("")
  const [stashing, setStashing] = useState(false)

  useEffect(() => {
    loadStashes()
  }, [currentRepo])

  const loadStashes = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git stash list",
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const parsedStashes = output.split('\n')
          .filter((line: string) => line.trim())
          .map((line: string, index: number) => {
            // Format: stash@{0}: WIP on branch: message
            const match = line.match(/stash@\{(\d+)\}: (.+)/)
            return {
              index: match ? parseInt(match[1]) : index,
              name: `stash@{${match ? match[1] : index}}`,
              message: match ? match[2] : line
            }
          })
        setStashes(parsedStashes)
      }
    } catch (error) {
      console.error("Failed to load stashes:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStash = async () => {
    setStashing(true)
    try {
      const command = stashMessage.trim()
        ? `git stash push -m "${stashMessage}"`
        : "git stash"

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
        setStashMessage("")
        loadStashes()
      } else {
        toast.error(`Failed to create stash: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to create stash: ${error.message}`)
    } finally {
      setStashing(false)
    }
  }

  const handleApplyStash = async (stashName: string) => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git stash apply ${stashName}`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success("Stash applied successfully!")
      } else {
        toast.error(`Failed to apply stash: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to apply stash: ${error.message}`)
    }
  }

  const handlePopStash = async (stashName: string) => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git stash pop ${stashName}`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadStashes()
        toast.success("Stash popped successfully!")
      } else {
        toast.error(`Failed to pop stash: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to pop stash: ${error.message}`)
    }
  }

  const handleDropStash = async (stashName: string) => {
    if (!confirm(`Are you sure you want to delete ${stashName}?`)) {
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git stash drop ${stashName}`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadStashes()
      } else {
        toast.error(`Failed to drop stash: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to drop stash: ${error.message}`)
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
      <div className="p-4 space-y-4">
        {/* Create Stash */}
        <div className="space-y-2">
          <Input
            placeholder="Stash message (optional)..."
            value={stashMessage}
            onChange={(e) => setStashMessage(e.target.value)}
          />
          <Button onClick={handleCreateStash} disabled={stashing} className="w-full">
            {stashing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Archive className="mr-2 h-4 w-4" />}
            Create Stash
          </Button>
        </div>

        {/* Stashes List */}
        <div className="space-y-2">
          {stashes.map((stash) => (
            <div
              key={stash.name}
              className="border border-border rounded-lg p-3 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Archive className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium font-mono">{stash.name}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{stash.message}</p>
                </div>

                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleApplyStash(stash.name)}
                    title="Apply stash (keep in list)"
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handlePopStash(stash.name)}
                    title="Pop stash (apply and remove)"
                  >
                    <Play className="h-4 w-4 fill-current" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDropStash(stash.name)}
                    title="Delete stash"
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {stashes.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">No stashes found</p>
          </div>
        )}
      </div>
    </ScrollArea>
  )
}
