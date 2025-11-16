import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const NODE_CATALOG = path.join(process.cwd(), 'flow-architect/catalogs/node-catalog.json');

// GET - List all nodes that can be authenticated
export async function GET() {
  try {
    // Read node catalog
    const catalogContent = await fs.readFile(NODE_CATALOG, 'utf-8');
    const catalog = JSON.parse(catalogContent);

    // Filter nodes that require authentication (have auth fields)
    const authNodes = (catalog.nodes || [])
      .filter((node: any) => {
        // Nodes that require services or have authentication fields
        return node.requires_auth ||
               node.requires_service ||
               node.parameters?.some((p: string) =>
                 p.includes('api_key') ||
                 p.includes('token') ||
                 p.includes('connection_string') ||
                 p.includes('auth')
               );
      })
      .map((node: any) => {
        // Determine auth fields based on node type
        const authFields = determineAuthFields(node);

        return {
          id: node.type,
          displayName: node.name || node.type,
          description: node.description || `${node.name} integration`,
          operations: 0, // Will be populated when operations are loaded
          tags: node.tags || [node.requires_service || 'integration'],
          authInfo: {
            requiresAuth: true,
            authFields: authFields
          }
        };
      });

    return NextResponse.json({ nodes: authNodes });
  } catch (error: any) {
    console.error('Error reading node catalog:', error);
    return NextResponse.json(
      { error: 'Failed to read node catalog', details: error.message },
      { status: 500 }
    );
  }
}

// Determine authentication fields based on node type and parameters
function determineAuthFields(node: any): Array<{
  field: string;
  type: string;
  description: string;
  required: boolean;
}> {
  const authFields: Array<{
    field: string;
    type: string;
    description: string;
    required: boolean;
  }> = [];

  // Common patterns
  const params = node.parameters || [];

  if (params.includes('connection_string')) {
    authFields.push({
      field: 'connection_string',
      type: 'secret',
      description: `${node.name} connection string`,
      required: true
    });
  }

  if (params.includes('api_key')) {
    authFields.push({
      field: 'api_key',
      type: 'secret',
      description: `${node.name} API key`,
      required: true
    });
  }

  if (params.includes('token') || params.includes('access_token')) {
    authFields.push({
      field: 'token',
      type: 'secret',
      description: `${node.name} access token`,
      required: true
    });
  }

  if (params.includes('username')) {
    authFields.push({
      field: 'username',
      type: 'text',
      description: 'Username',
      required: true
    });
  }

  if (params.includes('password')) {
    authFields.push({
      field: 'password',
      type: 'secret',
      description: 'Password',
      required: true
    });
  }

  // Node-specific auth requirements
  switch (node.type) {
    case 'github':
      if (authFields.length === 0) {
        authFields.push({
          field: 'token',
          type: 'secret',
          description: 'GitHub personal access token',
          required: true
        });
      }
      break;

    case 'openai':
    case 'claude':
      if (authFields.length === 0) {
        authFields.push({
          field: 'api_key',
          type: 'secret',
          description: `${node.name} API key`,
          required: true
        });
      }
      break;

    case 'slack':
      if (authFields.length === 0) {
        authFields.push({
          field: 'bot_token',
          type: 'secret',
          description: 'Slack bot token (xoxb-...)',
          required: true
        });
      }
      break;

    case 'discord':
      if (authFields.length === 0) {
        authFields.push({
          field: 'bot_token',
          type: 'secret',
          description: 'Discord bot token',
          required: true
        });
      }
      break;

    case 'email':
    case 'smtp':
      if (authFields.length === 0) {
        authFields.push(
          {
            field: 'smtp_host',
            type: 'text',
            description: 'SMTP server host',
            required: true
          },
          {
            field: 'smtp_port',
            type: 'text',
            description: 'SMTP port (usually 587)',
            required: true
          },
          {
            field: 'username',
            type: 'text',
            description: 'Email username',
            required: true
          },
          {
            field: 'password',
            type: 'secret',
            description: 'Email password',
            required: true
          }
        );
      }
      break;
  }

  // If no auth fields determined, add a generic API key field
  if (authFields.length === 0 && node.requires_service) {
    authFields.push({
      field: 'api_key',
      type: 'secret',
      description: `API key for ${node.name}`,
      required: true
    });
  }

  return authFields;
}
