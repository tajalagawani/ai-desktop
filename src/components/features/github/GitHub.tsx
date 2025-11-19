"use client"

import { useState } from "react"
import { Toaster } from "sonner"
import { GitHubHeader } from "./github/header"
import { GitHubSidebar } from "./github/sidebar"
import { GitHubMainContent } from "./github/main-content"
import { GitHubDiffPanel } from "./github/diff-panel"

export type GitHubView = "changes" | "history" | "branches" | "pull-requests" | "stashes"

export function GitHubApp() {
  const [currentView, setCurrentView] = useState<GitHubView>("changes")
  const [currentRepo, setCurrentRepo] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  return (
    <div className="h-full w-full bg-background flex flex-col">
      <Toaster position="top-center" richColors />
      {/* Header - Repository Selector & Actions */}
      <GitHubHeader
        currentRepo={currentRepo}
        onRepoChange={setCurrentRepo}
      />

      {/* Main Content Area - Three Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Navigation */}
        <GitHubSidebar
          currentView={currentView}
          onViewChange={setCurrentView}
        />

        {/* Center - Main Content (Changes/History/Branches) */}
        <GitHubMainContent
          view={currentView}
          currentRepo={currentRepo}
          selectedFile={selectedFile}
          onFileSelect={setSelectedFile}
        />

        {/* Right - Diff/Details Panel */}
        {selectedFile && (
          <GitHubDiffPanel
            file={selectedFile}
            currentRepo={currentRepo}
            onClose={() => setSelectedFile(null)}
          />
        )}
      </div>
    </div>
  )
}
