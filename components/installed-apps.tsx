"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Search, Settings, Trash2, Play, Github, Slack, Brain, Grid3X3, List } from "lucide-react"

interface InstalledApp {
  id: string
  name: string
  developer: string
  version: string
  size: string
  lastUsed: string
  icon: React.ReactNode
  status: "active" | "inactive" | "updating"
}

const installedApps: InstalledApp[] = [
  {
    id: "github",
    name: "GitHub Desktop",
    developer: "GitHub, Inc.",
    version: "3.3.6",
    size: "89 MB",
    lastUsed: "Today",
    icon: <Github className="h-8 w-8" />,
    status: "active",
  },
  {
    id: "openai",
    name: "ChatGPT",
    developer: "OpenAI",
    version: "1.2024.352",
    size: "234 MB",
    lastUsed: "Yesterday",
    icon: <Brain className="h-8 w-8" />,
    status: "inactive",
  },
  {
    id: "slack",
    name: "Slack",
    developer: "Slack Technologies",
    version: "4.38.0",
    size: "145 MB",
    lastUsed: "2 days ago",
    icon: <Slack className="h-8 w-8" />,
    status: "updating",
  },
]

export function InstalledApps() {
  const [searchQuery, setSearchQuery] = useState("")
  const [viewMode, setViewMode] = useState<"grid" | "list">("list")
  const [apps, setApps] = useState(installedApps)

  const filteredApps = apps.filter(
    (app) =>
      app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.developer.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const uninstallApp = (appId: string) => {
    setApps((prev) => prev.filter((app) => app.id !== appId))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500"
      case "updating":
        return "bg-yellow-500"
      default:
        return "bg-gray-400"
    }
  }

  return (
    <div className="h-full bg-background">
      {/* Header */}
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Installed Apps</h1>
          <div className="flex items-center gap-2">
            <Button variant={viewMode === "grid" ? "secondary" : "ghost"} size="sm" onClick={() => setViewMode("grid")}>
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button variant={viewMode === "list" ? "secondary" : "ghost"} size="sm" onClick={() => setViewMode("list")}>
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search installed apps..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-muted/50"
            />
          </div>
          <div className="text-sm text-muted-foreground">{filteredApps.length} apps installed</div>
        </div>
      </div>

      {/* Apps List/Grid */}
      <div className="p-6">
        {viewMode === "list" ? (
          <div className="space-y-3">
            {filteredApps.map((app) => (
              <Card key={app.id} className="p-4">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 text-primary">
                      {app.icon}
                    </div>
                    <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${getStatusColor(app.status)}`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{app.name}</h3>
                      <Badge variant="outline" className="text-xs">
                        v{app.version}
                      </Badge>
                      {app.status === "updating" && (
                        <Badge variant="secondary" className="text-xs">
                          Updating...
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">{app.developer}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{app.size}</span>
                      <span>Last used: {app.lastUsed}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline">
                      <Play className="h-4 w-4 mr-1" />
                      Open
                    </Button>
                    <Button size="sm" variant="ghost">
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-destructive hover:text-destructive"
                      onClick={() => uninstallApp(app.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredApps.map((app) => (
              <Card key={app.id} className="p-4 text-center">
                <div className="relative inline-block mb-3">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 text-primary">
                    {app.icon}
                  </div>
                  <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${getStatusColor(app.status)}`} />
                </div>

                <h3 className="font-semibold mb-1">{app.name}</h3>
                <p className="text-sm text-muted-foreground mb-2">{app.developer}</p>

                <div className="space-y-1 text-xs text-muted-foreground mb-3">
                  <div>
                    v{app.version} • {app.size}
                  </div>
                  <div>Last used: {app.lastUsed}</div>
                </div>

                <div className="flex gap-1">
                  <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                    <Play className="h-3 w-3 mr-1" />
                    Open
                  </Button>
                  <Button size="sm" variant="ghost">
                    <Settings className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-destructive hover:text-destructive"
                    onClick={() => uninstallApp(app.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
