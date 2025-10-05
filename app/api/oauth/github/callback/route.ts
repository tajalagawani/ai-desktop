import { NextRequest, NextResponse } from 'next/server'
import { getOAuthProvider } from '@/lib/mcp/oauth-config'
import { saveToken } from '@/lib/mcp/token-store'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const error = searchParams.get('error')

    if (error) {
      return new NextResponse(`
        <html>
          <body>
            <h1>OAuth Error</h1>
            <p>${error}: ${searchParams.get('error_description')}</p>
            <script>
              setTimeout(() => window.close(), 3000)
            </script>
          </body>
        </html>
      `, {
        headers: { 'Content-Type': 'text/html' }
      })
    }

    if (!code) {
      throw new Error('No authorization code received')
    }

    const provider = await getOAuthProvider('github')
    if (!provider) {
      throw new Error('GitHub OAuth not configured. Please set up credentials in Security Center.')
    }

    // Exchange code for access token
    const tokenResponse = await fetch(provider.tokenUrl, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        client_id: provider.clientId,
        client_secret: provider.clientSecret,
        code,
        redirect_uri: provider.redirectUri
      })
    })

    if (!tokenResponse.ok) {
      throw new Error(`Token exchange failed: ${tokenResponse.statusText}`)
    }

    const tokenData = await tokenResponse.json()

    if (tokenData.error) {
      throw new Error(`Token error: ${tokenData.error_description || tokenData.error}`)
    }

    // Save token to storage
    await saveToken({
      provider: 'github',
      serverId: 'github-official',
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      scope: tokenData.scope,
      createdAt: Date.now(),
      expiresAt: tokenData.expires_in ? Date.now() + (tokenData.expires_in * 1000) : undefined
    })

    // Return success page that closes the popup
    return new NextResponse(`
      <html>
        <head>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              margin: 0;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
            }
            .container {
              text-align: center;
              background: rgba(255,255,255,0.1);
              padding: 40px;
              border-radius: 20px;
              backdrop-filter: blur(10px);
            }
            .checkmark {
              font-size: 64px;
              animation: pop 0.3s ease-out;
            }
            @keyframes pop {
              0% { transform: scale(0); }
              50% { transform: scale(1.2); }
              100% { transform: scale(1); }
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="checkmark">✓</div>
            <h1>GitHub Connected!</h1>
            <p>You can close this window now.</p>
          </div>
          <script>
            // Send message to parent window
            if (window.opener) {
              window.opener.postMessage({ type: 'oauth_success', provider: 'github' }, '*')
            }
            // Auto-close after 2 seconds
            setTimeout(() => window.close(), 2000)
          </script>
        </body>
      </html>
    `, {
      headers: { 'Content-Type': 'text/html' }
    })

  } catch (error: any) {
    console.error('GitHub OAuth callback error:', error)

    return new NextResponse(`
      <html>
        <head>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              margin: 0;
              background: #f5f5f5;
            }
            .container {
              text-align: center;
              background: white;
              padding: 40px;
              border-radius: 20px;
              box-shadow: 0 10px 40px rgba(0,0,0,0.1);
              max-width: 500px;
            }
            .error {
              color: #e53e3e;
              font-size: 48px;
              margin-bottom: 20px;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="error">✗</div>
            <h1>OAuth Failed</h1>
            <p>${error.message}</p>
            <p><small>This window will close automatically.</small></p>
          </div>
          <script>
            setTimeout(() => window.close(), 5000)
          </script>
        </body>
      </html>
    `, {
      status: 500,
      headers: { 'Content-Type': 'text/html' }
    })
  }
}
