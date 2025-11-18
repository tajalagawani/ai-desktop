import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import { exec } from 'child_process'
import { promisify } from 'util'
import { DeploymentConfig } from '@/lib/deployment/types'

const execAsync = promisify(exec)
const DEPLOYMENTS_FILE = '/var/www/ai-desktop/data/deployments.json'

async function loadDeployments(): Promise<DeploymentConfig[]> {
  try {
    const data = await fs.readFile(DEPLOYMENTS_FILE, 'utf-8')
    const parsed = JSON.parse(data)
    return parsed.deployments || []
  } catch {
    return []
  }
}

async function saveDeployments(deployments: DeploymentConfig[]): Promise<void> {
  await fs.writeFile(
    DEPLOYMENTS_FILE,
    JSON.stringify({ deployments }, null, 2),
    'utf-8'
  )
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const body = await request.json()
    const { action } = body

    const deployments = await loadDeployments()
    const deployment = deployments.find(d => d.id === id)

    if (!deployment) {
      return NextResponse.json(
        { error: 'Deployment not found' },
        { status: 404 }
      )
    }

    switch (action) {
      case 'start':
        await execAsync(`pm2 start ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return NextResponse.json({
          success: true,
          message: `${deployment.repoName} started`
        })

      case 'stop':
        await execAsync(`pm2 stop ${deployment.pm2Name}`)
        deployment.status = 'stopped'
        await saveDeployments(deployments)
        return NextResponse.json({
          success: true,
          message: `${deployment.repoName} stopped`
        })

      case 'restart':
        await execAsync(`pm2 restart ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return NextResponse.json({
          success: true,
          message: `${deployment.repoName} restarted`
        })

      case 'delete':
        // Stop and delete from PM2
        try {
          await execAsync(`pm2 delete ${deployment.pm2Name}`)
          await execAsync('pm2 save')
        } catch (error) {
          console.error('Error deleting from PM2:', error)
        }

        // Delete ecosystem config
        try {
          const ecosystemPath = `${deployment.repoPath}/ecosystem.${deployment.id}.config.js`
          await fs.unlink(ecosystemPath)
        } catch (error) {
          console.error('Error deleting ecosystem config:', error)
        }

        // Delete nginx config if exists
        if (deployment.nginxConfig) {
          try {
            await fs.unlink(deployment.nginxConfig)
            await execAsync('nginx -s reload')
          } catch (error) {
            console.error('Error deleting nginx config:', error)
          }
        }

        // Close firewall port
        try {
          await execAsync(`ufw delete allow ${deployment.port}/tcp`)
          console.log(`Closed firewall port ${deployment.port}`)
        } catch (error) {
          console.error('Error closing firewall port:', error)
        }

        // Remove from deployments
        const index = deployments.findIndex(d => d.id === id)
        if (index !== -1) {
          deployments.splice(index, 1)
          await saveDeployments(deployments)
        }

        return NextResponse.json({
          success: true,
          message: `${deployment.repoName} deployment deleted`
        })

      case 'rebuild':
        // Stop current deployment
        try {
          await execAsync(`pm2 stop ${deployment.pm2Name}`)
        } catch {}

        deployment.status = 'building'
        await saveDeployments(deployments)

        // Trigger rebuild (implementation needed - similar to initial deploy)
        return NextResponse.json({
          success: true,
          message: `${deployment.repoName} rebuild started`
        })

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error: any) {
    console.error('Error performing deployment action:', error)
    return NextResponse.json(
      { error: error.message || 'Action failed' },
      { status: 500 }
    )
  }
}
