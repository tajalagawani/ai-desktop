import path from 'path';
import crypto from 'crypto';
import fs from 'fs';

const AUTH_FILE_PATH = path.join(process.cwd(), 'data', 'user-auth.json');

// Ensure data directory exists
const dataDir = path.dirname(AUTH_FILE_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Initialize auth file if it doesn't exist
if (!fs.existsSync(AUTH_FILE_PATH)) {
  fs.writeFileSync(AUTH_FILE_PATH, JSON.stringify({ users: {}, services: {} }, null, 2));
  console.log('✅ Auth file created at:', AUTH_FILE_PATH);
}

console.log('✅ Auth system initialized at:', AUTH_FILE_PATH);

// Encryption key (in production, use environment variable)
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'default-key-change-in-production-32'; // Must be 32 bytes

/**
 * Read auth data from file
 */
function readAuthData(): any {
  try {
    const data = fs.readFileSync(AUTH_FILE_PATH, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading auth data:', error);
    return { users: {} };
  }
}

/**
 * Write auth data to file
 */
function writeAuthData(data: any): void {
  try {
    fs.writeFileSync(AUTH_FILE_PATH, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error writing auth data:', error);
    throw error;
  }
}

/**
 * Encrypt sensitive data
 */
export function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

/**
 * Decrypt sensitive data
 */
export function decrypt(text: string): string {
  const parts = text.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const encrypted = parts[1];
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

/**
 * Save node authentication
 */
export function saveNodeAuth(nodeType: string, authData: Record<string, any>, userId: string = 'default') {
  const data = readAuthData();

  // Initialize user if doesn't exist
  if (!data.users[userId]) {
    data.users[userId] = { nodes: {} };
  }

  if (!data.users[userId].nodes) {
    data.users[userId].nodes = {};
  }

  const encryptedData = encrypt(JSON.stringify(authData));
  const now = new Date().toISOString();

  // Create or update node auth
  data.users[userId].nodes[nodeType] = {
    enabled: true,
    auth_data: encryptedData,
    created_at: data.users[userId].nodes[nodeType]?.created_at || now,
    updated_at: now
  };

  writeAuthData(data);

  return { success: true, nodeType, enabled: true };
}

/**
 * Get node authentication
 */
export function getNodeAuth(nodeType: string, userId: string = 'default'): Record<string, any> | null {
  const data = readAuthData();

  const nodeAuth = data.users?.[userId]?.nodes?.[nodeType];

  if (!nodeAuth || !nodeAuth.enabled) {
    return null;
  }

  try {
    const decryptedData = decrypt(nodeAuth.auth_data);
    return JSON.parse(decryptedData);
  } catch (error) {
    console.error('Error decrypting auth data:', error);
    return null;
  }
}

/**
 * Get all enabled nodes
 */
export function getEnabledNodes(userId: string = 'default'): string[] {
  const data = readAuthData();

  const userNodes = data.users?.[userId]?.nodes || {};

  return Object.keys(userNodes).filter(nodeType => userNodes[nodeType].enabled);
}

/**
 * Disable node
 */
export function disableNode(nodeType: string, userId: string = 'default') {
  const data = readAuthData();

  if (data.users?.[userId]?.nodes?.[nodeType]) {
    data.users[userId].nodes[nodeType].enabled = false;
    data.users[userId].nodes[nodeType].updated_at = new Date().toISOString();
    writeAuthData(data);
  }

  return { success: true, nodeType, enabled: false };
}

/**
 * Delete node auth completely
 */
export function deleteNodeAuth(nodeType: string, userId: string = 'default') {
  const data = readAuthData();

  if (data.users?.[userId]?.nodes?.[nodeType]) {
    delete data.users[userId].nodes[nodeType];
    writeAuthData(data);
  }

  return { success: true, nodeType };
}

/**
 * Update test result
 */
export function updateTestResult(nodeType: string, success: boolean, userId: string = 'default') {
  const data = readAuthData();

  if (data.users?.[userId]?.nodes?.[nodeType]) {
    data.users[userId].nodes[nodeType].last_tested = new Date().toISOString();
    data.users[userId].nodes[nodeType].test_result = success;
    writeAuthData(data);
  }
}

/**
 * Get all node auth with status
 */
export function getAllNodeAuth(userId: string = 'default') {
  const data = readAuthData();

  const userNodes = data.users?.[userId]?.nodes || {};

  return Object.keys(userNodes).map(nodeType => ({
    node_type: nodeType,
    enabled: userNodes[nodeType].enabled,
    last_tested: userNodes[nodeType].last_tested,
    test_result: userNodes[nodeType].test_result,
    created_at: userNodes[nodeType].created_at,
    updated_at: userNodes[nodeType].updated_at
  }));
}

// ==================== SERVICE AUTH ====================

/**
 * Save service authentication (Docker services)
 */
export function saveServiceAuth(serviceId: string, authData: Record<string, any>, userId: string = 'default') {
  const data = readAuthData();

  // Initialize services object if doesn't exist
  if (!data.services) {
    data.services = {};
  }

  if (!data.services[userId]) {
    data.services[userId] = {};
  }

  const encryptedData = encrypt(JSON.stringify(authData));
  const now = new Date().toISOString();

  // Create or update service auth
  data.services[userId][serviceId] = {
    auth_data: encryptedData,
    created_at: data.services[userId][serviceId]?.created_at || now,
    updated_at: now
  };

  writeAuthData(data);

  return { success: true, serviceId };
}

/**
 * Get service authentication
 */
export function getServiceAuth(serviceId: string, userId: string = 'default'): Record<string, any> | null {
  const data = readAuthData();

  const serviceAuth = data.services?.[userId]?.[serviceId];

  if (!serviceAuth) {
    return null;
  }

  try {
    const decryptedData = decrypt(serviceAuth.auth_data);
    return JSON.parse(decryptedData);
  } catch (error) {
    console.error('Error decrypting service auth data:', error);
    return null;
  }
}

/**
 * Get all services with stored auth
 */
export function getAllServiceAuth(userId: string = 'default'): string[] {
  const data = readAuthData();

  const userServices = data.services?.[userId] || {};

  return Object.keys(userServices);
}

/**
 * Delete service auth completely
 */
export function deleteServiceAuth(serviceId: string, userId: string = 'default') {
  const data = readAuthData();

  if (data.services?.[userId]?.[serviceId]) {
    delete data.services[userId][serviceId];
    writeAuthData(data);
  }

  return { success: true, serviceId };
}
