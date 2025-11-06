import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'
import { randomUUID } from 'crypto'

const execAsync = promisify(exec)

/**
 * POST /api/act/execute
 *
 * Execute an ACT flow file
 *
 * Body:
 * {
 *   "flowContent": "...",  // ACT file content (TOML)
 *   "flowName": "..."      // Optional name for the flow
 * }
 */
export async function POST(request: NextRequest) {
  const executionId = randomUUID()
  const startTime = Date.now()

  try {
    console.log('[ACT Execute] ========================================')
    console.log('[ACT Execute] New execution request:', executionId)
    console.log('[ACT Execute] ========================================')

    const body = await request.json()
    const { flowContent, flowName, sessionId, projectName } = body

    if (!flowContent) {
      return NextResponse.json(
        { error: 'flowContent is required' },
        { status: 400 }
      )
    }

    // Create temp directory for executions
    const tempDir = path.join(process.cwd(), 'temp-act-executions')
    await fs.mkdir(tempDir, { recursive: true })

    // Create temp file
    const fileName = flowName || `temp-${Date.now()}-${executionId.slice(0, 8)}.act`
    const filePath = path.join(tempDir, fileName)

    console.log('[ACT Execute] Writing flow to:', filePath)
    await fs.writeFile(filePath, flowContent, 'utf-8')

    try {
      // Execute using external ACT repo
      const actDockerDir = path.join(process.cwd(), '../../act')

      console.log('[ACT Execute] Executing flow...')
      console.log('[ACT Execute] ACT Docker dir:', actDockerDir)

      // Run ACT execution via Python
      const pythonScript = `import sys
import os
import json
from pathlib import Path

# Add ACT docker directory to path
sys.path.insert(0, '${actDockerDir}')

try:
    # Import ACT ExecutionManager
    from act.execution_manager import ExecutionManager

    # Initialize execution manager with the ACT file
    execution_manager = ExecutionManager('${filePath}')

    # Check if this is an agent workflow (has ACI routes)
    if execution_manager.has_agent_config():
        # This is an API workflow - needs deployment
        config = execution_manager.get_agent_config()
        deployment = execution_manager.get_deployment_config() if hasattr(execution_manager, 'get_deployment_config') else {}

        result = {
            "success": True,
            "mode": "agent",
            "workflow_name": config.get('agent_name', 'Unknown'),
            "port": config.get('port', deployment.get('port', 9000)),
            "message": "API workflow detected - requires deployment to Docker",
            "requires_deployment": True,
            "flow_file": '${fileName}'
        }
    else:
        # This is a mini-ACT - execute it immediately
        execution_result = execution_manager.execute_workflow(initial_input=None)

        result = {
            "success": True,
            "mode": "miniact",
            "message": "Flow executed successfully",
            "result": execution_result
        }

    print(json.dumps(result, default=str))

except Exception as e:
    import traceback
    result = {
        "success": False,
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    print(json.dumps(result))
`

      // Write Python script to temp file
      const pythonScriptPath = path.join(tempDir, `exec-${executionId.slice(0, 8)}.py`)
      await fs.writeFile(pythonScriptPath, pythonScript, 'utf-8')

      const { stdout, stderr } = await execAsync(
        `python3 ${pythonScriptPath}`,
        {
          timeout: 30000,
          maxBuffer: 10 * 1024 * 1024,
          cwd: actDockerDir
        }
      )

      // Clean up Python script
      try {
        await fs.unlink(pythonScriptPath)
      } catch {}

      console.log('[ACT Execute] Execution completed')
      if (stdout) console.log('[ACT Execute] stdout:', stdout.substring(0, 500))
      if (stderr) console.log('[ACT Execute] stderr:', stderr.substring(0, 500))

      // Parse result - extract JSON from stdout (may have warnings before it)
      let result
      try {
        // Find the JSON object in stdout (starts with { and ends with })
        const jsonMatch = stdout.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          result = JSON.parse(jsonMatch[0])
        } else {
          throw new Error('No JSON found in output')
        }
      } catch (e) {
        console.error('[ACT Execute] Failed to parse output as JSON')
        result = {
          success: false,
          error: 'Failed to parse execution output',
          raw_output: stdout
        }
      }

      // Clean up temp file
      try {
        await fs.unlink(filePath)
        console.log('[ACT Execute] Cleaned up temp file')
      } catch (e) {
        console.warn('[ACT Execute] Failed to clean up temp file:', e)
      }

      console.log('[ACT Execute] ========================================')
      console.log('[ACT Execute] Execution result:', result.success ? '✅ Success' : '❌ Failed')
      console.log('[ACT Execute] ========================================')

      // Save execution to history if sessionId and projectName provided
      if (sessionId && projectName) {
        const duration = Date.now() - startTime
        try {
          const serverPort = process.env.PORT || '3000'
          await fetch(`http://localhost:${serverPort}/api/projects/${projectName}/sessions/${sessionId}/executions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              executionId,
              flowName,
              flowContent,
              mode: result.mode,
              success: result.success,
              duration,
              result: result.result,
              deployment: result.deployment,
              error: result.error,
              errorType: result.error_type,
              traceback: result.traceback
            })
          })
          console.log('[ACT Execute] ✅ Execution saved to history')
        } catch (historyError: any) {
          console.warn('[ACT Execute] ⚠️  Failed to save execution history:', historyError.message)
          // Don't fail the execution if history save fails
        }
      }

      // Auto-deploy if this is an API workflow
      if (result.success && result.mode === 'agent' && result.requires_deployment) {
        console.log('[ACT Execute] API workflow detected - deploying automatically...')

        try {
          // Move flow file to flows directory if needed
          const flowsDir = path.join(process.cwd(), '../../act/flows')
          await fs.mkdir(flowsDir, { recursive: true })

          // Extract flow name (remove extension)
          const flowNameMatch = result.flow_file.match(/^(.+)\.(act|flow)$/)
          const deployFlowName = flowNameMatch ? flowNameMatch[1] : result.flow_file.replace(/\.(act|flow)$/, '')

          // ALWAYS save agent workflows with .flow extension (required for docker-compose discovery)
          const flowFileName = `${deployFlowName}.flow`
          const finalFlowPath = path.join(flowsDir, flowFileName)

          // Inject metadata section into flow content for session linking
          let enhancedFlowContent = flowContent
          if (sessionId && projectName) {
            // Check if metadata section already exists
            if (!flowContent.includes('[metadata]')) {
              // Add metadata section after [workflow] section
              const metadataSection = `\n[metadata]\nsessionId = "${sessionId}"\nprojectName = "${projectName}"\ncreatedAt = "${new Date().toISOString()}"\n`

              // Find the end of [workflow] section (next section starting with [)
              const workflowMatch = flowContent.match(/\[workflow\][\s\S]*?(?=\n\[)/m)
              if (workflowMatch) {
                const insertIndex = workflowMatch.index! + workflowMatch[0].length
                enhancedFlowContent = flowContent.slice(0, insertIndex) + metadataSection + flowContent.slice(insertIndex)
              } else {
                // If we can't find the workflow section, append at the beginning after [workflow]
                enhancedFlowContent = flowContent.replace('[workflow]', `[workflow]${metadataSection}`)
              }

              console.log('[ACT Execute] Added metadata section to flow:', { sessionId, projectName })
            }
          }

          // Write the flow content to flows directory
          await fs.writeFile(finalFlowPath, enhancedFlowContent, 'utf-8')

          console.log('[ACT Execute] Flow file saved to:', finalFlowPath)

          console.log('[ACT Execute] Starting deployment for flow:', deployFlowName)

          // Call deployment API
          const serverPort = process.env.PORT || '3000'
          const deployResponse = await fetch(`http://localhost:${serverPort}/api/flows`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'start',
              flowName: deployFlowName
            })
          })

          const deployResult = await deployResponse.json()

          console.log('[ACT Execute] Deployment result:', deployResult)

          result.deployment = {
            deployed: deployResult.success,
            flow_name: deployFlowName,
            port: result.port,
            message: deployResult.message || deployResult.error,
            url: `http://localhost:${result.port}`
          }

          console.log('[ACT Execute] ✅ Flow deployed successfully at port', result.port)

        } catch (deployError: any) {
          console.error('[ACT Execute] ❌ Deployment failed:', deployError.message)
          result.deployment = {
            deployed: false,
            error: deployError.message
          }
        }
      }

      return NextResponse.json({
        executionId,
        ...result
      })

    } catch (execError: any) {
      console.error('[ACT Execute] ❌ Execution error:', execError.message)

      // Clean up temp file
      try {
        await fs.unlink(filePath)
      } catch {}

      return NextResponse.json(
        {
          executionId,
          success: false,
          error: execError.message || 'Execution failed',
          details: execError.stderr || execError.stdout
        },
        { status: 500 }
      )
    }

  } catch (error: any) {
    console.error('[ACT Execute] ❌ Error:', error.message)
    return NextResponse.json(
      {
        executionId,
        success: false,
        error: error.message || 'Failed to execute flow'
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/act/execute
 *
 * Get execution status or info
 */
export async function GET() {
  try {
    const tempDir = path.join(process.cwd(), 'temp-act-executions')

    let files: string[] = []
    try {
      files = await fs.readdir(tempDir)
    } catch {
      // Directory doesn't exist yet
    }

    return NextResponse.json({
      success: true,
      tempExecutions: files.filter(f => f.endsWith('.act')),
      count: files.filter(f => f.endsWith('.act')).length,
      tempDir
    })

  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}
