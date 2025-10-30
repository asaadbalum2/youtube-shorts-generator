"""
Free Music Archive API - Completely free, no subscriptions, no trials
https://freemusicarchive.org/api
"""
import os
import requests
import random
from typing import Optional, Dict
from core.config import Config

class FreeMusicArchiveAPI:
    """Free Music Archive - 100% free, no subscriptions"""
    
    def __init__(self):
        # FMA API requires registration but is completely free
        # You can also use without API key for public endpoints
        self.api_key = os.getenv('FMA_API_KEY', '')  # Optional - works without it too
        self.base_url = "https://freemusicarchive.org/api/get"
    
    def search_music(self, genre: str = None, mood: str = None) -> Optional[str]:
        """
        Search for free music tracks
        Returns path to downloaded music file
        """
        try:
            # FMA has curated playlists by genre/mood
            # For now, we'll use a simple approach: download from curated collections
            # Since FMA doesn't have direct streaming API, we'll guide users to pre-download
            
            # Alternative: Use YouTube Audio Library music (pre-downloaded)
            # Or use Mixkit which has direct download URLs
            
            print("📝 Note: Free Music Archive requires pre-downloading tracks")
            print("💡 Better option: Use pre-downloaded music from YouTube Audio Library")
            return None
            
        except Exception as e:
            print(f"⚠️ FMA error: {e}")
            return None efficiently

