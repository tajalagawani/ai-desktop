"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Search,
  Filter,
  MoreVertical,
  Play,
  Square,
  Download,
  Trash2,
  Pin,
  Power,
  Settings,
  ChevronDown,
  Grid3X3,
  List,
  LayoutList,
  Star,
  Info,
  CheckCircle2,
  XCircle,
} from "lucide-react"

// Import data and utilities
import {
  INSTALLED_APPS_DATA,
  APP_CATEGORIES,
  SORT_OPTIONS,
  FILTER_OPTIONS,
  STATUS_CONFIG,
  VIEW_MODES,
  type InstalledApp,
  type ViewMode,
} from "@/data/installed-apps-data"
import { useInstalledApps, useAppUpdates } from "@/hooks/use-installed-apps"
import { getIcon, getIconProps } from "@/utils/icon-mapper"

export function InstalledApps() {
  const {
    apps,
    statistics,
    viewMode,
    filters,
    sort,
    selectedApps,
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
    clearSelection,
  } = useInstalledApps(INSTALLED_APPS_DATA)

  const { appsWithUpdates, checkForUpdates, isCheckingUpdates } = useAppUpdates(apps)

  return (
    <div className="h-full bg-background flex flex-col">
      {/* Header */}
      <Header
        statistics={statistics}
        viewMode={viewMode}
        setViewMode={setViewMode}
        onCheckUpdates={checkForUpdates}
        isCheckingUpdates={isCheckingUpdates}
        updatesCount={appsWithUpdates.length}
      />

      {/* Filters and Search Bar */}
      <FilterBar
        filters={filters}
        setFilter={setFilter}
        resetFilters={resetFilters}
        sort={sort}
        setSortBy={setSortBy}
        totalApps={apps.length}
        selectedCount={selectedApps.length}
        onClearSelection={clearSelection}
        onDeleteSelected={() => uninstallMultiple(selectedApps)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex">
        {/* Sidebar Categories */}
        <Sidebar
          categories={APP_CATEGORIES}
          currentCategory={filters.category}
          onCategoryChange={(category: string) => setFilter("category", category as any)}
          statistics={statistics}
        />

        {/* Apps Display */}
        <ScrollArea className="flex-1">
          <div className="p-6">
            {viewMode === "grid" && (
              <AppsGrid
                apps={apps}
                selectedApps={selectedApps}
                onAppAction={handleAppAction}
                onSelectApp={toggleSelectApp}
              />
            )}
            {viewMode === "list" && (
              <AppsList
                apps={apps}
                selectedApps={selectedApps}
                onAppAction={handleAppAction}
                onSelectApp={toggleSelectApp}
              />
            )}
            {viewMode === "compact" && (
              <AppsCompact
                apps={apps}
                selectedApps={selectedApps}
                onAppAction={handleAppAction}
                onSelectApp={toggleSelectApp}
              />
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  )

  function handleAppAction(app: InstalledApp, action: string) {
    switch (action) {
      case "launch":
        launchApp(app.id)
        break
      case "stop":
        stopApp(app.id)
        break
      case "update":
        updateApp(app.id)
        break
      case "uninstall":
        uninstallApp(app.id)
        break
      case "pin":
        togglePinApp(app.id)
        break
      case "autostart":
        toggleAutoStart(app.id)
        break
    }
  }
}

// Header Component
function Header({ statistics, viewMode, setViewMode, onCheckUpdates, isCheckingUpdates, updatesCount }: any) {
  return (
    <div className="border-b border-border">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-normal">Installed Applications</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage and monitor your installed applications
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={onCheckUpdates}
              disabled={isCheckingUpdates}
            >
              <Download className="h-4 w-4 mr-2" />
              {isCheckingUpdates ? "Checking..." : `Updates (${updatesCount})`}
            </Button>
            <div className="flex items-center gap-1 border rounded-lg p-1">
              {Object.values(VIEW_MODES).map((mode) => {
                const Icon = getIcon(mode.icon)
                return (
                  <Button
                    key={mode.id}
                    variant={viewMode === mode.id ? "secondary" : "ghost"}
                    size="sm"
                    onClick={() => setViewMode(mode.id as ViewMode)}
                    className="h-8 w-8 p-0"
                  >
                    <Icon className="h-4 w-4" />
                  </Button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Statistics Bar */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-muted-foreground">Active:</span>
            <span className="font-normal">{statistics.activeApps}</span>
          </div>
          <Separator orientation="vertical" className="h-4" />
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Total Apps:</span>
            <span className="font-normal">{statistics.totalApps}</span>
          </div>
          <Separator orientation="vertical" className="h-4" />
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Storage:</span>
            <span className="font-normal">{statistics.totalSize}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Filter Bar Component
function FilterBar({ filters, setFilter, resetFilters, sort, setSortBy, totalApps, selectedCount, onClearSelection, onDeleteSelected }: any) {
  return (
    <div className="border-b border-border px-6 py-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search apps by name, developer, or description..."
              value={filters.search}
              onChange={(e) => setFilter("search", e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filters Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {Object.values(filters).some(v => v && v !== "all") && (
                  <Badge variant="secondary" className="ml-2">
                    Active
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
              <DropdownMenuLabel>Filter Options</DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              <DropdownMenuLabel className="text-xs text-muted-foreground">Status</DropdownMenuLabel>
              {FILTER_OPTIONS.status.map(option => (
                <DropdownMenuItem
                  key={option.id}
                  onClick={() => setFilter("status", option.id as any)}
                >
                  <div className={`w-2 h-2 rounded-full mr-2 bg-${option.color}-500`} />
                  {option.label}
                  {filters.status === option.id && <CheckCircle2 className="h-3 w-3 ml-auto" />}
                </DropdownMenuItem>
              ))}
              
              <DropdownMenuSeparator />
              <DropdownMenuLabel className="text-xs text-muted-foreground">Features</DropdownMenuLabel>
              
              <DropdownMenuCheckboxItem
                checked={filters.showPinned}
                onCheckedChange={(checked) => setFilter("showPinned", checked)}
              >
                Pinned Apps
              </DropdownMenuCheckboxItem>
              
              <DropdownMenuCheckboxItem
                checked={filters.showAutoStart}
                onCheckedChange={(checked) => setFilter("showAutoStart", checked)}
              >
                Auto Start
              </DropdownMenuCheckboxItem>
              
              <DropdownMenuCheckboxItem
                checked={filters.showUpdatesAvailable}
                onCheckedChange={(checked) => setFilter("showUpdatesAvailable", checked)}
              >
                Updates Available
              </DropdownMenuCheckboxItem>
              
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={resetFilters}>
                <XCircle className="h-4 w-4 mr-2" />
                Clear Filters
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Sort Dropdown */}
          <Select value={sort.by} onValueChange={setSortBy}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Sort by..." />
            </SelectTrigger>
            <SelectContent>
              {SORT_OPTIONS.map(option => {
                const Icon = getIcon(option.icon)
                return (
                  <SelectItem key={option.id} value={option.id}>
                    <div className="flex items-center">
                      <Icon className="h-4 w-4 mr-2" />
                      {option.label}
                    </div>
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Selection Actions */}
        {selectedCount > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {selectedCount} selected
            </span>
            <Button variant="ghost" size="sm" onClick={onClearSelection}>
              Clear
            </Button>
            <Button variant="destructive" size="sm" onClick={onDeleteSelected}>
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </Button>
          </div>
        )}

        <div className="text-sm text-muted-foreground">
          {totalApps} apps found
        </div>
      </div>
    </div>
  )
}

// Sidebar Component
function Sidebar({ categories, currentCategory, onCategoryChange, statistics }: any) {
  return (
    <div className="w-64 border-r border-border bg-card/30">
      <ScrollArea className="h-full">
        <div className="p-4">
          <h3 className="font-normal mb-3">Categories</h3>
          <div className="space-y-1">
            {categories.map((category: any) => {
              const Icon = getIcon(category.icon)
              const count = category.id === "all" 
                ? statistics.totalApps 
                : statistics.categories.find((c: any) => c.name === category.id)?.count || 0
              
              return (
                <button
                  key={category.id}
                  onClick={() => onCategoryChange(category.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                    currentCategory === category.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    <span>{category.name}</span>
                  </div>
                  <Badge variant={currentCategory === category.id ? "secondary" : "outline"}>
                    {count}
                  </Badge>
                </button>
              )
            })}
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}

// Apps Grid View
function AppsGrid({ apps, selectedApps, onAppAction, onSelectApp }: any) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {apps.map((app: InstalledApp) => (
        <AppCard
          key={app.id}
          app={app}
          isSelected={selectedApps.includes(app.id)}
          onAction={onAppAction}
          onSelect={onSelectApp}
        />
      ))}
    </div>
  )
}

// Apps List View
function AppsList({ apps, selectedApps, onAppAction, onSelectApp }: any) {
  return (
    <div className="space-y-2">
      {apps.map((app: InstalledApp) => (
        <AppListItem
          key={app.id}
          app={app}
          isSelected={selectedApps.includes(app.id)}
          onAction={onAppAction}
          onSelect={onSelectApp}
        />
      ))}
    </div>
  )
}

// Apps Compact View
function AppsCompact({ apps, selectedApps, onAppAction, onSelectApp }: any) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {apps.map((app: InstalledApp) => (
        <AppCompactItem
          key={app.id}
          app={app}
          isSelected={selectedApps.includes(app.id)}
          onAction={onAppAction}
          onSelect={onSelectApp}
        />
      ))}
    </div>
  )
}

// App Card Component (Grid View)
function AppCard({ app, isSelected, onAction, onSelect }: any) {
  const Icon = getIcon(app.icon)
  const statusConfig = STATUS_CONFIG[app.status]
  
  return (
    <Card className={`p-4 transition-all hover:shadow-lg ${isSelected ? "ring-2 ring-primary" : ""}`}>
      <div className="flex flex-col items-center text-center">
        {/* App Icon */}
        <div className="relative mb-3">
          <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10">
            <Icon className="h-12 w-12 text-primary" />
          </div>
          <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${statusConfig.color}`} />
          {app.pinned && (
            <Pin className="absolute -top-2 -left-2 h-4 w-4 text-primary" />
          )}
        </div>

        {/* App Info */}
        <h3 className="font-normal text-sm mb-1">{app.displayName}</h3>
        <p className="text-xs text-muted-foreground mb-2">{app.developer}</p>
        
        {/* Version and Size */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
          <span>v{app.version}</span>
          <span>•</span>
          <span>{app.size}</span>
        </div>

        {/* Update Available Badge */}
        {app.updateAvailable && (
          <Badge variant="secondary" className="mb-3 text-xs">
            <Download className="h-3 w-3 mr-1" />
            Update to v{app.newVersion}
          </Badge>
        )}

        {/* Actions */}
        <div className="flex gap-1 w-full">
          <Button
            size="sm"
            variant={app.status === "active" ? "secondary" : "default"}
            className="flex-1"
            onClick={() => onAction(app, app.status === "active" ? "stop" : "launch")}
          >
            {app.status === "active" ? (
              <>
                <Square className="h-3 w-3 mr-1" />
                Stop
              </>
            ) : (
              <>
                <Play className="h-3 w-3 mr-1" />
                Open
              </>
            )}
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {app.updateAvailable && (
                <>
                  <DropdownMenuItem onClick={() => onAction(app, "update")}>
                    <Download className="h-4 w-4 mr-2" />
                    Update
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem onClick={() => onAction(app, "pin")}>
                <Pin className="h-4 w-4 mr-2" />
                {app.pinned ? "Unpin" : "Pin"}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onAction(app, "autostart")}>
                <Power className="h-4 w-4 mr-2" />
                {app.autoStart ? "Disable" : "Enable"} Auto Start
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Info className="h-4 w-4 mr-2" />
                App Info
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive"
                onClick={() => onAction(app, "uninstall")}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Uninstall
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </Card>
  )
}

// App List Item Component
function AppListItem({ app, isSelected, onAction, onSelect }: any) {
  const Icon = getIcon(app.icon)
  const statusConfig = STATUS_CONFIG[app.status]
  
  return (
    <Card className={`p-4 ${isSelected ? "ring-2 ring-primary" : ""}`}>
      <div className="flex items-center gap-4">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onSelect(app.id)}
          className="h-4 w-4"
        />

        {/* Icon */}
        <div className="relative">
          <div className="p-2 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10">
            <Icon className="h-8 w-8 text-primary" />
          </div>
          <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${statusConfig.color}`} />
        </div>

        {/* App Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-normal">{app.displayName}</h3>
            {app.pinned && <Pin className="h-3 w-3 text-primary" />}
            <Badge variant="outline" className="text-xs">v{app.version}</Badge>
            {app.status === "updating" && (
              <Badge variant="secondary" className="text-xs">
                <Download className="h-3 w-3 mr-1 animate-pulse" />
                Updating...
              </Badge>
            )}
            {app.updateAvailable && !app.status.includes("updating") && (
              <Badge variant="secondary" className="text-xs">
                Update available
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground mb-1">{app.developer}</p>
          <p className="text-xs text-muted-foreground line-clamp-1">{app.description}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
            <span>{app.size}</span>
            <span>Last used: {app.lastUsed}</span>
            {app.rating && (
              <div className="flex items-center gap-1">
                <Star className="h-3 w-3 fill-current text-yellow-500" />
                <span>{app.rating}</span>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={app.status === "active" ? "secondary" : "outline"}
            onClick={() => onAction(app, app.status === "active" ? "stop" : "launch")}
          >
            {app.status === "active" ? (
              <>
                <Square className="h-4 w-4 mr-1" />
                Stop
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-1" />
                Open
              </>
            )}
          </Button>
          
          {app.updateAvailable && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onAction(app, "update")}
            >
              <Download className="h-4 w-4" />
            </Button>
          )}
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onAction(app, "uninstall")}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
    </Card>
  )
}

// App Compact Item Component
function AppCompactItem({ app, isSelected, onAction, onSelect }: any) {
  const Icon = getIcon(app.icon)
  const statusConfig = STATUS_CONFIG[app.status]
  
  return (
    <Card className={`p-3 ${isSelected ? "ring-2 ring-primary" : ""}`}>
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onSelect(app.id)}
          className="h-4 w-4"
        />
        
        <div className="relative">
          <Icon className="h-6 w-6 text-primary" />
          <div className={`absolute -top-1 -right-1 w-2 h-2 rounded-full ${statusConfig.color}`} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-normal text-sm">{app.displayName}</span>
            {app.pinned && <Pin className="h-3 w-3 text-primary" />}
          </div>
          <div className="text-xs text-muted-foreground">
            {app.developer} • v{app.version} • {app.size}
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            className="h-7 w-7 p-0"
            onClick={() => onAction(app, app.status === "active" ? "stop" : "launch")}
          >
            {app.status === "active" ? (
              <Square className="h-3 w-3" />
            ) : (
              <Play className="h-3 w-3" />
            )}
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                <MoreVertical className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onAction(app, "uninstall")}>
                <Trash2 className="h-4 w-4 mr-2" />
                Uninstall
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </Card>
  )
}