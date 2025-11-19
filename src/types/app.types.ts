export type AppStatus = "running" | "updating" | "stopped" | "installing"
export type AppCategory = "productivity" | "development" | "communication" | "media" | "system" | "utilities"

export interface InstalledApp {
  id: string
  displayName: string
  developer: string
  version: string
  icon: string
  status: AppStatus
  category: AppCategory
  size: string
  lastUpdated: string
  updateAvailable?: boolean
  newVersion?: string
  pinned?: boolean
}

export interface AppCardProps {
  app: InstalledApp
  isSelected?: boolean
  onAction?: (app: InstalledApp, action: string) => void
  onSelect?: (id: string) => void
  className?: string
  variant?: "default" | "compact"
}

export interface AppActionButtonProps {
  app: InstalledApp
  onAction?: (app: InstalledApp, action: string) => void
  className?: string
}

export interface DropdownActionsProps {
  app: InstalledApp
  onAction?: (app: InstalledApp, action: string) => void
  variant?: "icon" | "button"
}