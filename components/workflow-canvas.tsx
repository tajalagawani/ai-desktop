"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, Plus, Save, Slack, Github, Brain, Settings } from "lucide-react"

interface WorkflowNode {
  id: string
  type: string
  name: string
  icon: React.ReactNode
  position: { x: number; y: number }
  status: "idle" | "running" | "success" | "error"
}

interface Connection {
  from: string
  to: string
}

export function WorkflowCanvas() {
  const [nodes, setNodes] = useState<WorkflowNode[]>([
    {
      id: "github-1",
      type: "github",
      name: "GitHub PR Created",
      icon: <Github className="h-4 w-4" />,
      position: { x: 100, y: 200 },
      status: "idle",
    },
    {
      id: "openai-1",
      type: "openai",
      name: "Generate Summary",
      icon: <Brain className="h-4 w-4" />,
      position: { x: 350, y: 200 },
      status: "idle",
    },
    {
      id: "slack-1",
      type: "slack",
      name: "Send to Channel",
      icon: <Slack className="h-4 w-4" />,
      position: { x: 600, y: 200 },
      status: "idle",
    },
  ])

  const [connections] = useState<Connection[]>([
    { from: "github-1", to: "openai-1" },
    { from: "openai-1", to: "slack-1" },
  ])

  const [isRunning, setIsRunning] = useState(false)

  const runWorkflow = () => {
    setIsRunning(true)
    // Simulate workflow execution
    setTimeout(() => {
      setNodes((prev) => prev.map((node) => ({ ...node, status: "running" })))
      setTimeout(() => {
        setNodes((prev) => prev.map((node) => ({ ...node, status: "success" })))
        setIsRunning(false)
      }, 2000)
    }, 500)
  }

  const getStatusColor = (status: WorkflowNode["status"]) => {
    switch (status) {
      case "running":
        return "bg-yellow-500"
      case "success":
        return "bg-green-500"
      case "error":
        return "bg-red-500"
      default:
        return "bg-muted"
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="border-b border-border/50 p-4 bg-card/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="font-semibold">PR → Summary → Slack</h2>
            <Badge variant="secondary">Draft</Badge>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline">
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button size="sm" onClick={runWorkflow} disabled={isRunning} className="bg-primary hover:bg-primary/90">
              {isRunning ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {isRunning ? "Running..." : "Run Workflow"}
            </Button>
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative bg-muted/20 overflow-hidden">
        {/* Grid Background */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(to right, oklch(0.22 0.02 264) 1px, transparent 1px),
              linear-gradient(to bottom, oklch(0.22 0.02 264) 1px, transparent 1px)
            `,
            backgroundSize: "20px 20px",
          }}
        />

        {/* Connections */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {connections.map((connection, index) => {
            const fromNode = nodes.find((n) => n.id === connection.from)
            const toNode = nodes.find((n) => n.id === connection.to)

            if (!fromNode || !toNode) return null

            const fromX = fromNode.position.x + 120
            const fromY = fromNode.position.y + 40
            const toX = toNode.position.x
            const toY = toNode.position.y + 40

            return (
              <g key={index}>
                <path
                  d={`M ${fromX} ${fromY} C ${fromX + 50} ${fromY} ${toX - 50} ${toY} ${toX} ${toY}`}
                  stroke="oklch(0.65 0.25 264)"
                  strokeWidth="2"
                  fill="none"
                  className={isRunning ? "animate-pulse" : ""}
                />
                <circle cx={toX - 8} cy={toY} r="4" fill="oklch(0.65 0.25 264)" />
              </g>
            )
          })}
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <Card
            key={node.id}
            className="absolute w-32 p-3 cursor-move hover:shadow-lg transition-shadow"
            style={{
              left: node.position.x,
              top: node.position.y,
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="p-1 rounded bg-primary/10 text-primary">{node.icon}</div>
              <div className={`w-2 h-2 rounded-full ${getStatusColor(node.status)}`} />
            </div>
            <div className="text-xs font-medium text-balance">{node.name}</div>
            <Button size="sm" variant="ghost" className="w-full mt-2 h-6 text-xs">
              <Settings className="h-3 w-3 mr-1" />
              Config
            </Button>
          </Card>
        ))}

        {/* Add Node Button */}
        <Button className="absolute bottom-4 right-4 rounded-full w-12 h-12" size="sm">
          <Plus className="h-5 w-5" />
        </Button>
      </div>

      {/* Status Bar */}
      <div className="border-t border-border/50 p-2 bg-card/30 text-xs text-muted-foreground">
        <div className="flex items-center justify-between">
          <span>3 nodes • 2 connections</span>
          <span>Last run: Never</span>
        </div>
      </div>
    </div>
  )
}
