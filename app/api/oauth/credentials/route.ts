import { NextRequest, NextResponse } from 'next/server'
import { getCredential, saveCredential, deleteCredential, getAllCredentials, OAuthCredential } from '@/lib/mcp/credential-store'

// GET - Get all configured OAuth credentials
export async function GET(request: NextRequest) {
  try {
    const credentials = await getAllCredentials()

    // Return credentials without exposing full secrets
    const safeCredentials = credentials.map(cred => ({
      provider: cred.provider,
      clientId: cred.clientId,
      clientSecret: cred.clientSecret.substring(0, 4) + '••••••••••',
      configured: true,
      createdAt: cred.createdAt,
      updatedAt: cred.updatedAt
    }))

    return NextResponse.json({
      success: true,
      credentials: safeCredentials
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to load credentials' },
      { status: 500 }
    )
  }
}

// POST - Save OAuth credentials for a provider
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { provider, clientId, clientSecret } = body

    if (!provider || !clientId || !clientSecret) {
      return NextResponse.json(
        { error: 'Missing required fields: provider, clientId, clientSecret' },
        { status: 400 }
      )
    }

    const validProviders = ['github', 'gitlab', 'google', 'slack', 'stripe']
    if (!validProviders.includes(provider)) {
      return NextResponse.json(
        { error: `Invalid provider. Must be one of: ${validProviders.join(', ')}` },
        { status: 400 }
      )
    }

    const credential: OAuthCredential = {
      provider: provider as any,
      clientId,
      clientSecret,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    await saveCredential(credential)

    return NextResponse.json({
      success: true,
      message: `${provider} credentials saved successfully`
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to save credentials' },
      { status: 500 }
    )
  }
}

// DELETE - Delete OAuth credentials for a provider
export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const provider = searchParams.get('provider')

    if (!provider) {
      return NextResponse.json(
        { error: 'Missing provider parameter' },
        { status: 400 }
      )
    }

    await deleteCredential(provider)

    return NextResponse.json({
      success: true,
      message: `${provider} credentials deleted`
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to delete credentials' },
      { status: 500 }
    )
  }
}
