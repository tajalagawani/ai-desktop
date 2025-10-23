"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Shield,
  Key,
  Plus,
  Trash2,
  ArrowLeft,
  AlertCircle,
  Check,
  Search,
  RotateCw,
  Copy,
  Eye,
  EyeOff,
  FileKey
} from "lucide-react"
import { cn } from "@/lib/utils"

interface AuthenticatedNode {
  node_type: string
  display_name: string
  authenticated: boolean
  required_auth: string[]
  auth: Record<string, string>
  defaults: Record<string, string>
  added_at: string
}

interface CatalogNode {
  id: string
  displayName: string
  description: string
  operations: number
  tags: string[]
  authInfo?: {
    requiresAuth: boolean
    authFields: Array<{
      field: string
      type: string
      description: string
      required: boolean
    }>
  }
}

export function SecurityCenter() {
  const [nodes, setNodes] = useState<AuthenticatedNode[]>([])
  const [catalogNodes, setCatalogNodes] = useState<CatalogNode[]>([])
  const [loading, setLoading] = useState(true)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<AuthenticatedNode | CatalogNode | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [authData, setAuthData] = useState<Record<string, string>>({})
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({})
  const [logs, setLogs] = useState<string>("")
  const [signatureContent, setSignatureContent] = useState<string>("")
  const [selectedOperations, setSelectedOperations] = useState<string[]>([])
  const [nodeOperations, setNodeOperations] = useState<any[]>([])
  const [loadingOperations, setLoadingOperations] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; nodeType: string; nodeName: string }>({
    open: false,
    nodeType: '',
    nodeName: ''
  })

  // DEFINE addLog FIRST before using it!
  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    console.log(`[Security Center ${timestamp}] ${message}`)
    setLogs(prev => `[${timestamp}] ${message}\n${prev}`)
  }, [])

  // Load authenticated nodes from signature
  const loadNodes = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
      addLog('→ Loading authenticated nodes from signature...')
    }
    try {
      if (!silent) addLog('→ Fetching /api/signature')
      const response = await fetch('/api/signature')
      if (!silent) addLog(`← Response: ${response.status} ${response.statusText}`)

      const data = await response.json()
      if (!silent) addLog(`← Data received: ${JSON.stringify(data).substring(0, 100)}...`)

      if (data.authenticated_nodes && Array.isArray(data.authenticated_nodes)) {
        // Response format: { authenticated_nodes: ["github", "openai", ...] }
        if (!silent) {
          addLog(`✓ Found ${data.authenticated_nodes.length} authenticated node IDs`)
          addLog(`→ Node IDs: ${data.authenticated_nodes.join(', ')}`)
        }

        // Convert array of node IDs to node objects
        const nodeObjects = data.authenticated_nodes.map((nodeId: string) => ({
          node_type: nodeId,
          display_name: nodeId.charAt(0).toUpperCase() + nodeId.slice(1),
          authenticated: true,
          required_auth: [],
          auth: {},
          defaults: {},
          added_at: new Date().toISOString()
        }))

        setNodes(nodeObjects)
        if (!silent) addLog(`✓ Loaded ${nodeObjects.length} authenticated nodes`)
      } else if (data.status === 'success' && data.data) {
        setNodes(data.data.nodes || [])
        if (!silent) addLog(`✓ Loaded ${data.data.nodes?.length || 0} authenticated nodes`)
      } else if (data.nodes) {
        // Direct MCP response format
        setNodes(data.nodes || [])
        if (!silent) addLog(`✓ Loaded ${data.nodes?.length || 0} authenticated nodes (direct format)`)
      } else {
        if (!silent) {
          addLog('⚠ No nodes found in response')
          addLog(`→ Response structure: ${JSON.stringify(Object.keys(data))}`)
        }
      }
    } catch (error: any) {
      console.error('Failed to load nodes:', error)
      if (!silent) addLog(`✗ Failed to load nodes: ${error.message}`)
    } finally {
      if (!silent) setLoading(false)
    }
  }, [addLog])

  // Load catalog nodes
  const loadCatalog = useCallback(async () => {
    setCatalogLoading(true)
    addLog('→ Loading node catalog from database...')
    try {
      addLog('→ Fetching /api/nodes/auth-required')
      const response = await fetch('/api/nodes/auth-required')
      addLog(`← Response: ${response.status} ${response.statusText}`)

      const data = await response.json()
      addLog(`← Catalog data: ${JSON.stringify(data).substring(0, 100)}...`)

      if (data.nodes) {
        setCatalogNodes(data.nodes)
        addLog(`✓ Loaded ${data.nodes.length} nodes from catalog`)
      } else {
        addLog('⚠ No catalog nodes found')
      }
    } catch (error: any) {
      console.error('Failed to load catalog:', error)
      addLog(`✗ Failed to load catalog: ${error.message}`)
    } finally {
      setCatalogLoading(false)
    }
  }, [addLog])

  // Load signature file content
  const loadSignatureFile = useCallback(async () => {
    addLog('→ Loading signature file content...')
    try {
      const response = await fetch('/api/signature/raw')
      const content = await response.text()
      setSignatureContent(content)
      addLog(`✓ Loaded signature file (${content.length} characters)`)
    } catch (error: any) {
      addLog(`✗ Failed to load signature file: ${error.message}`)
    }
  }, [addLog])

  useEffect(() => {
    addLog('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    addLog('🚀 Security Center initialized')
    addLog('→ Starting initial data load...')
    loadNodes(false)
    loadCatalog()
    loadSignatureFile()

    // Silent refresh every 30 seconds
    addLog('→ Setting up auto-refresh (every 30 seconds)')
    const interval = setInterval(() => {
      addLog('⟳ Auto-refresh triggered')
      loadNodes(true)
    }, 30000)
    return () => {
      addLog('🛑 Security Center unmounting, clearing interval')
      clearInterval(interval)
    }
  }, [loadNodes, loadCatalog, loadSignatureFile])

  const handleRemoveNode = async (nodeType: string, nodeName: string) => {
    // Open confirmation dialog
    setDeleteDialog({ open: true, nodeType, nodeName })
  }

  const confirmRemoveNode = async () => {
    const { nodeType } = deleteDialog
    addLog(`→ User confirmed removal of '${nodeType}'`)
    setDeleteDialog({ open: false, nodeType: '', nodeName: '' })
    setActionLoading(nodeType)
    try {
      addLog(`→ Sending DELETE request to /api/signature?node_type=${nodeType}`)
      const response = await fetch(`/api/signature?node_type=${nodeType}`, {
        method: 'DELETE'
      })
      addLog(`← Response: ${response.status} ${response.statusText}`)

      const data = await response.json()
      addLog(`← Response data: ${JSON.stringify(data)}`)

      if (data.status === 'success' || data.success) {
        addLog(`✓ Node '${nodeType}' removed from signature successfully`)
        // Update nodes list without reloading (prevents flashing)
        setNodes(prev => prev.filter(n => n.node_type !== nodeType))
        setSelectedNode(null)
        loadSignatureFile()
        addLog(`✓ UI updated`)
      } else {
        throw new Error(data.error || 'Failed to remove node')
      }
    } catch (error: any) {
      addLog(`✗ Failed to remove node: ${error.message}`)
    } finally {
      setTimeout(() => setActionLoading(null), 1000)
    }
  }

  // Load operations for a node from CATALOG (for unauthenticated nodes)
  const loadNodeOperations = useCallback(async (nodeType: string, silent = false) => {
    setLoadingOperations(true)
    if (!silent) addLog(`→ Loading operations for '${nodeType}' from catalog...`)
    try {
      const response = await fetch(`/api/nodes/operations?node_type=${nodeType}`)
      const data = await response.json()

      if (data.operations) {
        setNodeOperations(data.operations)
        setSelectedOperations([]) // Clear previous selection
        if (!silent) addLog(`✓ Loaded ${data.operations.length} operations from catalog`)
      }
    } catch (error: any) {
      if (!silent) addLog(`✗ Failed to load operations: ${error.message}`)
    } finally {
      setLoadingOperations(false)
    }
  }, [addLog])

  // Load operations from SIGNATURE FILE (for authenticated nodes)
  const loadSignatureOperations = useCallback(async (nodeType: string, silent = false) => {
    setLoadingOperations(true)
    if (!silent) addLog(`→ Loading operations for '${nodeType}' from signature file...`)
    try {
      const response = await fetch(`/api/signature/operations?node_type=${nodeType}`)
      const data = await response.json()

      if (data.operations) {
        setNodeOperations(data.operations)
        if (!silent) addLog(`✓ Loaded ${data.operations.length} operations from signature`)
      } else {
        setNodeOperations([])
        if (!silent) addLog(`⚠ No operations found in signature for '${nodeType}'`)
      }
    } catch (error: any) {
      if (!silent) addLog(`✗ Failed to load operations from signature: ${error.message}`)
      setNodeOperations([])
    } finally {
      setLoadingOperations(false)
    }
  }, [addLog])

  // AUTO-LOAD operations when a node is selected (silent mode to prevent flashing)
  useEffect(() => {
    if (selectedNode) {
      const nodeId = 'id' in selectedNode ? selectedNode.id : selectedNode.node_type
      const isAuthenticated = 'authenticated' in selectedNode && selectedNode.authenticated

      // Clear previous operations first
      setNodeOperations([])
      setSelectedOperations([])

      // Load operations from signature for authenticated nodes, catalog for unauthenticated
      if (isAuthenticated) {
        loadSignatureOperations(nodeId, true)
      } else {
        loadNodeOperations(nodeId, true)
      }
    }
  }, [selectedNode, loadNodeOperations, loadSignatureOperations])

  const handleAddNode = async (catalogNode: CatalogNode) => {
    addLog(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`)
    addLog(`→ Starting authentication for '${catalogNode.displayName}' (${catalogNode.id})`)
    addLog(`→ Auth fields provided: ${Object.keys(authData).join(', ')}`)
    addLog(`→ Selected operations: ${selectedOperations.length === 0 ? 'ALL' : selectedOperations.join(', ')}`)

    setActionLoading(catalogNode.id)
    try {
      const requestBody = {
        node_type: catalogNode.id,
        auth: authData,
        defaults: {},
        operations: selectedOperations.length > 0 ? selectedOperations : undefined // Only include if user selected specific ones
      }

      addLog(`→ Preparing POST request to /api/signature`)
      addLog(`→ selectedOperations count: ${selectedOperations.length}`)
      addLog(`→ selectedOperations array: [${selectedOperations.join(', ')}]`)
      addLog(`→ Full request body:`)
      addLog(JSON.stringify(requestBody, null, 2))

      const response = await fetch('/api/signature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      addLog(`← Response: ${response.status} ${response.statusText}`)

      const data = await response.json()
      addLog(`← Response data: ${JSON.stringify(data)}`)

      if (data.status === 'success' || data.success) {
        addLog(`✓✓✓ SUCCESS! Node '${catalogNode.id}' authenticated!`)
        addLog(`  → Node type: ${catalogNode.id}`)
        addLog(`  → Display name: ${catalogNode.displayName}`)
        addLog(`  → Operations included: ${selectedOperations.length === 0 ? 'ALL' : selectedOperations.length}`)
        addLog(`  → Authenticated: ${data.data?.authenticated || data.authenticated || 'unknown'}`)
        addLog(`→ Clearing auth form data...`)
        // Add node to list without full reload (prevents flashing)
        const newNode = {
          node_type: catalogNode.id,
          display_name: catalogNode.displayName,
          authenticated: true,
          required_auth: [],
          auth: {},
          defaults: {},
          added_at: new Date().toISOString()
        }
        setNodes(prev => [...prev, newNode])
        setAuthData({})
        setSelectedOperations([])
        setNodeOperations([])
        setSelectedNode(null)
        loadSignatureFile()
        addLog(`✓ UI updated and form cleared`)
        addLog(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`)

        // Dispatch event to notify chat that authentication is complete
        window.dispatchEvent(new CustomEvent('node-authenticated', {
          detail: {
            nodeType: catalogNode.id,
            nodeName: catalogNode.displayName
          }
        }))
        addLog(`→ Dispatched 'node-authenticated' event for ${catalogNode.displayName}`)
      } else {
        throw new Error(data.error || 'Failed to add node')
      }
    } catch (error: any) {
      addLog(`✗✗✗ ERROR! Failed to add node: ${error.message}`)
      addLog(`  → Stack: ${error.stack?.substring(0, 200)}`)
      addLog(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`)
    } finally {
      setTimeout(() => setActionLoading(null), 1000)
    }
  }

  const copyToClipboard = (text: string) => {
    addLog(`→ Copying to clipboard: ${text.substring(0, 50)}...`)
    navigator.clipboard.writeText(text)
      .then(() => {
        addLog(`✓ Successfully copied to clipboard`)
      })
      .catch((error) => {
        addLog(`✗ Failed to copy to clipboard: ${error.message}`)
      })
  }

  const filteredCatalogNodes = useMemo(() => {
    if (!searchQuery.trim()) return catalogNodes
    const query = searchQuery.toLowerCase()
    return catalogNodes.filter(node =>
      node.displayName.toLowerCase().includes(query) ||
      node.description.toLowerCase().includes(query)
    )
  }, [catalogNodes, searchQuery])

  const allNodes = useMemo(() => {
    // Merge authenticated nodes with catalog info
    return catalogNodes.map(catalogNode => {
      const authNode = nodes.find(n => n.node_type === catalogNode.id)
      return authNode || catalogNode
    })
  }, [nodes, catalogNodes])

  const filteredNodes = useMemo(() => {
    if (!searchQuery.trim()) return allNodes
    const query = searchQuery.toLowerCase()
    return allNodes.filter(node => {
      const displayName = 'display_name' in node ? node.display_name : node.displayName
      const desc = 'description' in node ? node.description : ''
      return displayName.toLowerCase().includes(query) || desc.toLowerCase().includes(query)
    })
  }, [allNodes, searchQuery])

  const stats = useMemo(() => {
    return {
      total: catalogNodes.length,
      authenticated: nodes.filter(n => n.authenticated).length,
      available: catalogNodes.length - nodes.length,
    }
  }, [nodes, catalogNodes])

  const isAuthenticated = (nodeId: string) => {
    return nodes.some(n => n.node_type === nodeId && n.authenticated)
  }

  if (loading) {
    return (
      <div className="h-full bg-background">
        <div className="grid h-full grid-cols-[320px_1fr]">
          <div className="border-r p-6 flex flex-col">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
          <div className="p-8">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-background">
      <div className="grid h-full grid-cols-[320px_1fr]">
        {/* Left Panel - Stats */}
        <div className="relative overflow-hidden border-r bg-background p-6 h-full flex flex-col">
          <div className="mb-6">
            <h2 className="text-lg font-normal mb-2">Security Center</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Manage node authentication for ACT workflows.
            </p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.authenticated}</div>
              <div className="text-xs text-muted-foreground">Authenticated</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.available}</div>
              <div className="text-xs text-muted-foreground">Available</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{nodes.length}</div>
              <div className="text-xs text-muted-foreground">In Signature</div>
            </Card>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => loadNodes(false)} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <span>→</span>
            </Button>
          </div>
        </div>

        {/* Right Panel - Dynamic Content */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedNode ? (
            // Node Detail View with Tabs
            <div className="flex flex-col flex-1 min-h-0">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2 w-fit"
                onClick={() => {
                  addLog('← User clicked "Back to nodes"')
                  setSelectedNode(null)
                  setAuthData({})
                  setNodeOperations([])
                  setSelectedOperations([])
                  addLog('✓ Cleared selection and auth data')
                }}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to nodes
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
                  <Shield className="h-8 w-8 text-primary" />
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-2xl font-normal">
                      {'display_name' in selectedNode ? selectedNode.display_name : selectedNode.displayName}
                    </h2>
                    {'authenticated' in selectedNode && selectedNode.authenticated ? (
                      <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                        <Check className="mr-1 h-3 w-3" />
                        Authenticated
                      </Badge>
                    ) : (
                      <Badge variant="secondary">Not Authenticated</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {'node_type' in selectedNode ? selectedNode.node_type : selectedNode.id}
                  </p>
                </div>

                {/* Action Buttons */}
                {'authenticated' in selectedNode && selectedNode.authenticated && (
                  <div className="flex gap-2 items-center flex-shrink-0">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRemoveNode(selectedNode.node_type, selectedNode.display_name)}
                      disabled={actionLoading === selectedNode.node_type}
                      title="Remove node"
                    >
                      {actionLoading === selectedNode.node_type ? (
                        <RotateCw className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Trash2 className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Overview Content - Always Visible */}
              <div className="space-y-3 flex-shrink-0">
                {/* Auth Details for Authenticated Nodes */}
                {'authenticated' in selectedNode && selectedNode.authenticated && (
                  <div className="p-3 bg-muted/50 rounded-lg space-y-2.5">
                    <h3 className="font-normal text-sm flex items-center gap-2">
                      <Key className="h-3.5 w-3.5" />
                      Authentication Details
                    </h3>
                    <div className="space-y-1.5">
                      {selectedNode.required_auth.map(field => (
                        <div key={field} className="flex justify-between items-center text-sm">
                          <span className="text-muted-foreground">{field}:</span>
                          <div className="flex items-center gap-1.5">
                            <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                              {selectedNode.auth[field]?.substring(0, 20)}***
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => copyToClipboard(selectedNode.auth[field])}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                      <div className="flex justify-between items-center text-sm border-t pt-1.5 mt-1.5">
                        <span className="text-muted-foreground">Added:</span>
                        <span className="text-xs">{new Date(selectedNode.added_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Auth Form for Catalog Nodes */}
                {!('authenticated' in selectedNode) && 'authInfo' in selectedNode && selectedNode.authInfo && (
                  <form
                    className="p-3 bg-muted/50 rounded-lg space-y-3"
                    onSubmit={(e) => {
                      e.preventDefault()
                      handleAddNode(selectedNode)
                    }}
                  >
                    <h3 className="font-normal text-sm flex items-center gap-2">
                      <Key className="h-3.5 w-3.5" />
                      Configure Authentication
                    </h3>
                    {selectedNode.authInfo.authFields.map(field => (
                      <div key={field.field}>
                        <label className="text-sm font-medium mb-1 block">
                          {field.field.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <div className="relative">
                          <Input
                            type={showPassword[field.field] ? 'text' : (field.type === 'secret' ? 'password' : 'text')}
                            placeholder={field.description}
                            value={authData[field.field] || ''}
                            onChange={(e) => setAuthData({ ...authData, [field.field]: e.target.value })}
                            className="pr-10"
                            autoComplete={field.type === 'secret' ? 'off' : 'on'}
                          />
                          {field.type === 'secret' && (
                            <Button
                              type="button"
                              size="sm"
                              variant="ghost"
                              className="absolute right-0 top-0 h-full"
                              onClick={() => setShowPassword({ ...showPassword, [field.field]: !showPassword[field.field] })}
                            >
                              {showPassword[field.field] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{field.description}</p>
                      </div>
                    ))}

                    <Button
                      type="submit"
                      disabled={actionLoading === selectedNode.id || (nodeOperations.length > 0 && selectedOperations.length === 0)}
                    >
                      {actionLoading === selectedNode.id ? (
                        <>
                          <RotateCw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                          Authenticating...
                        </>
                      ) : nodeOperations.length > 0 && selectedOperations.length === 0 ? (
                        <>
                          <Check className="w-4 h-4 mr-2" />
                          Select operations in Configuration tab
                        </>
                      ) : (
                        <>
                          <Check className="w-4 h-4 mr-2" />
                          Add to Signature
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </div>

              {/* Tabs for Configuration, Logs, Signature */}
              <Tabs defaultValue="config" className="flex-1 flex flex-col mt-2 min-h-0">
                <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
                  <TabsTrigger value="config">Configuration</TabsTrigger>
                  <TabsTrigger value="logs">Logs</TabsTrigger>
                  <TabsTrigger value="signature">Signature File</TabsTrigger>
                </TabsList>

                {/* Configuration Tab - Operations Selector ONLY */}
                <TabsContent value="config" className="flex-1 overflow-auto mt-0 min-h-0">
                  <Card className="p-3">
                    {/* Operations Manager - For authenticated nodes - SHOW OPERATIONS FROM SIG */}
                    {'authenticated' in selectedNode && selectedNode.authenticated ? (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-normal text-sm">Operations in Signature</h3>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              loadSignatureOperations(selectedNode.node_type, false)
                            }}
                            disabled={loadingOperations}
                          >
                            {loadingOperations ? (
                              <><RotateCw className="h-3 w-3 mr-1 animate-spin" />Loading...</>
                            ) : (
                              'Reload from Signature'
                            )}
                          </Button>
                        </div>

                        <div className="text-sm text-muted-foreground mb-3">
                          This node is authenticated. Operations listed below are stored in the signature file.
                        </div>

                        {nodeOperations.length > 0 ? (
                          <div className="space-y-2">
                            <div className="text-xs text-muted-foreground mb-2">
                              {nodeOperations.length} operations available
                            </div>
                            <div className="max-h-96 overflow-y-auto border rounded p-2 space-y-1">
                              {nodeOperations.map((op: any) => (
                                <div
                                  key={op.name}
                                  className="flex items-start gap-3 p-2 rounded bg-muted/30"
                                >
                                  <Check className="h-4 w-4 text-primary mt-1 flex-shrink-0" />
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-medium">{op.displayName || op.name}</span>
                                      {op.category && (
                                        <Badge variant="secondary" className="text-xs">
                                          {op.category}
                                        </Badge>
                                      )}
                                    </div>
                                    {op.description && (
                                      <p className="text-xs text-muted-foreground mt-1">{op.description}</p>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-sm text-muted-foreground text-center py-8 border rounded bg-muted/30">
                            <Shield className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
                            <p className="mb-2">Click "Load All Operations" to see what operations are available for this node.</p>
                            <p className="text-xs">These operations are stored in your signature file.</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      /* Operations Manager - For unauthenticated nodes */
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-normal text-sm">Select Operations</h3>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                if (nodeOperations.length > 0) {
                                  setSelectedOperations(nodeOperations.map(op => op.name))
                                  addLog(`✓ Selected all ${nodeOperations.length} operations`)
                                } else {
                                  loadNodeOperations('id' in selectedNode ? selectedNode.id : selectedNode.node_type)
                                }
                              }}
                              disabled={loadingOperations}
                            >
                              {loadingOperations ? (
                                <><RotateCw className="h-3 w-3 mr-1 animate-spin" />Loading...</>
                              ) : nodeOperations.length > 0 ? (
                                'Select All'
                              ) : (
                                'Load Operations'
                              )}
                            </Button>
                            {nodeOperations.length > 0 && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setSelectedOperations([])
                                  addLog('✓ Cleared operation selection')
                                }}
                              >
                                Clear All
                              </Button>
                            )}
                          </div>
                        </div>

                        {nodeOperations.length > 0 ? (
                          <div className="space-y-2">
                            <div className="text-xs text-muted-foreground mb-2">
                              {selectedOperations.length > 0
                                ? `${selectedOperations.length} of ${nodeOperations.length} operations selected`
                                : `Select at least 1 operation to continue`}
                            </div>
                            <div className="max-h-96 overflow-y-auto border rounded p-2 space-y-1">
                              {nodeOperations.map((op: any) => (
                                <label
                                  key={op.name}
                                  className="flex items-start gap-3 p-2 hover:bg-muted rounded cursor-pointer transition-colors"
                                >
                                  <input
                                    type="checkbox"
                                    checked={selectedOperations.includes(op.name)}
                                    onChange={(e) => {
                                      if (e.target.checked) {
                                        setSelectedOperations([...selectedOperations, op.name])
                                      } else {
                                        setSelectedOperations(selectedOperations.filter(n => n !== op.name))
                                      }
                                    }}
                                    className="mt-1 rounded"
                                  />
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-medium">{op.displayName || op.name}</span>
                                      {op.category && (
                                        <Badge variant="secondary" className="text-xs">
                                          {op.category}
                                        </Badge>
                                      )}
                                    </div>
                                    {op.description && (
                                      <p className="text-xs text-muted-foreground mt-1">{op.description}</p>
                                    )}
                                  </div>
                                </label>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-sm text-muted-foreground text-center py-4">
                            Click "Load Operations" to see available operations for this node
                          </div>
                        )}
                      </div>
                    )}
                  </Card>
                </TabsContent>

                {/* Logs Tab */}
                <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
                  <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
                    <div className="flex items-center justify-between mb-2 flex-shrink-0">
                      <h3 className="font-normal text-sm">Operation Logs</h3>
                      <Button size="sm" onClick={() => {
                        addLog('🗑 User clicked "Clear Logs"')
                        setTimeout(() => setLogs(''), 100)
                      }}>
                        <Trash2 className="h-3 w-3 mr-1.5" />
                        Clear
                      </Button>
                    </div>
                    <div className="flex-1 min-h-0 bg-black rounded overflow-hidden">
                      <pre className="h-full w-full p-3 text-green-400 font-mono text-xs overflow-y-scroll overflow-x-hidden whitespace-pre-wrap break-words scrollbar-thin will-change-scroll">
                        {logs || 'No operations yet. Logs will appear here when you add or remove nodes.'}
                      </pre>
                    </div>
                  </Card>
                </TabsContent>

                {/* Signature File Tab */}
                <TabsContent value="signature" className="flex-1 flex flex-col mt-0 min-h-0">
                  <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
                    <div className="flex items-center justify-between mb-2 flex-shrink-0">
                      <h3 className="font-normal text-sm">user.act.sig</h3>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => {
                          addLog('🔄 Reloading signature file...')
                          loadSignatureFile()
                        }}>
                          <RotateCw className="h-3 w-3 mr-1.5" />
                          Reload
                        </Button>
                        <Button size="sm" onClick={() => {
                          addLog('📋 Copied signature file path to clipboard')
                          navigator.clipboard.writeText('/Users/tajnoah/Downloads/ai-desktop/signature-system/signatures/user.act.sig')
                        }}>
                          <Copy className="h-3 w-3 mr-1.5" />
                          Copy Path
                        </Button>
                      </div>
                    </div>
                    <div className="flex-1 min-h-0 bg-black rounded overflow-hidden">
                      <pre className="h-full w-full p-3 text-green-400 font-mono text-xs overflow-y-scroll overflow-x-auto whitespace-pre scrollbar-thin will-change-scroll">
                        {signatureContent || 'Loading signature file...'}
                      </pre>
                    </div>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          ) : (
            // Nodes List View
            <div className="flex flex-col flex-1 min-h-0">
              <div className="mb-6 flex items-start justify-between gap-4 flex-shrink-0">
                <div className="flex-1">
                  <h2 className="mb-2 text-lg font-normal">Available Nodes</h2>
                  <p className="text-sm text-muted-foreground">
                    Authenticate nodes to use them in your workflows.
                  </p>
                </div>
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search nodes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </div>

              {/* Nodes List */}
              <div className="flex-1 min-h-0 overflow-y-scroll overflow-x-hidden pr-4 scrollbar-thin will-change-scroll">
                <div className="space-y-3">
                  {filteredNodes.map((node) => {
                    const nodeId = 'node_type' in node ? node.node_type : node.id
                    const displayName = 'display_name' in node ? node.display_name : node.displayName
                    const authenticated = isAuthenticated(nodeId)

                    return (
                      <div
                        key={nodeId}
                        onClick={() => setSelectedNode(node)}
                        className="flex items-center gap-4 p-4 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                      >
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                          <Shield className="w-6 h-6 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-normal">{displayName}</h3>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {'description' in node ? node.description : `Type: ${nodeId}`}
                          </p>
                        </div>

                        {/* Status Badge & Action Buttons */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {authenticated ? (
                            <>
                              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                                <Check className="mr-1 h-3 w-3" />
                                Authenticated
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleRemoveNode(nodeId, displayName)
                                }}
                                disabled={actionLoading === nodeId}
                                title="Remove node"
                              >
                                {actionLoading === nodeId ? (
                                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                ) : (
                                  <Trash2 className="h-3.5 w-3.5" />
                                )}
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              className="bg-transparent"
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedNode(node)
                              }}
                            >
                              <Plus className="h-3.5 w-3.5 mr-1.5" />
                              Add
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialog.open} onOpenChange={(open) => !open && setDeleteDialog({ open: false, nodeType: '', nodeName: '' })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Node from Signature?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove <strong>{deleteDialog.nodeName}</strong> ({deleteDialog.nodeType}) from your signature file?
              <br /><br />
              This will remove all authentication credentials and operations for this node. You'll need to re-authenticate if you want to use it again.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => {
              addLog(`✗ User cancelled removal of '${deleteDialog.nodeType}'`)
              setDeleteDialog({ open: false, nodeType: '', nodeName: '' })
            }}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={confirmRemoveNode} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Remove Node
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
