"""
Auto-recovery helper for YouTube token issues
Detects token expiration and guides user through fix
"""
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from core.config import Config

def check_token_health():
    """Check if YouTube token is healthy and can be used"""
    refresh_token = Config.YOUTUBE_REFRESH_TOKEN
    client_id = Config.YOUTUBE_CLIENT_ID
    client_secret = Config.YOUTUBE_CLIENT_SECRET
    
    if not all([refresh_token, client_id, client_secret]):
        return False, "Missing credentials in config"
    
    try:
        # Try to create credentials and refresh
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Try to refresh
        creds.refresh(Request())
        
        # If successful, try a simple API call to verify it works
        from googleapiclient.discovery import build
        service = build('youtube', 'v3', credentials=creds)
        
        # Try a lightweight API call (this doesn't require special permissions)
        request = service.channels().list(part='id', mine=True)
        request.execute()  # This will fail if token is truly invalid
        
        return True, "Token is valid"
    
    except Exception as e:
        error_str = str(e)
        if 'invalid_grant' in error_str.lower():
            return False, "Refresh token is invalid or expired - needs regeneration"
        elif '401' in error_str or 'unauthorized' in error_str.lower():
            return False, f"Authentication failed: {error_str[:100]}"
        else:
            return False, f"Token check failed: {error_str[:100]}"

def generate_regeneration_instructions():
    """Generate instructions for token regeneration"""
    instructions = """
    ⚠️  YouTube Token Needs Regeneration
    =====================================
    
    Your YouTube refresh token is invalid or expired. Follow these steps:
    
    1. Go to: https://console.cloud.google.com/
    2. Make sure you're in the correct project
    3. Go to: APIs & Services → Credentials
    4. Note your OAuth 2.0 Client ID and Client Secret
    
    5. In Replit, check if manual_auth.py exists:
       python manual_auth.py
   
    6. Follow the prompts to generate a new refresh token
    
    7. Update the YOUTUBE_REFRESH_TOKEN in Replit Secrets
    
    The app will automatically retry once you update the token.
    """
    return instructions

