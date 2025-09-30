import { useState, useCallback, useEffect, useRef } from "react"
import { FileItem, FolderStructure } from "@/data/file-manager-data"

export interface FileManagerState {
  sidebarOpen: boolean
  selectedFile: FileItem | null
  selectedFiles: string[]
  currentPath: string
  viewMode: "grid" | "list" | "columns"
  sortBy: "name" | "date" | "size" | "type"
  sortOrder: "asc" | "desc"
  searchQuery: string
  previewWidth: number
  isResizing: boolean
}

export const useFileManager = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [currentPath, setCurrentPath] = useState("/")
  const [viewMode, setViewMode] = useState<"grid" | "list" | "columns">("grid")
  const [sortBy, setSortBy] = useState<"name" | "date" | "size" | "type">("name")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")
  const [searchQuery, setSearchQuery] = useState("")
  const [previewWidth, setPreviewWidth] = useState(300)
  const [isResizing, setIsResizing] = useState(false)
  
  // Folder states
  const [folderStates, setFolderStates] = useState<Record<string, boolean>>({
    documents: true,
    downloads: false,
    pictures: false,
    videos: false,
    music: false,
  })

  const toggleFolder = useCallback((folderId: string) => {
    setFolderStates(prev => ({
      ...prev,
      [folderId]: !prev[folderId]
    }))
  }, [])

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev)
  }, [])

  const selectFile = useCallback((file: FileItem) => {
    setSelectedFile(file)
    setSelectedFiles([file.id])
  }, [])

  const selectMultipleFiles = useCallback((fileIds: string[]) => {
    setSelectedFiles(fileIds)
  }, [])

  const toggleFileSelection = useCallback((fileId: string) => {
    setSelectedFiles(prev => {
      if (prev.includes(fileId)) {
        return prev.filter(id => id !== fileId)
      }
      return [...prev, fileId]
    })
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedFile(null)
    setSelectedFiles([])
  }, [])

  const navigateToPath = useCallback((path: string) => {
    setCurrentPath(path)
    clearSelection()
  }, [clearSelection])

  const changeViewMode = useCallback((mode: "grid" | "list" | "columns") => {
    setViewMode(mode)
  }, [])

  const changeSortBy = useCallback((sort: "name" | "date" | "size" | "type") => {
    if (sortBy === sort) {
      setSortOrder(prev => prev === "asc" ? "desc" : "asc")
    } else {
      setSortBy(sort)
      setSortOrder("asc")
    }
  }, [sortBy])

  const search = useCallback((query: string) => {
    setSearchQuery(query)
  }, [])

  return {
    // States
    sidebarOpen,
    selectedFile,
    selectedFiles,
    currentPath,
    viewMode,
    sortBy,
    sortOrder,
    searchQuery,
    folderStates,
    previewWidth,
    isResizing,
    
    // Actions
    toggleSidebar,
    selectFile,
    selectMultipleFiles,
    toggleFileSelection,
    clearSelection,
    navigateToPath,
    changeViewMode,
    changeSortBy,
    search,
    toggleFolder,
    setPreviewWidth,
    setIsResizing,
  }
}

export const useFilePreview = () => {
  const [previewWidth, setPreviewWidth] = useState(300)
  const [isResizing, setIsResizing] = useState(false)
  const resizeStartX = useRef<number>(0)
  const startWidth = useRef<number>(300)

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return
    const deltaX = resizeStartX.current - e.clientX
    const newWidth = Math.max(200, Math.min(600, startWidth.current + deltaX))
    setPreviewWidth(newWidth)
  }, [isResizing])

  const handleMouseUp = useCallback(() => {
    setIsResizing(false)
  }, [])

  const startResize = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
    resizeStartX.current = e.clientX
    startWidth.current = previewWidth
  }, [previewWidth])

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'ew-resize'
      document.body.style.userSelect = 'none'
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }
    }
  }, [isResizing, handleMouseMove, handleMouseUp])

  return {
    previewWidth,
    isResizing,
    startResize,
  }
}

export const useFileOperations = () => {
  const createFolder = useCallback((name: string, path: string) => {
    console.log(`Creating folder: ${name} at ${path}`)
    // Implementation would go here
  }, [])

  const deleteFiles = useCallback((fileIds: string[]) => {
    console.log(`Deleting files: ${fileIds.join(', ')}`)
    // Implementation would go here
  }, [])

  const renameFile = useCallback((fileId: string, newName: string) => {
    console.log(`Renaming file ${fileId} to ${newName}`)
    // Implementation would go here
  }, [])

  const copyFiles = useCallback((fileIds: string[], destination: string) => {
    console.log(`Copying files ${fileIds.join(', ')} to ${destination}`)
    // Implementation would go here
  }, [])

  const moveFiles = useCallback((fileIds: string[], destination: string) => {
    console.log(`Moving files ${fileIds.join(', ')} to ${destination}`)
    // Implementation would go here
  }, [])

  const openFile = useCallback((file: FileItem) => {
    console.log(`Opening file: ${file.name}`)
    // Implementation would go here
  }, [])

  return {
    createFolder,
    deleteFiles,
    renameFile,
    copyFiles,
    moveFiles,
    openFile,
  }
}

export const useFileSearch = (files: FileItem[], query: string) => {
  const [results, setResults] = useState<FileItem[]>([])

  useEffect(() => {
    if (!query) {
      setResults(files)
      return
    }

    const searchResults = files.filter(file => 
      file.name.toLowerCase().includes(query.toLowerCase())
    )
    
    setResults(searchResults)
  }, [files, query])

  return results
}

export const useFileSort = (files: FileItem[], sortBy: string, sortOrder: string) => {
  const [sortedFiles, setSortedFiles] = useState<FileItem[]>([])

  useEffect(() => {
    const sorted = [...files].sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case "name":
          comparison = a.name.localeCompare(b.name)
          break
        case "date":
          comparison = (a.modified?.getTime() || 0) - (b.modified?.getTime() || 0)
          break
        case "size":
          comparison = (a.size || 0) - (b.size || 0)
          break
        case "type":
          comparison = a.type.localeCompare(b.type)
          break
        default:
          comparison = 0
      }
      
      return sortOrder === "asc" ? comparison : -comparison
    })
    
    setSortedFiles(sorted)
  }, [files, sortBy, sortOrder])

  return sortedFiles
}