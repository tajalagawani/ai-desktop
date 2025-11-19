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
  const [clonePath, setClonePath] = useState('/var/www/repositories/')
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

      // First, ensure the parent directory exists
      const parentDir = clonePath.endsWith('/') ? clonePath.slice(0, -1) : clonePath
      try {
        const mkdirResponse = await fetch("/api/files", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: "create-folder",
            path: parentDir,
          }),
        })

        const mkdirResult = await mkdirResponse.json()
        // Ignore error if directory already exists
        if (!mkdirResponse.ok && !mkdirResult.error?.includes('exists')) {
          console.warn('Failed to create directory:', mkdirResult.error)
          // Continue anyway, maybe it already exists
        }
      } catch (mkdirError) {
        console.warn('Failed to create directory:', mkdirError)
        // Continue anyway
      }

      // Prepare clone command
      let command = `clone ${cloneUrl} ${fullPath}`

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
            command = `clone ${urlWithToken} ${fullPath}`
            console.log('Using GitHub token for authentication')
          } else {
            setError("GitHub token not found in settings. Please add your token in Settings.")
            return
          }
        } else {
          setError("GitHub token not found in settings. Please add your token in Settings.")
          return
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

      // Add to saved repositories (localStorage - kept for backward compatibility)
      const savedRepos = JSON.parse(localStorage.getItem("git-repositories") || "[]")
      if (!savedRepos.includes(fullPath)) {
        savedRepos.push(fullPath)
        localStorage.setItem("git-repositories", JSON.stringify(savedRepos))
      }

      // Add to centralized repository registry
      try {
        // Find an available port starting from 8100
        const portResponse = await fetch("/api/repositories")
        const portData = await portResponse.json()
        const usedPorts = portData.repositories?.map((r: any) => r.port) || []
        let port = 8100
        while (usedPorts.includes(port)) {
          port++
        }

        const repoResponse = await fetch("/api/repositories", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: repoName,
            path: fullPath,
            type: "git",
            port: port,
            url: cloneUrl,
            branch: "main"
          })
        })

        const repoResult = await repoResponse.json()
        if (repoResult.success) {
          console.log(`Added ${repoName} to centralized repository registry (port ${port})`)
        } else {
          console.error("Failed to add to repository registry:", repoResult.error)
        }
      } catch (error) {
        console.error("Failed to add to repository registry:", error)
        // Continue anyway, localStorage backup exists
      }

      onCloneComplete(fullPath)
      onOpenChange(false)

      // Reset form
      setCloneUrl("")
      setClonePath('/var/www/repositories/')
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
                placeholder="/var/www/repositories/"
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
