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
        # Jamendo API is free, no key needed for basic usage
        # But for commercial use, you may need to register
        self.api_key = os.getenv('JAMENDO_API_KEY', '')
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
            
            # Jamendo API search
            params = {
                'client_id': self.api_key or 'test',  # Can work without key for testing
                'format': 'json',
                'limit': 10,
                'tags': '+'.join(search_tags[:3]) if search_tags else 'instrumental',
                'order': 'popularity_week',  # Get trending/popular tracks
                'audioformat': 'mp32',
                'imagesize': '200'
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
            
            print("⚠️ No Jamendo music found")
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

