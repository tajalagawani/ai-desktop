// Icon names are strings that map to Lucide React components
// We use string names to avoid importing unused icons

export interface AppConfig {
  id: string
  name: string
  icon: string // Lucide icon name or image path
  iconType?: "lucide" | "image" // Type of icon (default: lucide)
  category: "system" | "productivity" | "development" | "communication" | "media" | "utilities"
  description?: string
  version?: string
  isPinned?: boolean
  isSystem?: boolean
}

export interface WindowConfig {
  defaultWidth: number
  defaultHeight: number
  minWidth: number
  minHeight: number
  resizable: boolean
  maximizable: boolean
  minimizable: boolean
  closable: boolean
  openMaximized?: boolean
}

export interface DesktopFolder {
  id: string
  name: string
  x: number
  y: number
  items?: string[]
}

export const DOCK_APPS: AppConfig[] = [
  {
    id: "app-store",
    name: "App Store",
    icon: "Store",
    category: "system",
    isSystem: true,
    description: "Browse and install applications"
  },
  {
    id: "installed",
    name: "Installed Apps",
    icon: "Folder",
    category: "system",
    isSystem: true,
    description: "View all installed applications"
  },
  {
    id: "workflows",
    name: "Workflows",
    icon: "Workflow",
    category: "productivity",
    description: "Create and manage automation workflows"
  },
  {
    id: "terminal",
    name: "Terminal",
    icon: "TerminalIcon",
    category: "development",
    description: "Command line interface"
  },
  {
    id: "claude-cli",
    name: "Claude Code",
    icon: "/icons/claude.png",
    iconType: "image",
    category: "development",
    description: "AI-powered coding assistant"
  },
  {
    id: "monitor",
    name: "System Monitor",
    icon: "Activity",
    category: "utilities",
    isSystem: true,
    description: "Monitor system performance"
  },
  {
    id: "file-manager",
    name: "File Manager",
    icon: "Folder",
    category: "system",
    isSystem: true,
    description: "Browse and manage files"
  },
  {
    id: "service-manager",
    name: "Services",
    icon: "Package",
    category: "system",
    isSystem: true,
    description: "Install and manage VPS services"
  },
]

export const INSTALLED_APPS: AppConfig[] = [
  {
    id: "github",
    name: "GitHub Desktop",
    icon: "GitBranch",
    category: "development",
    version: "3.2.1",
    description: "Version control and collaboration"
  },
  {
    id: "slack",
    name: "Slack",
    icon: "MessageSquare",
    category: "communication",
    version: "4.33.90",
    description: "Team communication platform"
  },
  {
    id: "chatgpt",
    name: "ChatGPT",
    icon: "Brain",
    category: "productivity",
    version: "1.0.0",
    description: "AI assistant"
  },
]

export const WINDOW_CONFIGS: Record<string, WindowConfig> = {
  "app-store": {
    defaultWidth: 1200,
    defaultHeight: 800,
    minWidth: 800,
    minHeight: 600,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "installed": {
    defaultWidth: 900,
    defaultHeight: 600,
    minWidth: 600,
    minHeight: 400,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "workflows": {
    defaultWidth: 1400,
    defaultHeight: 900,
    minWidth: 800,
    minHeight: 600,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "terminal": {
    defaultWidth: 800,
    defaultHeight: 500,
    minWidth: 400,
    minHeight: 300,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "claude-cli": {
    defaultWidth: 900,
    defaultHeight: 600,
    minWidth: 500,
    minHeight: 400,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "monitor": {
    defaultWidth: 1000,
    defaultHeight: 700,
    minWidth: 600,
    minHeight: 400,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "file-manager": {
    defaultWidth: 1100,
    defaultHeight: 700,
    minWidth: 700,
    minHeight: 500,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  "service-manager": {
    defaultWidth: 1400,
    defaultHeight: 900,
    minWidth: 1000,
    minHeight: 700,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
  default: {
    defaultWidth: 800,
    defaultHeight: 600,
    minWidth: 320,
    minHeight: 240,
    resizable: true,
    maximizable: true,
    minimizable: true,
    closable: true,
  },
}

export const SYSTEM_STATUS = {
  cpu: {
    usage: 23,
    temperature: 65,
    cores: 8,
  },
  memory: {
    used: 8.2,
    total: 16,
    percentage: 51,
  },
  storage: {
    used: 256,
    total: 512,
    percentage: 50,
  },
  network: {
    download: 125,
    upload: 45,
    ping: 12,
  },
  workflows: {
    active: 3,
    completed: 127,
    failed: 2,
  },
  apps: {
    installed: 12,
    running: 5,
    updates: 2,
  },
}

export const RECENT_ACTIVITY = [
  {
    id: "1",
    action: "Slack node executed",
    time: "2m ago",
    type: "workflow",
  },
  {
    id: "2", 
    action: "GitHub workflow started",
    time: "5m ago",
    type: "workflow",
  },
  {
    id: "3",
    action: "OpenAI node installed",
    time: "12m ago",
    type: "install",
  },
  {
    id: "4",
    action: "System backup completed",
    time: "1h ago",
    type: "system",
  },
  {
    id: "5",
    action: "Terminal session opened",
    time: "2h ago",
    type: "app",
  },
]

export const CONTEXT_MENU_ACTIONS = {
  desktop: [
    { id: "refresh", label: "Refresh", icon: "RefreshCw", shortcut: "⌘R" },
    { type: "separator" },
    { id: "new-folder", label: "New Folder", icon: "FolderPlus", shortcut: "⇧⌘N" },
    { id: "new-file", label: "New File", icon: "FilePlus" },
    { type: "separator" },
    { 
      id: "sort",
      label: "Sort By",
      icon: "ArrowUpDown",
      submenu: [
        { id: "sort-name", label: "Name" },
        { id: "sort-date", label: "Date Modified" },
        { id: "sort-size", label: "Size" },
        { id: "sort-type", label: "Type" },
      ]
    },
    {
      id: "view",
      label: "View As",
      icon: "Layout",
      submenu: [
        { id: "view-grid", label: "Grid" },
        { id: "view-list", label: "List" },
        { id: "view-columns", label: "Columns" },
      ]
    },
    { type: "separator" },
    { id: "settings", label: "Desktop Settings", icon: "Settings" },
    { id: "properties", label: "Properties", icon: "Info" },
  ],
  icon: [
    { id: "open", label: "Open", icon: "ExternalLink" },
    { type: "separator" },
    { id: "pause", label: "Pause", icon: "Pause" },
    { id: "resume", label: "Resume", icon: "Play" },
    { type: "separator" },
    { id: "rename", label: "Rename", icon: "Edit", shortcut: "F2" },
    { id: "copy", label: "Copy", icon: "Copy", shortcut: "⌘C" },
    { id: "duplicate", label: "Duplicate", icon: "Copy2", shortcut: "⌘D" },
    { type: "separator" },
    { id: "pin", label: "Pin to Desktop", icon: "Pin" },
    { id: "unpin", label: "Unpin from Desktop", icon: "PinOff" },
    { id: "add-to-dock", label: "Add to Dock", icon: "Plus" },
    { type: "separator" },
    { id: "settings", label: "App Settings", icon: "Settings" },
    { id: "properties", label: "Properties", icon: "Info", shortcut: "⌘I" },
    { type: "separator" },
    { id: "delete", label: "Delete", icon: "Trash2", shortcut: "⌘⌫" },
  ],
}

export const FOOTER_CONFIG = {
  left: [
    { type: "branch", icon: "GitBranch", label: "main" },
    { type: "sync", icon: "Sync" },
    { type: "problems", icons: ["X", "AlertCircle"], values: [0, 0] },
  ],
  right: [
    { type: "language", label: "TypeScript React" },
    { type: "encoding", label: "UTF-8" },
    { type: "eol", label: "LF" },
    { type: "indentation", label: "Spaces: 2" },
    { type: "windows", icon: "Folder" },
    { type: "notifications", icon: "Bell" },
    { type: "theme", icons: ["Sun", "Moon"] },
  ],
}