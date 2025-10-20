import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET() {
  try {
    // Direct Docker command - FAST!
    const { stdout } = await execAsync(
      'docker ps --format "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}|{{.CreatedAt}}"'
    );

    const services = stdout
      .trim()
      .split('\n')
      .filter(line => line)
      .map(line => {
        const [id, name, status, image, ports, created] = line.split('|');
        return {
          id: id.substring(0, 12),
          name,
          status: status.toLowerCase().includes('up') ? 'running' : 'stopped',
          image,
          ports: ports ? ports.split(',').map(p => p.trim()) : [],
          created
        };
      });

    return NextResponse.json({ services });
  } catch (error: any) {
    console.error('Docker ps error:', error);
    return NextResponse.json({ services: [] });
  }
}
