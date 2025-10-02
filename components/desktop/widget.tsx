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
    <Card className={`bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800 p-4 w-64 rounded-2xl ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-4 w-4 text-neutral-500 dark:text-neutral-300" />
        <span className="text-sm font-medium text-neutral-700 dark:text-white">{title}</span>
      </div>
      <div className="widget-content">
        {children}
      </div>
    </Card>
  )
}
