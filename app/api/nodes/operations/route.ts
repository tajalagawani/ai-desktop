import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const NODE_CATALOG = path.join(process.cwd(), 'flow-architect/catalogs/node-catalog.json');

// GET - Get operations for a specific node type
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const nodeType = searchParams.get('node_type');

    if (!nodeType) {
      return NextResponse.json(
        { error: 'Missing node_type parameter' },
        { status: 400 }
      );
    }

    // Read node catalog
    const catalogContent = await fs.readFile(NODE_CATALOG, 'utf-8');
    const catalog = JSON.parse(catalogContent);

    // Find node
    const node = catalog.nodes?.find((n: any) => n.type === nodeType);

    if (!node) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' not found` },
        { status: 404 }
      );
    }

    // Get operations for this node
    const operations = getOperationsForNode(node);

    return NextResponse.json({ operations });
  } catch (error: any) {
    console.error('Error reading operations:', error);
    return NextResponse.json(
      { error: 'Failed to read operations', details: error.message },
      { status: 500 }
    );
  }
}

// Get operations based on node type
function getOperationsForNode(node: any): Array<{
  name: string;
  displayName: string;
  description: string;
  category?: string;
}> {
  // If node has explicit operations list
  if (node.operations && Array.isArray(node.operations)) {
    return node.operations.map((op: any) => {
      if (typeof op === 'string') {
        return {
          name: op,
          displayName: formatDisplayName(op),
          description: `Perform ${op} operation`
        };
      }
      return {
        name: op.name || op.id,
        displayName: op.displayName || formatDisplayName(op.name || op.id),
        description: op.description || '',
        category: op.category
      };
    });
  }

  // Generate common operations based on node type
  const operations: Array<{
    name: string;
    displayName: string;
    description: string;
    category?: string;
  }> = [];

  switch (node.type) {
    case 'mongo':
    case 'mongodb':
      operations.push(
        { name: 'find', displayName: 'Find Documents', description: 'Query documents from collection', category: 'read' },
        { name: 'find_one', displayName: 'Find One', description: 'Find single document', category: 'read' },
        { name: 'insert', displayName: 'Insert Document', description: 'Insert new document', category: 'write' },
        { name: 'update', displayName: 'Update Documents', description: 'Update existing documents', category: 'write' },
        { name: 'delete', displayName: 'Delete Documents', description: 'Remove documents', category: 'write' },
        { name: 'aggregate', displayName: 'Aggregate', description: 'Run aggregation pipeline', category: 'read' }
      );
      break;

    case 'neon':
    case 'postgresql':
    case 'postgres':
    case 'mysql':
      operations.push(
        { name: 'execute_query', displayName: 'Execute Query', description: 'Run SQL query', category: 'query' },
        { name: 'select', displayName: 'Select Data', description: 'Query data from tables', category: 'read' },
        { name: 'insert', displayName: 'Insert Data', description: 'Insert new records', category: 'write' },
        { name: 'update', displayName: 'Update Data', description: 'Update existing records', category: 'write' },
        { name: 'delete', displayName: 'Delete Data', description: 'Delete records', category: 'write' }
      );
      break;

    case 'github':
      operations.push(
        { name: 'create_issue', displayName: 'Create Issue', description: 'Create new GitHub issue', category: 'issues' },
        { name: 'list_issues', displayName: 'List Issues', description: 'Get repository issues', category: 'issues' },
        { name: 'create_pr', displayName: 'Create Pull Request', description: 'Create new pull request', category: 'pull_requests' },
        { name: 'list_prs', displayName: 'List Pull Requests', description: 'Get pull requests', category: 'pull_requests' },
        { name: 'get_repo', displayName: 'Get Repository', description: 'Get repository information', category: 'repositories' },
        { name: 'create_commit', displayName: 'Create Commit', description: 'Create new commit', category: 'git' }
      );
      break;

    case 'openai':
      operations.push(
        { name: 'chat_completion', displayName: 'Chat Completion', description: 'Generate chat response', category: 'chat' },
        { name: 'completion', displayName: 'Text Completion', description: 'Complete text prompt', category: 'text' },
        { name: 'embedding', displayName: 'Create Embedding', description: 'Generate text embeddings', category: 'embeddings' },
        { name: 'image_generation', displayName: 'Generate Image', description: 'Create AI-generated image', category: 'images' }
      );
      break;

    case 'claude':
    case 'anthropic':
      operations.push(
        { name: 'chat', displayName: 'Chat', description: 'Send message to Claude', category: 'chat' },
        { name: 'completion', displayName: 'Text Completion', description: 'Complete text with Claude', category: 'text' }
      );
      break;

    case 'slack':
      operations.push(
        { name: 'send_message', displayName: 'Send Message', description: 'Post message to channel', category: 'messages' },
        { name: 'list_channels', displayName: 'List Channels', description: 'Get workspace channels', category: 'channels' },
        { name: 'upload_file', displayName: 'Upload File', description: 'Upload file to Slack', category: 'files' },
        { name: 'get_user_info', displayName: 'Get User Info', description: 'Get user information', category: 'users' }
      );
      break;

    case 'discord':
      operations.push(
        { name: 'send_message', displayName: 'Send Message', description: 'Send message to channel', category: 'messages' },
        { name: 'create_channel', displayName: 'Create Channel', description: 'Create new channel', category: 'channels' },
        { name: 'get_guild', displayName: 'Get Server Info', description: 'Get server information', category: 'server' }
      );
      break;

    case 'email':
    case 'smtp':
      operations.push(
        { name: 'send_email', displayName: 'Send Email', description: 'Send email message', category: 'send' },
        { name: 'send_html', displayName: 'Send HTML Email', description: 'Send formatted HTML email', category: 'send' }
      );
      break;

    case 'http_request':
    case 'http':
      operations.push(
        { name: 'get', displayName: 'HTTP GET', description: 'Send GET request', category: 'http' },
        { name: 'post', displayName: 'HTTP POST', description: 'Send POST request', category: 'http' },
        { name: 'put', displayName: 'HTTP PUT', description: 'Send PUT request', category: 'http' },
        { name: 'delete', displayName: 'HTTP DELETE', description: 'Send DELETE request', category: 'http' }
      );
      break;

    default:
      // Generic operations based on parameters
      if (node.parameters?.includes('query')) {
        operations.push({
          name: 'query',
          displayName: 'Query',
          description: `Execute ${node.type} query`
        });
      }
      if (node.parameters?.includes('operation')) {
        operations.push({
          name: 'execute',
          displayName: 'Execute',
          description: `Execute ${node.type} operation`
        });
      }
  }

  // If still no operations, provide a generic one
  if (operations.length === 0) {
    operations.push({
      name: 'execute',
      displayName: 'Execute',
      description: `Execute ${node.name || node.type} operation`
    });
  }

  return operations;
}

// Format operation name to display name
function formatDisplayName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
