#!/usr/bin/env python3
"""
Automated Asana OAuth Token Retrieval
This script attempts to get an Asana token using various methods
"""

import json
import webbrowser
import urllib.parse
import http.server
import socketserver
import threading
import time
import requests
import sys
from urllib.parse import parse_qs, urlparse

CLIENT_ID = '1211165391258955'
CLIENT_SECRET = '81e00c7028b9c5f19ba7cf072dd1419c'
PORT = 9999
REDIRECT_URI = f'http://localhost:{PORT}/callback'

class TokenHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/callback':
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                code = params['code'][0]
                print(f"\n✅ Authorization code received: {code[:20]}...")
                
                # Exchange code for token
                try:
                    response = requests.post('https://app.asana.com/oauth2/token', json={
                        'grant_type': 'authorization_code',
                        'client_id': CLIENT_ID,
                        'client_secret': CLIENT_SECRET,
                        'code': code,
                        'redirect_uri': REDIRECT_URI
                    })
                    
                    if response.status_code == 200:
                        tokens = response.json()
                        access_token = tokens.get('access_token')
                        refresh_token = tokens.get('refresh_token')
                        
                        # Save to file
                        with open('asana_tokens.json', 'w') as f:
                            json.dump(tokens, f, indent=2)
                        
                        # Create HTML response
                        html = f"""
                        <html>
                        <head>
                            <title>Asana Token Retrieved!</title>
                            <style>
                                body {{ font-family: sans-serif; padding: 40px; }}
                                .token {{ 
                                    background: #f0f0f0; 
                                    padding: 20px; 
                                    margin: 20px 0;
                                    word-break: break-all;
                                    border: 2px solid #4CAF50;
                                    border-radius: 8px;
                                }}
                                h1 {{ color: green; }}
                            </style>
                        </head>
                        <body>
                            <h1>✅ Success! Token Retrieved</h1>
                            <div class="token">
                                <h3>Access Token:</h3>
                                <code>{access_token}</code>
                            </div>
                            <p>Token has been saved to <code>asana_tokens.json</code></p>
                            <p>You can close this window.</p>
                        </body>
                        </html>
                        """
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html.encode())
                        
                        # Print to console
                        print("\n" + "="*80)
                        print("🎉 SUCCESS! ASANA ACCESS TOKEN RETRIEVED")
                        print("="*80)
                        print(f"\nAccess Token:\n{access_token}")
                        if refresh_token:
                            print(f"\nRefresh Token:\n{refresh_token}")
                        print("\n" + "="*80)
                        print("Token saved to: asana_tokens.json")
                        print("="*80)
                        
                        # Update TOML file
                        try:
                            with open('asana-complete-test.toml', 'r') as f:
                                content = f.read()
                            
                            content = content.replace('PASTE_YOUR_ACCESS_TOKEN_HERE', access_token)
                            if refresh_token:
                                content = content.replace('PASTE_YOUR_REFRESH_TOKEN_HERE_IF_AVAILABLE', refresh_token)
                            
                            with open('asana-complete-test.toml', 'w') as f:
                                f.write(content)
                            
                            print("\n✅ Updated asana-complete-test.toml with your token!")
                        except Exception as e:
                            print(f"\n⚠️ Could not update TOML file: {e}")
                            print("Please manually update the ASANA_ACCESS_TOKEN in asana-complete-test.toml")
                        
                        # Shutdown server after 2 seconds
                        threading.Timer(2.0, lambda: sys.exit(0)).start()
                        
                    else:
                        print(f"\n❌ Failed to exchange code: {response.text}")
                        self.send_error(500, f"Token exchange failed: {response.text}")
                        
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    self.send_error(500, str(e))
                    
            else:
                error = params.get('error', ['Unknown error'])[0]
                print(f"\n❌ Authorization failed: {error}")
                self.send_error(400, f"Authorization failed: {error}")
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    print("🚀 Asana OAuth Token Automated Retrieval")
    print("="*50)
    print(f"Client ID: {CLIENT_ID}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print("="*50)
    
    # Start local server
    handler = TokenHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    # Run server in background thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"\n📡 Server listening on port {PORT}")
    
    # Generate auth URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'automated_' + str(int(time.time()))
    }
    
    auth_url = f"https://app.asana.com/oauth2/authorize?{urllib.parse.urlencode(auth_params)}"
    
    print(f"\n🌐 Opening browser for authentication...")
    print(f"📍 If browser doesn't open, visit:\n\n{auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("⏳ Waiting for authorization...")
    print("   Please authorize the app in your browser.")
    print("   Press Ctrl+C to cancel.\n")
    
    try:
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    main()