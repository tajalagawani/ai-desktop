// Token Storage System for MCP OAuth
// Stores OAuth tokens securely for MCP server authentication

import { promises as fs } from 'fs'
import path from 'path'

const TOKEN_STORE_PATH = path.join(process.cwd(), 'data', 'mcp-tokens.json')

export interface MCPToken {
  provider: string // github, gitlab, google, slack, stripe
  serverId: string // github-official, gitlab, etc.
  accessToken: string
  refreshToken?: string
  expiresAt?: number // Unix timestamp
  scope?: string
  createdAt: number
  userId?: string // For future multi-user support
}

interface TokenStore {
  tokens: MCPToken[]
  version: string
}

// Ensure token store file exists
async function ensureTokenStore(): Promise<void> {
  try {
    await fs.access(TOKEN_STORE_PATH)
  } catch {
    // Create data directory if it doesn't exist
    const dataDir = path.dirname(TOKEN_STORE_PATH)
    await fs.mkdir(dataDir, { recursive: true })

    // Create empty token store
    const initialStore: TokenStore = {
      tokens: [],
      version: '1.0.0'
    }
    await fs.writeFile(TOKEN_STORE_PATH, JSON.stringify(initialStore, null, 2))
  }
}

// Read token store
async function readTokenStore(): Promise<TokenStore> {
  await ensureTokenStore()
  const content = await fs.readFile(TOKEN_STORE_PATH, 'utf-8')
  return JSON.parse(content)
}

// Write token store
async function writeTokenStore(store: TokenStore): Promise<void> {
  await fs.writeFile(TOKEN_STORE_PATH, JSON.stringify(store, null, 2))
}

// Save a token
export async function saveToken(token: MCPToken): Promise<void> {
  const store = await readTokenStore()

  // Remove existing token for same provider/server
  store.tokens = store.tokens.filter(
    t => !(t.provider === token.provider && t.serverId === token.serverId)
  )

  // Add new token
  store.tokens.push({
    ...token,
    createdAt: Date.now()
  })

  await writeTokenStore(store)
}

// Get token by provider and serverId
export async function getToken(provider: string, serverId: string): Promise<MCPToken | null> {
  const store = await readTokenStore()
  const token = store.tokens.find(
    t => t.provider === provider && t.serverId === serverId
  )

  if (!token) return null

  // Check if token is expired
  if (token.expiresAt && token.expiresAt < Date.now()) {
    // Token expired, remove it
    await deleteToken(provider, serverId)
    return null
  }

  return token
}

// Get all tokens
export async function getAllTokens(): Promise<MCPToken[]> {
  const store = await readTokenStore()

  // Filter out expired tokens
  const now = Date.now()
  const validTokens = store.tokens.filter(
    t => !t.expiresAt || t.expiresAt > now
  )

  // Update store if any tokens were expired
  if (validTokens.length !== store.tokens.length) {
    store.tokens = validTokens
    await writeTokenStore(store)
  }

  return validTokens
}

// Delete a token
export async function deleteToken(provider: string, serverId: string): Promise<void> {
  const store = await readTokenStore()
  store.tokens = store.tokens.filter(
    t => !(t.provider === provider && t.serverId === serverId)
  )
  await writeTokenStore(store)
}

// Delete all tokens
export async function deleteAllTokens(): Promise<void> {
  const store = await readTokenStore()
  store.tokens = []
  await writeTokenStore(store)
}

// Check if token exists and is valid
export async function hasValidToken(provider: string, serverId: string): Promise<boolean> {
  const token = await getToken(provider, serverId)
  return token !== null
}
