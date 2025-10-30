"""
Freesound.org API integration for royalty-free music
Free tier: 10,000 API calls/day
"""
import os
import requests
import tempfile
from typing import Optional, Dict, List
from core.config import Config

class FreesoundMusicAPI:
    """Freesound.org music API client"""
    
    def __init__(self):
        self.api_key = os.getenv('FREESOUND_API_KEY', '')
        self.base_url = "https://freesound.org/apiv2"
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Get access token from API key"""
        if not self.api_key:
            print("⚠️ FREESOUND_API_KEY not configured")
            return
        
        try:
            response = requests.post(
                f"{self.base_url}/oauth2/access_token/",
                data={
                    'client_id': self.api_key.split('|')[0] if '|' in self.api_key else self.api_key,
                    'client_secret': self.api_key.split('|')[1] if '|' in self.api_key else '',
                    'grant_type': 'client_credentials'
                }
            )
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                print("✅ Freesound API authenticated")
            else:
                print(f"⚠️ Freesound auth failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Freesound auth error: {e}")
    
    def search_music(self, query: str, mood: str = None, duration: float = 30.0) -> Optional[str]:
        """
        Search for music based on query and mood
        Returns path to downloaded music file
        """
        if not self.token:
            return None
        
        try:
            # Build query with mood hints
            search_query = query
            if mood:
                mood_keywords = {
                    'upbeat': 'upbeat energetic happy',
                    'dramatic': 'dramatic intense epic',
                    'ambient': 'ambient calm peaceful',
                    'minimalist': 'minimal simple quiet',
                    'cinematic': 'cinematic orchestral epic',
                    'suspenseful': 'suspenseful dark tense',
                    'inspiring': 'inspiring uplifting motivational'
                }
                search_query = f"{search_query} {mood_keywords.get(mood, '')}"
            
            params = {
                'query': search_query,
                'filter': f'duration:[{duration * 0.8:.1f} TO {duration * 1.5:.1f}]',
                'fields': 'id,name,previews,duration',
                'page_size': 5
            }
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.base_url}/search/text/", params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    # Get preview URL (usually MP3)
                    sound = results[0]
                    preview_url = sound.get('previews', {}).get('preview-hq-mp3') or sound.get('previews', {}).get('preview-lq-mp3')
                    
                    if preview_url:
                        # Download music
                        music_path = os.path.join(Config.TEMP_DIR, f"music_{sound['id']}.mp3")
                        os.makedirs(Config.TEMP_DIR, exist_ok=True)
                        
                        audio_response = requests.get(preview_url)
                        if audio_response.status_code == 200:
                            with open(music_path, 'wb') as f:
                                f.write(audio_response.content)
                            print(f"✅ Downloaded music: {sound['name']}")
                            return music_path
            
        except Exception as e:
            print(f"⚠️ Freesound search error: {e}")
        
        return None


