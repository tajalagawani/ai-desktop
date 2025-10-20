import fs from 'fs';
import path from 'path';

const NODES_DIR = path.join(process.cwd(), 'components/apps/act-docker/act/nodes');

// Node information structure
export interface NodeOperation {
  name: string;
  displayName: string;
  category: string;
}

export interface NodeParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default?: any;
  secret?: boolean;
  enum?: string[];
}

export interface NodeCapabilities {
  canRead: boolean;
  canWrite: boolean;
  canUpdate: boolean;
  canDelete: boolean;
  canStream: boolean;
  canAggregate: boolean;
  requiresAuth: boolean;
}

export interface AuthRequirement {
  field: string;
  type: string;
  description: string;
  required: boolean;
  pattern?: string;
  example?: string;
  sensitive: boolean;
}

export interface NodeAuthInfo {
  requiresAuth: boolean;
  authType?: string;
  authFields: AuthRequirement[];
}

export interface NodeInfo {
  id: string;
  displayName: string;
  description: string;
  version: string;
  author: string;
  tags: string[];
  operations: NodeOperation[];
  operationCategories: Record<string, string[]>;
  parameters: NodeParameter[];
  capabilities: NodeCapabilities;
  authInfo: NodeAuthInfo;
  sourceFile: string;
}

export interface NodeCatalog {
  nodes: NodeInfo[];
  total: number;
  generated: string;
  version: string;
}

/**
 * Parse all node files and return complete catalog
 */
export function parseAllNodes(): NodeCatalog {
  console.log(`Parsing nodes from: ${NODES_DIR}`);

  if (!fs.existsSync(NODES_DIR)) {
    throw new Error(`Nodes directory not found: ${NODES_DIR}`);
  }

  const files = fs.readdirSync(NODES_DIR)
    .filter(f => f.endsWith('Node.py') && f !== 'base_node.py');

  console.log(`Found ${files.length} node files`);

  const nodes = files
    .map(file => {
      try {
        const content = fs.readFileSync(path.join(NODES_DIR, file), 'utf-8');
        return parseNode(content, file);
      } catch (error) {
        console.error(`Error parsing ${file}:`, error);
        return null;
      }
    })
    .filter((node): node is NodeInfo => node !== null);

  console.log(`Successfully parsed ${nodes.length} nodes`);

  return {
    nodes,
    total: nodes.length,
    generated: new Date().toISOString(),
    version: '2.0.0'
  };
}

/**
 * Extract authentication requirements from node file
 */
function extractAuthRequirements(content: string): NodeAuthInfo {
  const authFields: AuthRequirement[] = [];
  let authType: string | undefined;

  // Pattern 1: Universal Request Node CONFIG
  const configMatch = content.match(/CONFIG\s*=\s*{([\s\S]*?)(?=\n\s*class\s+\w+Node|\n\s*def\s+|$)/);
  if (configMatch) {
    const configBlock = configMatch[1];

    // Extract auth type from api_config
    const authTypeMatch = configBlock.match(/"type":\s*"([^"]+)"/);
    if (authTypeMatch) {
      authType = authTypeMatch[1];
    }

    // Extract parameters marked as sensitive
    const paramPattern = /"(\w+)":\s*{([^}]*"sensitive":\s*True[^}]*)}/g;
    let match;

    while ((match = paramPattern.exec(configBlock)) !== null) {
      const fieldName = match[1];
      const fieldBlock = match[2];

      const descMatch = fieldBlock.match(/"description":\s*"([^"]+)"/);
      const requiredMatch = fieldBlock.match(/"required":\s*(True|False)/);
      const patternMatch = fieldBlock.match(/"pattern":\s*"([^"]+)"/);

      authFields.push({
        field: fieldName,
        type: 'secret',
        description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
        required: requiredMatch ? requiredMatch[1] === 'True' : false,
        pattern: patternMatch ? patternMatch[1] : undefined,
        sensitive: true
      });
    }
  }

  // Pattern 2: NodeParameter with SECRET type
  const secretParamRegex = /NodeParameter\s*\(\s*name\s*=\s*["']([^"']+)["'][^)]*type\s*=\s*NodeParameterType\.SECRET/g;
  let secretMatch;

  while ((secretMatch = secretParamRegex.exec(content)) !== null) {
    const fieldName = secretMatch[1];

    // Check if already added
    if (authFields.find(f => f.field === fieldName)) continue;

    // Try to find description
    const paramBlock = content.substring(secretMatch.index, secretMatch.index + 500);
    const descMatch = paramBlock.match(/description\s*=\s*["']([^"']+)["']/);
    const requiredMatch = paramBlock.match(/required\s*=\s*(True|False)/);

    authFields.push({
      field: fieldName,
      type: 'secret',
      description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
      required: requiredMatch ? requiredMatch[1] === 'True' : false,
      sensitive: true
    });
  }

  // Pattern 3: Common auth parameter names
  const commonAuthParams = ['api_key', 'token', 'password', 'secret', 'credential', 'auth_token', 'access_token'];
  const nodeParamRegex = /NodeParameter\s*\(\s*name\s*=\s*["']([^"']+)["'][^)]+\)/g;
  let paramMatch;

  while ((paramMatch = nodeParamRegex.exec(content)) !== null) {
    const fieldName = paramMatch[1];
    const fieldLower = fieldName.toLowerCase();

    if (commonAuthParams.some(auth => fieldLower.includes(auth))) {
      // Check if already added
      if (authFields.find(f => f.field === fieldName)) continue;

      const paramBlock = content.substring(paramMatch.index, paramMatch.index + 500);
      const descMatch = paramBlock.match(/description\s*=\s*["']([^"']+)["']/);
      const requiredMatch = paramBlock.match(/required\s*=\s*(True|False)/);

      authFields.push({
        field: fieldName,
        type: 'secret',
        description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
        required: requiredMatch ? requiredMatch[1] === 'True' : false,
        sensitive: true
      });
    }
  }

  return {
    requiresAuth: authFields.length > 0,
    authType,
    authFields
  };
}

/**
 * Parse a single node file
 */
function parseNode(content: string, filename: string): NodeInfo {
  const id = extractNodeId(content, filename);

  const operations = extractOperations(content);
  const parameters = extractParameters(content);
  const authInfo = extractAuthRequirements(content);
  const capabilities = inferCapabilities(operations, parameters);
  const tags = inferTags(id, operations);

  return {
    id,
    displayName: formatDisplayName(id),
    description: extractDescription(content),
    version: extractVersion(content),
    author: extractAuthor(content),
    tags,
    operations,
    operationCategories: groupOperationsByCategory(operations),
    parameters,
    capabilities: {
      ...capabilities,
      requiresAuth: authInfo.requiresAuth
    },
    authInfo,
    sourceFile: filename
  };
}

/**
 * Extract node ID from content or filename
 */
function extractNodeId(content: string, filename: string): string {
  // Try to find node_type in get_schema
  const nodeTypeMatch = content.match(/node_type\s*=\s*["']([^"']+)["']/);
  if (nodeTypeMatch) {
    return nodeTypeMatch[1];
  }

  // Fall back to filename
  return filename.replace('Node.py', '').toLowerCase();
}

/**
 * Extract description from docstring or get_schema
 */
function extractDescription(content: string): string {
  // Try to find description in get_schema
  const schemaDescMatch = content.match(/description\s*=\s*["']([^"']+)["']/);
  if (schemaDescMatch) {
    return schemaDescMatch[1];
  }

  // Try to find class docstring
  const docstringMatch = content.match(/class\s+\w+Node[^:]*:\s*"""([^"]+)"""/);
  if (docstringMatch) {
    return docstringMatch[1].trim().split('\n')[0];
  }

  // Try module docstring
  const moduleDocMatch = content.match(/^"""([^"]+)"""/m);
  if (moduleDocMatch) {
    return moduleDocMatch[1].trim().split('\n')[0];
  }

  return 'No description available';
}

/**
 * Extract version from get_schema
 */
function extractVersion(content: string): string {
  const versionMatch = content.match(/version\s*=\s*["']([^"']+)["']/);
  return versionMatch ? versionMatch[1] : '1.0.0';
}

/**
 * Extract author from get_schema
 */
function extractAuthor(content: string): string {
  const authorMatch = content.match(/author\s*=\s*["']([^"']+)["']/);
  return authorMatch ? authorMatch[1] : 'ACT Framework';
}

/**
 * Extract operations from Operation class
 */
function extractOperations(content: string): NodeOperation[] {
  const operations: NodeOperation[] = [];

  // Find Operation class definitions
  const operationClassMatch = content.match(/class\s+\w*Operation[^:]*:([\s\S]*?)(?=\n\nclass|\nclass \w+:|$)/);

  if (operationClassMatch) {
    const operationBlock = operationClassMatch[1];

    // Find all operation constants: OPERATION_NAME = "operation_value"
    const regex = /^\s*([A-Z_]+)\s*=\s*["']([a-z_]+)["']/gm;
    let match;

    while ((match = regex.exec(operationBlock)) !== null) {
      const name = match[2];
      operations.push({
        name,
        displayName: formatDisplayName(name),
        category: inferOperationCategory(name)
      });
    }
  }

  // If no operations found, check if this is a single-operation node
  if (operations.length === 0) {
    // Some nodes like PyNode, IfNode don't have operation classes
    const nodeId = extractNodeId(content, '');
    operations.push({
      name: 'execute',
      displayName: 'Execute',
      category: 'execute'
    });
  }

  return operations;
}

/**
 * Infer operation category from name
 */
function inferOperationCategory(operation: string): string {
  const op = operation.toLowerCase();

  if (/insert|create|add|post|save|put/.test(op)) return 'create';
  if (/find|get|read|select|list|fetch|query|search/.test(op)) return 'read';
  if (/update|modify|patch|replace|edit|set/.test(op)) return 'update';
  if (/delete|remove|drop|destroy|clear/.test(op)) return 'delete';
  if (/aggregate|group|sum|count|analyze/.test(op)) return 'aggregation';
  if (/index|optimize/.test(op)) return 'indexing';
  if (/send|email|notify|message/.test(op)) return 'communication';
  if (/watch|stream|subscribe/.test(op)) return 'streaming';
  if (/transaction|commit|rollback/.test(op)) return 'transaction';

  return 'other';
}

/**
 * Extract parameters from NodeParameter definitions
 */
function extractParameters(content: string): NodeParameter[] {
  const parameters: NodeParameter[] = [];

  // Find all NodeParameter definitions
  const paramRegex = /NodeParameter\s*\(([\s\S]*?)\)/g;
  let match;

  while ((match = paramRegex.exec(content)) !== null) {
    const paramBlock = match[1];

    const param: NodeParameter = {
      name: extractParamValue(paramBlock, 'name') || '',
      type: extractParamType(paramBlock),
      description: extractParamValue(paramBlock, 'description') || '',
      required: extractParamValue(paramBlock, 'required') === 'True',
    };

    // Extract default value
    const defaultMatch = paramBlock.match(/default\s*=\s*([^,\n]+)/);
    if (defaultMatch && defaultMatch[1].trim() !== 'None') {
      param.default = defaultMatch[1].trim();
    }

    // Check if it's a secret parameter
    if (param.type === 'secret' || /password|token|key|credential|secret/i.test(param.name)) {
      param.secret = true;
    }

    // Extract enum values
    const enumMatch = paramBlock.match(/enum\s*=\s*\[([^\]]+)\]/);
    if (enumMatch) {
      param.enum = enumMatch[1]
        .split(',')
        .map(v => v.trim().replace(/["']/g, ''));
    }

    if (param.name) {
      parameters.push(param);
    }
  }

  return parameters;
}

/**
 * Extract parameter value by key
 */
function extractParamValue(paramBlock: string, key: string): string | null {
  const regex = new RegExp(`${key}\\s*=\\s*["']([^"']+)["']`);
  const match = paramBlock.match(regex);
  return match ? match[1] : null;
}

/**
 * Extract parameter type
 */
function extractParamType(paramBlock: string): string {
  const typeMatch = paramBlock.match(/type\s*=\s*NodeParameterType\.(\w+)/);
  if (typeMatch) {
    return typeMatch[1].toLowerCase();
  }
  return 'string';
}

/**
 * Infer capabilities from operations and parameters
 */
function inferCapabilities(operations: NodeOperation[], parameters: NodeParameter[]): NodeCapabilities {
  const opNames = operations.map(op => op.name).join(' ').toLowerCase();

  return {
    canRead: operations.some(op => op.category === 'read'),
    canWrite: operations.some(op => op.category === 'create'),
    canUpdate: operations.some(op => op.category === 'update'),
    canDelete: operations.some(op => op.category === 'delete'),
    canStream: /stream|watch|subscribe/.test(opNames),
    canAggregate: operations.some(op => op.category === 'aggregation'),
    requiresAuth: parameters.some(p => p.secret)
  };
}

/**
 * Infer tags from node id and operations
 */
function inferTags(id: string, operations: NodeOperation[]): string[] {
  const tags: Set<string> = new Set();

  // Add tags based on node ID
  const idLower = id.toLowerCase();
  if (/mongo|postgres|mysql|redis|neo4j|sqlite/.test(idLower)) {
    tags.add('database');
  }
  if (/sql/.test(idLower)) {
    tags.add('sql');
  }
  if (/mongo|redis|neo4j/.test(idLower)) {
    tags.add('nosql');
  }
  if (/api|http|request/.test(idLower)) {
    tags.add('api');
  }
  if (/email|smtp|mail/.test(idLower)) {
    tags.add('email');
  }
  if (/file|storage|s3/.test(idLower)) {
    tags.add('storage');
  }
  if (/openai|anthropic|ai/.test(idLower)) {
    tags.add('ai');
  }

  // Add category tags from operations
  operations.forEach(op => {
    tags.add(op.category);
  });

  return Array.from(tags);
}

/**
 * Group operations by category
 */
function groupOperationsByCategory(operations: NodeOperation[]): Record<string, string[]> {
  const categories: Record<string, string[]> = {};

  operations.forEach(op => {
    if (!categories[op.category]) {
      categories[op.category] = [];
    }
    categories[op.category].push(op.name);
  });

  return categories;
}

/**
 * Format name for display (snake_case to Title Case)
 */
function formatDisplayName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

// Cache for parsed nodes
let cachedCatalog: NodeCatalog | null = null;
let cacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Get parsed catalog with caching
 */
export function getNodeCatalog(forceRefresh = false): NodeCatalog {
  const now = Date.now();

  if (!forceRefresh && cachedCatalog && (now - cacheTime < CACHE_TTL)) {
    return cachedCatalog;
  }

  cachedCatalog = parseAllNodes();
  cacheTime = now;

  return cachedCatalog;
}
