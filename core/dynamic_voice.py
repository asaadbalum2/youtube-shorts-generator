"""
Dynamic Voice Selector - Selects voice characteristics based on content analysis
Supports multiple TTS options with different accents and speeds
"""
import os
import random
from typing import Dict, Optional
from gtts import gTTS
from core.config import Config

class DynamicVoiceSelector:
    """Selects voice characteristics dynamically based on content analysis"""
    
    # Voice configurations based on analysis
    VOICE_CONFIGS = {
        "formal": {
            "tld": "com",
            "lang": "en",
            "slow": False,
            "accent": "american"
        },
        "casual": {
            "tld": "com.au",
            "lang": "en",
            "slow": False,
            "accent": "australian"
        },
        "energetic": {
            "tld": "com",
            "lang": "en",
            "slow": False,
            "accent": "american"
        },
        "calm": {
            "tld": "co.uk",
            "lang": "en",
            "slow": False,
            "accent": "british"
        },
        "authoritative": {
            "tld": "com",
            "lang": "en",
            "slow": False,
            "accent": "american"
        },
        "friendly": {
            "tld": "com.au",
            "lang": "en",
            "slow": False,
            "accent": "australian"
        },
        "dramatic": {
            "tld": "co.uk",
            "lang": "en",
            "slow": False,
            "accent": "british"
        }
    }
    
    def get_voice_config(self, analysis: Dict) -> Dict:
        """
        Get voice configuration based on content analysis
        
        Args:
            analysis: Content analysis dict with voice_style, mood, etc.
            
        Returns:
            Voice configuration dict for TTS
        """
        voice_style = analysis.get("voice_style", "casual")
        mood = analysis.get("mood", "informative")
        energy = analysis.get("energy_level", "medium")
        
        print(f"🎤 Selecting voice: {voice_style} style, {mood} mood, {energy} energy")
        
        # Always use American accent (user preference)
        # Get base config but override accent to American
        if voice_style in self.VOICE_CONFIGS:
            config = self.VOICE_CONFIGS[voice_style].copy()
        elif mood in ["calm", "serious"]:
            config = self.VOICE_CONFIGS["calm"].copy()
        elif mood in ["energetic", "upbeat"]:
            config = self.VOICE_CONFIGS["energetic"].copy()
        else:
            config = self.VOICE_CONFIGS["casual"].copy()
        
        # Force American accent (tld='com')
        config["tld"] = "com"
        config["accent"] = "american"
        
        # Adjust speed based on energy
        if energy == "high":
            config["slow"] = False
        elif energy == "low":
            config["slow"] = False  # Keep normal speed for clarity
        else:
            config["slow"] = False
        
        return config
    
    def generate_speech(self, text: str, analysis: Dict, output_path: str) -> str:
        """
        Generate TTS speech with dynamic voice selection
        
        Args:
            text: Text to convert to speech
            analysis: Content analysis dict
            output_path: Path to save audio file
            
        Returns:
            Path to generated audio file
        """
        config = self.get_voice_config(analysis)
        
        print(f"🎙️ Generating speech with {config['accent']} accent ({config['tld']})")
        
        tts = gTTS(
            text=text,
            lang=config["lang"],
            slow=config["slow"],
            tld=config["tld"]
        )
        
        tts.save(output_path)
        print(f"✅ Speech saved: {output_path}")
        
        return output_path

