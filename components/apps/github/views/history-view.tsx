"use client"

import { ScrollArea } from "@/components/ui/scroll-area"

interface HistoryViewProps {
  currentRepo: string
}

export function HistoryView({ currentRepo }: HistoryViewProps) {
  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        <p className="text-sm text-muted-foreground">
          Loading commit history...
        </p>
        {/* TODO: Load git log */}
      </div>
    </ScrollArea>
  )
}
