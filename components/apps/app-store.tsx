"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Download, Star, Github, Slack, Mail, Database, Brain, Cloud } from "lucide-react"

interface Node {
  id: string
  name: string
  description: string
  category: string
  icon: React.ReactNode
  installed: boolean
  rating: number
  downloads: string
  tags: string[]
}

const mockNodes: Node[] = [
  {
    id: "slack",
    name: "Slack",
    description: "Send messages, create channels, and manage your Slack workspace",
    category: "Communication",
    icon: <Slack className="h-6 w-6" />,
    installed: false,
    rating: 4.8,
    downloads: "50K+",
    tags: ["messaging", "team", "productivity"],
  },
  {
    id: "github",
    name: "GitHub",
    description: "Manage repositories, issues, and pull requests",
    category: "Dev Tools",
    icon: <Github className="h-6 w-6" />,
    installed: true,
    rating: 4.9,
    downloads: "100K+",
    tags: ["git", "code", "collaboration"],
  },
  {
    id: "openai",
    name: "OpenAI",
    description: "Access GPT models for text generation and analysis",
    category: "AI/ML",
    icon: <Brain className="h-6 w-6" />,
    installed: true,
    rating: 4.7,
    downloads: "75K+",
    tags: ["ai", "gpt", "text-generation"],
  },
  {
    id: "email",
    name: "Email",
    description: "Send and receive emails with SMTP/IMAP support",
    category: "Communication",
    icon: <Mail className="h-6 w-6" />,
    installed: false,
    rating: 4.5,
    downloads: "30K+",
    tags: ["email", "smtp", "communication"],
  },
  {
    id: "database",
    name: "PostgreSQL",
    description: "Connect and query PostgreSQL databases",
    category: "Database",
    icon: <Database className="h-6 w-6" />,
    installed: false,
    rating: 4.6,
    downloads: "25K+",
    tags: ["database", "sql", "postgres"],
  },
  {
    id: "aws",
    name: "AWS S3",
    description: "Upload, download, and manage files in Amazon S3",
    category: "Cloud/Infra",
    icon: <Cloud className="h-6 w-6" />,
    installed: false,
    rating: 4.4,
    downloads: "40K+",
    tags: ["aws", "storage", "cloud"],
  },
]

const categories = ["All Categories", "Communication", "Dev Tools", "AI/ML", "Database", "Cloud/Infra", "Utilities"]

export function AppStore() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All Categories")
  const [nodes, setNodes] = useState(mockNodes)

  const filteredNodes = nodes.filter((node) => {
    const matchesSearch =
      node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      node.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      node.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesCategory = selectedCategory === "All Categories" || node.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const installNode = (nodeId: string) => {
    setNodes((prev) => prev.map((node) => (node.id === nodeId ? { ...node, installed: true } : node)))
  }

  const uninstallNode = (nodeId: string) => {
    setNodes((prev) => prev.map((node) => (node.id === nodeId ? { ...node, installed: false } : node)))
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-64 border-r border-border/50 p-4 bg-card/30">
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Categories</h3>
            <div className="space-y-1">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "secondary" : "ghost"}
                  size="sm"
                  className="w-full justify-start text-sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Installed Nodes</h3>
            <div className="text-sm text-muted-foreground">
              {nodes.filter((n) => n.installed).length} of {nodes.length} installed
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Node Registry</h1>
          <p className="text-muted-foreground mb-4">
            Discover and install nodes to extend your AI workflow capabilities
          </p>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Node Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNodes.map((node) => (
            <Card key={node.id} className="p-4 node-card-hover">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 rounded-lg bg-primary/10 text-primary">{node.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">{node.name}</h3>
                    {node.installed && (
                      <Badge variant="secondary" className="text-xs">
                        Installed
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{node.description}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      {node.rating}
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="h-3 w-3" />
                      {node.downloads}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-3">
                {node.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              <div className="flex gap-2">
                {node.installed ? (
                  <>
                    <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                      Configure
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => uninstallNode(node.id)}>
                      Remove
                    </Button>
                  </>
                ) : (
                  <Button size="sm" className="flex-1" onClick={() => installNode(node.id)}>
                    <Download className="h-4 w-4 mr-2" />
                    Install
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
