import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'

const execAsync = promisify(exec)

const ACT_DOCKER_DIR = path.join(process.cwd(), 'components/apps/act-docker')

/**
 * GET /api/ports - Get next available port
 *
 * Query params:
 *   - verbose: boolean - Include detailed port usage info
 *
 * Returns:
 *   - available_port: number - Next available port
 *   - used_ports: number[] - All currently used ports
 *   - sources: object - Breakdown by source (flows, catalog, docker)
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const verbose = searchParams.get('verbose') === 'true'

    // Run the port detection script
    const { stdout, stderr } = await execAsync(
      `cd ${ACT_DOCKER_DIR} && python3 find-available-port.py --json`,
      { timeout: 10000 }
    )

    if (stderr) {
      console.warn('[Port Detection] Warning:', stderr)
    }

    // Parse JSON output
    const result = JSON.parse(stdout)

    // Return response
    return NextResponse.json({
      success: true,
      available_port: result.available_port,
      used_ports: result.used_ports,
      sources: result.sources,
      timestamp: new Date().toISOString()
    })

  } catch (error: any) {
    console.error('[Port Detection] Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to detect available port',
        available_port: null
      },
      { status: 500 }
    )
  }
}
