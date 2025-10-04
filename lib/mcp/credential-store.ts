/**
 * Credential Store - User-configured OAuth credentials
 * Each VPS user configures their own OAuth app credentials through Security Center
 */

import fs from 'fs/promises'
import path from 'path'
import crypto from 'crypto'

const CREDENTIALS_FILE = path.join(process.cwd(), 'data', 'oauth-credentials.json')
const ENCRYPTION_KEY = process.env.CREDENTIAL_ENCRYPTION_KEY || 'default-key-change-me' // User sets this in Security Center

export interface OAuthCredential {
  provider: 'github' | 'gitlab' | 'google' | 'slack' | 'stripe'
  clientId: string
  clientSecret: string
  createdAt: number
  updatedAt: number
}

interface CredentialStore {
  [provider: string]: OAuthCredential
}

// Encrypt sensitive data
function encrypt(text: string): string {
  const cipher = crypto.createCipher('aes-256-cbc', ENCRYPTION_KEY)
  let encrypted = cipher.update(text, 'utf8', 'hex')
  encrypted += cipher.final('hex')
  return encrypted
}

// Decrypt sensitive data
function decrypt(text: string): string {
  try {
    const decipher = crypto.createDecipher('aes-256-cbc', ENCRYPTION_KEY)
    let decrypted = decipher.update(text, 'hex', 'utf8')
    decrypted += decipher.final('utf8')
    return decrypted
  } catch {
    return text // If decryption fails, return as-is (backward compatibility)
  }
}

// Ensure data directory exists
async function ensureDataDir() {
  const dataDir = path.join(process.cwd(), 'data')
  try {
    await fs.access(dataDir)
  } catch {
    await fs.mkdir(dataDir, { recursive: true })
  }
}

// Load credentials from file
async function loadCredentials(): Promise<CredentialStore> {
  try {
    await ensureDataDir()
    const data = await fs.readFile(CREDENTIALS_FILE, 'utf-8')
    const store: CredentialStore = JSON.parse(data)

    // Decrypt secrets
    for (const provider in store) {
      store[provider].clientSecret = decrypt(store[provider].clientSecret)
    }

    return store
  } catch {
    return {}
  }
}

// Save credentials to file
async function saveCredentials(store: CredentialStore): Promise<void> {
  await ensureDataDir()

  // Encrypt secrets before saving
  const encryptedStore: CredentialStore = {}
  for (const provider in store) {
    encryptedStore[provider] = {
      ...store[provider],
      clientSecret: encrypt(store[provider].clientSecret)
    }
  }

  await fs.writeFile(CREDENTIALS_FILE, JSON.stringify(encryptedStore, null, 2))
}

// Get credential for a provider
export async function getCredential(provider: string): Promise<OAuthCredential | null> {
  const store = await loadCredentials()
  return store[provider] || null
}

// Save credential for a provider
export async function saveCredential(credential: OAuthCredential): Promise<void> {
  const store = await loadCredentials()
  store[credential.provider] = {
    ...credential,
    updatedAt: Date.now()
  }
  await saveCredentials(store)
}

// Delete credential for a provider
export async function deleteCredential(provider: string): Promise<void> {
  const store = await loadCredentials()
  delete store[provider]
  await saveCredentials(store)
}

// Get all configured providers
export async function getAllCredentials(): Promise<OAuthCredential[]> {
  const store = await loadCredentials()
  return Object.values(store)
}

// Check if provider has credentials
export async function hasCredential(provider: string): Promise<boolean> {
  const credential = await getCredential(provider)
  return credential !== null && !!credential.clientId && !!credential.clientSecret
}
