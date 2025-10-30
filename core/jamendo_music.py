"""
Jamendo Music API - Free royalty-free music
https://developer.jamendo.com/
"""
import os
import requests
import random
from typing import Optional, Dict, List
from core.config import Config

class JamendoMusicAPI:
    """Jamendo API for free royalty-free music"""
    
    def __init__(self):
        # Jamendo uses CLIENT_ID and CLIENT_SECRET (free tier - no credit card)
        self.client_id = os.getenv('JAMENDO_CLIENT_ID', '')
        self.client_secret = os.getenv('JAMENDO_CLIENT_SECRET', '')
        # Fallback to old API_KEY if provided
        self.api_key = self.client_id or os.getenv('JAMENDO_API_KEY', '')
        self.base_url = "https://api.jamendo.com/v3.0"
    
    def search_music(self, genre: str = None, mood: str = None, tags: List[str] = None) -> Optional[str]:
        """
        Search for royalty-free music matching mood/genre
        Returns path to downloaded music file or None
        """
        try:
            # Map our moods to Jamendo tags
            mood_tags = {
                'upbeat': ['energetic', 'happy'],
                'dramatic': ['dramatic', 'epic'],
                'calm': ['ambient', 'calm'],
                'suspenseful': ['dark', 'suspense'],
                'inspiring': ['uplifting', 'motivational'],
                'minimalist': ['minimal', 'ambient']
            }
            
            # Build search tags
            search_tags = []
            if mood and mood.lower() in mood_tags:
                search_tags.extend(mood_tags[mood.lower()])
            if tags:
                search_tags.extend(tags)
            
            # Jamendo API search - use client_id parameter (required)
            # Free tier: https://developer.jamendo.com/ - no credit card, truly free
            client_id_to_use = self.client_id or self.api_key or '58c7c0f1'  # Use CLIENT_ID if set
            params = {
                'client_id': client_id_to_use,
                'format': 'json',
                'limit': 20,  # Get more results
                'tags': '+'.join(search_tags[:3]) if search_tags else 'instrumental',
                'order': 'popularity_week',  # Get trending/popular tracks
                'audioformat': 'mp32',  # MP3 format
                'imagesize': '200',
                'speed': '0.8-1.2',  # Match tempo if possible
                'boost': 'popularity_total'  # Boost by total popularity
            }
            
            response = requests.get(f"{self.base_url}/tracks", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('results', [])
                
                if tracks:
                    # Pick a random popular track
                    track = random.choice(tracks)
                    audio_url = track.get('audio', '')
                    
                    if audio_url:
                        # Download the music
                        music_path = self._download_music(audio_url, track.get('id'))
                        if music_path:
                            print(f"✅ Jamendo music: {track.get('name', 'Unknown')} by {track.get('artist_name', 'Unknown')}")
                            return music_path
            
            # If no results, try a simpler search without specific mood tags
            if not tracks or response.status_code != 200 or len(tracks) == 0:
                simple_params = {
                    'client_id': self.client_id or self.api_key or '58c7c0f1', 
                    'format': 'json',
                    'limit': 10,
                    'tags': 'instrumental',
                    'order': 'popularity_week',
                    'audioformat': 'mp32'
                }
                try:
                    response = requests.get(f"{self.base_url}/tracks", params=simple_params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        tracks = data.get('results', [])
                        if tracks:
                            track = random.choice(tracks)
                            audio_url = track.get('audio', '')
                            if audio_url:
                                music_path = self._download_music(audio_url, track.get('id'))
                                if music_path:
                                    print(f"✅ Jamendo music (generic): {track.get('name', 'Unknown')} by {track.get('artist_name', 'Unknown')}")
                                    return music_path
                except:
                    pass
            
            # Jamendo API may require registration for better results
            return None
            
        except Exception as e:
            print(f"⚠️ Jamendo API error: {e}")
            return None
    
    def _download_music(self, url: str, track_id: str) -> Optional[str]:
        """Download music file"""
        try:
            import tempfile
            import os
            from pathlib import Path
            
            music_dir = Path(Config.ASSETS_DIR) / "music" / "jamendo"
            music_dir.mkdir(parents=True, exist_ok=True)
            
            music_path = music_dir / f"jamendo_{track_id}.mp3"
            
            # Download if not already cached
            if not music_path.exists():
                response = requests.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                with open(music_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return str(music_path) if music_path.exists() else None
            
        except Exception as e:
            print(f"⚠️ Error downloading Jamendo music: {e}")
            return None

