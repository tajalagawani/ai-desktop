import { NextResponse } from 'next/server'
import { getSystemStats } from '@/lib/services/system-stats.service'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const stats = await getSystemStats()
    return NextResponse.json(stats)
  } catch (error) {
    console.error('Error fetching system stats:', error)
    return NextResponse.json(
      { error: 'Failed to fetch system stats' },
      { status: 500 }
    )
  }
}
