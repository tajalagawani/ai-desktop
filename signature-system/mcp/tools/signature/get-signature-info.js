/**
 * Get Signature Info Tool
 * Retrieves information about authenticated nodes from signature file
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { SignatureManager } from '../../lib/signature-manager.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function getSignatureInfo(args) {
  try {
    const {
      node_type = null,
      signature_path = 'signatures/user.act.sig'
    } = args || {};

    // Load signature
    const sigPath = path.resolve(__dirname, '../../../', signature_path);
    const sigManager = new SignatureManager(sigPath);
    await sigManager.load();

    // Get signature info
    const info = sigManager.getSignatureInfo(node_type);

    return ErrorHandler.success(info);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
