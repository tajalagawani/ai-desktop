"use client"

import { Card } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import { ReactNode } from "react"

interface WidgetProps {
  icon: LucideIcon
  title: string
  children: ReactNode
  className?: string
}

export function Widget({ icon: Icon, title, children, className = "" }: WidgetProps) {
  return (
    <Card className={`bg-muted border-border p-4 w-64 rounded-2xl ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-4 w-4 text-foreground" />
        <span className="text-sm font-normal text-foreground">{title}</span>
      </div>
      <div className="widget-content">
        {children}
      </div>
    </Card>
  )
}
