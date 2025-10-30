"""
Automatic YouTube token expiration detection and recovery
Attempts to regenerate token automatically when expired
"""
import os
import sys
import subprocess
import webbrowser
import requests
from typing import Optional
from core.config import Config

def detect_token_expiration(error_message: str) -> bool:
    """Detect if an error indicates token expiration"""
    error_lower = error_message.lower()
    return any(keyword in error_lower for keyword in [
        '401', 'unauthorized', 'invalid_grant', 'expired', 
        'token', 'authentication', 'credentials'
    ])

def regenerate_token_auto() -> Optional[str]:
    """
    Attempt to automatically regenerate YouTube token
    Returns new refresh token if successful, None otherwise
    """
    print("\n" + "="*70)
    print("🔄 AUTOMATIC TOKEN REGENERATION")
    print("="*70)
    print()
    
    client_id = Config.YOUTUBE_CLIENT_ID
    client_secret = Config.YOUTUBE_CLIENT_SECRET
    
    if not client_id or not client_secret:
        print("❌ Error: YouTube credentials not configured!")
        return None
    
    # Build authorization URL - Use localhost redirect (OOB flow is blocked by Google)
    redirect_uri = "http://localhost:8080"
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    print("Step 1: Opening browser for authorization...")
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened! If it didn't open, copy this URL:")
    except:
        print("⚠️ Could not auto-open browser. Please copy this URL manually:")
    
    print()
    print(auth_url)
    print()
    print("="*70)
    print("Step 2: After authorizing, you'll see a code. Paste it below:")
    print("="*70)
    print()
    
    # Get authorization code from user
    auth_code = input("Authorization code: ").strip()
    
    if not auth_code:
        print("❌ No code provided!")
        return None
    
    print()
    print("Step 3: Exchanging code for tokens...")
    
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,  # Must match authorization URL!
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
            print("⚠️ Make sure 'prompt=consent' was in the URL and you granted all permissions.")
            return None
        
        print("✅ Token generated successfully!")
        return refresh_token
        
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        return None

def update_replit_secret(token: str) -> bool:
    """
    Attempt to update Replit secret programmatically
    Returns True if successful, False otherwise
    """
    # Check if we're in Replit
    if not os.getenv('REPL_SLUG'):
        return False
    
    # Try using Replit API if available
    api_token = os.getenv('REPLIT_API_TOKEN')
    if not api_token:
        return False
    
    try:
        import requests
        repl_slug = os.getenv('REPL_SLUG')
        repl_owner = os.getenv('REPL_OWNER')
        
        # Replit GraphQL API for updating secrets
        url = "https://replit.com/graphql"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        mutation = """
        mutation UpdateSecret($input: UpdateSecretInput!) {
            updateSecret(input: $input) {
                success
            }
        }
        """
        
        variables = {
            "input": {
                "replId": f"{repl_owner}/{repl_slug}",
                "key": "YOUTUBE_REFRESH_TOKEN",
                "value": token
            }
        }
        
        response = requests.post(url, json={
            "query": mutation,
            "variables": variables
        }, headers=headers)
        
        if response.json().get('data', {}).get('updateSecret', {}).get('success'):
            print("✅ Successfully updated Replit secret!")
            return True
        
    except Exception as e:
        print(f"⚠️ Could not auto-update Replit secret: {e}")
    
    return False

def auto_recover_token() -> bool:
    """
    Main auto-recovery function
    Attempts to regenerate token and update it
    Returns True if successful
    """
    new_token = regenerate_token_auto()
    
    if not new_token:
        return False
    
    print()
    print("="*70)
    print("✅ TOKEN RECOVERY SUCCESSFUL")
    print("="*70)
    print()
    print(f"New refresh token: {new_token[:20]}...{new_token[-10:]}")
    print()
    
    # Try to auto-update Replit secret
    if update_replit_secret(new_token):
        print("✅ Token updated automatically in Replit!")
        print("⚠️ Please restart your app for changes to take effect.")
        return True
    
    # Fallback: print instructions
    print("⚠️ Could not auto-update Replit secret.")
    print()
    print("Manual steps:")
    print("1. Copy this token:")
    print(f"   {new_token}")
    print()
    print("2. In Replit, go to Secrets (🔒 icon)")
    print("3. Find YOUTUBE_REFRESH_TOKEN")
    print("4. Update it with the token above")
    print("5. Restart your app")
    print()
    print("="*70)
    
    return False

