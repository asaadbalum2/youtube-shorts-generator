#!/usr/bin/env python3
"""
Quick script to exchange an authorization code for a refresh token
Use this if you already have the code from the browser URL
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Config

def exchange_code(code: str):
    """Exchange authorization code for refresh token"""
    client_id = Config.YOUTUBE_CLIENT_ID
    client_secret = Config.YOUTUBE_CLIENT_SECRET
    redirect_uri = "http://localhost:8080"  # Must match what was used in auth URL
    
    if not client_id or not client_secret:
        print("❌ Error: YouTube credentials not configured!")
        return None
    
    print("="*70)
    print("🔄 EXCHANGING CODE FOR TOKEN")
    print("="*70)
    print()
    print(f"Code: {code[:30]}...")
    print()
    print("Exchanging with Google...")
    
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': code.strip(),
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
            print()
            print("Full response:", token_data)
            
            if 'redirect_uri_mismatch' in str(token_data):
                print()
                print("⚠️  Redirect URI mismatch!")
                print(f"Make sure you added '{redirect_uri}' to Google Cloud Console:")
                print("https://console.cloud.google.com/apis/credentials")
            
            return None
        
        refresh_token = token_data.get('refresh_token')
        
        if not refresh_token:
            print("❌ No refresh token received!")
            print("Response:", token_data)
            print()
            print("⚠️  This might mean:")
            print("1. The code was already used (codes can only be used once)")
            print("2. You need to get a fresh code with 'prompt=consent'")
            return None
        
        print("✅ Success! Refresh token generated!")
        print()
        print("="*70)
        print("✅ NEW REFRESH TOKEN")
        print("="*70)
        print()
        print("Copy this token:")
        print()
        print(f"{refresh_token}")
        print()
        print("Next steps:")
        print("1. In Replit, click Secrets (🔒 icon)")
        print("2. Find YOUTUBE_REFRESH_TOKEN")
        print("3. Update it with the token above")
        print("4. Restart your app")
        print()
        print("="*70)
        
        return refresh_token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        print("Paste your authorization code here:")
        code = input("Code: ").strip()
    
    if not code:
        print("❌ No code provided!")
        sys.exit(1)
    
    exchange_code(code)

