"use client"

import * as React from "react"
import { ChevronRight, ChevronsUpDown, Menu, RefreshCw, Plus, Trash2, FolderPlus, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"

// Import utilities
import {
  QUICK_ACCESS_ITEMS,
  PROJECT_ITEMS,
  SECONDARY_NAV_ITEMS,
  FILE_TYPE_ICONS,
  USER_PROFILE,
} from "@/data/file-manager-data"
import { getIcon, getIconProps } from "@/utils/icon-mapper"

interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size: number
  modified: string
  path: string
}

export function FileManager() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true)
  const [currentPath, setCurrentPath] = React.useState('/')
  const [files, setFiles] = React.useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = React.useState<FileItem | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [newFolderMode, setNewFolderMode] = React.useState(false)
  const [newFolderName, setNewFolderName] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [showHidden, setShowHidden] = React.useState(false)

  const loadFiles = React.useCallback(async (path: string, hidden: boolean) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/files?path=${encodeURIComponent(path)}&showHidden=${hidden}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load files')
      }

      setFiles(data.items || [])
    } catch (error: any) {
      console.error('Failed to load files:', error)
      setError(error.message || 'Failed to load files')
      setFiles([])
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    loadFiles(currentPath, showHidden)
  }, [currentPath, showHidden, loadFiles])

  const handleOpenFolder = (folder: FileItem) => {
    if (folder.type === 'folder') {
      setCurrentPath(folder.path)
      setSelectedFile(null)
    }
  }

  const handleBreadcrumbClick = (path: string) => {
    setCurrentPath(path)
    setSelectedFile(null)
  }

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return

    try {
      const response = await fetch('/api/files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create-folder',
          path: currentPath,
          name: newFolderName
        })
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error || 'Failed to create folder')
      }

      setNewFolderName('')
      setNewFolderMode(false)
      setError(null)
      await loadFiles(currentPath, showHidden)
    } catch (error: any) {
      console.error('Failed to create folder:', error)
      setError(error.message || 'Failed to create folder')
    }
  }

  const handleDelete = async (item: FileItem) => {
    if (confirm(`Are you sure you want to delete ${item.name}?`)) {
      try {
        const response = await fetch('/api/files', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'delete',
            path: item.path
          })
        })

        const data = await response.json()
        if (!response.ok) {
          throw new Error(data.error || 'Failed to delete item')
        }

        setError(null)
        await loadFiles(currentPath, showHidden)
        if (selectedFile?.id === item.id) {
          setSelectedFile(null)
        }
      } catch (error: any) {
        console.error('Failed to delete item:', error)
        setError(error.message || 'Failed to delete item')
      }
    }
  }

  const breadcrumbs = React.useMemo(() => {
    const parts = currentPath.split('/').filter(Boolean)
    const crumbs = [{ path: '/', label: 'Home' }]

    let buildPath = ''
    for (const part of parts) {
      buildPath += `/${part}`
      crumbs.push({ path: buildPath, label: part })
    }

    return crumbs
  }, [currentPath])

  return (
    <div className="flex h-full w-full">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onNavigate={handleBreadcrumbClick}
      />

      {/* Main Content */}
      <div className="flex-1 flex bg-background overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            breadcrumbs={breadcrumbs}
            onBreadcrumbClick={handleBreadcrumbClick}
            onRefresh={() => loadFiles(currentPath, showHidden)}
            onNewFolder={() => setNewFolderMode(true)}
            showHidden={showHidden}
            onToggleHidden={() => setShowHidden(!showHidden)}
          />

          {/* New Folder Input */}
          {newFolderMode && (
            <div className="px-4 py-2 border-b flex items-center gap-2">
              <Input
                placeholder="New folder name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleCreateFolder()
                  if (e.key === 'Escape') {
                    setNewFolderMode(false)
                    setNewFolderName('')
                  }
                }}
                autoFocus
                className="max-w-xs"
              />
              <Button size="sm" onClick={handleCreateFolder}>Create</Button>
              <Button size="sm" variant="ghost" onClick={() => {
                setNewFolderMode(false)
                setNewFolderName('')
              }}>Cancel</Button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="px-4 py-2 bg-destructive/10 border-b border-destructive/20">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* File Grid */}
          <FileGrid
            files={files}
            selectedFile={selectedFile}
            onSelectFile={setSelectedFile}
            onOpenFile={handleOpenFolder}
            onDelete={handleDelete}
            loading={loading}
          />
        </div>
      </div>
    </div>
  )
}

// Sidebar Component
function Sidebar({ isOpen, onNavigate }: any) {
  const CommandIcon = getIcon("Command")
  
  return (
    <div className={`${isOpen ? 'w-[280px]' : 'w-0'} transition-all duration-300 border-r bg-sidebar overflow-hidden flex-shrink-0`}>
      <div className="flex h-full flex-col w-[280px]">
        {/* Sidebar Header */}
        <div className="flex h-14 items-center border-b px-4">
          <div className="flex items-center gap-2">
            <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <CommandIcon className="size-4" />
            </div>
            <div className="grid flex-1 text-left text-xs leading-tight">
              <span className="truncate font-medium">{USER_PROFILE.company}</span>
              <span className="truncate text-[10px] text-muted-foreground">{USER_PROFILE.plan}</span>
            </div>
          </div>
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-auto py-2">
          {/* Quick Access */}
          <QuickAccessSection items={QUICK_ACCESS_ITEMS} onNavigate={onNavigate} />

          <Separator className="my-4" />

          {/* Projects */}
          <ProjectsSection projects={PROJECT_ITEMS} />

          {/* Secondary Navigation */}
          <SecondaryNav items={SECONDARY_NAV_ITEMS} />
        </div>

        {/* User Section */}
        <UserSection profile={USER_PROFILE} />
      </div>
    </div>
  )
}

// Header Component
function Header({ onToggleSidebar, breadcrumbs, onBreadcrumbClick, onRefresh, onNewFolder, showHidden, onToggleHidden }: any) {
  const EyeIcon = getIcon(showHidden ? "Eye" : "EyeOff")

  return (
    <header className="flex h-14 items-center gap-4 border-b px-4">
      <Button
        variant="ghost"
        size="sm"
        className="h-7 w-7 p-0"
        onClick={onToggleSidebar}
      >
        <Menu className="h-4 w-4" />
      </Button>
      <Separator orientation="vertical" className="h-6" />
      <Breadcrumb>
        <BreadcrumbList>
          {breadcrumbs.map((item: any, index: number) => (
            <React.Fragment key={item.path}>
              {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
              <BreadcrumbItem className={index === 0 ? "hidden md:block" : ""}>
                {index === breadcrumbs.length - 1 ? (
                  <BreadcrumbPage>{item.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      onBreadcrumbClick(item.path)
                    }}
                  >
                    {item.label}
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </React.Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>
      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleHidden}
          className="h-8 w-8 p-0"
          title={showHidden ? "Hide hidden files" : "Show hidden files"}
        >
          <EyeIcon className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onRefresh}
          className="h-8 w-8 p-0"
          title="Refresh"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onNewFolder}
          className="h-8 w-8 p-0"
          title="New folder"
        >
          <FolderPlus className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}

// Quick Access Section
function QuickAccessSection({ items, onNavigate }: any) {
  return (
    <div className="px-3 py-2">
      <h2 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Quick Access</h2>
      <div className="space-y-0.5">
        {items.map((item: any) => {
          const Icon = getIcon(item.icon)
          return (
            <button
              key={item.id}
              className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              onClick={() => item.path && onNavigate(item.path)}
            >
              <Icon className="h-4 w-4" />
              <span className="flex-1 text-left">{item.name}</span>
              {item.badge && (
                <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded">
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}


// Projects Section
function ProjectsSection({ projects }: any) {
  return (
    <div className="px-3 py-2">
      <h2 className="mb-2 px-2 text-lg font-normal tracking-tight">Projects</h2>
      <div className="space-y-1">
        {projects.map((project: any) => {
          const Icon = getIcon(project.icon)
          return (
            <button 
              key={project.id}
              className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-muted-foreground hover:text-primary hover:bg-accent"
            >
              <Icon {...getIconProps("sm")} />
              {project.name}
            </button>
          )
        })}
      </div>
    </div>
  )
}

// Secondary Navigation
function SecondaryNav({ items }: any) {
  return (
    <div className="mt-auto px-3 py-2">
      <div className="space-y-1">
        {items.map((item: any) => {
          const Icon = getIcon(item.icon)
          return (
            <button 
              key={item.id}
              className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-muted-foreground hover:text-primary hover:bg-accent"
            >
              <Icon {...getIconProps("sm")} />
              {item.name}
            </button>
          )
        })}
      </div>
    </div>
  )
}

// User Section
function UserSection({ profile }: any) {
  return (
    <div className="mt-auto border-t p-3">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 hover:bg-accent transition-colors">
            <Avatar className="h-7 w-7">
              <AvatarImage src={profile.avatar} />
              <AvatarFallback className="text-xs">{profile.initials}</AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-xs leading-tight">
              <span className="truncate font-medium">{profile.name}</span>
              <span className="truncate text-[10px] text-muted-foreground">{profile.email}</span>
            </div>
            <ChevronsUpDown className="h-3 w-3 text-muted-foreground" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="start">
          <DropdownMenuLabel>My Account</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Profile</DropdownMenuItem>
          <DropdownMenuItem>Billing</DropdownMenuItem>
          <DropdownMenuItem>Team</DropdownMenuItem>
          <DropdownMenuItem>Subscription</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Log out</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

// File Grid Component
function FileGrid({ files, selectedFile, onSelectFile, onOpenFile, onDelete, loading }: any) {
  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-4 lg:p-6 flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="flex-1 overflow-auto p-4 lg:p-6 flex items-center justify-center">
        <div className="text-muted-foreground">This folder is empty</div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-auto p-4 lg:p-6">
      <div className="grid grid-cols-[repeat(auto-fill,minmax(100px,1fr))] gap-4">
        {files.map((item: FileItem) => {
          const isFolder = item.type === "folder"
          const extension = item.name.split('.').pop()?.toLowerCase() || 'default'
          const Icon = isFolder
            ? getIcon("Folder")
            : getIcon(FILE_TYPE_ICONS[extension]?.icon || FILE_TYPE_ICONS.default.icon)
          const iconColor = isFolder
            ? "text-blue-500"
            : FILE_TYPE_ICONS[extension]?.color || FILE_TYPE_ICONS.default.color

          return (
            <div
              key={item.id}
              className={`flex flex-col items-center p-2.5 rounded-md hover:bg-accent cursor-pointer group relative transition-colors ${
                selectedFile?.id === item.id ? 'bg-accent' : ''
              }`}
              onClick={() => onSelectFile(item)}
              onDoubleClick={() => onOpenFile(item)}
              onContextMenu={(e) => {
                e.preventDefault()
                onSelectFile(item)
              }}
            >
              <Icon className={`w-10 h-10 mb-1.5 ${iconColor}`} />
              <span className="text-[11px] text-center truncate w-full leading-tight">{item.name}</span>

              {/* Delete button on hover */}
              <button
                className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity bg-destructive text-destructive-foreground rounded p-1 hover:bg-destructive/90"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(item)
                }}
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}