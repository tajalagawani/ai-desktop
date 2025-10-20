import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';

export async function GET(
  request: NextRequest,
  { params }: { params: { nodeType: string; operation: string } }
) {
  try {
    const { nodeType, operation } = params;

    const catalog = getNodeCatalog();
    const nodes = catalog.nodes;

    // Find the requested node
    const node = nodes.find((n: any) =>
      n.id === nodeType || n.id.toLowerCase() === nodeType.toLowerCase()
    );

    if (!node) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' not found` },
        { status: 404 }
      );
    }

    // Find the specific operation
    const op = node.operations.find((o: any) =>
      o.name === operation || o.name.toLowerCase() === operation.toLowerCase()
    );

    if (!op) {
      return NextResponse.json(
        {
          error: `Operation '${operation}' not found for node '${nodeType}'`,
          availableOperations: node.operations.map((o: any) => o.name)
        },
        { status: 404 }
      );
    }

    // Build complete operation detail response
    const response = {
      nodeType: node.id,
      nodeName: node.displayName,
      operation: op,
      globalParameters: node.parameters,
      requiresAuth: node.capabilities.requiresAuth,
      relatedOperations: node.operations
        .filter((o: any) => o.category === op.category && o.name !== op.name)
        .map((o: any) => ({ name: o.name, displayName: o.displayName })),
      example: {
        toml: generateOperationExample(node, op)
      }
    };

    return NextResponse.json(response);

  } catch (error: any) {
    console.error(`Error getting operation ${params.operation} for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

function generateOperationExample(node: any, operation: any): string {
  const lines = [
    `[node:Example${node.displayName.replace(/\s/g, '')}]`,
    `type = ${node.id}`,
    `label = ${operation.displayName} operation`
  ];

  if (operation.name !== 'execute') {
    lines.push(`operation = ${operation.name}`);
  }

  // Add required parameters
  node.parameters
    .filter((p: any) => p.required)
    .slice(0, 3) // Show max 3 params in example
    .forEach((p: any) => {
      if (p.secret) {
        lines.push(`${p.name} = "YOUR_${p.name.toUpperCase()}"`);
      } else if (p.type === 'string') {
        lines.push(`${p.name} = "example_value"`);
      } else if (p.type === 'number') {
        lines.push(`${p.name} = 100`);
      } else if (p.type === 'boolean') {
        lines.push(`${p.name} = true`);
      }
    });

  return lines.join('\n');
}
