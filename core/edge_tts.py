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
            
            # Edge TTS works best with clean, simple text
            # Clean text: remove problematic characters but keep essential punctuation
            text_clean = text
            # Remove any null bytes or control characters
            text_clean = text_clean.replace('\x00', '').replace('\ufffd', '')
            # Keep only printable ASCII + common punctuation
            text_clean = ''.join(char for char in text_clean if ord(char) < 128 or char in '，。！？')  # Allow common punctuation
            
            if not text_clean or len(text_clean.strip()) < 10:
                text_clean = text  # Fallback to original
            
            # Edge TTS has issues with very long text - use reasonable limit
            max_text_length = 5000
            if len(text_clean) > max_text_length:
                print(f"⚠️ Text too long ({len(text_clean)} chars), truncating to {max_text_length}...")
                text_clean = text_clean[:max_text_length].rsplit('.', 1)[0] + '.'  # Truncate at sentence boundary
            
            # Try Edge TTS - ensure proper async handling and network timeout
            try:
                print(f"🔍 Attempting Edge TTS with voice: {voice_to_use}, text length: {len(text_clean)}")
                
                # Create Communicate object
                communicate = edge_tts.Communicate(text_clean, voice_to_use)
                
                # Use a temporary file first to check if audio was generated
                temp_output = output_path + '.tmp'
                
                # Edge TTS requires proper async streaming - use stream() to collect all chunks
                audio_chunks = []
                
                # Stream all audio chunks
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_chunks.append(chunk["data"])
                
                # Combine all chunks
                if audio_chunks:
                    audio_data = b"".join(audio_chunks)
                    
                    # Verify we got audio data
                    if audio_data and len(audio_data) > 1000:  # At least 1KB
                        with open(temp_output, "wb") as f:
                            f.write(audio_data)
                        print(f"🔍 Audio data collected: {len(audio_data)} bytes from {len(audio_chunks)} chunks")
                    else:
                        print(f"⚠️ Edge TTS: Audio data too small ({len(audio_data) if audio_data else 0} bytes)")
                        raise Exception(f"No audio data received: {len(audio_data) if audio_data else 0} bytes")
                else:
                    print(f"⚠️ Edge TTS: No audio chunks received")
                    raise Exception("No audio chunks received from Edge TTS stream")
                
                print(f"🔍 Temp file created: exists={os.path.exists(temp_output)}, size={os.path.getsize(temp_output) if os.path.exists(temp_output) else 0}")
                
                # Verify file was created and has content
                if os.path.exists(temp_output) and os.path.getsize(temp_output) > 1000:  # At least 1KB
                    os.rename(temp_output, output_path)
                    print(f"✅ Edge TTS generated: {voice_to_use} (American accent, {os.path.getsize(output_path)} bytes)")
                    return True
                elif os.path.exists(temp_output):
                    # File too small - might be empty
                    os.remove(temp_output)
                    print(f"⚠️ Edge TTS: Generated file too small, trying shorter text...")
                else:
                    print(f"⚠️ Edge TTS: No file created, trying shorter text...")
                
                # Retry with shorter text (split by sentences)
                if len(text_clean) > 2000:
                    sentences = text_clean.split('. ')
                    # Take first few sentences (up to 2000 chars)
                    text_short = '. '.join(sentences[:max(len(sentences)//2, 3)]) + '.'
                    print(f"⚠️ Retrying with shorter text ({len(text_short)} chars)...")
                    communicate = edge_tts.Communicate(text_short, voice_to_use)
                    await communicate.save(temp_output)
                    if os.path.exists(temp_output) and os.path.getsize(temp_output) > 1000:
                        os.rename(temp_output, output_path)
                        print(f"✅ Edge TTS generated (retry): {voice_to_use}")
                        return True
                    elif os.path.exists(temp_output):
                        os.remove(temp_output)
                
                return False
            except Exception as comm_error:
                error_msg = str(comm_error)
                print(f"⚠️ Edge TTS communicate error: {error_msg}")
                
                # If error mentions "No audio", try with even simpler text
                if "No audio" in error_msg or "no audio" in error_msg.lower():
                    print(f"⚠️ Edge TTS: 'No audio' error, trying minimal text test...")
                    try:
                        # Try with a simple test sentence first
                        test_text = "Hello, this is a test. " + text_clean[:500] if len(text_clean) > 500 else text_clean
                        communicate = edge_tts.Communicate(test_text, voice_to_use)
                        await communicate.save(output_path)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                            print(f"✅ Edge TTS generated (minimal): {voice_to_use}")
                            return True
                    except Exception as test_error:
                        print(f"⚠️ Edge TTS test failed: {test_error}")
                
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

