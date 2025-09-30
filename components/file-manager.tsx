"use client"

import * as React from "react"
import { ChevronRight, ChevronsUpDown, Menu } from "lucide-react"
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

// Import data and utilities
import {
  QUICK_ACCESS_ITEMS,
  FOLDER_STRUCTURE,
  PROJECT_ITEMS,
  SECONDARY_NAV_ITEMS,
  FILE_TYPE_ICONS,
  FILE_GRID_ITEMS,
  USER_PROFILE,
  BREADCRUMB_ITEMS,
} from "@/data/file-manager-data"
import { useFileManager, useFileOperations } from "@/hooks/use-file-manager"
import { getIcon, getIconProps } from "@/utils/icon-mapper"

export function FileManager() {
  const {
    sidebarOpen,
    selectedFile,
    folderStates,
    toggleSidebar,
    selectFile,
    toggleFolder,
  } = useFileManager()
  
  const { openFile } = useFileOperations()

  return (
    <div className="flex h-full w-full">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen}
        folderStates={folderStates}
        onToggleFolder={toggleFolder}
        onSelectFile={selectFile}
      />

      {/* Main Content */}
      <div className="flex-1 flex bg-background overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header 
            onToggleSidebar={toggleSidebar}
            breadcrumbs={BREADCRUMB_ITEMS}
          />

          {/* File Grid */}
          <FileGrid 
            files={FILE_GRID_ITEMS}
            selectedFile={selectedFile}
            onSelectFile={selectFile}
            onOpenFile={openFile}
          />
        </div>
      </div>
    </div>
  )
}

// Sidebar Component
function Sidebar({ isOpen, folderStates, onToggleFolder, onSelectFile }: any) {
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
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">{USER_PROFILE.company}</span>
              <span className="truncate text-xs">{USER_PROFILE.plan}</span>
            </div>
          </div>
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-auto py-2">
          {/* Quick Access */}
          <QuickAccessSection items={QUICK_ACCESS_ITEMS} />
          
          <Separator className="my-4" />
          
          {/* Folders */}
          <FoldersSection 
            folders={FOLDER_STRUCTURE}
            folderStates={folderStates}
            onToggleFolder={onToggleFolder}
            onSelectFile={onSelectFile}
          />
          
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
function Header({ onToggleSidebar, breadcrumbs }: any) {
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
            <React.Fragment key={item.id}>
              {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
              <BreadcrumbItem className={index === 0 ? "hidden md:block" : ""}>
                {item.href ? (
                  <BreadcrumbLink href={item.href}>{item.label}</BreadcrumbLink>
                ) : (
                  <BreadcrumbPage>{item.label}</BreadcrumbPage>
                )}
              </BreadcrumbItem>
            </React.Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>
    </header>
  )
}

// Quick Access Section
function QuickAccessSection({ items }: any) {
  return (
    <div className="px-3 py-2">
      <h2 className="mb-2 px-2 text-lg font-semibold tracking-tight">Quick Access</h2>
      <div className="space-y-1">
        {items.map((item: any) => {
          const Icon = getIcon(item.icon)
          return (
            <button 
              key={item.id}
              className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-muted-foreground hover:text-primary hover:bg-accent"
            >
              <Icon {...getIconProps("sm")} />
              <span className="flex-1 text-left">{item.name}</span>
              {item.badge && (
                <span className="text-xs bg-muted px-1.5 py-0.5 rounded">
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

// Folders Section
function FoldersSection({ folders, folderStates, onToggleFolder, onSelectFile }: any) {
  return (
    <div className="px-3 py-2">
      <h2 className="mb-2 px-2 text-lg font-semibold tracking-tight">Folders</h2>
      <div className="space-y-1">
        {folders.map((folder: any) => {
          const FolderIcon = getIcon(folder.icon)
          const isOpen = folderStates[folder.id]
          
          return (
            <Collapsible 
              key={folder.id} 
              open={isOpen} 
              onOpenChange={() => onToggleFolder(folder.id)}
            >
              <CollapsibleTrigger className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-muted-foreground transition-all hover:text-primary hover:bg-accent">
                <FolderIcon {...getIconProps("sm", "primary")} />
                <span className="flex-1 text-left">{folder.name}</span>
                <ChevronRight className={`size-4 transition-transform ${isOpen ? 'rotate-90' : ''}`} />
              </CollapsibleTrigger>
              {folder.children && (
                <CollapsibleContent className="mt-1 space-y-1 pl-6">
                  {folder.children.map((file: any) => {
                    const fileIcon = FILE_TYPE_ICONS[file.extension || 'default']
                    const FileIcon = getIcon(fileIcon.icon)
                    
                    return (
                      <button 
                        key={file.id}
                        className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-sm text-muted-foreground hover:text-primary hover:bg-accent"
                        onClick={() => onSelectFile(file)}
                      >
                        <FileIcon className={`w-4 h-4 ${fileIcon.color}`} />
                        {file.name}
                      </button>
                    )
                  })}
                </CollapsibleContent>
              )}
            </Collapsible>
          )
        })}
        
        {/* Static folders without children */}
        {["Videos", "Music"].map((name) => {
          const FolderIcon = getIcon("Folder")
          return (
            <button 
              key={name.toLowerCase()}
              className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-muted-foreground hover:text-primary hover:bg-accent"
            >
              <FolderIcon {...getIconProps("sm", "primary")} />
              <span className="flex-1 text-left">{name}</span>
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
      <h2 className="mb-2 px-2 text-lg font-semibold tracking-tight">Projects</h2>
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
    <div className="mt-auto border-t p-4">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-accent">
            <Avatar className="h-8 w-8">
              <AvatarImage src={profile.avatar} />
              <AvatarFallback>{profile.initials}</AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">{profile.name}</span>
              <span className="truncate text-xs">{profile.email}</span>
            </div>
            <ChevronsUpDown className="size-4" />
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
function FileGrid({ files, selectedFile, onSelectFile, onOpenFile }: any) {
  return (
    <div className="flex-1 overflow-auto p-4 lg:p-6">
      <div className="grid grid-cols-[repeat(auto-fill,minmax(100px,1fr))] gap-4">
        {files.map((item: any) => {
          const isFolder = item.type === "folder"
          const Icon = isFolder 
            ? getIcon("Folder")
            : getIcon(FILE_TYPE_ICONS[item.extension || 'default'].icon)
          const iconColor = isFolder 
            ? "text-blue-500"
            : FILE_TYPE_ICONS[item.extension || 'default'].color
          
          return (
            <div 
              key={item.id}
              className={`flex flex-col items-center p-3 rounded-lg hover:bg-accent cursor-pointer ${
                selectedFile?.id === item.id ? 'bg-accent' : ''
              }`}
              onClick={() => onSelectFile(item)}
              onDoubleClick={() => onOpenFile(item)}
            >
              <Icon className={`w-12 h-12 mb-2 ${iconColor}`} />
              <span className="text-xs text-center truncate w-full">{item.name}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}