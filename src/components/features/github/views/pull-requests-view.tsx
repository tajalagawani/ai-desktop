"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
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
import { GitPullRequest, GitMerge, Plus, Loader2, MessageSquare, Check, X, GitBranch } from "lucide-react"
import { apiFetch } from "@/lib/utils/api"

interface PullRequestsViewProps {
  currentRepo: string
}

interface PullRequest {
  number: number
  title: string
  state: "open" | "closed" | "merged"
  author: string
  created_at: string
  head: string
  base: string
  mergeable: boolean
  comments: number
}

export function PullRequestsView({ currentRepo }: PullRequestsViewProps) {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [branches, setBranches] = useState<string[]>([])
  const [newPR, setNewPR] = useState({
    title: "",
    body: "",
    head: "",
    base: "main"
  })

  useEffect(() => {
    loadPullRequests()
    loadBranches()
  }, [currentRepo])

  const loadBranches = async () => {
    if (!currentRepo) return

    try {
      const response = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git branch -a",
        }),
      })

      const result = await response.json()
      const output = result.stdout || result.output || ''
      if (result.success && output) {
        const branchList = output.split('\n')
          .filter((line: string) => line.trim())
          .map((line: string) => line.replace('* ', '').replace('remotes/origin/', '').trim())
          .filter((branch: string) => !branch.includes('HEAD'))
        setBranches([...new Set(branchList)])
      }
    } catch (error) {
      console.error("Failed to load branches:", error)
    }
  }

  const loadPullRequests = async () => {
    if (!currentRepo) return

    setLoading(true)
    try {
      // Get GitHub remote URL
      const remoteResponse = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git remote get-url origin",
        }),
      })

      const remoteResult = await remoteResponse.json()
      if (!remoteResult.success) {
        setPrs([])
        return
      }

      // Parse GitHub repo from URL
      const remoteUrl = remoteResult.output.trim()
      const match = remoteUrl.match(/github\.com[:/](.+?)\/(.+?)(\.git)?$/)

      if (!match) {
        setPrs([])
        return
      }

      const [, owner, repo] = match

      // Fetch PRs from GitHub API
      const settings = localStorage.getItem("git-settings")
      let token = ""

      if (settings) {
        const parsed = JSON.parse(settings)
        token = parsed.githubToken || ""
      }

      const headers: HeadersInit = {
        "Accept": "application/vnd.github.v3+json"
      }

      if (token) {
        headers["Authorization"] = `token ${token}`
      }

      const prResponse = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/pulls?state=all`,
        { headers }
      )

      if (prResponse.ok) {
        const data = await prResponse.json()
        const parsedPRs: PullRequest[] = data.map((pr: any) => ({
          number: pr.number,
          title: pr.title,
          state: pr.merged_at ? "merged" : pr.state,
          author: pr.user.login,
          created_at: pr.created_at,
          head: pr.head.ref,
          base: pr.base.ref,
          mergeable: pr.mergeable ?? true,
          comments: pr.comments
        }))
        setPrs(parsedPRs)
      } else {
        toast.error("Failed to fetch pull requests. Check your GitHub token.")
        setPrs([])
      }
    } catch (error) {
      console.error("Failed to load pull requests:", error)
      setPrs([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePR = async () => {
    if (!newPR.title.trim() || !newPR.head) {
      toast.error("Please enter a title and select a head branch")
      return
    }

    try {
      // Get GitHub remote URL
      const remoteResponse = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git remote get-url origin",
        }),
      })

      const remoteResult = await remoteResponse.json()
      const remoteUrl = remoteResult.output.trim()
      const match = remoteUrl.match(/github\.com[:/](.+?)\/(.+?)(\.git)?$/)

      if (!match) {
        toast.error("Not a GitHub repository")
        return
      }

      const [, owner, repo] = match

      const settings = localStorage.getItem("git-settings")
      let token = ""

      if (settings) {
        const parsed = JSON.parse(settings)
        token = parsed.githubToken || ""
      }

      if (!token) {
        toast.error("GitHub token required. Please add it in Settings.")
        return
      }

      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/pulls`,
        {
          method: "POST",
          headers: {
            "Authorization": `token ${token}`,
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            title: newPR.title,
            body: newPR.body,
            head: newPR.head,
            base: newPR.base
          })
        }
      )

      if (response.ok) {
        toast.success("Pull request created successfully!")
        setCreateOpen(false)
        setNewPR({ title: "", body: "", head: "", base: "main" })
        loadPullRequests()
      } else {
        const error = await response.json()
        toast.error(`Failed to create PR: ${error.message}`)
      }
    } catch (error: any) {
      toast.error(`Failed to create PR: ${error.message}`)
    }
  }

  const handleMergePR = async (prNumber: number) => {
    if (!confirm(`Are you sure you want to merge PR #${prNumber}?`)) {
      return
    }

    try {
      const remoteResponse = await apiFetch("/api/git", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoPath: currentRepo,
          command: "git remote get-url origin",
        }),
      })

      const remoteResult = await remoteResponse.json()
      const remoteUrl = remoteResult.output.trim()
      const match = remoteUrl.match(/github\.com[:/](.+?)\/(.+?)(\.git)?$/)

      if (!match) return

      const [, owner, repo] = match
      const settings = localStorage.getItem("git-settings")
      const token = settings ? JSON.parse(settings).githubToken : ""

      if (!token) {
        toast.error("GitHub token required")
        return
      }

      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/merge`,
        {
          method: "PUT",
          headers: {
            "Authorization": `token ${token}`,
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            merge_method: "merge"
          })
        }
      )

      if (response.ok) {
        toast.success("Pull request merged successfully!")
        loadPullRequests()
      } else {
        const error = await response.json()
        toast.error(`Failed to merge PR: ${error.message}`)
      }
    } catch (error: any) {
      toast.error(`Failed to merge PR: ${error.message}`)
    }
  }

  const getStateColor = (state: string) => {
    switch (state) {
      case "open": return "bg-green-500"
      case "closed": return "bg-red-500"
      case "merged": return "bg-purple-500"
      default: return "bg-gray-500"
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
          {/* Create PR Button */}
          <Button onClick={() => setCreateOpen(true)} className="w-full">
            <Plus className="mr-2 h-4 w-4" />
            Create Pull Request
          </Button>

          {/* PRs List */}
          <div className="space-y-2">
            {prs.map((pr) => (
              <div
                key={pr.number}
                className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <GitPullRequest className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-semibold">#{pr.number}</span>
                      <Badge className={`${getStateColor(pr.state)} text-white`}>
                        {pr.state}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium">{pr.title}</p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>{pr.author}</span>
                      <span>•</span>
                      <span>{new Date(pr.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <GitBranch className="h-3 w-3" />
                        {pr.head} → {pr.base}
                      </span>
                      {pr.comments > 0 && (
                        <>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />
                            {pr.comments}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  {pr.state === "open" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleMergePR(pr.number)}
                      disabled={!pr.mergeable}
                    >
                      <GitMerge className="h-4 w-4 mr-2" />
                      Merge
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {prs.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No pull requests found</p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Create PR Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Pull Request</DialogTitle>
            <DialogDescription>
              Create a new pull request to merge your changes
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Title</label>
              <Input
                placeholder="PR title..."
                value={newPR.title}
                onChange={(e) => setNewPR({ ...newPR, title: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Textarea
                placeholder="Describe your changes..."
                value={newPR.body}
                onChange={(e) => setNewPR({ ...newPR, body: e.target.value })}
                rows={4}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Head Branch</label>
                <Select value={newPR.head} onValueChange={(v) => setNewPR({ ...newPR, head: v })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select branch" />
                  </SelectTrigger>
                  <SelectContent>
                    {branches.map((branch) => (
                      <SelectItem key={branch} value={branch}>
                        {branch}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Base Branch</label>
                <Select value={newPR.base} onValueChange={(v) => setNewPR({ ...newPR, base: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {branches.map((branch) => (
                      <SelectItem key={branch} value={branch}>
                        {branch}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreatePR}>
              Create Pull Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
