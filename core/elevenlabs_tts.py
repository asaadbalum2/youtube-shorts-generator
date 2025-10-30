"""
ElevenLabs TTS API integration
Free tier: 10,000 characters/month
Multiple high-quality voices
"""
import os
import requests
from typing import Dict
from core.config import Config

class ElevenLabsTTS:
    """ElevenLabs text-to-speech API"""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - natural American voice (default)
    
    # Voice IDs (American voices)
    VOICES = {
        "casual": "21m00Tcm4TlvDq8ikWAM",      # Rachel - friendly
        "energetic": "pNInz6obpgDQGcFmaJgB",   # Adam - energetic
        "calm": "EXAVITQu4vr4xnSDxMaL",        # Bella - calm
        "authoritative": "ThT5KcBeYPX3keUQqHPh", # Dorothy - professional
        "dramatic": "VR6AewLTigWG4xSOukaG",    # Arnold - expressive
    }
    
    def generate_speech(self, text: str, voice_style: str = "casual", output_path: str = None) -> str:
        """
        Generate speech using ElevenLabs
        Returns path to audio file
        """
        if not self.api_key:
            print("⚠️ ELEVENLABS_API_KEY not configured, using gTTS fallback")
            return None
        
        try:
            voice_id = self.VOICES.get(voice_style, self.voice_id)
            
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            data = {
                'text': text,
                'model_id': 'eleven_monolingual_v1',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.75
                }
            }
            
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                if not output_path:
                    import tempfile
                    output_path = os.path.join(Config.TEMP_DIR, f"elevenlabs_{hash(text) % 10000}.mp3")
                    os.makedirs(Config.TEMP_DIR, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ ElevenLabs TTS generated: {output_path}")
                return output_path
            else:
                print(f"⚠️ ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"⚠️ ElevenLabs error: {e}")
            return None

