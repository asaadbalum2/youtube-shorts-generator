#!/usr/bin/env python3
"""
Alternative token regeneration using localhost redirect (easier for Google Cloud setup)
"""
import os
import sys
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Config

class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth redirect"""
    auth_code = None
    
    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            OAuthHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>✅ Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <p>The token generation will continue automatically.</p>
                </body>
                </html>
            """)
        else:
            error = params.get('error', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please check the terminal for instructions.</p>
                </body>
                </html>
            """.encode())
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass

def regenerate_with_localhost():
    """Regenerate token using localhost redirect"""
    client_id = Config.YOUTUBE_CLIENT_ID
    client_secret = Config.YOUTUBE_CLIENT_SECRET
    
    if not client_id or not client_secret:
        print("❌ Error: YouTube credentials not configured!")
        return None
    
    # Start local server
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("="*70)
    print("🔄 TOKEN REGENERATION (Localhost Method)")
    print("="*70)
    print()
    print("Using localhost redirect - this should work if http://localhost is")
    print("already configured in your Google Cloud OAuth client.")
    print()
    
    # Build authorization URL with localhost redirect
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        "redirect_uri=http://localhost:8080&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    print("Step 1: Opening browser...")
    print()
    print("If browser doesn't open, copy this URL:")
    print(auth_url)
    print()
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened!")
    except:
        print("⚠️ Could not auto-open browser. Please copy the URL above manually.")
    
    print()
    print("Step 2: Authorize in the browser")
    print("After you click 'Allow', you'll be redirected back here automatically.")
    print("Waiting for authorization...")
    print()
    
    # Wait for authorization code (max 5 minutes)
    import time
    timeout = 300
    start_time = time.time()
    
    while OAuthHandler.auth_code is None:
        if time.time() - start_time > timeout:
            print("⏱️ Timeout waiting for authorization")
            server.shutdown()
            return None
        time.sleep(1)
    
    auth_code = OAuthHandler.auth_code
    server.shutdown()
    
    print("✅ Authorization code received!")
    print()
    print("Step 3: Exchanging code for tokens...")
    
    # Exchange code for tokens
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': 'http://localhost:8080',
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if 'error' in token_data:
            error = token_data.get('error_description', token_data.get('error'))
            print(f"❌ Error: {error}")
            return None
        
        refresh_token = token_data.get('refresh_token')
        
        if not refresh_token:
            print("❌ No refresh token received!")
            print("⚠️ Make sure you granted all permissions.")
            return None
        
        print("✅ Token generated successfully!")
        return refresh_token
        
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        return None

if __name__ == "__main__":
    token = regenerate_with_localhost()
    
    if token:
        print()
        print("="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print()
        print("Your new refresh token:")
        print(f"YOUTUBE_REFRESH_TOKEN={token}")
        print()
        print("Next steps:")
        print("1. Copy the token above")
        print("2. In Replit, go to Secrets (🔒 icon)")
        print("3. Update YOUTUBE_REFRESH_TOKEN with the new token")
        print("4. Restart your app")
        print()
    else:
        print()
        print("❌ Failed to generate token")
        print()
        print("If localhost redirect didn't work, you need to:")
        print("1. Go to Google Cloud Console → Credentials")
        print("2. Find your OAuth client")
        print("3. Add redirect URI: http://localhost:8080")
        print("4. Try again")

