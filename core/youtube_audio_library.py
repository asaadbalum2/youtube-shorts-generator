"""
YouTube Audio Library - 100% free, no API needed
Music is pre-downloaded and organized in folders
"""
import os
import random
from typing import Optional, Dict, List
from core.config import Config

class YouTubeAudioLibrary:
    """
    YouTube Audio Library music - completely free, no API, no subscriptions
    User downloads music manually from YouTube Studio and places in folders
    """
    
    def __init__(self):
        self.music_dir = os.path.join(Config.ASSETS_DIR, "music")
        os.makedirs(self.music_dir, exist_ok=True)
    
    def get_music(self, mood: str, style: str, duration: float) -> Optional[str]:
        """
        Get music from pre-downloaded YouTube Audio Library tracks
        Returns path to music file or None
        """
        # Try style folder first
        style_dir = os.path.join(self.music_dir, style)
        if os.path.exists(style_dir):
            music_files = [f for f in os.listdir(style_dir) 
                          if f.endswith(('.mp3', '.wav', '.m4a', '.ogg'))]
            if music_files:
                selected = random.choice(music_files)
                path = os.path.join(style_dir, selected)
                print(f"✅ Found YouTube Audio Library music: {selected}")
                return path
        
        # Try mood folder as fallback
        mood_dir = os.path.join(self.music_dir, mood)
        if os.path.exists(mood_dir):
            music_files = [f for f in os.listdir(mood_dir) 
                          if f.endswith(('.mp3', '.wav', '.m4a', '.ogg'))]
            if music_files:
                selected = random.choice(music_files)
                path = os.path.join(mood_dir, selected)
                print(f"✅ Found YouTube Audio Library music: {selected}")
                return path
        
        return None

