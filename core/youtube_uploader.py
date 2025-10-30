"""
YouTube upload automation
Handles OAuth authentication and video uploads
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from typing import Dict, Optional
from core.config import Config

# YouTube API scopes
# YouTube API scopes - need both upload and basic read access
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'  # Full access for better compatibility
]

class YouTubeUploader:
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self, retry=False):
        """Authenticate with YouTube API with automatic refresh and recovery"""
        creds = None
        token_file = 'token.pickle'
        
        try:
            # Load existing token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # Check if credentials need refresh
            if creds and not creds.valid:
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Token refresh failed, using refresh token from config: {e}")
                        creds = None  # Force recreation
        
            # If no valid credentials, create new ones using refresh token
            if not creds or not creds.valid:
                if Config.YOUTUBE_REFRESH_TOKEN:
                    try:
                        creds = Credentials(
                            None,  # No initial token needed for refresh
                            refresh_token=Config.YOUTUBE_REFRESH_TOKEN,
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=Config.YOUTUBE_CLIENT_ID,
                            client_secret=Config.YOUTUBE_CLIENT_SECRET
                        )
                        creds.refresh(Request())
                        print("✅ Successfully refreshed YouTube credentials")
                    except Exception as e:
                        if not retry:
                            print(f"⚠️ Refresh token invalid, attempting recovery: {e}")
                            # Refresh token might be expired - log error but continue
                            raise Exception(f"YouTube refresh token expired. Please regenerate: {e}")
                        else:
                            raise
                else:
                    raise Exception("No refresh token available. Cannot authenticate.")
            
            # Save credentials for next time
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            self.credentials = creds
            self.service = build('youtube', 'v3', credentials=creds)
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            if not retry and Config.YOUTUBE_REFRESH_TOKEN:
                # Try once more
                return self._authenticate(retry=True)
            raise
    
    def upload_video(self, video_path: str, title: str, description: str, 
                     tags: list, category_id: str = "22") -> Optional[Dict]:
        """
        Upload video to YouTube
        
        Returns: Video information including URL and ID
        """
        if not self.service:
            raise ValueError("YouTube service not initialized")
        
        try:
            # Prepare metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': tags[:10],  # Max 10 tags
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',  # Set to public for maximum reach
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # YouTube Shorts specific settings
            body['snippet']['tags'].append('shorts')
            body['snippet']['tags'].append('youtubeshorts')
            
            # Insert video
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            insert_request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with retry logic
            response = None
            max_retries = 3
            retry_count = 0
            
            while response is None and retry_count < max_retries:
                try:
                    while response is None:
                        status, response = insert_request.next_chunk()
                        if status:
                            print(f"Upload progress: {int(status.progress() * 100)}%")
                except Exception as upload_error:
                    retry_count += 1
                    error_str = str(upload_error)
                    
                    # Check for authentication errors
                    if '401' in error_str or 'Unauthorized' in error_str or 'invalid_grant' in error_str:
                        print(f"⚠️ Authentication error detected (attempt {retry_count}/{max_retries})...")
                        
                        # Check if it's a permanent token issue
                        if 'invalid_grant' in error_str.lower():
                            print("\n" + "="*70)
                            print("❌ REFRESH TOKEN EXPIRED - REGENERATION REQUIRED")
                            print("="*70)
                            print("\nYour YouTube refresh token has expired.")
                            print("\nTo fix:")
                            print("1. In Replit, check if 'manual_auth.py' exists")
                            print("2. Run: python manual_auth.py (if it exists)")
                            print("3. Follow prompts to get new refresh token")
                            print("4. Update YOUTUBE_REFRESH_TOKEN in Replit Secrets")
                            print("5. Restart the app")
                            print("\nOr manually:")
                            print("  - Go to Google Cloud Console")
                            print("  - Regenerate OAuth token")
                            print("  - Update Replit Secrets")
                            print("\nThe app will automatically retry once token is updated.")
                            print("="*70 + "\n")
                            raise Exception("Refresh token expired. See instructions above to regenerate.")
                        
                        # Try re-authenticating (might be a temporary issue)
                        try:
                            self._authenticate(retry=True)
                            self.service = build('youtube', 'v3', credentials=self.credentials)
                            insert_request = self.service.videos().insert(
                                part=','.join(body.keys()),
                                body=body,
                                media_body=media
                            )
                            response = None
                            print("✅ Re-authenticated, retrying upload...")
                        except Exception as auth_error:
                            if 'invalid_grant' in str(auth_error).lower() or 'expired' in str(auth_error).lower():
                                raise Exception("Refresh token expired. Regenerate token in Replit Secrets.")
                            raise auth_error
                    else:
                        if retry_count >= max_retries:
                            raise
                        print(f"Upload error (attempt {retry_count}/{max_retries}): {upload_error}")
                        import time
                        time.sleep(5)  # Wait before retry
                        response = None  # Retry
            
            if response and 'id' in response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/shorts/{video_id}"
                
                return {
                    'video_id': video_id,
                    'url': video_url,
                    'title': title,
                    'response': response
                }
            else:
                # Check if we got 401 errors consistently - likely token issue
                raise Exception("Upload failed after retries - likely expired refresh token. Run 'python scripts/regenerate_youtube_token.py' to fix.")
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a quota issue (different from token issue)
            if 'quota' in error_str or ('403' in str(e) and 'quotaexceeded' in error_str):
                print("\n" + "="*70)
                print("⚠️  YOUTUBE API QUOTA WEEK")
                print("="*70)
                print("\nYou've used up your daily YouTube API quota (10,000 units/day by default).")
                print("\nThis is NOT a token issue - your token is valid!")
                print("\nSolutions:")
                print("1. Wait until tomorrow when quota resets (PST timezone)")
                print("2. Request quota increase in Google Cloud Console:")
                print("   https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas")
                print("3. The system will automatically retry after quota resets")
                print("="*70 + "\n")
                raise Exception(f"YouTube API quota exceeded: {e}")
            
            # Check if it's a token expiration issue
            if any(keyword in error_str for keyword in ['401', 'unauthorized', 'invalid_grant', 'expired', 'token']):
                print("\n" + "="*70)
                print("❌ YOUTUBE REFRESH TOKEN EXPIRED OR INVALID")
                print("="*70)
                
                # Try automatic recovery
                try:
                    from core.token_auto_recovery import auto_recover_token, update_config_token
                    print("\nAttempting automatic token regeneration...")
                    new_token = auto_recover_token()
                    if new_token:
                        print("\n✅ Token regenerated successfully!")
                        # Update the token in memory with the NEW token
                        if update_config_token(new_token):
                            print("✅ Token updated in memory - continuing upload...")
                            # Retry the upload with the new token
                            return self.upload_video(video_path, title, description, tags, category_id)
                        else:
                            print("⚠️ Please restart the app for the new token to take effect.")
                    else:
                        print("\n⚠️ Automatic recovery failed. Using manual method...")
                        print("\nTo fix this issue manually:")
                        print("1. In Replit Shell, run: python scripts/regenerate_youtube_token.py")
                        print("2. Follow the prompts to get a new refresh token")
                        print("3. Copy the new refresh token and update YOUTUBE_REFRESH_TOKEN in Replit Secrets")
                        print("4. Restart the app")
                except Exception as recovery_error:
                    print(f"\n⚠️ Automatic recovery error: {recovery_error}")
                    print("\nTo fix this issue manually:")
                    print("1. In Replit Shell, run: python scripts/regenerate_youtube_token.py")
                    print("2. Follow the prompts to get a new refresh token")
                    print("3. Copy the new refresh token and update YOUTUBE_REFRESH_TOKEN in Replit Secrets")
                    print("4. Restart the app")
                
                print("\nThe system will automatically retry uploading pending videos once the token is updated.")
                print("="*70 + "\n")
                raise Exception("YouTube refresh token expired. Attempted automatic recovery.")
            
            error_msg = f"Error uploading video: {e}"
            print(error_msg)
            
            # Log error details for debugging
            import logging
            logging.error(f"YouTube upload error: {e}", exc_info=True)
            
            raise
    
    def get_channel_id(self) -> Optional[str]:
        """Get YouTube channel ID"""
        if not self.service:
            return None
        
        try:
            request = self.service.channels().list(
                part='id',
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['id']
        except Exception as e:
            print(f"Error getting channel ID: {e}")
        
        return None

