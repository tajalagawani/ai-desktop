import { NextRequest, NextResponse } from 'next/server'
import { getRunningServices } from '@/lib/deployment/services'

export async function GET(request: NextRequest) {
  try {
    const services = await getRunningServices()

    return NextResponse.json({
      success: true,
      services
    })
  } catch (error: any) {
    console.error('Error getting running services:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to get services' },
      { status: 500 }
    )
  }
}
