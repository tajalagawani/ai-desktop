"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronDown, Plus, GitBranch, Download, Upload, RefreshCw, Settings, FolderPlus, FolderGit2 } from "lucide-react"
import { GitSettingsDialog } from "./settings-dialog"
import { CloneDialog } from "./clone-dialog"

interface GitHubHeaderProps {
  currentRepo: string | null
  onRepoChange: (repo: string | null) => void
}

export function GitHubHeader({ currentRepo, onRepoChange }: GitHubHeaderProps) {
  const [repositories, setRepositories] = useState<string[]>([])
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [cloneOpen, setCloneOpen] = useState(false)
  const [currentBranch, setCurrentBranch] = useState("main")

  // Load saved repositories
  useEffect(() => {
    const saved = localStorage.getItem("git-repositories")
    if (saved) {
      setRepositories(JSON.parse(saved))
    }
  }, [])

  // Get current branch when repo changes
  useEffect(() => {
    if (currentRepo) {
      fetchCurrentBranch()
    }
  }, [currentRepo])

  const fetchCurrentBranch = async () => {
    if (!currentRepo) return

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git branch --show-current",
        }),
      })

      const result = await response.json()
      if (result.success && result.output) {
        setCurrentBranch(result.output.trim())
      }
    } catch (error) {
      console.error("Failed to fetch current branch:", error)
    }
  }

  const handleAddExisting = () => {
    const path = prompt("Enter the path to an existing Git repository:")
    if (path) {
      const repos = [...repositories, path]
      setRepositories(repos)
      localStorage.setItem("git-repositories", JSON.stringify(repos))
      onRepoChange(path)
    }
  }

  const handleCloneComplete = (repoPath: string) => {
    setRepositories([...repositories, repoPath])
    onRepoChange(repoPath)
  }

  const handleGitOperation = async (operation: "fetch" | "pull" | "push") => {
    if (!currentRepo) return

    try {
      const response = await fetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: `git ${operation}`,
        }),
      })

      const result = await response.json()
      if (result.success) {
        alert(`${operation.charAt(0).toUpperCase() + operation.slice(1)} completed successfully!`)
      } else {
        alert(`${operation} failed: ${result.error}`)
      }
    } catch (error: any) {
      alert(`${operation} failed: ${error.message}`)
    }
  }
  return (
    <>
      <div className="border-b border-border bg-muted/30">
        <div className="px-4 py-3 flex items-center justify-between">
          {/* Left - Repository Selector */}
          <div className="flex items-center gap-3">
            <Select value={currentRepo || undefined} onValueChange={onRepoChange}>
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select repository..." />
              </SelectTrigger>
              <SelectContent>
                {repositories.map((repo) => (
                  <SelectItem key={repo} value={repo}>
                    {repo.split('/').pop() || repo}
                  </SelectItem>
                ))}
                {repositories.length === 0 && (
                  <SelectItem value="__none__" disabled>
                    No repositories added
                  </SelectItem>
                )}
              </SelectContent>
            </Select>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => console.log('Add button clicked')}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="z-[10000]">
                <DropdownMenuItem onClick={() => {
                  console.log('Clone clicked')
                  setCloneOpen(true)
                }}>
                  <FolderGit2 className="h-4 w-4 mr-2" />
                  Clone Repository
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => {
                  console.log('Add existing clicked')
                  handleAddExisting()
                }}>
                  <FolderPlus className="h-4 w-4 mr-2" />
                  Add Existing Repository
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Right - Actions */}
          <div className="flex items-center gap-2">
            {/* Current Branch */}
            <Button variant="outline" size="sm" disabled={!currentRepo}>
              <GitBranch className="h-4 w-4 mr-2" />
              {currentBranch}
              <ChevronDown className="h-3 w-3 ml-1" />
            </Button>

            {/* Fetch */}
            <Button
              variant="outline"
              size="sm"
              disabled={!currentRepo}
              onClick={() => handleGitOperation("fetch")}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Fetch
            </Button>

            {/* Pull */}
            <Button
              variant="outline"
              size="sm"
              disabled={!currentRepo}
              onClick={() => handleGitOperation("pull")}
            >
              <Download className="h-4 w-4 mr-2" />
              Pull
            </Button>

            {/* Push */}
            <Button
              variant="default"
              size="sm"
              disabled={!currentRepo}
              onClick={() => handleGitOperation("push")}
            >
              <Upload className="h-4 w-4 mr-2" />
              Push
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSettingsOpen(true)}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <GitSettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
      <CloneDialog open={cloneOpen} onOpenChange={setCloneOpen} onCloneComplete={handleCloneComplete} />
    </>
  )
}
