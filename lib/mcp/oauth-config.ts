// OAuth Configuration for MCP Providers
// Contains OAuth endpoints, scopes, and client credentials for each provider
// User configures credentials through Security Center, not env vars

export interface OAuthProvider {
  name: string
  authUrl: string
  tokenUrl: string
  scope: string
  clientId: string // Set by user in Security Center
  clientSecret: string // Set by user in Security Center
  redirectUri: string
  requiresPKCE?: boolean
}

export interface OAuthProviderTemplate {
  name: string
  authUrl: string
  tokenUrl: string
  scope: string
  redirectUri: string
  requiresPKCE?: boolean
}

// Base URL for OAuth callbacks (VPS URL)
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
}

// Provider templates (without credentials)
export const OAUTH_PROVIDER_TEMPLATES: Record<string, OAuthProviderTemplate> = {
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
}


// Server-side only: Get provider config with user's credentials from Security Center
// This function should only be called from API routes, not client components
export async function getOAuthProvider(provider: string): Promise<OAuthProvider | null> {
  // Ensure this is server-side
  if (typeof window !== 'undefined') {
    throw new Error('getOAuthProvider can only be called server-side')
  }

  const { getCredential } = await import('./credential-store')
  const template = OAUTH_PROVIDER_TEMPLATES[provider]
  if (!template) return null

  const credential = await getCredential(provider)
  if (!credential) return null

  return {
    ...template,
    clientId: credential.clientId,
    clientSecret: credential.clientSecret
  }
}
