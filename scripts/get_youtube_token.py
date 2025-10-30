"""
One-time YouTube OAuth token generator
Run this locally (just once) to get tokens for hosting
"""
import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def extract_token_info():
    """
    Extract refresh token and channel ID from OAuth flow
    This is a one-time setup - run locally, copy tokens to hosting
    """
    print("=" * 60)
    print("YouTube OAuth Token Generator")
    print("=" * 60)
    print()
    
    # Check for client_secrets.json
    if not os.path.exists('client_secrets.json'):
        print("❌ ERROR: client_secrets.json not found!")
        print()
        print("To get this file:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. APIs & Services → Credentials")
        print("3. Create OAuth Client ID (Desktop app)")
        print("4. Download JSON → save as 'client_secrets.json'")
        return None
    
    print("Starting OAuth flow...")
    print()
    
    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', SCOPES)
    
    # Get authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    print("=" * 60)
    print("STEP 1: Open this URL in your browser:")
    print("=" * 60)
    print(authorization_url)
    print()
    print("=" * 60)
    print("After authorizing, you'll be redirected to a page.")
    print("Copy the ENTIRE URL from your browser's address bar.")
    print("Paste it here when ready.")
    print("=" * 60)
    print()
    
    # Wait for user to paste the redirect URL
    redirect_response = input("Paste the redirect URL here: ").strip()
    
    # Extract the code from the redirect URL
    flow.fetch_token(authorization_response=redirect_response)
    creds = flow.credentials
    
    # Get channel ID
    service = build('youtube', 'v3', credentials=creds)
    request = service.channels().list(part='id,snippet', mine=True)
    response = request.execute()
    
    if not response.get('items'):
        print("❌ ERROR: Could not retrieve channel information")
        return None
    
    channel = response['items'][0]
    channel_id = channel['id']
    channel_name = channel['snippet']['title']
    
    # Extract refresh token
    refresh_token = creds.refresh_token if creds.refresh_token else None
    
    # Read client ID and secret from file
    with open('client_secrets.json', 'r') as f:
        secrets = json.load(f)
        client_data = secrets.get('installed', secrets.get('web', {}))
        client_id = client_data.get('client_id', '')
        client_secret = client_data.get('client_secret', '')
    
    # Display results
    print()
    print("=" * 60)
    print("✅ SUCCESS! Copy these to your hosting environment:")
    print("=" * 60)
    print()
    print("Add these to your hosting platform's environment variables:")
    print()
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print(f"YOUTUBE_CHANNEL_ID={channel_id}")
    print()
    print("Channel Info:")
    print(f"  Name: {channel_name}")
    print(f"  ID: {channel_id}")
    print()
    print("=" * 60)
    print()
    print("📋 Instructions:")
    print("1. Copy the 4 variables above")
    print("2. Go to your hosting platform (Railway/Replit/etc.)")
    print("3. Add them as environment variables")
    print("4. Your app will now be able to upload videos!")
    print()
    print("⚠️  Keep these tokens secure - don't share them!")
    print()
    
    # Also save to file for easy copy-paste
    output = {
        'YOUTUBE_CLIENT_ID': client_id,
        'YOUTUBE_CLIENT_SECRET': client_secret,
        'YOUTUBE_REFRESH_TOKEN': refresh_token,
        'YOUTUBE_CHANNEL_ID': channel_id
    }
    
    with open('youtube_tokens.txt', 'w') as f:
        f.write("# Copy these to your hosting platform:\n\n")
        for key, value in output.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Also saved to 'youtube_tokens.txt' for easy reference")
    print()
    
    # Optionally save token.pickle for local use
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    print("✅ Saved token.pickle (for local testing if needed)")
    print()
    
    return output

if __name__ == "__main__":
    result = extract_token_info()
    if not result:
        exit(1)

