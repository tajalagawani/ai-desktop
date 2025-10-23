import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Ensures the Flow Architect agent file exists in ~/.claude/agents/
 * If not, copies it from the source directory
 */
export async function ensureAgentFile() {
  try {
    const homeDir = os.homedir();
    const agentDir = path.join(homeDir, '.claude', 'agents');
    const targetAgentFile = path.join(agentDir, 'flow-architect.md');

    // Source agent file location
    const sourceAgentFile = path.join(__dirname, '../../.claude/agents/flow-architect.md');

    console.log('[Setup] Checking Flow Architect agent file...');

    // Always update the agent file to ensure latest version
    // (Don't skip if it exists - we want to overwrite with latest)

    // Verify source file exists
    try {
      await fs.access(sourceAgentFile);
    } catch (error) {
      console.error('[Setup] ❌ Source agent file not found:', sourceAgentFile);
      return { success: false, error: 'Source agent file not found' };
    }

    // Create ~/.claude/agents directory if it doesn't exist
    try {
      await fs.mkdir(agentDir, { recursive: true });
      console.log('[Setup] Created agents directory:', agentDir);
    } catch (error) {
      if (error.code !== 'EEXIST') {
        console.error('[Setup] ❌ Failed to create agents directory:', error.message);
        return { success: false, error: error.message };
      }
    }

    // Copy/Update agent file (always overwrite to ensure latest version)
    try {
      const agentContent = await fs.readFile(sourceAgentFile, 'utf8');
      await fs.writeFile(targetAgentFile, agentContent, 'utf8');
      console.log('[Setup] ✅ Updated agent file:', targetAgentFile);
      return { success: true, updated: true };
    } catch (error) {
      console.error('[Setup] ❌ Failed to update agent file:', error.message);
      return { success: false, error: error.message };
    }

  } catch (error) {
    console.error('[Setup] ❌ Error in ensureAgentFile:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Validates that the agent file exists and is properly configured
 */
export async function validateAgentFile() {
  try {
    const homeDir = os.homedir();
    const targetAgentFile = path.join(homeDir, '.claude', 'agents', 'flow-architect.md');

    const content = await fs.readFile(targetAgentFile, 'utf8');

    // Basic validation - check for required frontmatter
    const hasName = content.includes('name: flow-architect');
    const hasDescription = content.includes('description:');
    const hasTools = content.includes('tools:');

    if (!hasName || !hasDescription || !hasTools) {
      console.warn('[Setup] ⚠️  Agent file exists but may be malformed');
      return { valid: false, error: 'Missing required frontmatter fields' };
    }

    console.log('[Setup] ✅ Agent file validated');
    return { valid: true };

  } catch (error) {
    console.error('[Setup] ❌ Failed to validate agent file:', error.message);
    return { valid: false, error: error.message };
  }
}
