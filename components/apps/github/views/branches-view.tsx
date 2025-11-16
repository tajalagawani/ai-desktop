"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { GitBranch, Check, Plus, Trash2, Loader2 } from "lucide-react"

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
      if (result.success && result.output) {
        const parsedBranches = result.output.split('\n')
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
      alert("Please enter a branch name")
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
        alert(`Failed to create branch: ${result.error}`)
      }
    } catch (error: any) {
      alert(`Failed to create branch: ${error.message}`)
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
        alert(`Failed to checkout branch: ${result.error}`)
      }
    } catch (error: any) {
      alert(`Failed to checkout branch: ${error.message}`)
    }
  }

  const handleDeleteBranch = async (branchName: string, isCurrent: boolean) => {
    if (isCurrent) {
      alert("Cannot delete the current branch")
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
      alert(`Failed to delete branch: ${error.message}`)
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

              {!branch.current && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteBranch(branch.name, branch.current)
                  }}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              )}
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
  )
}
