"use client"

import { useState, useEffect } from "react"
import { getIcon } from "@/utils/icon-mapper"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface OAuthCredential {
  provider: string
  clientId: string
  clientSecret: string
  configured: boolean
}

const OAUTH_PROVIDERS = [
  {
    id: 'github',
    name: 'GitHub',
    icon: 'Github',
    color: 'text-gray-900 dark:text-white',
    setupUrl: 'https://github.com/settings/developers',
    callbackPath: '/api/oauth/github/callback',
    description: 'For GitHub MCP server (repositories, issues, PRs)',
    scopes: 'repo, user, read:org'
  },
  {
    id: 'gitlab',
    name: 'GitLab',
    icon: 'GitBranch',
    color: 'text-orange-600',
    setupUrl: 'https://gitlab.com/-/profile/applications',
    callbackPath: '/api/oauth/gitlab/callback',
    description: 'For GitLab MCP server (projects, pipelines)',
    scopes: 'api, read_user, read_repository'
  },
  {
    id: 'google',
    name: 'Google',
    icon: 'Chrome',
    color: 'text-blue-600',
    setupUrl: 'https://console.cloud.google.com/apis/credentials',
    callbackPath: '/api/oauth/google/callback',
    description: 'For Google Drive, Gmail, Calendar MCP servers',
    scopes: 'drive, gmail.readonly, calendar'
  },
  {
    id: 'slack',
    name: 'Slack',
    icon: 'MessageSquare',
    color: 'text-purple-600',
    setupUrl: 'https://api.slack.com/apps',
    callbackPath: '/api/oauth/slack/callback',
    description: 'For Slack MCP server (messages, channels)',
    scopes: 'channels:history, channels:read, chat:write, users:read'
  },
  {
    id: 'stripe',
    name: 'Stripe',
    icon: 'CreditCard',
    color: 'text-indigo-600',
    setupUrl: 'https://dashboard.stripe.com/settings/applications',
    callbackPath: '/api/oauth/stripe/callback',
    description: 'For Stripe MCP server (payments, customers)',
    scopes: 'read_write'
  }
]

export function SecurityCenter() {
  const [credentials, setCredentials] = useState<OAuthCredential[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)
  const [editingProvider, setEditingProvider] = useState<string | null>(null)
  const [formData, setFormData] = useState({ clientId: '', clientSecret: '' })
  const [vpsUrl, setVpsUrl] = useState('')

  const ShieldIcon = getIcon("Shield")
  const LockIcon = getIcon("Lock")
  const ExternalLinkIcon = getIcon("ExternalLink")
  const CheckIcon = getIcon("Check")
  const XIcon = getIcon("X")
  const EyeIcon = getIcon("Eye")
  const EyeOffIcon = getIcon("EyeOff")
  const CopyIcon = getIcon("Copy")

  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  useEffect(() => {
    loadCredentials()
    // Get VPS URL from window location
    if (typeof window !== 'undefined') {
      setVpsUrl(window.location.origin)
    }
  }, [])

  const loadCredentials = async () => {
    try {
      const response = await fetch('/api/oauth/credentials')
      const data = await response.json()
      setCredentials(data.credentials || [])
    } catch (error) {
      console.error('Failed to load credentials:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (provider: string) => {
    setSaving(provider)
    try {
      const response = await fetch('/api/oauth/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          clientId: formData.clientId,
          clientSecret: formData.clientSecret
        })
      })

      if (!response.ok) throw new Error('Failed to save credentials')

      await loadCredentials()
      setEditingProvider(null)
      setFormData({ clientId: '', clientSecret: '' })
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setSaving(null)
    }
  }

  const handleDelete = async (provider: string) => {
    if (!confirm(`Delete ${provider} credentials?`)) return

    try {
      await fetch(`/api/oauth/credentials?provider=${provider}`, {
        method: 'DELETE'
      })
      await loadCredentials()
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const handleEdit = (provider: string) => {
    const existing = credentials.find(c => c.provider === provider)
    if (existing) {
      setFormData({
        clientId: existing.clientId,
        clientSecret: existing.clientSecret
      })
    } else {
      setFormData({ clientId: '', clientSecret: '' })
    }
    setEditingProvider(provider)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getCallbackUrl = (callbackPath: string) => {
    return `${vpsUrl}${callbackPath}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <ShieldIcon className="w-12 h-12 mx-auto mb-4 animate-pulse text-blue-500" />
          <p className="text-sm text-gray-500">Loading Security Center...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3">
          <ShieldIcon className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Security Center</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">Configure OAuth credentials for MCP servers</p>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="p-6 bg-blue-50 dark:bg-blue-950 border-b border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <LockIcon className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm">
            <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">Your VPS, Your Credentials</p>
            <p className="text-blue-700 dark:text-blue-300">
              Configure your own OAuth apps for each provider. Credentials are encrypted and stored only on your VPS.
              Use the callback URLs below when creating OAuth apps.
            </p>
          </div>
        </div>
      </div>

      {/* Provider List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {OAUTH_PROVIDERS.map((provider) => {
            const IconComponent = getIcon(provider.icon)
            const credential = credentials.find(c => c.provider === provider.id)
            const isConfigured = credential?.configured || false
            const isEditing = editingProvider === provider.id
            const callbackUrl = getCallbackUrl(provider.callbackPath)

            return (
              <div
                key={provider.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
              >
                {/* Provider Header */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <IconComponent className={`w-6 h-6 ${provider.color}`} />
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{provider.name}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{provider.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isConfigured && !isEditing && (
                      <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                        <CheckIcon className="w-4 h-4" />
                        Configured
                      </span>
                    )}
                    {!isConfigured && !isEditing && (
                      <span className="flex items-center gap-1 text-xs text-gray-400">
                        <XIcon className="w-4 h-4" />
                        Not configured
                      </span>
                    )}
                  </div>
                </div>

                {/* Configuration Form */}
                {isEditing ? (
                  <div className="p-4 space-y-4 bg-white dark:bg-gray-900">
                    {/* Setup Instructions */}
                    <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-md border border-blue-200 dark:border-blue-800">
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">Setup Instructions:</p>
                      <ol className="text-xs text-blue-700 dark:text-blue-300 space-y-1 list-decimal list-inside">
                        <li>
                          Go to{' '}
                          <a
                            href={provider.setupUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline inline-flex items-center gap-1"
                          >
                            {provider.name} OAuth Apps
                            <ExternalLinkIcon className="w-3 h-3" />
                          </a>
                        </li>
                        <li>Create a new OAuth application</li>
                        <li>Use the callback URL below</li>
                        <li>Set the required scopes: <code className="text-xs bg-blue-100 dark:bg-blue-900 px-1 rounded">{provider.scopes}</code></li>
                        <li>Copy Client ID and Client Secret here</li>
                      </ol>
                    </div>

                    {/* Callback URL */}
                    <div>
                      <Label className="text-xs text-gray-500 dark:text-gray-400">Callback URL (Redirect URI)</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input
                          value={callbackUrl}
                          readOnly
                          className="text-xs font-mono bg-gray-50 dark:bg-gray-800"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(callbackUrl)}
                        >
                          <CopyIcon className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    {/* Client ID */}
                    <div>
                      <Label htmlFor={`${provider.id}-client-id`}>Client ID</Label>
                      <Input
                        id={`${provider.id}-client-id`}
                        value={formData.clientId}
                        onChange={(e) => setFormData({ ...formData, clientId: e.target.value })}
                        placeholder="Enter Client ID"
                        className="mt-1"
                      />
                    </div>

                    {/* Client Secret */}
                    <div>
                      <Label htmlFor={`${provider.id}-client-secret`}>Client Secret</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input
                          id={`${provider.id}-client-secret`}
                          type={showSecrets[provider.id] ? "text" : "password"}
                          value={formData.clientSecret}
                          onChange={(e) => setFormData({ ...formData, clientSecret: e.target.value })}
                          placeholder="Enter Client Secret"
                          className="flex-1"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setShowSecrets({ ...showSecrets, [provider.id]: !showSecrets[provider.id] })}
                        >
                          {showSecrets[provider.id] ? <EyeOffIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 pt-2">
                      <Button
                        onClick={() => handleSave(provider.id)}
                        disabled={!formData.clientId || !formData.clientSecret || saving === provider.id}
                        className="flex-1"
                      >
                        {saving === provider.id ? 'Saving...' : 'Save Credentials'}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setEditingProvider(null)
                          setFormData({ clientId: '', clientSecret: '' })
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 flex items-center justify-between">
                    {isConfigured ? (
                      <div className="flex-1">
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          Client ID: <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">{credential?.clientId}</code>
                        </p>
                        <p className="text-xs text-gray-400 mt-1">Client Secret: ••••••••••••</p>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Configure {provider.name} OAuth to enable {provider.name} MCP servers
                      </p>
                    )}
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(provider.id)}
                      >
                        {isConfigured ? 'Edit' : 'Configure'}
                      </Button>
                      {isConfigured && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(provider.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
