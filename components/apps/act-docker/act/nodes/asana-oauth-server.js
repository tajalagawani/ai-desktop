/**
 * Asana OAuth2 Authentication Server
 * 
 * This server handles the OAuth2 flow for Asana API authentication.
 * Run with: node asana-oauth-server.js
 * Then visit: http://localhost:3000/auth
 */

const express = require('express');
const axios = require('axios');
const crypto = require('crypto');
const app = express();

// Your Asana OAuth2 credentials
const CLIENT_ID = '1211165391258955';
const CLIENT_SECRET = '81e00c7028b9c5f19ba7cf072dd1419c';
const REDIRECT_URI = 'http://localhost:3000/callback';
const PORT = process.env.PORT || 3000;

// Store tokens in memory (use a database in production)
let tokens = {
  access_token: null,
  refresh_token: null,
  expires_at: null
};

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Homepage with authentication status
app.get('/', (req, res) => {
  const isAuthenticated = tokens.access_token && new Date() < new Date(tokens.expires_at);
  
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Asana OAuth2 Test</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          max-width: 800px;
          margin: 50px auto;
          padding: 20px;
          background: #f5f5f5;
        }
        .container {
          background: white;
          padding: 30px;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .status {
          padding: 15px;
          margin: 20px 0;
          border-radius: 5px;
          background: ${isAuthenticated ? '#d4edda' : '#f8d7da'};
          color: ${isAuthenticated ? '#155724' : '#721c24'};
        }
        .button {
          display: inline-block;
          padding: 12px 24px;
          background: #ff5858;
          color: white;
          text-decoration: none;
          border-radius: 5px;
          margin: 10px 5px;
        }
        .button:hover { background: #ff4040; }
        .button.secondary {
          background: #6c757d;
        }
        .button.secondary:hover { background: #5a6268; }
        .token-info {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 5px;
          margin: 20px 0;
          word-break: break-all;
        }
        code {
          background: #e9ecef;
          padding: 2px 5px;
          border-radius: 3px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🎯 Asana OAuth2 Authentication</h1>
        
        <div class="status">
          <strong>Status:</strong> ${isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
          ${isAuthenticated ? `<br><strong>Expires:</strong> ${new Date(tokens.expires_at).toLocaleString()}` : ''}
        </div>
        
        <h2>Client Information</h2>
        <div class="token-info">
          <strong>Client ID:</strong> <code>${CLIENT_ID}</code><br>
          <strong>Redirect URI:</strong> <code>${REDIRECT_URI}</code>
        </div>
        
        ${isAuthenticated ? `
          <h2>Current Token</h2>
          <div class="token-info">
            <strong>Access Token:</strong> <code>${tokens.access_token.substring(0, 20)}...</code><br>
            <strong>Refresh Token:</strong> <code>${tokens.refresh_token ? tokens.refresh_token.substring(0, 20) + '...' : 'N/A'}</code>
          </div>
          
          <a href="/test-api" class="button">Test API Call</a>
          <a href="/refresh" class="button secondary">Refresh Token</a>
          <a href="/logout" class="button secondary">Logout</a>
        ` : `
          <p>Click the button below to authenticate with Asana:</p>
          <a href="/auth" class="button">Connect to Asana</a>
        `}
        
        <h2>API Endpoints</h2>
        <ul>
          <li><code>GET /auth</code> - Start OAuth flow</li>
          <li><code>GET /callback</code> - OAuth callback handler</li>
          <li><code>GET /refresh</code> - Refresh access token</li>
          <li><code>GET /test-api</code> - Test Asana API call</li>
          <li><code>GET /token</code> - Get current token (JSON)</li>
          <li><code>GET /logout</code> - Clear stored tokens</li>
        </ul>
      </div>
    </body>
    </html>
  `);
});

// Step 1: Initiate OAuth flow
app.get('/auth', (req, res) => {
  const state = crypto.randomBytes(16).toString('hex');
  
  // In production, store state in session for validation
  const authUrl = 'https://app.asana.com/oauth2/authorize?' +
    `response_type=code&` +
    `client_id=${CLIENT_ID}&` +
    `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
    `state=${state}`;
  
  console.log('🚀 Redirecting to Asana for authorization...');
  res.redirect(authUrl);
});

// Step 2: Handle OAuth callback
app.get('/callback', async (req, res) => {
  const { code, state, error } = req.query;
  
  if (error) {
    return res.status(400).send(`
      <h1>Authorization Failed</h1>
      <p>Error: ${error}</p>
      <a href="/">Go Back</a>
    `);
  }
  
  if (!code) {
    return res.status(400).send('No authorization code received');
  }
  
  try {
    console.log('🔄 Exchanging code for access token...');
    
    const tokenResponse = await axios.post('https://app.asana.com/oauth2/token', {
      grant_type: 'authorization_code',
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code: code,
      redirect_uri: REDIRECT_URI
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    const { access_token, refresh_token, expires_in } = tokenResponse.data;
    
    // Store tokens
    tokens = {
      access_token,
      refresh_token,
      expires_at: new Date(Date.now() + expires_in * 1000)
    };
    
    console.log('✅ Successfully authenticated with Asana!');
    console.log(`📝 Access Token: ${access_token.substring(0, 20)}...`);
    
    res.send(`
      <html>
      <head>
        <title>Authentication Successful</title>
        <style>
          body { font-family: sans-serif; padding: 40px; text-align: center; }
          .success { color: green; }
          .token { background: #f0f0f0; padding: 20px; margin: 20px; border-radius: 5px; word-break: break-all; }
        </style>
      </head>
      <body>
        <h1 class="success">✅ Successfully Connected to Asana!</h1>
        <div class="token">
          <h3>Access Token (truncated):</h3>
          <code>${access_token.substring(0, 40)}...</code>
        </div>
        <p><a href="/test-api">Test API Call</a> | <a href="/">Back to Home</a></p>
      </body>
      </html>
    `);
    
  } catch (error) {
    console.error('❌ Error exchanging code for token:', error.response?.data || error.message);
    res.status(500).send(`
      <h1>Authentication Failed</h1>
      <pre>${JSON.stringify(error.response?.data || error.message, null, 2)}</pre>
      <a href="/">Try Again</a>
    `);
  }
});

// Refresh access token
app.get('/refresh', async (req, res) => {
  if (!tokens.refresh_token) {
    return res.status(400).json({ error: 'No refresh token available' });
  }
  
  try {
    console.log('🔄 Refreshing access token...');
    
    const response = await axios.post('https://app.asana.com/oauth2/token', {
      grant_type: 'refresh_token',
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: tokens.refresh_token
    });
    
    const { access_token, expires_in } = response.data;
    
    tokens.access_token = access_token;
    tokens.expires_at = new Date(Date.now() + expires_in * 1000);
    
    console.log('✅ Token refreshed successfully');
    res.redirect('/');
    
  } catch (error) {
    console.error('❌ Error refreshing token:', error.response?.data || error.message);
    res.status(500).json({ error: error.response?.data || error.message });
  }
});

// Test API call
app.get('/test-api', async (req, res) => {
  if (!tokens.access_token) {
    return res.status(401).send('Not authenticated. <a href="/auth">Login first</a>');
  }
  
  try {
    // Get current user info
    const userResponse = await axios.get('https://app.asana.com/api/1.0/users/me', {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`
      }
    });
    
    // Get workspaces
    const workspacesResponse = await axios.get('https://app.asana.com/api/1.0/workspaces', {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`
      }
    });
    
    res.send(`
      <html>
      <head>
        <title>Asana API Test</title>
        <style>
          body { font-family: sans-serif; padding: 40px; }
          .result { background: #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 5px; }
          pre { white-space: pre-wrap; }
        </style>
      </head>
      <body>
        <h1>✅ API Test Successful!</h1>
        
        <div class="result">
          <h2>Current User:</h2>
          <pre>${JSON.stringify(userResponse.data.data, null, 2)}</pre>
        </div>
        
        <div class="result">
          <h2>Workspaces:</h2>
          <pre>${JSON.stringify(workspacesResponse.data.data, null, 2)}</pre>
        </div>
        
        <p><a href="/">Back to Home</a></p>
      </body>
      </html>
    `);
    
  } catch (error) {
    console.error('❌ API call failed:', error.response?.data || error.message);
    res.status(500).send(`
      <h1>API Call Failed</h1>
      <pre>${JSON.stringify(error.response?.data || error.message, null, 2)}</pre>
      <a href="/">Back</a>
    `);
  }
});

// Get current token (JSON endpoint)
app.get('/token', (req, res) => {
  if (!tokens.access_token) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  
  res.json({
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    expires_at: tokens.expires_at,
    is_valid: new Date() < new Date(tokens.expires_at)
  });
});

// Logout
app.get('/logout', (req, res) => {
  tokens = {
    access_token: null,
    refresh_token: null,
    expires_at: null
  };
  console.log('🔒 Logged out successfully');
  res.redirect('/');
});

// Start server
app.listen(PORT, () => {
  console.log('🚀 Asana OAuth2 Server Started');
  console.log(`📍 Visit: http://localhost:${PORT}`);
  console.log(`🔗 Start OAuth: http://localhost:${PORT}/auth`);
  console.log('');
  console.log('Client ID:', CLIENT_ID);
  console.log('Redirect URI:', REDIRECT_URI);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down server...');
  process.exit(0);
});