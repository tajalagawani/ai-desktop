"use client"

import { ScrollArea } from "@/components/ui/scroll-area"

interface StashesViewProps {
  currentRepo: string
}

export function StashesView({ currentRepo }: StashesViewProps) {
  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        <p className="text-sm text-muted-foreground">
          Loading stashes...
        </p>
        {/* TODO: Load git stash list */}
      </div>
    </ScrollArea>
  )
}
