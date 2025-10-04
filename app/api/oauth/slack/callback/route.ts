import { NextRequest, NextResponse } from 'next/server'
import { getOAuthProvider } from '@/lib/mcp/oauth-config'
import { saveToken } from '@/lib/mcp/token-store'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) throw new Error(`OAuth error: ${error}`)
    if (!code) throw new Error('No authorization code received')

    const provider = await getOAuthProvider('slack')
    if (!provider) throw new Error('Slack OAuth not configured. Please configure in Security Center first.')

    const tokenResponse = await fetch(provider.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: provider.clientId,
        client_secret: provider.clientSecret,
        code,
        redirect_uri: provider.redirectUri
      })
    })

    const tokenData = await tokenResponse.json()
    if (!tokenData.ok) throw new Error(`Token error: ${tokenData.error}`)

    await saveToken({
      provider: 'slack',
      serverId: 'slack',
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      scope: tokenData.scope,
      createdAt: Date.now()
    })

    return new NextResponse(`<html><head><style>body{font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:linear-gradient(135deg,#667eea,#764ba2);color:white}.c{text-align:center;background:rgba(255,255,255,0.1);padding:40px;border-radius:20px;backdrop-filter:blur(10px)}.check{font-size:64px}</style></head><body><div class="c"><div class="check">✓</div><h1>Slack Connected!</h1><p>Closing...</p></div><script>if(window.opener)window.opener.postMessage({type:'oauth_success',provider:'slack'},'*');setTimeout(()=>window.close(),2000)</script></body></html>`, { headers: { 'Content-Type': 'text/html' } })

  } catch (error: any) {
    return new NextResponse(`<html><body style="font-family:system-ui;text-align:center;padding:40px"><h1>❌ OAuth Failed</h1><p>${error.message}</p><script>setTimeout(()=>window.close(),5000)</script></body></html>`, { status: 500, headers: { 'Content-Type': 'text/html' } })
  }
}
