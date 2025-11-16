"use client"

import { Button } from "@/components/ui/button"
import { FileEdit, History, GitBranch, GitPullRequest, Archive } from "lucide-react"
import type { GitHubView } from "../github"

interface GitHubSidebarProps {
  currentView: GitHubView
  onViewChange: (view: GitHubView) => void
}

const SIDEBAR_ITEMS = [
  { id: "changes" as GitHubView, label: "Changes", icon: FileEdit },
  { id: "history" as GitHubView, label: "History", icon: History },
  { id: "branches" as GitHubView, label: "Branches", icon: GitBranch },
  { id: "pull-requests" as GitHubView, label: "Pull Requests", icon: GitPullRequest },
  { id: "stashes" as GitHubView, label: "Stashes", icon: Archive },
]

export function GitHubSidebar({ currentView, onViewChange }: GitHubSidebarProps) {
  return (
    <div className="w-56 border-r border-border bg-muted/30">
      <div className="p-3 space-y-1">
        {SIDEBAR_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.id

          return (
            <Button
              key={item.id}
              variant={isActive ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => onViewChange(item.id)}
            >
              <Icon className="h-4 w-4 mr-3" />
              {item.label}
            </Button>
          )
        })}
      </div>
    </div>
  )
}
