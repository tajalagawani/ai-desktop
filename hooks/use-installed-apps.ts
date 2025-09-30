import { useState, useCallback, useMemo, useEffect } from "react"
import { 
  InstalledApp, 
  AppStatus, 
  AppCategory, 
  ViewMode,
  getAppStatistics 
} from "@/data/installed-apps-data"

export interface AppFilters {
  search: string
  category: AppCategory | "all"
  status: AppStatus | "all"
  showPinned: boolean
  showAutoStart: boolean
  showUpdatesAvailable: boolean
  showSystemApps: boolean
}

export interface AppSort {
  by: "name" | "size" | "lastUsed" | "installDate" | "developer" | "status"
  order: "asc" | "desc"
}

export const useInstalledApps = (initialApps: InstalledApp[]) => {
  const [apps, setApps] = useState<InstalledApp[]>(initialApps)
  const [viewMode, setViewMode] = useState<ViewMode>("grid")
  const [filters, setFilters] = useState<AppFilters>({
    search: "",
    category: "all",
    status: "all",
    showPinned: false,
    showAutoStart: false,
    showUpdatesAvailable: false,
    showSystemApps: true,
  })
  const [sort, setSort] = useState<AppSort>({
    by: "name",
    order: "asc",
  })
  const [selectedApps, setSelectedApps] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Filter apps
  const filteredApps = useMemo(() => {
    let result = [...apps]

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      result = result.filter(
        app =>
          app.displayName.toLowerCase().includes(searchLower) ||
          app.developer.toLowerCase().includes(searchLower) ||
          app.description?.toLowerCase().includes(searchLower)
      )
    }

    // Category filter
    if (filters.category !== "all") {
      result = result.filter(app => app.category === filters.category)
    }

    // Status filter
    if (filters.status !== "all") {
      result = result.filter(app => app.status === filters.status)
    }

    // Feature filters
    if (filters.showPinned) {
      result = result.filter(app => app.pinned)
    }
    if (filters.showAutoStart) {
      result = result.filter(app => app.autoStart)
    }
    if (filters.showUpdatesAvailable) {
      result = result.filter(app => app.updateAvailable)
    }
    if (!filters.showSystemApps) {
      result = result.filter(app => !app.isSystem)
    }

    return result
  }, [apps, filters])

  // Sort apps
  const sortedApps = useMemo(() => {
    const sorted = [...filteredApps]
    
    sorted.sort((a, b) => {
      let comparison = 0
      
      switch (sort.by) {
        case "name":
          comparison = a.displayName.localeCompare(b.displayName)
          break
        case "size":
          comparison = a.sizeBytes - b.sizeBytes
          break
        case "lastUsed":
          // Parse lastUsed strings for comparison
          comparison = parseLastUsed(a.lastUsed) - parseLastUsed(b.lastUsed)
          break
        case "installDate":
          comparison = new Date(a.installDate).getTime() - new Date(b.installDate).getTime()
          break
        case "developer":
          comparison = a.developer.localeCompare(b.developer)
          break
        case "status":
          comparison = a.status.localeCompare(b.status)
          break
      }
      
      return sort.order === "asc" ? comparison : -comparison
    })
    
    return sorted
  }, [filteredApps, sort])

  // App statistics
  const statistics = useMemo(() => {
    return getAppStatistics(apps)
  }, [apps])

  // Actions
  const uninstallApp = useCallback((appId: string) => {
    setApps(prev => prev.filter(app => app.id !== appId))
    setSelectedApps(prev => prev.filter(id => id !== appId))
  }, [])

  const uninstallMultiple = useCallback((appIds: string[]) => {
    setApps(prev => prev.filter(app => !appIds.includes(app.id)))
    setSelectedApps([])
  }, [])

  const updateApp = useCallback((appId: string) => {
    setApps(prev =>
      prev.map(app =>
        app.id === appId
          ? { ...app, status: "updating" as AppStatus, updateAvailable: false }
          : app
      )
    )
    
    // Simulate update completion
    setTimeout(() => {
      setApps(prev =>
        prev.map(app =>
          app.id === appId
            ? { ...app, status: "inactive" as AppStatus, version: app.newVersion || app.version }
            : app
        )
      )
    }, 3000)
  }, [])

  const togglePinApp = useCallback((appId: string) => {
    setApps(prev =>
      prev.map(app =>
        app.id === appId ? { ...app, pinned: !app.pinned } : app
      )
    )
  }, [])

  const toggleAutoStart = useCallback((appId: string) => {
    setApps(prev =>
      prev.map(app =>
        app.id === appId ? { ...app, autoStart: !app.autoStart } : app
      )
    )
  }, [])

  const launchApp = useCallback((appId: string) => {
    setApps(prev =>
      prev.map(app =>
        app.id === appId
          ? { ...app, status: "active" as AppStatus, lastUsed: "Just now" }
          : app
      )
    )
  }, [])

  const stopApp = useCallback((appId: string) => {
    setApps(prev =>
      prev.map(app =>
        app.id === appId
          ? { ...app, status: "inactive" as AppStatus }
          : app
      )
    )
  }, [])

  const toggleSelectApp = useCallback((appId: string) => {
    setSelectedApps(prev =>
      prev.includes(appId)
        ? prev.filter(id => id !== appId)
        : [...prev, appId]
    )
  }, [])

  const selectAllApps = useCallback(() => {
    setSelectedApps(sortedApps.map(app => app.id))
  }, [sortedApps])

  const clearSelection = useCallback(() => {
    setSelectedApps([])
  }, [])

  const setFilter = useCallback(<K extends keyof AppFilters>(key: K, value: AppFilters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }, [])

  const resetFilters = useCallback(() => {
    setFilters({
      search: "",
      category: "all",
      status: "all",
      showPinned: false,
      showAutoStart: false,
      showUpdatesAvailable: false,
      showSystemApps: true,
    })
  }, [])

  const setSortBy = useCallback((by: AppSort["by"]) => {
    setSort(prev => ({
      by,
      order: prev.by === by && prev.order === "asc" ? "desc" : "asc"
    }))
  }, [])

  return {
    // Data
    apps: sortedApps,
    statistics,
    viewMode,
    filters,
    sort,
    selectedApps,
    isLoading,
    
    // Actions
    setViewMode,
    setFilter,
    resetFilters,
    setSortBy,
    uninstallApp,
    uninstallMultiple,
    updateApp,
    togglePinApp,
    toggleAutoStart,
    launchApp,
    stopApp,
    toggleSelectApp,
    selectAllApps,
    clearSelection,
  }
}

// Helper function to parse lastUsed strings
function parseLastUsed(lastUsed: string): number {
  const now = Date.now()
  
  if (lastUsed === "Just now") return now
  if (lastUsed === "Today") return now - 1000 * 60 * 60 // 1 hour ago
  if (lastUsed === "Yesterday") return now - 1000 * 60 * 60 * 24
  
  const match = lastUsed.match(/(\d+)\s+(hour|day|week|month)s?\s+ago/)
  if (match) {
    const [, num, unit] = match
    const multipliers: Record<string, number> = {
      hour: 1000 * 60 * 60,
      day: 1000 * 60 * 60 * 24,
      week: 1000 * 60 * 60 * 24 * 7,
      month: 1000 * 60 * 60 * 24 * 30,
    }
    return now - parseInt(num) * multipliers[unit]
  }
  
  return 0
}

// Hook for app search
export const useAppSearch = (apps: InstalledApp[], query: string) => {
  const [results, setResults] = useState<InstalledApp[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    if (!query) {
      setResults([])
      return
    }

    setIsSearching(true)
    
    // Simulate search delay
    const timer = setTimeout(() => {
      const searchLower = query.toLowerCase()
      const searchResults = apps.filter(app => {
        const searchableText = `${app.displayName} ${app.developer} ${app.description}`.toLowerCase()
        return searchableText.includes(searchLower)
      })
      
      setResults(searchResults)
      setIsSearching(false)
    }, 200)

    return () => clearTimeout(timer)
  }, [apps, query])

  return { results, isSearching }
}

// Hook for app updates
export const useAppUpdates = (apps: InstalledApp[]) => {
  const [isCheckingUpdates, setIsCheckingUpdates] = useState(false)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)
  
  const appsWithUpdates = useMemo(() => {
    return apps.filter(app => app.updateAvailable)
  }, [apps])

  const checkForUpdates = useCallback(async () => {
    setIsCheckingUpdates(true)
    
    // Simulate update check
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setLastChecked(new Date())
    setIsCheckingUpdates(false)
  }, [])

  const updateAll = useCallback(async (updateApps: (appIds: string[]) => void) => {
    const appIds = appsWithUpdates.map(app => app.id)
    
    // Update each app
    for (const appId of appIds) {
      updateApps([appId])
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }, [appsWithUpdates])

  return {
    appsWithUpdates,
    isCheckingUpdates,
    lastChecked,
    checkForUpdates,
    updateAll,
  }
}