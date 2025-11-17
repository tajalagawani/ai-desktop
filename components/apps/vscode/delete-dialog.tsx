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
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, AlertTriangle } from "lucide-react"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { toast } from "sonner"

interface DeleteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onDeleteComplete: () => void
  repoId: string
  repoName: string
  repoPath: string
}

export function DeleteDialog({
  open,
  onOpenChange,
  onDeleteComplete,
  repoId,
  repoName,
  repoPath
}: DeleteDialogProps) {
  const [deleteOption, setDeleteOption] = useState<"registry" | "both">("registry")
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async () => {
    setDeleting(true)
    setError(null)

    try {
      // If deleting both, delete the files first
      if (deleteOption === "both") {
        const deleteResponse = await fetch("/api/files", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: "delete",
            path: repoPath,
          }),
        })

        const deleteResult = await deleteResponse.json()
        if (!deleteResponse.ok) {
          throw new Error(deleteResult.error || "Failed to delete repository files")
        }
      }

      // Remove from registry
      const registryResponse = await fetch("/api/repositories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "remove",
          path: repoPath
        })
      })

      const registryResult = await registryResponse.json()
      if (!registryResult.success) {
        throw new Error("Failed to remove repository from registry")
      }

      const successMessage = deleteOption === "both"
        ? `Repository "${repoName}" deleted from disk and registry`
        : `Repository "${repoName}" removed from VS Code Manager (files preserved)`

      toast.success(successMessage)
      onDeleteComplete()
      onOpenChange(false)

      // Reset form
      setDeleteOption("registry")
    } catch (error: any) {
      setError(error.message || "Failed to delete repository")
      toast.error(error.message || "Failed to delete repository")
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            Delete Repository
          </DialogTitle>
          <DialogDescription>
            Choose how to remove "{repoName}" from VS Code Manager
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <Alert>
            <AlertDescription className="text-sm">
              <strong>Repository path:</strong> {repoPath}
            </AlertDescription>
          </Alert>

          <div className="space-y-3">
            <Label>Delete Options</Label>
            <RadioGroup value={deleteOption} onValueChange={(v) => setDeleteOption(v as any)}>
              <div className="flex items-start space-x-3 border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                <RadioGroupItem value="registry" id="registry" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="registry" className="font-medium cursor-pointer">
                    Remove from VS Code Manager only
                  </Label>
                  <p className="text-xs text-muted-foreground mt-1">
                    The repository will be removed from the list but files will remain on disk. You can add it back later.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 border-2 border-destructive rounded-lg p-3 hover:bg-destructive/5 transition-colors">
                <RadioGroupItem value="both" id="both" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="both" className="font-medium cursor-pointer text-destructive">
                    Delete from disk and VS Code Manager
                  </Label>
                  <p className="text-xs text-muted-foreground mt-1">
                    ⚠️ This will permanently delete all files in this repository. This action cannot be undone!
                  </p>
                </div>
              </div>
            </RadioGroup>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={deleting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {deleting ? "Deleting..." : deleteOption === "both" ? "Delete Permanently" : "Remove"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
