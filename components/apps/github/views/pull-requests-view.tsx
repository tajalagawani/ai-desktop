"use client"

import { ScrollArea } from "@/components/ui/scroll-area"

interface PullRequestsViewProps {
  currentRepo: string
}

export function PullRequestsView({ currentRepo }: PullRequestsViewProps) {
  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        <p className="text-sm text-muted-foreground">
          Pull Requests - Coming soon
        </p>
      </div>
    </ScrollArea>
  )
}
