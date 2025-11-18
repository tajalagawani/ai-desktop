/**
 * StatCard - Pattern for displaying statistics
 *
 * A reusable card component for showing metrics with icons,
 * values, and optional children (like progress bars).
 */

import { Card, CardHeader, CardTitle, CardContent } from "@/components/primitives/card"
import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

const statCardVariants = cva(
  "transition-colors",
  {
    variants: {
      variant: {
        default: "border-border",
        primary: "border-primary/20 bg-primary/5",
        accent: "border-accent/20 bg-accent/5",
        success: "border-green-500/20 bg-green-500/5",
        warning: "border-yellow-500/20 bg-yellow-500/5",
        destructive: "border-destructive/20 bg-destructive/5",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface StatCardProps extends VariantProps<typeof statCardVariants> {
  title: string
  value: string | React.ReactNode
  subtitle?: string
  icon?: React.ReactNode
  children?: React.ReactNode
  className?: string
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  children,
  variant,
  className,
}: StatCardProps) {
  return (
    <Card className={cn(statCardVariants({ variant }), className)}>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-3">
          {icon && <div className="text-muted-foreground">{icon}</div>}
          <span className="font-normal text-sm text-muted-foreground">{title}</span>
        </div>
        <div className="space-y-2">
          <div className="text-2xl font-semibold text-foreground">
            {value}
          </div>
          {subtitle && (
            <div className="text-xs text-muted-foreground">
              {subtitle}
            </div>
          )}
          {children}
        </div>
      </CardContent>
    </Card>
  )
}
