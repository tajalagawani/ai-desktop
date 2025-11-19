/**
 * JSON File Storage Utility
 * Simple file-based storage for lightweight data persistence
 */

const fs = require('fs').promises
const path = require('path')

/**
 * Read JSON file
 */
async function readJSON(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist, return empty structure
      return null
    }
    throw error
  }
}

/**
 * Write JSON file
 */
async function writeJSON(filePath, data) {
  const dir = path.dirname(filePath)

  // Ensure directory exists
  try {
    await fs.mkdir(dir, { recursive: true })
  } catch (error) {
    // Directory might already exist
  }

  await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8')
}

/**
 * Get data directory path
 */
function getDataPath(filename) {
  return path.join(__dirname, '../data', filename)
}

module.exports = {
  readJSON,
  writeJSON,
  getDataPath,
}
