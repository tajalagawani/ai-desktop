"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { GitBranch, FolderOpen, Loader2 } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface CloneDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCloneComplete: (repoPath: string) => void
}

export function CloneDialog({ open, onOpenChange, onCloneComplete }: CloneDialogProps) {
  const [cloneUrl, setCloneUrl] = useState("")
  const [clonePath, setClonePath] = useState("/var/www/")
  const [authMethod, setAuthMethod] = useState<"https" | "ssh">("https")
  const [cloning, setCloning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleClone = async () => {
    setCloning(true)
    setError(null)

    try {
      // Extract repo name from URL for the folder name
      const repoName = cloneUrl.split('/').pop()?.replace('.git', '') || 'repo'
      const fullPath = `${clonePath}${repoName}`

      // Prepare clone command
      let command = `git clone ${cloneUrl} ${fullPath}`

      // If using HTTPS, try to use stored token
      if (authMethod === "https") {
        const settings = localStorage.getItem("git-settings")
        if (settings) {
          const parsed = JSON.parse(settings)
          if (parsed.githubToken) {
            // Insert token into HTTPS URL
            const urlWithToken = cloneUrl.replace(
              'https://',
              `https://${parsed.githubToken}@`
            )
            command = `git clone ${urlWithToken} ${fullPath}`
          }
        }
      }

      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: "/tmp", // Execute from temp directory
          command: command,
        }),
      })

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || "Failed to clone repository")
      }

      // Add to saved repositories
      const savedRepos = JSON.parse(localStorage.getItem("git-repositories") || "[]")
      if (!savedRepos.includes(fullPath)) {
        savedRepos.push(fullPath)
        localStorage.setItem("git-repositories", JSON.stringify(savedRepos))
      }

      onCloneComplete(fullPath)
      onOpenChange(false)

      // Reset form
      setCloneUrl("")
      setClonePath("/var/www/")
    } catch (error: any) {
      setError(error.message || "Failed to clone repository")
    } finally {
      setCloning(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Clone Repository
          </DialogTitle>
          <DialogDescription>
            Clone a Git repository from GitHub or other Git hosting service.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="clone-url">Repository URL</Label>
            <Input
              id="clone-url"
              placeholder="https://github.com/username/repo.git or git@github.com:username/repo.git"
              value={cloneUrl}
              onChange={(e) => setCloneUrl(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Authentication Method</Label>
            <RadioGroup value={authMethod} onValueChange={(v) => setAuthMethod(v as any)}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="https" id="https" />
                <Label htmlFor="https" className="font-normal cursor-pointer">
                  HTTPS (uses GitHub token from settings)
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="ssh" id="ssh" />
                <Label htmlFor="ssh" className="font-normal cursor-pointer">
                  SSH (uses SSH keys from settings)
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="clone-path">Clone to Directory</Label>
            <div className="flex gap-2">
              <Input
                id="clone-path"
                placeholder="/var/www/"
                value={clonePath}
                onChange={(e) => setClonePath(e.target.value)}
              />
              <Button variant="outline" size="icon">
                <FolderOpen className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Repository will be cloned to: {clonePath}{cloneUrl.split('/').pop()?.replace('.git', '')}
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={cloning}>
            Cancel
          </Button>
          <Button onClick={handleClone} disabled={cloning || !cloneUrl}>
            {cloning && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {cloning ? "Cloning..." : "Clone Repository"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
