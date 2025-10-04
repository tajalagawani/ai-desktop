import { NextRequest, NextResponse } from 'next/server'
import { getCredential } from '@/lib/mcp/credential-store'

// GET - Get client ID for a specific provider (public, not secret)
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const provider = searchParams.get('provider')

    if (!provider) {
      return NextResponse.json(
        { error: 'Missing provider parameter' },
        { status: 400 }
      )
    }

    const credential = await getCredential(provider)
    if (!credential) {
      return NextResponse.json(
        { error: `${provider} credentials not configured. Please configure in Security Center.` },
        { status: 404 }
      )
    }

    // Return only client ID (not secret)
    return NextResponse.json({
      provider,
      clientId: credential.clientId
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to get client ID' },
      { status: 500 }
    )
  }
}
