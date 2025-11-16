"use client"

import type { GitHubView } from "../github"
import { ChangesView } from "./views/changes-view"
import { HistoryView } from "./views/history-view"
import { BranchesView } from "./views/branches-view"
import { PullRequestsView } from "./views/pull-requests-view"
import { StashesView } from "./views/stashes-view"

interface GitHubMainContentProps {
  view: GitHubView
  currentRepo: string | null
  selectedFile: string | null
  onFileSelect: (file: string | null) => void
}

export function GitHubMainContent({
  view,
  currentRepo,
  selectedFile,
  onFileSelect,
}: GitHubMainContentProps) {
  if (!currentRepo) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <p className="text-lg font-medium mb-2">No Repository Selected</p>
          <p className="text-sm">Select or add a repository to get started</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-hidden">
      {view === "changes" && (
        <ChangesView
          currentRepo={currentRepo}
          selectedFile={selectedFile}
          onFileSelect={onFileSelect}
        />
      )}
      {view === "history" && <HistoryView currentRepo={currentRepo} />}
      {view === "branches" && <BranchesView currentRepo={currentRepo} />}
      {view === "pull-requests" && <PullRequestsView currentRepo={currentRepo} />}
      {view === "stashes" && <StashesView currentRepo={currentRepo} />}
    </div>
  )
}
