/**
 * Signature Manager
 * Manages ACT signature files (.act.sig) for the MCP server
 */

import fs from 'fs/promises';
import path from 'path';
import toml from '@iarna/toml';

export class SignatureManager {
  constructor(signaturePath) {
    this.signaturePath = signaturePath;
    this.signature = null;
    this._loaded = false;
  }

  /**
   * Load and parse signature file
   */
  async load() {
    try {
      const content = await fs.readFile(this.signaturePath, 'utf-8');
      this.signature = toml.parse(content);
      this._loaded = true;
      return this.signature;
    } catch (error) {
      if (error.code === 'ENOENT') {
        throw new Error(`Signature file not found: ${this.signaturePath}`);
      }
      throw new Error(`Failed to parse signature file: ${error.message}`);
    }
  }

  /**
   * Save signature back to file
   */
  async save() {
    if (!this._loaded) {
      throw new Error('Signature must be loaded before saving');
    }

    // Update timestamp
    if (this.signature.signature) {
      this.signature.signature.updated_at = new Date().toISOString();
    }

    const content = toml.stringify(this.signature);
    await fs.writeFile(this.signaturePath, content, 'utf-8');
  }

  /**
   * Check if a node is authenticated
   */
  isAuthenticated(nodeType) {
    const nodeKey = `node:${nodeType}`;
    return this.signature[nodeKey]?.authenticated === true;
  }

  /**
   * Get authentication data for a node
   */
  getNodeAuth(nodeType, resolveEnv = true) {
    const authKey = `node:${nodeType}.auth`;
    let auth = this.signature[authKey] || {};

    if (resolveEnv) {
      auth = this._resolveEnvVars(auth);
    }

    return auth;
  }

  /**
   * Get default parameters for a node
   */
  getNodeDefaults(nodeType) {
    const defaultsKey = `node:${nodeType}.defaults`;
    return this.signature[defaultsKey] || {};
  }

  /**
   * Get available operations for a node
   */
  getOperations(nodeType) {
    const opsKey = `node:${nodeType}.operations`;
    return this.signature[opsKey] || {};
  }

  /**
   * Get metadata for a node
   */
  getNodeMetadata(nodeType) {
    const metaKey = `node:${nodeType}.metadata`;
    return this.signature[metaKey] || {};
  }

  /**
   * Add or update a node in the signature
   */
  async addNode(nodeType, auth, defaults = {}, operations = {}, metadata = {}) {
    // Base node section
    const nodeKey = `node:${nodeType}`;
    this.signature[nodeKey] = {
      type: nodeType,
      enabled: true,
      authenticated: true,
      auth_configured_at: new Date().toISOString()
    };

    // Auth section (store as env references)
    const authKey = `node:${nodeType}.auth`;
    this.signature[authKey] = this._toEnvReferences(nodeType, auth);

    // Defaults section
    if (Object.keys(defaults).length > 0) {
      const defaultsKey = `node:${nodeType}.defaults`;
      this.signature[defaultsKey] = defaults;
    }

    // Operations section
    if (Object.keys(operations).length > 0) {
      const opsKey = `node:${nodeType}.operations`;
      this.signature[opsKey] = operations;
    }

    // Metadata section
    if (Object.keys(metadata).length > 0) {
      const metaKey = `node:${nodeType}.metadata`;
      this.signature[metaKey] = metadata;
    }

    // Update global metadata
    if (!this.signature.metadata) {
      this.signature.metadata = {
        authenticated_nodes: 0,
        unauthenticated_nodes: 0
      };
    }

    // Check if this is a new node
    const existingNodes = this.getAuthenticatedNodes();
    if (!existingNodes.includes(nodeType)) {
      this.signature.metadata.authenticated_nodes =
        (this.signature.metadata.authenticated_nodes || 0) + 1;
    }

    await this.save();
  }

  /**
   * Remove a node from the signature
   */
  async removeNode(nodeType) {
    const nodeKey = `node:${nodeType}`;

    if (!this.signature[nodeKey]) {
      return false;
    }

    // Remove all sections for this node
    const keysToRemove = Object.keys(this.signature).filter(
      key => key.startsWith(`node:${nodeType}`)
    );

    for (const key of keysToRemove) {
      delete this.signature[key];
    }

    // Update metadata
    if (this.signature.metadata) {
      this.signature.metadata.authenticated_nodes =
        Math.max(0, (this.signature.metadata.authenticated_nodes || 1) - 1);
    }

    await this.save();
    return true;
  }

  /**
   * Update default parameters for a node
   */
  async updateNodeDefaults(nodeType, defaults) {
    if (!this.isAuthenticated(nodeType)) {
      return false;
    }

    const defaultsKey = `node:${nodeType}.defaults`;
    this.signature[defaultsKey] = defaults;

    await this.save();
    return true;
  }

  /**
   * Get list of all authenticated node types
   */
  getAuthenticatedNodes() {
    const nodes = [];
    for (const key of Object.keys(this.signature)) {
      if (key.startsWith('node:') && !key.includes('.')) {
        const nodeType = key.split(':')[1];
        if (this.isAuthenticated(nodeType)) {
          nodes.push(nodeType);
        }
      }
    }
    return nodes;
  }

  /**
   * Validate signature file structure
   */
  validate() {
    const errors = [];
    const warnings = [];

    // Check for required sections
    if (!this.signature.signature) {
      errors.push('Missing [signature] section');
    } else {
      if (!this.signature.signature.version) {
        errors.push('Missing signature.version');
      }
    }

    // Check node sections
    for (const key of Object.keys(this.signature)) {
      if (key.startsWith('node:') && !key.includes('.')) {
        const nodeType = key.split(':')[1];

        // Check for required fields
        if (this.signature[key].authenticated === undefined) {
          errors.push(`Node '${nodeType}' missing 'authenticated' field`);
        }

        // Check auth section if authenticated
        if (this.signature[key].authenticated) {
          const authKey = `node:${nodeType}.auth`;
          if (!this.signature[authKey]) {
            errors.push(`Node '${nodeType}' is authenticated but missing .auth section`);
          } else {
            // Check env references
            const auth = this.signature[authKey];
            for (const [field, value] of Object.entries(auth)) {
              if (typeof value === 'string' && value.includes('{{.env.')) {
                const envVar = this._extractEnvVar(value);
                if (envVar && !process.env[envVar]) {
                  warnings.push(`Environment variable '${envVar}' not set for ${nodeType}.${field}`);
                }
              }
            }
          }
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      authenticated_nodes: this.getAuthenticatedNodes().length
    };
  }

  /**
   * Get complete signature information
   */
  getSignatureInfo(nodeType = null) {
    if (nodeType) {
      // Return info for specific node
      if (!this.isAuthenticated(nodeType)) {
        return {
          authenticated: false,
          error: `Node '${nodeType}' is not authenticated`
        };
      }

      const operations = this.getOperations(nodeType);
      return {
        type: nodeType,
        authenticated: true,
        operations: Object.keys(operations),
        operation_count: Object.keys(operations).length,
        defaults: this.getNodeDefaults(nodeType),
        metadata: this.getNodeMetadata(nodeType)
      };
    }

    // Return info for all nodes
    const authenticated = this.getAuthenticatedNodes();

    return {
      version: this.signature.signature?.version || 'unknown',
      user_id: this.signature.signature?.user_id || 'unknown',
      authenticated_nodes: authenticated.map(nodeType => ({
        type: nodeType,
        operations: Object.keys(this.getOperations(nodeType)),
        operation_count: Object.keys(this.getOperations(nodeType)).length,
        defaults: this.getNodeDefaults(nodeType),
        metadata: this.getNodeMetadata(nodeType)
      })),
      total_authenticated: authenticated.length,
      updated_at: this.signature.signature?.updated_at || 'unknown'
    };
  }

  /**
   * Resolve {{.env.VARIABLE}} references recursively
   */
  _resolveEnvVars(obj) {
    if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        return obj.map(item => this._resolveEnvVars(item));
      } else {
        const resolved = {};
        for (const [key, value] of Object.entries(obj)) {
          resolved[key] = this._resolveEnvVars(value);
        }
        return resolved;
      }
    } else if (typeof obj === 'string' && obj.includes('{{.env.')) {
      const envVar = this._extractEnvVar(obj);
      if (envVar) {
        return process.env[envVar] || obj;
      }
    }
    return obj;
  }

  /**
   * Extract environment variable name from {{.env.VAR}} syntax
   */
  _extractEnvVar(value) {
    const match = value.match(/\{\{\.env\.(\w+)\}\}/);
    return match ? match[1] : null;
  }

  /**
   * Convert auth values to {{.env.VARIABLE}} references
   */
  _toEnvReferences(nodeType, auth) {
    const result = {};
    for (const [key, value] of Object.entries(auth)) {
      const envVarName = `${nodeType.toUpperCase()}_${key.toUpperCase()}`;
      result[key] = `{{.env.${envVarName}}}`;
    }
    return result;
  }

  /**
   * Test authentication with external API
   */
  async validateAuth(nodeType, authData) {
    // Node-specific validation
    if (nodeType === 'github') {
      const response = await fetch('https://api.github.com/user', {
        headers: {
          'Authorization': `Bearer ${authData.access_token}`,
          'User-Agent': 'Flow-Architect-MCP'
        }
      });
      if (!response.ok) {
        throw new Error('Invalid GitHub token');
      }
      return await response.json();
    }

    if (nodeType === 'openai') {
      const response = await fetch('https://api.openai.com/v1/models', {
        headers: {
          'Authorization': `Bearer ${authData.api_key}`
        }
      });
      if (!response.ok) {
        throw new Error('Invalid OpenAI API key');
      }
      return await response.json();
    }

    // Add more node types as needed

    // For unknown node types, just return true
    return { validated: true, message: 'No validation available for this node type' };
  }
}
