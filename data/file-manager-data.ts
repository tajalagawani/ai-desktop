// File Manager Configuration and Data

export interface FileItem {
  id: string
  name: string
  type: "file" | "folder"
  icon?: string
  extension?: string
  size?: number
  modified?: Date
  path?: string
  color?: string
}

export interface QuickAccessItem {
  id: string
  name: string
  icon: string
  path?: string
  badge?: number
}

export interface FolderStructure {
  id: string
  name: string
  icon: string
  isOpen?: boolean
  children?: FileItem[]
}

export interface ProjectItem {
  id: string
  name: string
  icon: string
  description?: string
}

// Quick Access Items - VPS Directories (relative to FILE_MANAGER_ROOT = /var/www)
export const QUICK_ACCESS_ITEMS: QuickAccessItem[] = [
  {
    id: "root",
    name: "Root",
    icon: "Home",
    path: "/",
  },
  {
    id: "github",
    name: "GitHub Repos",
    icon: "GitBranch",
    path: "/github",
  },
  {
    id: "ai-desktop",
    name: "AI Desktop",
    icon: "FolderOpen",
    path: "/ai-desktop",
  },
]

// Folder Structure
export const FOLDER_STRUCTURE: FolderStructure[] = [
  {
    id: "documents",
    name: "Documents",
    icon: "FolderOpen",
    isOpen: true,
    children: [
      { id: "doc1", name: "Work Report.pdf", type: "file", extension: "pdf" },
      { id: "doc2", name: "Notes.txt", type: "file", extension: "txt" },
      { id: "doc3", name: "Budget.xlsx", type: "file", extension: "xlsx" },
    ],
  },
  {
    id: "downloads",
    name: "Downloads",
    icon: "Download",
    isOpen: false,
    children: [
      { id: "down1", name: "installer.dmg", type: "file", extension: "dmg" },
      { id: "down2", name: "photo.jpg", type: "file", extension: "jpg" },
      { id: "down3", name: "archive.zip", type: "file", extension: "zip" },
    ],
  },
  {
    id: "pictures",
    name: "Pictures",
    icon: "Image",
    isOpen: false,
    children: [
      { id: "pic1", name: "vacation.png", type: "file", extension: "png" },
      { id: "pic2", name: "screenshot.jpg", type: "file", extension: "jpg" },
      { id: "pic3", name: "logo.svg", type: "file", extension: "svg" },
    ],
  },
  {
    id: "videos",
    name: "Videos",
    icon: "Video",
    isOpen: false,
  },
  {
    id: "music",
    name: "Music",
    icon: "Music",
    isOpen: false,
  },
]

// Projects Section - REMOVED (was fake data)
export const PROJECT_ITEMS: ProjectItem[] = []

// Secondary Navigation - REMOVED (was fake data)
export const SECONDARY_NAV_ITEMS: any[] = []

// File Type to Icon Mapping
export const FILE_TYPE_ICONS: Record<string, { icon: string; color: string }> = {
  // Documents
  pdf: { icon: "FileText", color: "text-red-500" },
  doc: { icon: "FileText", color: "text-blue-600" },
  docx: { icon: "FileText", color: "text-blue-600" },
  txt: { icon: "FileText", color: "text-gray-500" },
  md: { icon: "FileText", color: "text-gray-600" },
  
  // Spreadsheets
  xls: { icon: "Table", color: "text-green-600" },
  xlsx: { icon: "Table", color: "text-green-600" },
  csv: { icon: "Table", color: "text-green-500" },
  
  // Presentations
  ppt: { icon: "Presentation", color: "text-orange-600" },
  pptx: { icon: "Presentation", color: "text-orange-600" },
  
  // Images
  jpg: { icon: "Image", color: "text-purple-500" },
  jpeg: { icon: "Image", color: "text-purple-500" },
  png: { icon: "Image", color: "text-purple-500" },
  gif: { icon: "Image", color: "text-purple-500" },
  svg: { icon: "Image", color: "text-purple-600" },
  webp: { icon: "Image", color: "text-purple-500" },
  
  // Videos
  mp4: { icon: "Video", color: "text-pink-500" },
  avi: { icon: "Video", color: "text-pink-500" },
  mov: { icon: "Video", color: "text-pink-500" },
  mkv: { icon: "Video", color: "text-pink-500" },
  
  // Audio
  mp3: { icon: "Music", color: "text-indigo-500" },
  wav: { icon: "Music", color: "text-indigo-500" },
  flac: { icon: "Music", color: "text-indigo-500" },
  m4a: { icon: "Music", color: "text-indigo-500" },
  
  // Code
  js: { icon: "Code", color: "text-yellow-500" },
  ts: { icon: "Code", color: "text-blue-500" },
  jsx: { icon: "Code", color: "text-cyan-500" },
  tsx: { icon: "Code", color: "text-cyan-600" },
  py: { icon: "Code", color: "text-green-500" },
  java: { icon: "Code", color: "text-red-600" },
  cpp: { icon: "Code", color: "text-blue-700" },
  c: { icon: "Code", color: "text-blue-600" },
  html: { icon: "Code", color: "text-orange-500" },
  css: { icon: "Code", color: "text-blue-500" },
  json: { icon: "Code", color: "text-yellow-600" },
  xml: { icon: "Code", color: "text-orange-600" },
  
  // Archives
  zip: { icon: "Archive", color: "text-amber-500" },
  rar: { icon: "Archive", color: "text-amber-500" },
  "7z": { icon: "Archive", color: "text-amber-500" },
  tar: { icon: "Archive", color: "text-amber-500" },
  gz: { icon: "Archive", color: "text-amber-500" },
  
  // System
  exe: { icon: "Package", color: "text-gray-600" },
  dmg: { icon: "Package", color: "text-gray-600" },
  app: { icon: "Package", color: "text-gray-600" },
  deb: { icon: "Package", color: "text-gray-600" },
  rpm: { icon: "Package", color: "text-gray-600" },
  
  // Default
  default: { icon: "File", color: "text-gray-400" },
}

// File Grid Items (for main view)
export const FILE_GRID_ITEMS: FileItem[] = [
  // Folders
  { id: "f1", name: "Documents", type: "folder", icon: "Folder", color: "text-blue-500" },
  { id: "f2", name: "Downloads", type: "folder", icon: "Folder", color: "text-blue-500" },
  { id: "f3", name: "Pictures", type: "folder", icon: "Folder", color: "text-blue-500" },
  { id: "f4", name: "Videos", type: "folder", icon: "Folder", color: "text-blue-500" },
  { id: "f5", name: "Projects", type: "folder", icon: "Folder", color: "text-blue-500" },
  
  // Files
  { id: "file1", name: "README.md", type: "file", extension: "md" },
  { id: "file2", name: "report.pdf", type: "file", extension: "pdf" },
  { id: "file3", name: "data.xlsx", type: "file", extension: "xlsx" },
  { id: "file4", name: "image.png", type: "file", extension: "png" },
  { id: "file5", name: "document.docx", type: "file", extension: "docx" },
  { id: "file6", name: "script.js", type: "file", extension: "js" },
  { id: "file7", name: "notes.txt", type: "file", extension: "txt" },
]

// User Profile
export const USER_PROFILE = {
  name: "VPS User",
  email: "admin@server",
  avatar: "",
  initials: "VPS",
  company: "File Manager",
  plan: "VPS",
}

// Breadcrumb Navigation
export const BREADCRUMB_ITEMS = [
  {
    id: "root",
    label: "Building Your Application",
    href: "#",
  },
  {
    id: "current",
    label: "Data Fetching",
    href: null,
  },
]

// View Options
export const VIEW_OPTIONS = {
  grid: {
    id: "grid",
    name: "Grid View",
    icon: "LayoutGrid",
    columns: "grid-cols-[repeat(auto-fill,minmax(100px,1fr))]",
  },
  list: {
    id: "list",
    name: "List View",
    icon: "List",
    columns: "flex flex-col",
  },
  columns: {
    id: "columns",
    name: "Column View",
    icon: "Columns",
    columns: "grid grid-cols-3",
  },
}

// Sort Options
export const SORT_OPTIONS = [
  { id: "name", label: "Name", icon: "SortAsc" },
  { id: "date", label: "Date Modified", icon: "Calendar" },
  { id: "size", label: "Size", icon: "HardDrive" },
  { id: "type", label: "Type", icon: "FileType" },
]

// File Manager Settings
export const FILE_MANAGER_SETTINGS = {
  defaultView: "grid",
  showHiddenFiles: false,
  showFileExtensions: true,
  showFileSizes: true,
  sortBy: "name",
  sortOrder: "asc",
  previewPane: true,
  sidebarWidth: 280,
  previewWidth: 300,
}