import { NextRequest, NextResponse } from 'next/server'
import { getOAuthProvider } from '@/lib/mcp/oauth-config'
import { saveToken } from '@/lib/mcp/token-store'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      throw new Error(`OAuth error: ${searchParams.get('error_description') || error}`)
    }

    if (!code) {
      throw new Error('No authorization code received')
    }

    const provider = await getOAuthProvider('gitlab')
    if (!provider) throw new Error('GitLab OAuth not configured. Please configure in Security Center first.')

    const tokenResponse = await fetch(provider.tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        client_id: provider.clientId,
        client_secret: provider.clientSecret,
        code,
        grant_type: 'authorization_code',
        redirect_uri: provider.redirectUri
      })
    })

    const tokenData = await tokenResponse.json()

    if (tokenData.error) {
      throw new Error(`Token error: ${tokenData.error_description || tokenData.error}`)
    }

    await saveToken({
      provider: 'gitlab',
      serverId: 'gitlab',
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      scope: tokenData.scope,
      createdAt: Date.now(),
      expiresAt: tokenData.expires_in ? Date.now() + (tokenData.expires_in * 1000) : undefined
    })

    return new NextResponse(`
      <html><head><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white}.container{text-align:center;background:rgba(255,255,255,0.1);padding:40px;border-radius:20px;backdrop-filter:blur(10px)}.checkmark{font-size:64px;animation:pop 0.3s}@keyframes pop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}</style></head><body><div class="container"><div class="checkmark">✓</div><h1>GitLab Connected!</h1><p>Closing...</p></div><script>if(window.opener){window.opener.postMessage({type:'oauth_success',provider:'gitlab'},'*')}setTimeout(()=>window.close(),2000)</script></body></html>
    `, { headers: { 'Content-Type': 'text/html' } })

  } catch (error: any) {
    return new NextResponse(`
      <html><body style="font-family:system-ui;text-align:center;padding:40px"><h1>❌ OAuth Failed</h1><p>${error.message}</p><script>setTimeout(()=>window.close(),5000)</script></body></html>
    `, { status: 500, headers: { 'Content-Type': 'text/html' } })
  }
}
