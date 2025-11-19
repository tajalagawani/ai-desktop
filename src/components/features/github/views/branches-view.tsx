"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { GitBranch, Check, Plus, Trash2, Loader2, GitMerge, GitPullRequest, Edit, Upload } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface BranchesViewProps {
  currentRepo: string
}

interface Branch {
  name: string
  current: boolean
}

export function BranchesView({ currentRepo }: BranchesViewProps) {
  const [branches, setBranches] = useState<Branch[]>([])
  const [loading, setLoading] = useState(true)
  const [newBranchName, setNewBranchName] = useState("")
  const [creating, setCreating] = useState(false)
  const [mergeDialogOpen, setMergeDialogOpen] = useState(false)
  const [rebaseDialogOpen, setRebaseDialogOpen] = useState(false)
  const [renameDialogOpen, setRenameDialogOpen] = useState(false)
  const [selectedBranch, setSelectedBranch] = useState<string>("")
  const [targetBranch, setTargetBranch] = useState<string>("")
  const [newName, setNewName] = useState<string>("")

  useEffect(() => {
    loadBranches()
  }, [currentRepo])

  const loadBranches = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git branch",
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const parsedBranches = output.split('\n')
          .filter((line: string) => line.trim())
          .map((line: string) => ({
            name: line.replace('* ', '').trim(),
            current: line.startsWith('*')
          }))
        setBranches(parsedBranches)
      }
    } catch (error) {
      console.error("Failed to load branches:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateBranch = async () => {
    if (!newBranchName.trim()) {
      toast.error("Please enter a branch name")
      return
    }

    setCreating(true)
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git branch "${newBranchName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        setNewBranchName("")
        loadBranches()
      } else {
        toast.error(`Failed to create branch: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to create branch: ${error.message}`)
    } finally {
      setCreating(false)
    }
  }

  const handleCheckoutBranch = async (branchName: string) => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git checkout "${branchName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadBranches()
      } else {
        toast.error(`Failed to checkout branch: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to checkout branch: ${error.message}`)
    }
  }

  const handleDeleteBranch = async (branchName: string, isCurrent: boolean) => {
    if (isCurrent) {
      toast.error("Cannot delete the current branch")
      return
    }

    if (!confirm(`Are you sure you want to delete branch "${branchName}"?`)) {
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git branch -d "${branchName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        loadBranches()
      } else {
        // Try force delete
        const confirmForce = confirm(`Branch has unmerged changes. Force delete?`)
        if (confirmForce) {
          const forceResponse = await fetch("/api/git", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              repoPath: currentRepo,
              command: `git branch -D "${branchName}"`,
            }),
          })

          if (forceResponse.ok) {
            loadBranches()
          }
        }
      }
    } catch (error: any) {
      toast.error(`Failed to delete branch: ${error.message}`)
    }
  }

  const handleMergeBranch = async () => {
    if (!targetBranch) {
      toast.error("Please select a branch to merge")
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git merge "${targetBranch}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success(`Successfully merged ${targetBranch}!`)
        setMergeDialogOpen(false)
        setTargetBranch("")
        loadBranches()
      } else {
        if (result.error?.includes("CONFLICT")) {
          toast.error("Merge conflict detected! Please resolve conflicts manually.")
        } else {
          toast.error(`Failed to merge: ${result.error}`)
        }
      }
    } catch (error: any) {
      toast.error(`Failed to merge: ${error.message}`)
    }
  }

  const handleRebaseBranch = async () => {
    if (!targetBranch) {
      toast.error("Please select a branch to rebase onto")
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git rebase "${targetBranch}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success(`Successfully rebased onto ${targetBranch}!`)
        setRebaseDialogOpen(false)
        setTargetBranch("")
        loadBranches()
      } else {
        if (result.error?.includes("CONFLICT")) {
          toast.error("Rebase conflict detected! Resolve conflicts or run: git rebase --abort")
        } else {
          toast.error(`Failed to rebase: ${result.error}`)
        }
      }
    } catch (error: any) {
      toast.error(`Failed to rebase: ${error.message}`)
    }
  }

  const handleRenameBranch = async () => {
    if (!newName.trim()) {
      toast.error("Please enter a new branch name")
      return
    }

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git branch -m "${selectedBranch}" "${newName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success(`Branch renamed to ${newName}!`)
        setRenameDialogOpen(false)
        setNewName("")
        loadBranches()
      } else {
        toast.error(`Failed to rename branch: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to rename branch: ${error.message}`)
    }
  }

  const handlePushBranch = async (branchName: string) => {
    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git push -u origin "${branchName}"`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        toast.success(`Branch ${branchName} pushed to remote!`)
      } else {
        toast.error(`Failed to push branch: ${result.error}`)
      }
    } catch (error: any) {
      toast.error(`Failed to push branch: ${error.message}`)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const currentBranch = branches.find(b => b.current)

  return (
    <>
      <ScrollArea className="h-full">
        <div className="p-4 space-y-4">
          {/* Create Branch */}
          <div className="flex gap-2">
            <Input
              placeholder="New branch name..."
              value={newBranchName}
              onChange={(e) => setNewBranchName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreateBranch()}
            />
            <Button onClick={handleCreateBranch} disabled={creating}>
              {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
            </Button>
          </div>

          {/* Branch Operations */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setMergeDialogOpen(true)}
              disabled={!currentBranch}
              className="flex-1"
            >
              <GitMerge className="h-4 w-4 mr-2" />
              Merge
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setRebaseDialogOpen(true)}
              disabled={!currentBranch}
              className="flex-1"
            >
              <GitPullRequest className="h-4 w-4 mr-2" />
              Rebase
            </Button>
          </div>

          {/* Branches List */}
          <div className="space-y-2">
            {branches.map((branch) => (
              <div
                key={branch.name}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  branch.current
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:bg-muted/50'
                } cursor-pointer transition-colors`}
                onClick={() => !branch.current && handleCheckoutBranch(branch.name)}
              >
                <div className="flex items-center gap-3">
                  <GitBranch className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{branch.name}</span>
                  {branch.current && <Check className="h-4 w-4 text-primary" />}
                </div>

                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        •••
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handlePushBranch(branch.name)}>
                        <Upload className="h-4 w-4 mr-2" />
                        Push to remote
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setSelectedBranch(branch.name)
                        setNewName(branch.name)
                        setRenameDialogOpen(true)
                      }}>
                        <Edit className="h-4 w-4 mr-2" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => handleDeleteBranch(branch.name, branch.current)}
                        disabled={branch.current}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            ))}
          </div>

          {branches.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No branches found</p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Merge Dialog */}
      <Dialog open={mergeDialogOpen} onOpenChange={setMergeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Merge Branch</DialogTitle>
            <DialogDescription>
              Select a branch to merge into {currentBranch?.name}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={targetBranch} onValueChange={setTargetBranch}>
              <SelectTrigger>
                <SelectValue placeholder="Select branch to merge..." />
              </SelectTrigger>
              <SelectContent>
                {branches.filter(b => !b.current).map((branch) => (
                  <SelectItem key={branch.name} value={branch.name}>
                    {branch.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setMergeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleMergeBranch}>
              Merge
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rebase Dialog */}
      <Dialog open={rebaseDialogOpen} onOpenChange={setRebaseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rebase Branch</DialogTitle>
            <DialogDescription>
              Select a branch to rebase {currentBranch?.name} onto
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={targetBranch} onValueChange={setTargetBranch}>
              <SelectTrigger>
                <SelectValue placeholder="Select base branch..." />
              </SelectTrigger>
              <SelectContent>
                {branches.filter(b => !b.current).map((branch) => (
                  <SelectItem key={branch.name} value={branch.name}>
                    {branch.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRebaseDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleRebaseBranch}>
              Rebase
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rename Dialog */}
      <Dialog open={renameDialogOpen} onOpenChange={setRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Branch</DialogTitle>
            <DialogDescription>
              Enter a new name for branch "{selectedBranch}"
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="New branch name..."
              onKeyDown={(e) => e.key === 'Enter' && handleRenameBranch()}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleRenameBranch}>
              Rename
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
