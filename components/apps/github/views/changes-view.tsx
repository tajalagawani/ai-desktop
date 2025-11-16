"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

interface ChangesViewProps {
  currentRepo: string
  selectedFile: string | null
  onFileSelect: (file: string | null) => void
}

export function ChangesView({ currentRepo, selectedFile, onFileSelect }: ChangesViewProps) {
  return (
    <div className="h-full flex flex-col">
      {/* Changed Files List */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          <div className="text-sm text-muted-foreground mb-4">
            {currentRepo}
          </div>

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              No changes detected
            </p>
            {/* TODO: Load actual changed files from git status */}
          </div>
        </div>
      </ScrollArea>

      {/* Commit Panel */}
      <div className="border-t border-border p-4">
        <Input
          placeholder="Summary (required)"
          className="mb-2"
        />
        <Textarea
          placeholder="Description (optional)"
          className="mb-3 min-h-[100px]"
        />
        <Button className="w-full" disabled>
          Commit to main
        </Button>
      </div>
    </div>
  )
}
