/**
 * Flow Builder API Routes
 * Handles AI agent sessions for workflow generation
 * Storage: data/flow-sessions.json
 */

const express = require('express')
const router = express.Router()
const { readJSON, writeJSON, getDataPath } = require('../../lib/json-storage')
const { v4: uuidv4 } = require('uuid')

const SESSIONS_FILE = getDataPath('flow-sessions.json')

/**
 * Get all sessions from JSON file
 */
async function getSessions() {
  const data = await readJSON(SESSIONS_FILE)
  return data?.sessions || []
}

/**
 * Save sessions to JSON file
 */
async function saveSessions(sessions) {
  await writeJSON(SESSIONS_FILE, { sessions })
}

/**
 * GET /api/flow-builder/sessions
 * List all Flow Builder sessions
 */
router.get('/sessions', async (req, res) => {
  try {
    const { userId, limit = 50 } = req.query

    const sessions = await getSessions()

    // Apply limit
    const limitedSessions = sessions.slice(0, parseInt(limit))

    // Map to frontend format
    const formattedSessions = limitedSessions.map(session => ({
      id: session.id,
      status: session.status,
      prompt: session.prompt,
      title: session.prompt, // Alias for frontend
      output: session.output,
      userId: 'default-user',
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
    }))

    res.json({
      success: true,
      sessions: formattedSessions,
      count: formattedSessions.length
    })
  } catch (error) {
    console.error('[API Flow Builder GET Sessions] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/flow-builder/sessions
 * Create a new Flow Builder session
 */
router.post('/sessions', async (req, res) => {
  try {
    const { prompt, title, userId } = req.body

    // Accept either prompt or title
    const sessionTitle = prompt || title

    if (!sessionTitle) {
      return res.status(400).json({
        success: false,
        error: 'Prompt or title is required'
      })
    }

    const sessions = await getSessions()

    // Generate new ID
    const newId = sessions.length > 0
      ? Math.max(...sessions.map(s => s.id)) + 1
      : 1

    const session = {
      id: newId,
      status: 'idle',
      prompt: sessionTitle,
      output: null,
      messages: [],
      userId: userId || 'default-user',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    sessions.push(session)
    await saveSessions(sessions)

    console.log(`[Flow Builder] Created session ${session.id}: ${sessionTitle}`)

    res.json({
      success: true,
      session: {
        id: session.id,
        status: session.status,
        prompt: session.prompt,
        title: session.prompt, // Alias for frontend
        userId: session.userId,
        createdAt: session.createdAt,
      }
    })
  } catch (error) {
    console.error('[API Flow Builder POST Session] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/flow-builder/sessions/:id
 * Get a specific Flow Builder session
 */
router.get('/sessions/:id', async (req, res) => {
  try {
    const { id } = req.params

    const sessions = await getSessions()
    const session = sessions.find(s => s.id === parseInt(id))

    if (!session) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      })
    }

    res.json({
      success: true,
      session: {
        id: session.id,
        status: session.status,
        prompt: session.prompt,
        title: session.prompt, // Alias for frontend
        output: session.output,
        userId: 'default-user',
        createdAt: session.createdAt,
        updatedAt: session.updatedAt,
      }
    })
  } catch (error) {
    console.error('[API Flow Builder GET Session] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * PATCH /api/flow-builder/sessions/:id
 * Update a Flow Builder session (rename)
 */
router.patch('/sessions/:id', async (req, res) => {
  try {
    const { id } = req.params
    const { title } = req.body

    const sessions = await getSessions()
    const sessionIndex = sessions.findIndex(s => s.id === parseInt(id))

    if (sessionIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      })
    }

    sessions[sessionIndex].prompt = title
    sessions[sessionIndex].updatedAt = new Date().toISOString()

    await saveSessions(sessions)

    res.json({
      success: true,
      message: 'Session updated'
    })
  } catch (error) {
    console.error('[API Flow Builder PATCH Session] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/flow-builder/sessions/:id/archive
 * Archive a Flow Builder session
 */
router.post('/sessions/:id/archive', async (req, res) => {
  try {
    const { id } = req.params

    const sessions = await getSessions()
    const sessionIndex = sessions.findIndex(s => s.id === parseInt(id))

    if (sessionIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      })
    }

    sessions[sessionIndex].status = 'archived'
    sessions[sessionIndex].updatedAt = new Date().toISOString()

    await saveSessions(sessions)

    res.json({
      success: true,
      message: 'Session archived'
    })
  } catch (error) {
    console.error('[API Flow Builder Archive Session] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * DELETE /api/flow-builder/sessions/:id
 * Delete a Flow Builder session
 */
router.delete('/sessions/:id', async (req, res) => {
  try {
    const { id } = req.params

    const sessions = await getSessions()
    const filteredSessions = sessions.filter(s => s.id !== parseInt(id))

    await saveSessions(filteredSessions)

    res.json({
      success: true,
      message: 'Session deleted'
    })
  } catch (error) {
    console.error('[API Flow Builder DELETE Session] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/flow-builder/settings
 * Get Flow Builder settings
 */
router.get('/settings', async (req, res) => {
  try {
    // TODO: Implement settings storage
    const settings = {
      model: 'claude-3-sonnet',
      maxTokens: 4096,
      temperature: 0.7,
    }

    res.json({
      success: true,
      settings
    })
  } catch (error) {
    console.error('[API Flow Builder GET Settings] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/flow-builder/settings
 * Update Flow Builder settings
 */
router.post('/settings', async (req, res) => {
  try {
    const { model, maxTokens, temperature } = req.body

    // TODO: Implement settings storage
    const settings = {
      model,
      maxTokens,
      temperature,
    }

    res.json({
      success: true,
      settings
    })
  } catch (error) {
    console.error('[API Flow Builder POST Settings] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/flow-builder/messages
 * Get messages for a session
 */
router.get('/messages', async (req, res) => {
  try {
    const { sessionId } = req.query

    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'sessionId is required'
      })
    }

    const sessions = await getSessions()
    const session = sessions.find(s => s.id === parseInt(sessionId))

    if (!session) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      })
    }

    const messages = session.messages || []

    res.json({
      success: true,
      messages,
      count: messages.length
    })
  } catch (error) {
    console.error('[API Flow Builder GET Messages] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/flow-builder/messages
 * Create a new message
 */
router.post('/messages', async (req, res) => {
  try {
    const { id, sessionId, role, content, toolResults } = req.body

    if (!sessionId || !role || !content) {
      return res.status(400).json({
        success: false,
        error: 'sessionId, role, and content are required'
      })
    }

    const sessions = await getSessions()
    const sessionIndex = sessions.findIndex(s => s.id === parseInt(sessionId))

    if (sessionIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      })
    }

    const message = {
      id: id || uuidv4(),
      sessionId: parseInt(sessionId),
      role,
      content,
      toolResults: toolResults || [],
      createdAt: new Date().toISOString(),
    }

    // Initialize messages array if it doesn't exist
    if (!sessions[sessionIndex].messages) {
      sessions[sessionIndex].messages = []
    }

    sessions[sessionIndex].messages.push(message)
    sessions[sessionIndex].updatedAt = new Date().toISOString()

    await saveSessions(sessions)

    // Broadcast via WebSocket
    if (global.socketIO && global.socketIO.io) {
      global.socketIO.io.to(`agent:${sessionId}`).emit(`agent:${sessionId}:message`, message)
    }

    res.json({
      success: true,
      message
    })
  } catch (error) {
    console.error('[API Flow Builder POST Message] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/flow-builder/messages/:id
 * Get a specific message
 */
router.get('/messages/:id', async (req, res) => {
  try {
    const { id } = req.params

    const sessions = await getSessions()

    // Find message across all sessions
    let foundMessage = null
    for (const session of sessions) {
      if (session.messages) {
        foundMessage = session.messages.find(m => m.id === id)
        if (foundMessage) break
      }
    }

    if (!foundMessage) {
      return res.status(404).json({
        success: false,
        error: 'Message not found'
      })
    }

    res.json({
      success: true,
      message: foundMessage
    })
  } catch (error) {
    console.error('[API Flow Builder GET Message] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
