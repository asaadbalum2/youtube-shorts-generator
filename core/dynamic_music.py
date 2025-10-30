"""
Dynamic Music Selector - Selects background music based on content analysis
Uses free music sources: YouTube Audio Library, Incompetech, Freesound
"""
import os
import random
import requests
from typing import Optional, Dict, List
from core.config import Config
from core.youtube_audio_library import YouTubeAudioLibrary
from core.jamendo_music import JamendoMusicAPI

class DynamicMusicSelector:
    """Selects music dynamically based on content analysis"""
    
    def __init__(self):
        self.music_dir = os.path.join(Config.ASSETS_DIR, "music")
        os.makedirs(self.music_dir, exist_ok=True)
        
        # Create music library structure (will be populated)
        self.music_library = {
            "ambient": [],
            "upbeat": [],
            "dramatic": [],
            "minimalist": [],
            "cinematic": [],
            "electronic": [],
            "acoustic": [],
            "orchestral": [],
            "suspenseful": [],
            "inspiring": []
        }
    
    def get_music_for_content(self, analysis: Dict, duration: float) -> Optional[str]:
        """
        Get music file path based on content analysis
        
        Args:
            analysis: Content analysis dict with music_style, mood, etc.
            duration: Video duration in seconds
            
        Returns:
            Path to music file or None if not available
        """
        music_style = analysis.get("music_style", "minimalist")
        mood = analysis.get("mood", "informative")
        tempo = analysis.get("music_tempo", "medium")
        
        print(f"🎵 Selecting music: {music_style} style, {mood} mood, {tempo} tempo")
        
        # FIRST PRIORITY: YouTube Audio Library (100% free, copyright-safe, YouTube recognizes it)
        # YouTube automatically shows song name when you select "Attribution" during upload
        youtube_audio = YouTubeAudioLibrary()
        yt_music = youtube_audio.get_music(mood, music_style, duration)
        if yt_music:
            print(f"✅ Using YouTube Audio Library music (copyright-safe, YouTube recognizes it)")
            return yt_music
        
        # SECOND: Jamendo API (free, trending/popular tracks) - as backup
        jamendo = JamendoMusicAPI()
        jamendo_music = jamendo.search_music(genre=music_style, mood=mood, tags=[music_style, mood])
        if jamendo_music:
            print(f"✅ Using Jamendo music (free tier, trending tracks)")
            return jamendo_music
        
        # THIRD: Local music files
        local_music = self._get_local_music(music_style, mood, tempo)
        if local_music:
            return local_music
        
        print("⚠️ No music available, video will have voiceover only")
        return None
    
    def _get_local_music(self, style: str, mood: str, tempo: str) -> Optional[str]:
        """Check for local music files"""
        # Check specific style folder
        style_dir = os.path.join(self.music_dir, style)
        if os.path.exists(style_dir):
            music_files = [f for f in os.listdir(style_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
            if music_files:
                selected = random.choice(music_files)
                path = os.path.join(style_dir, selected)
                print(f"✅ Found local music: {path}")
                return path
        
        # Check mood folder as fallback
        mood_dir = os.path.join(self.music_dir, mood)
        if os.path.exists(mood_dir):
            music_files = [f for f in os.listdir(mood_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
            if music_files:
                selected = random.choice(music_files)
                path = os.path.join(mood_dir, selected)
                print(f"✅ Found local music: {path}")
                return path
        
        return None
    
    def _download_free_music(self, style: str, mood: str, duration: float) -> Optional[str]:
        """
        Download music from free sources
        TODO: Implement Freesound.org API integration
        """
        # Freesound.org API integration would go here
        # For now, we'll use a placeholder
        
        # You can add music files manually to assets/music/{style}/ or assets/music/{mood}/
        # The system will automatically find and use them
        
        return None
    
    def organize_music_library(self):
        """
        Helper function to organize music files
        Place music files in assets/music/{style}/ or assets/music/{mood}/ folders
        """
        print("📁 Music library structure:")
        print("   assets/music/")
        print("   ├── ambient/")
        print("   ├── upbeat/")
        print("   ├── dramatic/")
        print("   ├── minimalist/")
        print("   ├── cinematic/")
        print("   ├── electronic/")
        print("   ├── acoustic/")
        print("   ├── orchestral/")
        print("   ├── suspenseful/")
        print("   └── inspiring/")
        print("\n💡 Tip: Download free music from:")
        print("   - YouTube Audio Library: studio.youtube.com")
        print("   - Incompetech (Kevin MacLeod): incompetech.com")
        print("   - Freesound.org: freesound.org")
        print("   Place files in appropriate style folders!")

