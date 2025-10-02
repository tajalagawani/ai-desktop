import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export const dynamic = 'force-dynamic'

interface PM2Process {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'idle'
  uptime: string
  cpu: string
  memory: string
  restarts: number
}

export async function GET() {
  try {
    // Get PM2 process list as JSON
    const { stdout } = await execAsync('pm2 jlist')
    const processes = JSON.parse(stdout)

    const formattedProcesses: PM2Process[] = processes.map((proc: any) => {
      // Calculate uptime
      const uptimeMs = Date.now() - proc.pm2_env.pm_uptime
      const uptimeSec = Math.floor(uptimeMs / 1000)
      const uptimeMin = Math.floor(uptimeSec / 60)
      const uptimeHour = Math.floor(uptimeMin / 60)
      const uptimeDay = Math.floor(uptimeHour / 24)

      let uptimeStr = ''
      if (uptimeDay > 0) {
        uptimeStr = `${uptimeDay}d ${uptimeHour % 24}h`
      } else if (uptimeHour > 0) {
        uptimeStr = `${uptimeHour}h ${uptimeMin % 60}m`
      } else if (uptimeMin > 0) {
        uptimeStr = `${uptimeMin}m`
      } else {
        uptimeStr = `${uptimeSec}s`
      }

      // Determine status
      let status: PM2Process['status'] = 'idle'
      if (proc.pm2_env.status === 'online') {
        status = 'running'
      } else if (proc.pm2_env.status === 'stopped') {
        status = 'stopped'
      } else if (proc.pm2_env.status === 'errored') {
        status = 'error'
      }

      return {
        id: proc.pm_id.toString(),
        name: proc.name,
        status,
        uptime: uptimeStr,
        cpu: `${proc.monit.cpu}%`,
        memory: `${Math.round(proc.monit.memory / 1024 / 1024)}MB`,
        restarts: proc.pm2_env.restart_time
      }
    })

    return NextResponse.json({
      success: true,
      processes: formattedProcesses
    })
  } catch (error) {
    console.error('Error fetching PM2 processes:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch PM2 processes',
        processes: []
      },
      { status: 500 }
    )
  }
}
