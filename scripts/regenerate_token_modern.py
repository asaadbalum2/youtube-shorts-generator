#!/usr/bin/env python3
"""
Modern token regeneration using localhost callback (OOB flow is blocked by Google)
This works with Replit - creates a temporary web server to receive the OAuth callback
"""
import os
import sys
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Config

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth redirect callback"""
    auth_code = None
    error = None
    
    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            OAuthCallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authorization Successful</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding: 50px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 predictive                            color: white;
                        }
                        .container {
                            background: white;
                            color: #333;
                            padding: 40px;
                            border-radius: 15px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                            max-width: 500px;
                            margin: 0 auto;
                        }
                        h1 { color: #667eea; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✅ Authorization Successful!</h1>
                        <p>You can close this window now.</p>
                        <p>Return to the terminal to complete the token generation.</p>
                    </div>
                </body>
                </html>
            """)
        elif 'error' in params:
            OAuthCallbackHandler.error = params['error'][0]
            error_desc = params.get('error_description', [''])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authorization Failed</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding: 50px;
                            background: #f44336;
                            color: white;
                        }}
                        .container {{
                            background: white;
                            color: #333;
                            padding: 40px;
                            border-radius: 15px;
                            max-width: 500px;
                            margin: 0 auto;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>❌ Authorization Failed</h1>
                        <p>Error: {OAuthCallbackHandler.error}</p>
                        <p>{error_desc}</p>
                        <p>Please check the terminal for instructions.</p>
                    </div>
                </body>
                </html>
            """.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Invalid request")
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass

def regenerate_token_modern():
    """Regenerate token using localhost callback (modern method)"""
    client_id = Config.YOUTUBE_CLIENT_ID
    client_secret = Config.YOUTUBE_CLIENT_SECRET
    redirect_uri = "http://localhost:8080"
    
    if not client_id or not client_secret:
        print("❌ Error: YouTube credentials not configured!")
        return None
    
    print("="*70)
    print("🔄 MODERN TOKEN REGENERATION")
    print("="*70)
    print()
    print("⚠️  Note: Google has blocked the old OOB flow.")
    print("We're using localhost callback instead.")
    print()
    
    # Start local server to receive callback
    print("Step 1: Starting local server to receive callback...")
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("✅ Server started on http://localhost:8080")
    print()
    
    # Build authorization URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    print("Step 2: Opening browser for authorization...")
    print()
    print("⚠️  IMPORTANT: You must add this redirect URI to Google Cloud Console:")
    print(f"   {redirect_uri}")
    print()
    print("If you haven't done this yet:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click your OAuth client ID")
    print("3. Under 'Authorized redirect URIs', add: http://localhost:8080")
    print("4. Click SAVE")
    print("5. Wait 2 minutes, then try again")
    print()
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened!")
    except:
        print("⚠️  Could not auto-open browser. Please copy this URL:")
        print()
        print(auth_url)
        print()
    
    print()
    print("Step 3: Waiting for authorization...")
    print("After you authorize, you'll be redirected back here automatically.")
    print("The browser window will show a success message - you can close it.")
    print()
    
    # Wait for authorization code (max 5 minutes)
    timeout = 300
    start_time = time.time()
    
    while OAuthCallbackHandler.auth_code is None and OAuthCallbackHandler.error is None:
        if time.time() - start_time > timeout:
            print("⏱️  Timeout waiting for authorization")
            server.shutdown()
            return None
        time.sleep(0.5)
    
    # Clean up server
    server.shutdown()
    
    if OAuthCallbackHandler.error:
        print(f"❌ Authorization error: {OAuthCallbackHandler.error}")
        print()
        print("Common causes:")
        print("1. Redirect URI not added to Google Cloud Console")
        print("2. OAuth consent screen not configured")
        print("3. App not published or user not added as test user")
        return None
    
    auth_code = OAuthCallbackHandler.auth_code
    
    if not auth_code:
        print("❌ No authorization code received")
        return None
    
    print("✅ Authorization code received!")
    print()
    print("Step 4: Exchanging code for tokens...")
    
    # Exchange code for tokens
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if 'error' in token_data:
            error = token_data.get('error_description', token_data.get('error'))
            print(f"❌ Error: {error}")
            
            if 'redirect_uri_mismatch' in str(token_data):
                print()
                print("⚠️  Redirect URI mismatch!")
                print(f"Make sure you added '{redirect_uri}' to Google Cloud Console.")
            return None
        
        refresh_token = token_data.get('refresh_token')
        
        if not refresh_token:
            print("❌ No refresh token received!")
            print("⚠️  Make sure you granted all permissions and 'prompt=consent' is set.")
            return None
        
        print("✅ Token generated successfully!")
        return refresh_token
        
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    token = regenerate_token_modern()
    
    if token:
        print()
        print("="*70)
        print("✅ SUCCESS! NEW REFRESH TOKEN GENERATED")
        print("="*70)
        print()
        print("Copy this token:")
        print()
        print(f"YOUTUBE_REFRESH_TOKEN={token}")
        print()
        print("Next steps:")
        print("1. In Replit, click Secrets (🔒 icon)")
        print("2. Find YOUTUBE_REFRESH_TOKEN")
        print("3. Update it with the token above")
        print("4. Restart your app")
        print()
        print("="*70)
    else:
        print()
        print("="*70)
        print("❌ FAILED TO GENERATE TOKEN")
        print("="*70)
        print()
        print("Common fixes:")
        print("1. Make sure http://localhost:8080 is added to Google Cloud Console")
        print("2. Go to: https://console.cloud.google.com/apis/credentials")
        print("3. Click your OAuth client → Authorized redirect URIs")
        print("4. Add: http://localhost:8080")
        print("5. Wait 2-3 minutes, then try again")
        print()

