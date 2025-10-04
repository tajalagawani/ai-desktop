// Client-side OAuth utilities (no server dependencies)

// Base URL for OAuth callbacks (VPS URL)
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
}

// Provider templates (without credentials) - DUPLICATED from oauth-config to avoid server imports
const OAUTH_PROVIDER_TEMPLATES = {
  github: {
    name: 'GitHub',
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    scope: 'repo,user,read:org',
    redirectUri: `${getBaseUrl()}/api/oauth/github/callback`
  },
  gitlab: {
    name: 'GitLab',
    authUrl: 'https://gitlab.com/oauth/authorize',
    tokenUrl: 'https://gitlab.com/oauth/token',
    scope: 'api,read_user,read_repository,write_repository',
    redirectUri: `${getBaseUrl()}/api/oauth/gitlab/callback`
  },
  google: {
    name: 'Google',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scope: 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/userinfo.email',
    redirectUri: `${getBaseUrl()}/api/oauth/google/callback`
  },
  slack: {
    name: 'Slack',
    authUrl: 'https://slack.com/oauth/v2/authorize',
    tokenUrl: 'https://slack.com/api/oauth.v2.access',
    scope: 'channels:read,channels:write,chat:write,users:read',
    redirectUri: `${getBaseUrl()}/api/oauth/slack/callback`
  },
  stripe: {
    name: 'Stripe',
    authUrl: 'https://connect.stripe.com/oauth/authorize',
    tokenUrl: 'https://connect.stripe.com/oauth/token',
    scope: 'read_write',
    redirectUri: `${getBaseUrl()}/api/oauth/stripe/callback`
  }
} as const

// Generate OAuth authorization URL with client ID
export function buildOAuthUrl(provider: string, clientId: string, state?: string): string {
  const template = OAUTH_PROVIDER_TEMPLATES[provider]
  if (!template) {
    throw new Error(`Unknown OAuth provider: ${provider}`)
  }

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: template.redirectUri,
    scope: template.scope,
    response_type: 'code',
    ...(state && { state })
  })

  return `${template.authUrl}?${params.toString()}`
}

// Generate OAuth authorization URL (fetches client ID from API first)
export async function getAuthorizationUrl(provider: string, state?: string): Promise<string> {
  const clientId = await getClientId(provider)
  if (!clientId) {
    throw new Error(`${provider} credentials not configured. Please configure in Security Center first.`)
  }
  return buildOAuthUrl(provider, clientId, state)
}

// Fetch user's client ID for a provider (from API)
export async function getClientId(provider: string): Promise<string | null> {
  try {
    const response = await fetch(`/api/oauth/credentials/client-id?provider=${provider}`)
    if (!response.ok) return null

    const data = await response.json()
    return data.clientId || null
  } catch {
    return null
  }
}
