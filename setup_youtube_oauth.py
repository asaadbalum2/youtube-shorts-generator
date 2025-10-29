"""
Setup script for YouTube OAuth authentication
Run this once to authenticate with YouTube API
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_youtube_auth():
    """Guide user through YouTube OAuth setup"""
    print("=" * 60)
    print("YouTube OAuth Setup")
    print("=" * 60)
    print()
    print("To use this script, you need:")
    print("1. A Google Cloud Project with YouTube Data API v3 enabled")
    print("2. OAuth 2.0 credentials (Client ID and Secret)")
    print()
    print("Follow these steps:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable 'YouTube Data API v3'")
    print("4. Go to 'Credentials' > 'Create Credentials' > 'OAuth client ID'")
    print("5. Choose 'Desktop app' as application type")
    print("6. Download the credentials JSON file")
    print("7. Save it as 'client_secrets.json' in this directory")
    print()
    
    if not os.path.exists('client_secrets.json'):
        print("ERROR: client_secrets.json not found!")
        print("Please download your OAuth credentials and save as 'client_secrets.json'")
        return None
    
    print("Starting OAuth flow...")
    print("A browser window will open. Please authorize the application.")
    print()
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    # Test API access
    service = build('youtube', 'v3', credentials=creds)
    request = service.channels().list(part='id,snippet', mine=True)
    response = request.execute()
    
    if response.get('items'):
        channel = response['items'][0]
        print()
        print("=" * 60)
        print("SUCCESS! Authentication complete.")
        print("=" * 60)
        print(f"Channel: {channel['snippet']['title']}")
        print(f"Channel ID: {channel['id']}")
        print()
        print("Add these to your .env file:")
        print(f"YOUTUBE_CHANNEL_ID={channel['id']}")
        print()
        print("The token.pickle file contains your access credentials.")
        print("Keep it secure and don't share it!")
    else:
        print("ERROR: Could not retrieve channel information")
    
    return creds

if __name__ == "__main__":
    setup_youtube_auth()

