/**
 * Add Node to Signature Tool
 * Authenticates a node and adds it to the signature file
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { SignatureManager } from '../../lib/signature-manager.js';
import { EnvManager } from '../../lib/env-manager.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function addNodeToSignature(args) {
  try {
    // Validate required parameters
    ErrorHandler.validateParams(args, ['node_type', 'auth']);

    const {
      node_type,
      auth,
      defaults = {},
      operations = null,
      metadata = null,
      signature_path = 'signatures/user.act.sig'
    } = args;

    // Load signature
    const sigPath = path.resolve(__dirname, '../../../', signature_path);
    const sigManager = new SignatureManager(sigPath);

    try {
      await sigManager.load();
    } catch (error) {
      if (error.message.includes('not found')) {
        // Initialize empty signature if doesn't exist
        await initializeSignature(sigPath);
        await sigManager.load();
      } else {
        throw error;
      }
    }

    // Validate authentication with external API
    console.error(`Validating ${node_type} authentication...`);
    try {
      const validationResult = await sigManager.validateAuth(node_type, auth);
      console.error(`✓ ${node_type} authentication validated`);
    } catch (error) {
      throw Object.assign(
        new Error(`Authentication validation failed: ${error.message}`),
        { code: 'AUTH_VALIDATION_FAILED' }
      );
    }

    // Save auth to .env
    const envManager = new EnvManager('.env');
    const envKeys = await envManager.setNodeAuth(node_type, auth);
    console.error(`✓ Saved credentials to .env: ${envKeys.join(', ')}`);

    // Load operations from catalog if not provided
    let nodeOperations = operations;
    let nodeMetadata = metadata;

    if (!nodeOperations || !nodeMetadata) {
      const catalogData = await loadNodeFromCatalog(node_type);
      nodeOperations = nodeOperations || catalogData.operations;
      nodeMetadata = nodeMetadata || catalogData.metadata;
    }

    // Add node to signature
    await sigManager.addNode(
      node_type,
      auth,
      defaults,
      nodeOperations,
      nodeMetadata
    );

    console.error(`✓ Added ${node_type} to signature`);

    return ErrorHandler.success({
      node_type,
      authenticated: true,
      operations_available: Object.keys(nodeOperations).length,
      defaults_configured: Object.keys(defaults).length,
      env_keys: envKeys,
      message: `Successfully authenticated ${node_type}`
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}

/**
 * Initialize an empty signature file
 */
async function initializeSignature(signaturePath) {
  const fs = await import('fs/promises');
  const initialSignature = `[signature]
version = "1.0.0"
user_id = "default-user"
created_at = "${new Date().toISOString()}"
updated_at = "${new Date().toISOString()}"

[metadata]
authenticated_nodes = 0
unauthenticated_nodes = 0
`;

  // Ensure directory exists
  const dir = path.dirname(signaturePath);
  await fs.mkdir(dir, { recursive: true });

  await fs.writeFile(signaturePath, initialSignature, 'utf-8');
  console.error(`✓ Initialized new signature file: ${signaturePath}`);
}

/**
 * Load node information from catalog
 */
async function loadNodeFromCatalog(nodeType) {
  // Try to load from local catalog file
  const catalogPath = path.resolve(__dirname, '../../../cache/node-catalog.json');

  try {
    const fs = await import('fs/promises');
    const catalogContent = await fs.readFile(catalogPath, 'utf-8');
    const catalog = JSON.parse(catalogContent);

    const node = catalog.nodes.find(n => n.type === nodeType);
    if (node) {
      return {
        operations: node.operations || {},
        metadata: {
          display_name: node.display_name || nodeType,
          category: node.category || 'unknown',
          description: node.description || '',
          vendor: node.vendor || 'unknown',
          version: node.version || '1.0.0'
        }
      };
    }
  } catch (error) {
    console.error(`Warning: Could not load catalog: ${error.message}`);
  }

  // Return minimal default if catalog not available
  return {
    operations: {
      default: {
        description: 'Default operation',
        parameters: [],
        required_params: []
      }
    },
    metadata: {
      display_name: nodeType,
      category: 'unknown',
      description: 'Node type',
      vendor: 'unknown',
      version: '1.0.0'
    }
  };
}
