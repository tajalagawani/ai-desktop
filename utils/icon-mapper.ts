import {
  Store,
  Folder,
  FolderOpen,
  Workflow,
  Terminal,
  Activity,
  GitBranch,
  MessageSquare,
  Brain,
  Chrome,
  Music,
  Camera,
  Calculator,
  Calendar,
  Settings,
  Mail,
  MapPin,
  FileText,
  Image,
  Video,
  Download,
  Upload,
  Search,
  Home,
  User,
  Users,
  Bell,
  Lock,
  Unlock,
  Shield,
  Cpu,
  Monitor,
  Database,
  Cloud,
  CloudDownload,
  CloudUpload,
  Wifi,
  WifiOff,
  Battery,
  BatteryCharging,
  Zap,
  Code,
  Code2,
  Package,
  Package2,
  Archive,
  Trash,
  Trash2,
  Edit,
  Edit2,
  Edit3,
  Save,
  Copy,
  Clipboard,
  Link,
  Link2,
  ExternalLink,
  Eye,
  EyeOff,
  RefreshCw,
  RotateCw,
  Play,
  Pause,
  Square,
  Circle,
  Triangle,
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Send,
  Share,
  Share2,
  MoreHorizontal,
  MoreVertical,
  Menu,
  X,
  Plus,
  Minus,
  Check,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Sun,
  Moon,
  Clock,
  Timer,
  HelpCircle,
  TrendingUp,
  Palette,
  Table,
  Presentation,
  File,
  LayoutGrid,
  List,
  Columns,
  SortAsc,
  HardDrive,
  FileType,
  Briefcase,
  Gamepad2,
  Loader,
  AlertCircle,
  type LucideIcon,
} from "lucide-react"

// Central icon registry for the application
export const iconRegistry: Record<string, LucideIcon> = {
  // System & Navigation
  Store,
  Folder,
  FolderOpen,
  Home,
  Settings,
  Menu,
  X,
  Plus,
  Minus,
  Check,
  
  // Development
  Terminal,
  GitBranch,
  Code,
  Code2,
  Package,
  Package2,
  Database,
  
  // Communication
  MessageSquare,
  MessageCircle,
  Mail,
  Send,
  Share,
  Share2,
  Bell,
  
  // Workflow & Productivity
  Workflow,
  Brain,
  Calendar,
  Clock,
  Timer,
  
  // Media
  Image,
  Video,
  Music,
  Camera,
  Play,
  Pause,
  Square,
  
  // Files & Storage
  File,
  FileText,
  FileType,
  Archive,
  Download,
  Upload,
  CloudDownload,
  CloudUpload,
  Cloud,
  Save,
  Copy,
  Clipboard,
  
  // System Monitoring
  Activity,
  Cpu,
  Monitor,
  Battery,
  BatteryCharging,
  Wifi,
  WifiOff,
  Zap,
  
  // Security
  Lock,
  Unlock,
  Shield,
  Eye,
  EyeOff,
  
  // Actions
  Edit,
  Edit2,
  Edit3,
  Trash,
  Trash2,
  RefreshCw,
  RotateCw,
  Link,
  Link2,
  ExternalLink,
  Search,
  
  // UI Elements
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  MoreHorizontal,
  MoreVertical,
  
  // User & Social
  User,
  Users,
  Heart,
  Star,
  ThumbsUp,
  ThumbsDown,
  
  // Theme
  Sun,
  Moon,
  
  // Shapes
  Circle,
  Triangle,
  
  // Location
  MapPin,
  
  // Utilities
  Calculator,
  Chrome,
  HelpCircle,
  TrendingUp,
  Palette,
  Table,
  Presentation,
  LayoutGrid,
  List,
  Columns,
  SortAsc,
  HardDrive,
  Briefcase,
  Gamepad2,
  Loader,
  AlertCircle,
  
  // Aliases for compatibility
  TerminalIcon: Terminal,
  Map: MapPin,
}

// Get icon component by name with fallback
export function getIcon(name: string): LucideIcon {
  return iconRegistry[name] || Folder
}

// Icon categories for organization
export const iconCategories = {
  system: ["Store", "Folder", "FolderOpen", "Home", "Settings", "Menu"],
  development: ["Terminal", "GitBranch", "Code", "Code2", "Package", "Database"],
  communication: ["MessageSquare", "MessageCircle", "Mail", "Send", "Bell"],
  productivity: ["Workflow", "Brain", "Calendar", "Clock", "Timer"],
  media: ["Image", "Video", "Music", "Camera", "Play", "Pause"],
  files: ["FileText", "Archive", "Download", "Upload", "Save", "Copy"],
  monitoring: ["Activity", "Cpu", "Monitor", "Battery", "Wifi", "Zap"],
  security: ["Lock", "Unlock", "Shield", "Eye", "EyeOff"],
  actions: ["Edit", "Trash", "RefreshCw", "Link", "Search"],
  ui: ["ChevronRight", "ArrowRight", "MoreHorizontal", "X", "Plus", "Check"],
  user: ["User", "Users", "Heart", "Star", "ThumbsUp"],
  theme: ["Sun", "Moon"],
} as const

// App-specific icon configurations
export const appIcons: Record<string, string> = {
  // System apps
  "app-store": "Store",
  "file-manager": "Folder",
  "settings": "Settings",
  "terminal": "Terminal",
  
  // Productivity apps
  "workflows": "Workflow",
  "calendar": "Calendar",
  "notes": "FileText",
  "calculator": "Calculator",
  
  // Development apps
  "github": "GitBranch",
  "vscode": "Code",
  "docker": "Package",
  "database": "Database",
  
  // Communication apps
  "slack": "MessageSquare",
  "discord": "MessageCircle",
  "mail": "Mail",
  "chat": "Send",
  
  // Media apps
  "photos": "Image",
  "videos": "Video",
  "music": "Music",
  "camera": "Camera",
  
  // Monitoring apps
  "monitor": "Activity",
  "system": "Cpu",
  "network": "Wifi",
  "battery": "Battery",
  
  // AI/ML apps
  "chatgpt": "Brain",
  "ai-assistant": "Zap",
  
  // Browser
  "browser": "Chrome",
  
  // Default
  "default": "Folder",
}

// Get app icon with fallback
export function getAppIcon(appId: string): string {
  return appIcons[appId] || appIcons.default
}

// Icon size presets
export const iconSizes = {
  xs: "w-3 h-3",
  sm: "w-4 h-4",
  md: "w-5 h-5",
  lg: "w-6 h-6",
  xl: "w-8 h-8",
  "2xl": "w-10 h-10",
  "3xl": "w-12 h-12",
} as const

// Icon style presets for different contexts
export const iconStyles = {
  default: "text-gray-500 dark:text-gray-400",
  primary: "text-blue-500 dark:text-blue-400",
  secondary: "text-gray-600 dark:text-gray-300",
  success: "text-green-500 dark:text-green-400",
  warning: "text-yellow-500 dark:text-yellow-400",
  danger: "text-red-500 dark:text-red-400",
  info: "text-cyan-500 dark:text-cyan-400",
  muted: "text-gray-400 dark:text-gray-500",
  white: "text-white",
  black: "text-black",
} as const

// Helper function to get icon with size and style
export function getIconProps(
  size: keyof typeof iconSizes = "md",
  style: keyof typeof iconStyles = "default"
) {
  return {
    className: `${iconSizes[size]} ${iconStyles[style]}`,
  }
}