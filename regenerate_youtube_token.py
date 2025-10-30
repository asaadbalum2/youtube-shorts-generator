"""
Helper script to regenerate YouTube refresh token
Run this in Replit when your token expires
"""
import os
import json
import requests

print("=" * 70)
print("YouTube Token Regenerator")
print("=" * 70)
print()

# Get credentials from environment (Replit Secrets)
client_id = os.getenv('YOUTUBE_CLIENT_ID', '')
client_secret = os.getenv('YOUTUBE_CLIENT_SECRET', '')

if not client_id or not client_secret:
    print("❌ Error: YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET not found in environment!")
    print("   Make sure they're set in Replit Secrets.")
    exit(1)

# Build authorization URL with all required parameters
auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    "redirect_uri=urn:ietf:wg:oauth:2.0:oob&"
    "response_type=code&"
    "scope=https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube&"
    "access_type=offline&"
    "prompt=consent"
)

print("STEP 1: Copy and paste this URL into your browser:")
print()
print(auth_url)
print()
print("=" * 70)
print("STEP 2: Authorize and copy the code")
print("=" * 70)
print()
print("After clicking 'Allow', you'll see a page with a code.")
print("Copy that code and paste it below:")
print()

auth_code = input("Paste the authorization code here: ").strip()

if not auth_code:
    print("❌ No code provided!")
    exit(1)

print()
print("Exchanging code for tokens...")

try:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    token_data = response.json()
    
    if 'error' in token_data:
        raise Exception(f"Token exchange failed: {token_data.get('error_description', token_data.get('error'))}")
    
    refresh_token = token_data.get('refresh_token')
    access_token = token_data.get('access_token')
    
    if not refresh_token:
        raise Exception("No refresh token received. Make sure 'prompt=consent' is in the URL.")
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! Here's your new refresh token:")
    print("=" * 70)
    print()
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the refresh token above")
    print("2. In Replit, go to Secrets (🔒 icon)")
    print("3. Find YOUTUBE_REFRESH_TOKEN")
    print("4. Update it with the new token")
    print("5. Restart your app")
    print()
    print("The app will automatically use the new token!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

