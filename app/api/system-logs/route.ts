import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'

const execAsync = promisify(exec)

export const dynamic = 'force-dynamic'

interface LogEntry {
  time: string
  level: 'info' | 'warn' | 'error'
  message: string
}

async function getPM2Logs(): Promise<LogEntry[]> {
  try {
    const { stdout } = await execAsync('pm2 logs --nostream --lines 20 --raw')
    const lines = stdout.trim().split('\n')

    return lines.slice(-20).map(line => {
      const now = new Date()
      const time = now.toTimeString().split(' ')[0]

      let level: LogEntry['level'] = 'info'
      if (line.toLowerCase().includes('error') || line.toLowerCase().includes('failed')) {
        level = 'error'
      } else if (line.toLowerCase().includes('warn')) {
        level = 'warn'
      }

      return {
        time,
        level,
        message: line
      }
    }).reverse()
  } catch (error) {
    console.error('Error reading PM2 logs:', error)
    return []
  }
}

async function getAutoUpdateLogs(): Promise<LogEntry[]> {
  try {
    const logPath = path.join(process.cwd(), 'logs', 'auto-update.log')
    const content = await fs.readFile(logPath, 'utf-8')
    const lines = content.trim().split('\n')

    return lines.slice(-10).map(line => {
      // Parse format: [2025-10-02 17:01:26] message
      const match = line.match(/\[(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2}))\] (.+)/)

      if (match) {
        const time = match[2]
        const message = match[3]

        let level: LogEntry['level'] = 'info'
        if (message.includes('❌') || message.toLowerCase().includes('error')) {
          level = 'error'
        } else if (message.includes('⚠') || message.toLowerCase().includes('warn')) {
          level = 'warn'
        }

        return { time, level, message }
      }

      return {
        time: new Date().toTimeString().split(' ')[0],
        level: 'info' as const,
        message: line
      }
    }).reverse()
  } catch (error) {
    console.error('Error reading auto-update logs:', error)
    return []
  }
}

export async function GET() {
  try {
    const [pm2Logs, updateLogs] = await Promise.all([
      getPM2Logs(),
      getAutoUpdateLogs()
    ])

    // Combine and sort by time (newest first)
    const allLogs = [...pm2Logs, ...updateLogs]
      .sort((a, b) => b.time.localeCompare(a.time))
      .slice(0, 20)

    return NextResponse.json({
      success: true,
      logs: allLogs
    })
  } catch (error) {
    console.error('Error fetching system logs:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch system logs',
        logs: []
      },
      { status: 500 }
    )
  }
}
