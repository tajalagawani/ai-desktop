import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'
import os from 'os'

const CLAUDE_DIR = path.join(os.homedir(), '.claude')

/**
 * GET /api/projects/{projectName}/sessions/{sessionId}/executions
 *
 * Retrieve all executions for a specific session
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { projectName: string; sessionId: string } }
) {
  try {
    const { projectName, sessionId } = params
    const executionsPath = path.join(
      CLAUDE_DIR,
      'projects',
      projectName,
      'sessions',
      sessionId,
      'executions.jsonl'
    )

    console.log('[Executions API] Reading executions from:', executionsPath)

    try {
      const content = await fs.readFile(executionsPath, 'utf-8')
      const lines = content.trim().split('\n').filter(line => line.trim())
      const executions = lines.map(line => JSON.parse(line))

      console.log('[Executions API] Found', executions.length, 'executions')

      return NextResponse.json({
        success: true,
        executions: executions.reverse(), // Newest first
        count: executions.length
      })
    } catch (err: any) {
      if (err.code === 'ENOENT') {
        // File doesn't exist yet - return empty array
        console.log('[Executions API] No executions file found yet')
        return NextResponse.json({
          success: true,
          executions: [],
          count: 0
        })
      }
      throw err
    }
  } catch (error: any) {
    console.error('[Executions API] Error:', error.message)
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}

/**
 * POST /api/projects/{projectName}/sessions/{sessionId}/executions
 *
 * Save a new execution to the session's execution history
 *
 * Body:
 * {
 *   "executionId": "uuid",
 *   "flowName": "...",
 *   "flowContent": "...",
 *   "mode": "miniact" | "agent",
 *   "success": true/false,
 *   "result": {...},
 *   "deployment": {...},
 *   "error": "...",
 *   "duration": 1234
 * }
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { projectName: string; sessionId: string } }
) {
  try {
    const { projectName, sessionId } = params
    const body = await request.json()

    const sessionDir = path.join(
      CLAUDE_DIR,
      'projects',
      projectName,
      'sessions',
      sessionId
    )

    // Ensure session directory exists
    await fs.mkdir(sessionDir, { recursive: true })

    const executionsPath = path.join(sessionDir, 'executions.jsonl')

    // Create execution record
    const execution = {
      executionId: body.executionId,
      timestamp: new Date().toISOString(),
      flowName: body.flowName || 'Unnamed Flow',
      flowContent: body.flowContent,
      mode: body.mode,
      success: body.success,
      duration: body.duration || 0,
      result: body.result,
      deployment: body.deployment,
      error: body.error,
      errorType: body.errorType,
      traceback: body.traceback,
      sessionId
    }

    // Append to JSONL file
    const line = JSON.stringify(execution) + '\n'
    await fs.appendFile(executionsPath, line, 'utf-8')

    console.log('[Executions API] Saved execution:', execution.executionId)

    return NextResponse.json({
      success: true,
      execution
    })
  } catch (error: any) {
    console.error('[Executions API] Error saving execution:', error.message)
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}
