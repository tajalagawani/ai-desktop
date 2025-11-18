/**
 * Flow Builder Database Layer
 * SQLite database for persisting sessions and messages
 */

import Database from 'better-sqlite3';
import { join } from 'path';

// Database path
const DB_PATH = join(process.cwd(), 'data', 'flow-builder.db');

// Initialize database connection (singleton)
let db: Database.Database | null = null;

function getDb(): Database.Database {
  if (!db) {
    // Ensure data directory exists
    const fs = require('fs');
    const dataDir = join(process.cwd(), 'data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    db = new Database(DB_PATH);
    console.log('[DB] SQLite database initialized:', DB_PATH);

    // Enable foreign keys
    db.pragma('foreign_keys = ON');

    // Initialize schema
    initSchema();
  }
  return db;
}

function initSchema() {
  const db = getDb();

  // Sessions table
  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      title TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'ACTIVE',
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      last_activity_at TEXT NOT NULL
    )
  `);

  // Messages table
  db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      type TEXT NOT NULL DEFAULT 'TEXT',
      streaming INTEGER NOT NULL DEFAULT 0,
      error TEXT,
      metadata TEXT,
      input_tokens INTEGER,
      output_tokens INTEGER,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    )
  `);

  // Create indexes
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
    CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
  `);

  console.log('[DB] Schema initialized');
}

// ============================================================================
// Session Operations
// ============================================================================

export interface Session {
  id: string;
  userId: string;
  title: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  lastActivityAt: string;
}

export function createSession(session: {
  id: string;
  userId: string;
  title: string;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
  lastActivityAt?: string;
}): Session {
  const db = getDb();
  const now = new Date().toISOString();

  const stmt = db.prepare(`
    INSERT INTO sessions (id, user_id, title, status, created_at, updated_at, last_activity_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    session.id,
    session.userId,
    session.title,
    session.status || 'ACTIVE',
    session.createdAt || now,
    session.updatedAt || now,
    session.lastActivityAt || now
  );

  console.log('[DB] Session created:', session.id);
  return getSession(session.id)!;
}

export function getSession(sessionId: string): Session | null {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT
      id,
      user_id as userId,
      title,
      status,
      created_at as createdAt,
      updated_at as updatedAt,
      last_activity_at as lastActivityAt
    FROM sessions
    WHERE id = ?
  `);

  const session = stmt.get(sessionId) as Session | undefined;
  return session || null;
}

export function getUserSessions(userId: string, limit: number = 50): Session[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT
      id,
      user_id as userId,
      title,
      status,
      created_at as createdAt,
      updated_at as updatedAt,
      last_activity_at as lastActivityAt
    FROM sessions
    WHERE user_id = ?
    ORDER BY created_at DESC
    LIMIT ?
  `);

  return stmt.all(userId, limit) as Session[];
}

export function updateSession(sessionId: string, updates: Partial<Session>): boolean {
  const db = getDb();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.title !== undefined) {
    fields.push('title = ?');
    values.push(updates.title);
  }
  if (updates.status !== undefined) {
    fields.push('status = ?');
    values.push(updates.status);
  }
  if (updates.lastActivityAt !== undefined) {
    fields.push('last_activity_at = ?');
    values.push(updates.lastActivityAt);
  }

  fields.push('updated_at = ?');
  values.push(new Date().toISOString());
  values.push(sessionId);

  const stmt = db.prepare(`
    UPDATE sessions
    SET ${fields.join(', ')}
    WHERE id = ?
  `);

  const result = stmt.run(...values);
  return result.changes > 0;
}

export function deleteSession(sessionId: string): boolean {
  const db = getDb();
  const stmt = db.prepare('DELETE FROM sessions WHERE id = ?');
  const result = stmt.run(sessionId);
  console.log('[DB] Session deleted:', sessionId);
  return result.changes > 0;
}

// ============================================================================
// Message Operations
// ============================================================================

export interface Message {
  id: string;
  sessionId: string;
  role: string;
  content: string;
  type: string;
  streaming: boolean;
  error?: string | null;
  metadata?: any;
  inputTokens?: number | null;
  outputTokens?: number | null;
  createdAt: string;
  updatedAt: string;
}

export function createMessage(message: {
  id: string;
  sessionId: string;
  role: string;
  content: string;
  type?: string;
  streaming?: boolean;
  error?: string;
  metadata?: any;
  inputTokens?: number;
  outputTokens?: number;
  createdAt?: string;
  updatedAt?: string;
}): Message {
  const db = getDb();
  const now = new Date().toISOString();

  const stmt = db.prepare(`
    INSERT INTO messages (
      id, session_id, role, content, type, streaming,
      error, metadata, input_tokens, output_tokens,
      created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    message.id,
    message.sessionId,
    message.role,
    message.content,
    message.type || 'TEXT',
    message.streaming ? 1 : 0,
    message.error || null,
    message.metadata ? JSON.stringify(message.metadata) : null,
    message.inputTokens || null,
    message.outputTokens || null,
    message.createdAt || now,
    message.updatedAt || now
  );

  console.log('[DB] Message created:', message.id);
  return getMessage(message.id)!;
}

export function getMessage(messageId: string): Message | null {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT
      id,
      session_id as sessionId,
      role,
      content,
      type,
      streaming,
      error,
      metadata,
      input_tokens as inputTokens,
      output_tokens as outputTokens,
      created_at as createdAt,
      updated_at as updatedAt
    FROM messages
    WHERE id = ?
  `);

  const row = stmt.get(messageId) as any;
  if (!row) return null;

  return {
    ...row,
    streaming: row.streaming === 1,
    metadata: row.metadata ? JSON.parse(row.metadata) : null,
  };
}

export function getSessionMessages(sessionId: string): Message[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT
      id,
      session_id as sessionId,
      role,
      content,
      type,
      streaming,
      error,
      metadata,
      input_tokens as inputTokens,
      output_tokens as outputTokens,
      created_at as createdAt,
      updated_at as updatedAt
    FROM messages
    WHERE session_id = ?
    ORDER BY created_at ASC
  `);

  const rows = stmt.all(sessionId) as any[];
  return rows.map(row => ({
    ...row,
    streaming: row.streaming === 1,
    metadata: row.metadata ? JSON.parse(row.metadata) : null,
  }));
}

export function updateMessage(messageId: string, updates: Partial<Message>): boolean {
  const db = getDb();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.content !== undefined) {
    fields.push('content = ?');
    values.push(updates.content);
  }
  if (updates.type !== undefined) {
    fields.push('type = ?');
    values.push(updates.type);
  }
  if (updates.streaming !== undefined) {
    fields.push('streaming = ?');
    values.push(updates.streaming ? 1 : 0);
  }
  if (updates.error !== undefined) {
    fields.push('error = ?');
    values.push(updates.error);
  }
  if (updates.metadata !== undefined) {
    fields.push('metadata = ?');
    values.push(JSON.stringify(updates.metadata));
  }
  if (updates.inputTokens !== undefined) {
    fields.push('input_tokens = ?');
    values.push(updates.inputTokens);
  }
  if (updates.outputTokens !== undefined) {
    fields.push('output_tokens = ?');
    values.push(updates.outputTokens);
  }

  if (fields.length === 0) return false;

  fields.push('updated_at = ?');
  values.push(new Date().toISOString());
  values.push(messageId);

  const stmt = db.prepare(`
    UPDATE messages
    SET ${fields.join(', ')}
    WHERE id = ?
  `);

  const result = stmt.run(...values);
  return result.changes > 0;
}

export function upsertMessage(message: {
  id: string;
  sessionId: string;
  role: string;
  content: string;
  type?: string;
  streaming?: boolean;
  error?: string;
  metadata?: any;
  inputTokens?: number;
  outputTokens?: number;
}): { created: boolean; message: Message } {
  const existing = getMessage(message.id);

  if (existing) {
    // Update existing
    updateMessage(message.id, message);
    return { created: false, message: getMessage(message.id)! };
  } else {
    // Create new
    const created = createMessage(message);
    return { created: true, message: created };
  }
}

export function deleteMessage(messageId: string): boolean {
  const db = getDb();
  const stmt = db.prepare('DELETE FROM messages WHERE id = ?');
  const result = stmt.run(messageId);
  return result.changes > 0;
}

// ============================================================================
// Utility Functions
// ============================================================================

export function clearAllData() {
  const db = getDb();
  db.exec('DELETE FROM messages');
  db.exec('DELETE FROM sessions');
  console.log('[DB] All data cleared');
}

export function closeDb() {
  if (db) {
    db.close();
    db = null;
    console.log('[DB] Database connection closed');
  }
}
