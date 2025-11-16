"use client"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ChevronDown, Plus, GitBranch, Download, Upload, RefreshCw } from "lucide-react"

interface GitHubHeaderProps {
  currentRepo: string | null
  onRepoChange: (repo: string | null) => void
}

export function GitHubHeader({ currentRepo, onRepoChange }: GitHubHeaderProps) {
  return (
    <div className="border-b border-border bg-muted/30">
      <div className="px-4 py-3 flex items-center justify-between">
        {/* Left - Repository Selector */}
        <div className="flex items-center gap-3">
          <Select value={currentRepo || undefined} onValueChange={onRepoChange}>
            <SelectTrigger className="w-[300px]">
              <SelectValue placeholder="Select repository..." />
            </SelectTrigger>
            <SelectContent>
              {/* TODO: Load from saved repositories */}
              <SelectItem value="/var/www/ai-desktop">AI Desktop</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add
            <ChevronDown className="h-3 w-3 ml-1" />
          </Button>
        </div>

        {/* Right - Actions */}
        <div className="flex items-center gap-2">
          {/* Current Branch */}
          <Button variant="outline" size="sm" disabled={!currentRepo}>
            <GitBranch className="h-4 w-4 mr-2" />
            main
            <ChevronDown className="h-3 w-3 ml-1" />
          </Button>

          {/* Fetch */}
          <Button variant="outline" size="sm" disabled={!currentRepo}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Fetch
          </Button>

          {/* Pull */}
          <Button variant="outline" size="sm" disabled={!currentRepo}>
            <Download className="h-4 w-4 mr-2" />
            Pull
          </Button>

          {/* Push */}
          <Button variant="default" size="sm" disabled={!currentRepo}>
            <Upload className="h-4 w-4 mr-2" />
            Push
          </Button>
        </div>
      </div>
    </div>
  )
}
