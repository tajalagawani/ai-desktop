"use client"

import { Button } from "@/components/ui/button"
import { X } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

interface GitHubDiffPanelProps {
  file: string
  currentRepo: string | null
  onClose: () => void
}

export function GitHubDiffPanel({ file, currentRepo, onClose }: GitHubDiffPanelProps) {
  return (
    <div className="w-[500px] border-l border-border bg-muted/10 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <h3 className="font-medium text-sm truncate">{file}</h3>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Diff Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          <p className="text-sm text-muted-foreground">
            Loading diff for {file}...
          </p>
          {/* TODO: Load and display actual diff */}
        </div>
      </ScrollArea>
    </div>
  )
}
