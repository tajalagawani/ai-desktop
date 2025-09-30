// Installed Apps Data and Configuration

export type AppStatus = "active" | "inactive" | "updating" | "installing" | "error"
export type AppCategory = "productivity" | "development" | "communication" | "media" | "utilities" | "security" | "creative" | "entertainment"
export type ViewMode = "grid" | "list" | "compact"

export interface InstalledApp {
  id: string
  name: string
  displayName: string
  developer: string
  version: string
  size: string
  sizeBytes: number
  lastUsed: string
  lastUpdated: string
  installDate: string
  icon: string // Icon name from icon mapper
  status: AppStatus
  category: AppCategory
  description: string
  rating?: number
  reviewCount?: number
  permissions?: string[]
  autoStart?: boolean
  pinned?: boolean
  isSystem?: boolean
  updateAvailable?: boolean
  newVersion?: string
}

export interface AppStatistics {
  totalApps: number
  activeApps: number
  totalSize: string
  lastUpdated: string
  categories: { name: string; count: number }[]
}

// Sample installed apps data
export const INSTALLED_APPS_DATA: InstalledApp[] = [
  {
    id: "github-desktop",
    name: "github-desktop",
    displayName: "GitHub Desktop",
    developer: "GitHub, Inc.",
    version: "3.3.6",
    size: "89 MB",
    sizeBytes: 93323264,
    lastUsed: "Today",
    lastUpdated: "2 days ago",
    installDate: "2024-01-15",
    icon: "GitBranch",
    status: "active",
    category: "development",
    description: "Focus on what matters instead of fighting with Git. Whether you're new to Git or a seasoned user, GitHub Desktop simplifies your development workflow.",
    rating: 4.8,
    reviewCount: 12543,
    permissions: ["Files", "Network", "Notifications"],
    autoStart: false,
    pinned: true,
    updateAvailable: false,
  },
  {
    id: "chatgpt",
    name: "chatgpt",
    displayName: "ChatGPT",
    developer: "OpenAI",
    version: "1.2024.352",
    size: "234 MB",
    sizeBytes: 245366784,
    lastUsed: "Yesterday",
    lastUpdated: "1 week ago",
    installDate: "2024-02-01",
    icon: "Brain",
    status: "inactive",
    category: "productivity",
    description: "Get instant answers, find creative inspiration, and learn something new. Use ChatGPT on the go to help with all of life's moments.",
    rating: 4.9,
    reviewCount: 89234,
    permissions: ["Camera", "Microphone", "Network"],
    autoStart: true,
    pinned: true,
    updateAvailable: true,
    newVersion: "1.2024.360",
  },
  {
    id: "slack",
    name: "slack",
    displayName: "Slack",
    developer: "Slack Technologies",
    version: "4.38.0",
    size: "145 MB",
    sizeBytes: 151998464,
    lastUsed: "2 days ago",
    lastUpdated: "3 days ago",
    installDate: "2023-12-10",
    icon: "MessageSquare",
    status: "updating",
    category: "communication",
    description: "Slack is where work happens. It's a digital workspace that powers your organization — all the pieces and the people.",
    rating: 4.5,
    reviewCount: 45678,
    permissions: ["Camera", "Microphone", "Notifications", "Files"],
    autoStart: true,
    pinned: false,
    updateAvailable: false,
  },
  {
    id: "vscode",
    name: "vscode",
    displayName: "Visual Studio Code",
    developer: "Microsoft Corporation",
    version: "1.85.1",
    size: "367 MB",
    sizeBytes: 384827392,
    lastUsed: "Today",
    lastUpdated: "1 week ago",
    installDate: "2023-11-20",
    icon: "Code",
    status: "active",
    category: "development",
    description: "Visual Studio Code is a lightweight but powerful source code editor which runs on your desktop.",
    rating: 4.9,
    reviewCount: 234567,
    permissions: ["Files", "Network", "Terminal"],
    autoStart: false,
    pinned: true,
    updateAvailable: false,
  },
  {
    id: "discord",
    name: "discord",
    displayName: "Discord",
    developer: "Discord Inc.",
    version: "0.0.291",
    size: "178 MB",
    sizeBytes: 186646528,
    lastUsed: "5 hours ago",
    lastUpdated: "2 weeks ago",
    installDate: "2024-01-05",
    icon: "MessageCircle",
    status: "inactive",
    category: "communication",
    description: "Discord is the easiest way to talk over voice, video, and text. Talk, chat, hang out, and stay close with your friends and communities.",
    rating: 4.6,
    reviewCount: 156789,
    permissions: ["Camera", "Microphone", "Notifications"],
    autoStart: true,
    pinned: false,
    updateAvailable: true,
    newVersion: "0.0.293",
  },
  {
    id: "notion",
    name: "notion",
    displayName: "Notion",
    developer: "Notion Labs, Inc.",
    version: "3.1.0",
    size: "256 MB",
    sizeBytes: 268435456,
    lastUsed: "1 hour ago",
    lastUpdated: "4 days ago",
    installDate: "2024-01-20",
    icon: "FileText",
    status: "active",
    category: "productivity",
    description: "Notion is the all-in-one workspace for your notes, tasks, wikis, and databases.",
    rating: 4.7,
    reviewCount: 98765,
    permissions: ["Files", "Network", "Clipboard"],
    autoStart: false,
    pinned: true,
    updateAvailable: false,
  },
  {
    id: "spotify",
    name: "spotify",
    displayName: "Spotify",
    developer: "Spotify AB",
    version: "1.2.26.1187",
    size: "312 MB",
    sizeBytes: 327155712,
    lastUsed: "3 hours ago",
    lastUpdated: "1 month ago",
    installDate: "2023-10-15",
    icon: "Music",
    status: "inactive",
    category: "media",
    description: "With Spotify, you can play millions of songs and podcasts for free. Listen to the songs and podcasts you love and discover new music.",
    rating: 4.4,
    reviewCount: 567890,
    permissions: ["Audio", "Network", "Notifications"],
    autoStart: true,
    pinned: false,
    updateAvailable: false,
  },
  {
    id: "figma",
    name: "figma",
    displayName: "Figma",
    developer: "Figma, Inc.",
    version: "116.16.12",
    size: "198 MB",
    sizeBytes: 207618048,
    lastUsed: "Yesterday",
    lastUpdated: "5 days ago",
    installDate: "2023-12-25",
    icon: "Palette",
    status: "inactive",
    category: "creative",
    description: "Figma is the collaborative interface design tool. Build better products as a team.",
    rating: 4.8,
    reviewCount: 78901,
    permissions: ["Files", "Network", "Clipboard"],
    autoStart: false,
    pinned: true,
    updateAvailable: true,
    newVersion: "116.17.0",
  },
  {
    id: "docker",
    name: "docker",
    displayName: "Docker Desktop",
    developer: "Docker Inc.",
    version: "4.26.1",
    size: "589 MB",
    sizeBytes: 617611264,
    lastUsed: "Today",
    lastUpdated: "3 weeks ago",
    installDate: "2023-11-01",
    icon: "Package",
    status: "active",
    category: "development",
    description: "Docker Desktop is an easy-to-install application that enables you to build and share containerized applications.",
    rating: 4.6,
    reviewCount: 34567,
    permissions: ["System", "Network", "Files"],
    autoStart: true,
    pinned: false,
    isSystem: true,
    updateAvailable: false,
  },
  {
    id: "1password",
    name: "1password",
    displayName: "1Password",
    developer: "AgileBits Inc.",
    version: "8.10.23",
    size: "156 MB",
    sizeBytes: 163577856,
    lastUsed: "Today",
    lastUpdated: "1 week ago",
    installDate: "2023-09-20",
    icon: "Lock",
    status: "active",
    category: "security",
    description: "1Password remembers all your passwords for you, and keeps them safe and secure behind the one password that only you know.",
    rating: 4.9,
    reviewCount: 123456,
    permissions: ["System", "Network", "Clipboard"],
    autoStart: true,
    pinned: false,
    isSystem: true,
    updateAvailable: false,
  },
]

// App categories configuration
export const APP_CATEGORIES = [
  { id: "all", name: "All Apps", icon: "Grid3X3" },
  { id: "productivity", name: "Productivity", icon: "Briefcase" },
  { id: "development", name: "Development", icon: "Code" },
  { id: "communication", name: "Communication", icon: "MessageSquare" },
  { id: "media", name: "Media", icon: "Play" },
  { id: "creative", name: "Creative", icon: "Palette" },
  { id: "utilities", name: "Utilities", icon: "Tool" },
  { id: "security", name: "Security", icon: "Shield" },
  { id: "entertainment", name: "Entertainment", icon: "Gamepad2" },
]

// Sort options
export const SORT_OPTIONS = [
  { id: "name", label: "Name", icon: "SortAsc" },
  { id: "size", label: "Size", icon: "HardDrive" },
  { id: "lastUsed", label: "Last Used", icon: "Clock" },
  { id: "installDate", label: "Install Date", icon: "Calendar" },
  { id: "developer", label: "Developer", icon: "User" },
  { id: "status", label: "Status", icon: "Activity" },
]

// Filter options
export const FILTER_OPTIONS = {
  status: [
    { id: "all", label: "All", color: "gray" },
    { id: "active", label: "Active", color: "green" },
    { id: "inactive", label: "Inactive", color: "gray" },
    { id: "updating", label: "Updating", color: "yellow" },
    { id: "error", label: "Error", color: "red" },
  ],
  features: [
    { id: "pinned", label: "Pinned", icon: "Pin" },
    { id: "autoStart", label: "Auto Start", icon: "Power" },
    { id: "updateAvailable", label: "Updates Available", icon: "Download" },
    { id: "system", label: "System Apps", icon: "Shield" },
  ],
}

// Get app statistics
export function getAppStatistics(apps: InstalledApp[]): AppStatistics {
  const totalSizeBytes = apps.reduce((sum, app) => sum + app.sizeBytes, 0)
  const totalSizeGB = (totalSizeBytes / (1024 * 1024 * 1024)).toFixed(2)
  
  const categoryCount = apps.reduce((acc, app) => {
    acc[app.category] = (acc[app.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const categories = Object.entries(categoryCount).map(([name, count]) => ({ name, count }))
  
  return {
    totalApps: apps.length,
    activeApps: apps.filter(app => app.status === "active").length,
    totalSize: `${totalSizeGB} GB`,
    lastUpdated: new Date().toLocaleDateString(),
    categories,
  }
}

// Status configuration
export const STATUS_CONFIG = {
  active: { color: "bg-green-500", label: "Running", icon: "Play" },
  inactive: { color: "bg-gray-400", label: "Stopped", icon: "Square" },
  updating: { color: "bg-yellow-500", label: "Updating", icon: "Download" },
  installing: { color: "bg-blue-500", label: "Installing", icon: "Loader" },
  error: { color: "bg-red-500", label: "Error", icon: "AlertCircle" },
}

// View mode configurations
export const VIEW_MODES = {
  grid: {
    id: "grid",
    name: "Grid View",
    icon: "Grid3X3",
    columns: "grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5",
  },
  list: {
    id: "list",
    name: "List View",
    icon: "List",
    columns: "flex flex-col",
  },
  compact: {
    id: "compact",
    name: "Compact View",
    icon: "LayoutGrid",
    columns: "grid grid-cols-1 md:grid-cols-2",
  },
}