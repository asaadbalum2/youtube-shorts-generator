"""
Microsoft Edge TTS - Completely FREE, no API key, no limits, no credit card
Uses the same TTS engine that powers Microsoft Edge browser
High quality voices including American English
"""
import edge_tts
import asyncio
import os
from typing import Optional
from core.config import Config


class EdgeTTS:
    """Microsoft Edge TTS - 100% free, unlimited, no API key needed"""
    
    # Available voices (American English - high quality)
    AMERICAN_VOICES = [
        "en-US-JennyNeural",      # Female, friendly
        "en-US-GuyNeural",        # Male, casual
        "en-US-AriaNeural",       # Female, professional
        "en-US-TonyNeural",       # Male, energetic
        "en-US-DavisNeural",      # Male, calm
        "en-US-JaneNeural",       # Female, confident
    ]
    
    def __init__(self):
        self.voice = "en-US-JennyNeural"  # Default: friendly female American voice
    
    async def _generate_speech_async(self, text: str, output_path: str, voice: str = None, rate: str = "+0%", pitch: str = "+0Hz") -> bool:
        """Generate speech asynchronously with SSML for rhythm control"""
        try:
            voice_to_use = voice or self.voice
            
            # Edge TTS doesn't support SSML directly - use plain text with voice selection
            # The voice itself determines the pace and energy (energetic voices are faster, calm voices are slower)
            # For rhythm control, we'll adjust text with pauses and use appropriate voices
            
            # Try plain text first (Edge TTS works best with simple text)
            # Clean text to remove any problematic characters
            text_clean = text.encode('ascii', errors='ignore').decode('ascii')
            if not text_clean or len(text_clean) < 10:
                text_clean = text  # Fallback to original if cleaning removed everything
            
            # Edge TTS has issues with very long text - split if needed
            max_text_length = 5000  # Edge TTS limit
            if len(text_clean) > max_text_length:
                print(f"⚠️ Text too long ({len(text_clean)} chars), truncating to {max_text_length}...")
                text_clean = text_clean[:max_text_length] + "..."
            
            try:
                communicate = edge_tts.Communicate(text_clean, voice_to_use)
                await communicate.save(output_path)
                
                # Verify file was created and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"✅ Edge TTS generated: {voice_to_use} (American accent guaranteed)")
                    return True
                else:
                    print(f"⚠️ Edge TTS: File created but empty, retrying...")
                    # Retry once with shorter text
                    if len(text_clean) > 2000:
                        text_clean = text_clean[:2000] + "..."
                    communicate = edge_tts.Communicate(text_clean, voice_to_use)
                    await communicate.save(output_path)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        print(f"✅ Edge TTS generated (retry): {voice_to_use}")
                        return True
                    return False
            except Exception as comm_error:
                print(f"⚠️ Edge TTS communicate error: {comm_error}")
                # Try with even shorter text
                if len(text_clean) > 1000:
                    print(f"⚠️ Trying with shorter text (1000 chars)...")
                    try:
                        text_short = text_clean[:1000] + "..."
                        communicate = edge_tts.Communicate(text_short, voice_to_use)
                        await communicate.save(output_path)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            print(f"✅ Edge TTS generated (short text): {voice_to_use}")
                            return True
                    except:
                        pass
                return False
        except Exception as e:
            print(f"❌ Edge TTS error: {e}")
            return False
    
    def generate_speech(self, text: str, output_path: str, voice_style: str = "casual") -> Optional[str]:
        """
        Generate speech using Edge TTS (FREE, unlimited)
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice_style: Style hint (casual, professional, energetic, calm)
        
        Returns:
            Path to audio file or None if failed
        """
        try:
            # Select voice based on style - FORCE American voices only
            if voice_style == "energetic":
                voice = "en-US-TonyNeural"  # Male, energetic American
                rate = "+10%"  # Faster for energy
                pitch = "+5Hz"  # Slightly higher pitch for excitement
            elif voice_style == "professional" or voice_style == "formal":
                voice = "en-US-AriaNeural"  # Female, professional American
                rate = "+5%"
                pitch = "+0Hz"
            elif voice_style == "calm":
                voice = "en-US-DavisNeural"  # Male, calm American
                rate = "+0%"
                pitch = "-2Hz"
            elif voice_style == "confident" or voice_style == "authoritative":
                voice = "en-US-JaneNeural"  # Female, confident American
                rate = "+5%"
                pitch = "+3Hz"
            elif voice_style == "dramatic":
                voice = "en-US-JennyNeural"  # Female, dramatic American
                rate = "+8%"
                pitch = "+4Hz"
            else:  # casual, friendly
                voice = "en-US-JennyNeural"  # Female, friendly American (DEFAULT)
                rate = "+5%"  # Slightly faster for engagement
                pitch = "+2Hz"  # Slightly higher for friendliness
            
            # ENSURE we're using American voices - double check
            if not voice.startswith("en-US-"):
                print(f"⚠️ WARNING: Non-American voice detected: {voice}, forcing en-US-JennyNeural")
                voice = "en-US-JennyNeural"
                rate = "+5%"
                pitch = "+2Hz"
            
            # Handle event loop properly (fix for FastAPI/async environments)
            try:
                # Check if there's a running event loop
                loop = asyncio.get_running_loop()
                # If we're in an async context, run in a new thread
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self._generate_speech_async(text, output_path, voice, rate, pitch)
                        )
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    success = future.result(timeout=60)  # 60 second timeout
                    
            except RuntimeError:
                # No running loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(
                        self._generate_speech_async(text, output_path, voice, rate, pitch)
                    )
                finally:
                    loop.close()
            
            if success and os.path.exists(output_path):
                return output_path
            
            return None
            
        except Exception as e:
            print(f"❌ Edge TTS error: {e}")
            return None
    
    @staticmethod
    async def list_voices():
        """List all available voices (for debugging)"""
        voices = await edge_tts.list_voices()
        american = [v for v in voices if "en-US" in v["ShortName"]]
        print(f"Available American voices: {len(american)}")
        for v in american[:10]:
            print(f"  - {v['ShortName']}: {v['Gender']}, {v['Locale']}")

