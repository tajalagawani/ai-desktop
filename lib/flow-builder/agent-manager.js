const { spawn } = require('child_process');
const path = require('path');

class AgentProcessManager {
  constructor() {
    this.processes = new Map();
    this.sockets = new Map();
  }

  async startAgent(sessionId, request, socket, conversationHistory, apiKey) {
    // Clean up any existing process for this session
    this.stopAgent(sessionId);

    console.log(`[AgentManager] Starting agent for session ${sessionId}`);

    // Use AGENT_SDK_PATH from environment, fallback to local copy
    const agentSdkPath = process.env.AGENT_SDK_PATH ||
                         path.join(__dirname, '../../agent-sdk');
    const debugScript = path.join(agentSdkPath, 'debug-run.sh');

    console.log(`[AgentManager] Agent SDK Path: ${agentSdkPath}`);

    // Prepare context data to pass to the agent
    const contextData = {
      request,
      conversationHistory: conversationHistory || [],
      sessionId,
    };

    // Log environment for debugging
    console.log(`[AgentManager] Running debug script: ${debugScript}`);
    console.log(`[AgentManager] Request: ${request}`);
    console.log(`[AgentManager] Conversation history length: ${conversationHistory?.length || 0}`);
    console.log(`[AgentManager] API key from settings:`, apiKey ? apiKey.substring(0, 20) + '...' : 'NOT PROVIDED (will use .env fallback)');

    // Spawn the debug-run.sh script which handles all logging
    // Use full path to bash for better compatibility across systems
    const bashPath = process.platform === 'win32' ? 'bash' : '/usr/bin/bash';
    const agentProcess = spawn(bashPath, [debugScript, request], {
      cwd: agentSdkPath,
      env: {
        PATH: process.env.PATH || '/usr/local/bin:/usr/bin:/bin',
        HOME: process.env.HOME,
        USER: process.env.USER,
        NODE_ENV: process.env.NODE_ENV,
        SESSION_ID: sessionId,
        DEBUG: 'true',
        VERBOSE: 'true',
        CONVERSATION_CONTEXT: JSON.stringify(contextData),
        // CRITICAL: Pass API key from settings if provided, otherwise agent will use .env fallback
        ...(apiKey && { ANTHROPIC_API_KEY: apiKey }),
      },
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    // Store process info
    this.processes.set(sessionId, {
      process: agentProcess,
      sessionId,
      startedAt: Date.now(),
      buffer: '',
    });

    this.sockets.set(sessionId, socket);

    // Emit started event
    socket.emit('agent:started', { sessionId });

    // Handle stdout (agent logs and output)
    agentProcess.stdout.on('data', (data) => {
      const lines = data.toString().split('\n');

      for (const line of lines) {
        if (!line.trim()) continue;

        // Emit each line as a stream chunk
        socket.emit('stream:chunk', { chunk: line });
      }
    });

    // Handle stderr (errors and warnings)
    agentProcess.stderr.on('data', (data) => {
      const lines = data.toString().split('\n');

      for (const line of lines) {
        if (!line.trim()) continue;

        // Emit stderr as chunks too (agent may log to stderr)
        socket.emit('stream:chunk', { chunk: line });
      }
    });

    // Handle process exit
    agentProcess.on('exit', (code, signal) => {
      console.log(`[AgentManager] Agent process exited: ${code || signal}`);

      const startedAt = this.processes.get(sessionId)?.startedAt || Date.now();
      const duration = Date.now() - startedAt;

      socket.emit('agent:completed', {
        exitCode: code || 0,
        duration,
      });

      this.processes.delete(sessionId);
      this.sockets.delete(sessionId);
    });

    // Handle process error
    agentProcess.on('error', (error) => {
      console.error(`[AgentManager] Agent process error:`, error);

      socket.emit('error', {
        message: error.message,
        code: 'PROCESS_ERROR',
      });

      this.processes.delete(sessionId);
      this.sockets.delete(sessionId);
    });
  }

  stopAgent(sessionId) {
    const agentInfo = this.processes.get(sessionId);

    if (agentInfo) {
      console.log(`[AgentManager] Stopping agent for session ${sessionId}`);
      agentInfo.process.kill('SIGTERM');
      this.processes.delete(sessionId);
      this.sockets.delete(sessionId);
    }
  }

  stopAll() {
    console.log(`[AgentManager] Stopping all agents (${this.processes.size} active)`);

    for (const [sessionId, agentInfo] of this.processes.entries()) {
      console.log(`[AgentManager] Killing agent: ${sessionId}`);
      agentInfo.process.kill('SIGTERM');
    }

    this.processes.clear();
    this.sockets.clear();
  }

  getActiveCount() {
    return this.processes.size;
  }

  isRunning(sessionId) {
    return this.processes.has(sessionId);
  }
}

// Singleton instance
let instance = null;

function getFlowAgentManager() {
  if (!instance) {
    instance = new AgentProcessManager();
  }
  return instance;
}

module.exports = {
  AgentProcessManager,
  getFlowAgentManager,
};
