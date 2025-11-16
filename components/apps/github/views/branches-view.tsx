"use client"

import { ScrollArea } from "@/components/ui/scroll-area"

interface BranchesViewProps {
  currentRepo: string
}

export function BranchesView({ currentRepo }: BranchesViewProps) {
  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        <p className="text-sm text-muted-foreground">
          Loading branches...
        </p>
        {/* TODO: Load git branch */}
      </div>
    </ScrollArea>
  )
}
