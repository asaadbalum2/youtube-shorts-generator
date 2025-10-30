"""
Free Music Archive (FMA) API - Truly free, trending music
https://freemusicarchive.org/api/docs
No API key needed, completely free
"""
import requests
import random
from typing import Optional, List
import os


class FreeMusicArchiveAPI:
    """Free Music Archive - Free trending music, no API key needed"""
    
    def __init__(self):
        self.base_url = "https://freemusicarchive.org/api/get"
        # No API key needed for FMA
    
    def search_trending_music(self, genre: str = None, mood: str = None) -> Optional[str]:
        """
        Search for trending music from Free Music Archive
        Returns path to downloaded music file or None
        """
        try:
            # FMA has curated playlists and trending tracks
            # Get recent tracks (trending/new)
            params = {
                'page': 1,
                'limit': 20,
                'sort': 'track_date_published',  # Get newest first
                'order': 'desc'
            }
            
            # Map moods to FMA genres
            if mood:
                genre_map = {
                    'upbeat': 'Electronic',
                    'dramatic': 'Classical',
                    'calm': 'Ambient',
                    'suspenseful': 'Soundtrack',
                    'inspiring': 'Rock'
                }
                if mood.lower() in genre_map:
                    params['genre_handle'] = genre_map[mood.lower()]
            
            response = requests.get(f"{self.base_url}/tracks.json", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('dataset', [])
                
                if tracks:
                    # Get a random recent/trending track
                    track = random.choice(tracks[:10])  # Top 10 newest
                    download_url = track.get('track_file')
                    
                    if download_url:
                        # Download the track
                        music_path = self._download_music(download_url, track.get('track_id'))
                        if music_path:
                            print(f"✅ FMA music: {track.get('track_title', 'Unknown')} by {track.get('artist_name', 'Unknown')}")
                            return music_path
            
            return None
            
        except Exception as e:
            print(f"⚠️ FMA API error: {e}")
            return None
    
    def _download_music(self, url: str, track_id: str) -> Optional[str]:
        """Download music file from URL"""
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save to temp directory
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            music_path = os.path.join(temp_dir, f"fma_{track_id}_{random.randint(10000, 99999)}.mp3")
            
            with open(music_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return music_path if os.path.exists(music_path) else None
            
        except Exception as e:
            print(f"❌ Error downloading FMA music: {e}")
            return None

