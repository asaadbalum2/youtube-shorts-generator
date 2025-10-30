"""
Video creation module - generates YouTube Shorts videos
Uses FFmpeg/MoviePy for video processing with real b-roll from Pexels/Pixabay
"""
import os
import random
import requests
from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip
)
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from gtts import gTTS
import tempfile
from typing import Dict, Optional, List
from core.config import Config
from core.media_providers import MediaFetcher
from core.content_analyzer import ContentAnalyzer
from core.dynamic_music import DynamicMusicSelector
from core.dynamic_voice import DynamicVoiceSelector

class VideoCreator:
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
        self.output_dir = Config.OUTPUT_DIR
        self.media_fetcher = MediaFetcher()
        self.content_analyzer = ContentAnalyzer()
        self.music_selector = DynamicMusicSelector()
        self.voice_selector = DynamicVoiceSelector()
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # High-quality settings
        self.video_size = (1080, 1920)  # 9:16 for YouTube Shorts
        self.font_sizes = [60, 65, 70, 75, 80]  # Better sized fonts (not too big)
        self.font_paths = [
            "C:/Windows/Fonts/impact.ttf",  # Bold, engaging
            "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
            "C:/Windows/Fonts/verdana.ttf",  # Clean and readable
            "C:/Windows/Fonts/calibrib.ttf",  # Calibri Bold
        ]
    
    def create_video(self, content: Dict, topic: str) -> str:
        """
        Create a high-quality YouTube Shorts video with real b-roll
        
        Returns: Path to created video file
        """
        script = content.get('script', '')
        print(f"🎬 Creating high-quality video for: {topic}")
        
        # 0. Analyze content to determine mood, style, music, voice
        content_analysis = self.content_analyzer.analyze_content(topic, script)
        print(f"📊 Content analysis: {content_analysis.get('mood')} mood, {content_analysis.get('music_style')} music, {content_analysis.get('voice_style')} voice")
        
        # 1. Generate high-quality audio (TTS) with dynamic voice
        audio_path = self._generate_dynamic_audio(script, content_analysis)
        
        # 2. Calculate duration - ensure minimum 30 seconds
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        print(f"🎵 Audio duration: {audio_duration:.1f}s")
        
        # Ensure minimum duration for monetization
        if audio_duration < Config.MIN_DURATION_SECONDS:
            print(f"⚠️ Audio too short ({audio_duration:.1f}s), extending to minimum {Config.MIN_DURATION_SECONDS}s")
            # Extend audio by looping
            from moviepy.audio.AudioClip import concatenate_audioclips
            loops_needed = int(Config.MIN_DURATION_SECONDS / audio_duration) + 1
            extended_audio = concatenate_audioclips([audio_clip] * loops_needed)
            extended_audio = extended_audio.subclip(0, Config.MIN_DURATION_SECONDS)
            
            # Save extended audio
            extended_audio_path = os.path.join(self.temp_dir, f"extended_audio_{random.randint(10000, 99999)}.mp3")
            extended_audio.write_audiofile(extended_audio_path, verbose=False, logger=None)
            audio_clip.close()
            extended_audio.close()
            
            # Update audio path and duration
            audio_path = extended_audio_path
            duration = Config.MIN_DURATION_SECONDS
        else:
            duration = min(audio_duration, Config.VIDEO_DURATION_SECONDS)
        
        print(f"📏 Final video duration: {duration:.1f}s")
        
        # 3. Split script to know how many segments we need
        segments = self._split_script_into_segments(script)
        num_segments = len(segments) if segments else 1
        
        # 4. Fetch real b-roll images/videos (enough for all segments, no duplicates)
        broll_media = self._fetch_broll_media(topic, duration, num_segments)
        
        # 5. Create high-quality visual sequence
        video_clips = self._create_high_quality_visuals(script, duration, topic, broll_media)
        
        # 5. Add background music (dynamic based on content)
        music_path = self.music_selector.get_music_for_content(content_analysis, duration)
        
        # 6. Combine audio, visuals, and music
        final_video = self._combine_audio_video(video_clips, audio_path, duration, music_path)
        
        # 6. Export high-quality video
        video_id = f"short_{topic.replace(' ', '_')[:20]}_{random.randint(1000, 9999)}"
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        print(f"🎥 Exporting to: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='slow',  # Best quality
            bitrate='12000k',  # Very high bitrate
            audio_bitrate='256k',  # Very high audio quality
            ffmpeg_params=['-crf', '18']  # High quality encoding
        )
        
        # Cleanup
        audio_clip.close()
        final_video.close()
        
        print(f"✅ High-quality video created: {output_path}")
        return output_path
    
    def _generate_dynamic_audio(self, script: str, analysis: Dict) -> str:
        """Generate TTS audio with dynamic voice selection based on content"""
        print("🎤 Generating dynamic TTS audio...")
        
        audio_path = os.path.join(self.temp_dir, f"audio_{random.randint(10000, 99999)}.mp3")
        return self.voice_selector.generate_speech(script, analysis, audio_path)
    
    def _fetch_broll_media(self, topic: str, duration: float, num_segments: int = 0) -> List[Dict]:
        """Fetch real b-roll images and videos from Pexels/Pixabay"""
        print(f"🖼️ Fetching b-roll media for: {topic} (need {num_segments} unique items)")
        
        # Generate search keywords from topic
        keywords = self._extract_keywords(topic)
        
        # Fetch MORE media than needed to ensure variety
        target_count = max(num_segments, 8)  # Get at least 8 unique items
        
        all_media = []
        used_urls = set()  # Track URLs to avoid duplicates
        
        # First, try to get multiple items per keyword
        for keyword in keywords[:6]:  # Try more keywords
            print(f"🔍 Searching for: {keyword}")
            
            # Get multiple images for this keyword
            images = self.media_fetcher.get_images(keyword, count=3)
            for media in images:
                if media and media.get('url') and media['url'] not in used_urls:
                    all_media.append(media)
                    used_urls.add(media['url'])
                    if len(all_media) >= target_count:
                        break
            
            if len(all_media) >= target_count:
                break
            
            # Also try video
            media = self.media_fetcher.get_image(keyword, prefer_video=True)
            if media and media.get('url') and media['url'] not in used_urls:
                all_media.append(media)
                used_urls.add(media['url'])
            
            if len(all_media) >= target_count:
                break
        
        # If still not enough, try different search variations
        if len(all_media) < num_segments:
            variations = ['people', 'nature', 'technology', 'lifestyle', 'abstract', 'urban']
            for variation in variations:
                media = self.media_fetcher.get_image(f"{variation} {keywords[0] if keywords else 'background'}", prefer_video=False)
                if media and media.get('url') and media['url'] not in used_urls:
                    all_media.append(media)
                    used_urls.add(media['url'])
                    if len(all_media) >= target_count:
                        break
        
        # If no media found, use fallback
        if not all_media:
            print("⚠️ No b-roll found, using fallback backgrounds")
            all_media = [self._create_fallback_media()]
        
        print(f"📸 Total unique b-roll items: {len(all_media)}")
        return all_media[:num_segments] if num_segments > 0 else all_media
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract search keywords from topic"""
        # Simple keyword extraction
        words = topic.lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'that', 'this', 'these', 'those'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add the full topic as first keyword
        keywords.insert(0, topic)
        
        return keywords[:5]  # Top 5 keywords
    
    def _create_fallback_media(self) -> Dict:
        """Create fallback media when APIs fail"""
        return {
            'id': 'fallback',
            'url': None,
            'provider': 'fallback',
            'type': 'image'
        }
    
    def _create_high_quality_visuals(self, script: str, duration: float, topic: str, broll_media: List[Dict]) -> List:
        """Create high-quality visual sequence with real b-roll"""
        print("🎨 Creating high-quality visuals...")
        
        clips = []
        
        # Split script into segments
        segments = self._split_script_into_segments(script)
        segment_duration = duration / len(segments) if segments else duration
        
        for i, segment in enumerate(segments):
            print(f"📝 Processing segment {i+1}/{len(segments)}: {segment[:50]}...")
            
            # Get unique b-roll for this segment (no duplicates!)
            if i < len(broll_media):
                media = broll_media[i]  # Use different media for each segment
            else:
                # If somehow we run out, use fallback
                media = self._create_fallback_media()
            
            # Create visual for segment
            if media['provider'] == 'fallback':
                clip = self._create_fallback_visual(segment, topic, i, segment_duration)
            else:
                clip = self._create_broll_visual(segment, media, i, segment_duration)
            
            clips.append(clip)
        
        print(f"✅ Created {len(clips)} visual segments")
        return clips
    
    def _create_broll_visual(self, text: str, media: Dict, index: int, duration: float) -> CompositeVideoClip:
        """Create visual using real b-roll media"""
        try:
            # Download and process the media
            if media.get('url'):
                media_path = self._download_media(media['url'], index)
                
                if media_path and os.path.exists(media_path):
                    # Create base clip from b-roll
                    if media.get('type') == 'video' or media_path.endswith('.mp4'):
                        base_clip = VideoFileClip(media_path)
                    else:
                        base_clip = ImageClip(media_path)
                    
                    # Resize to fit 9:16 aspect ratio
                    base_clip = self._resize_for_shorts(base_clip)
                    
                    # Add text overlay
                    text_clip = self._create_kinetic_text(text, index)
                    
                    # Create composite
                    final_clip = CompositeVideoClip([
                        base_clip.set_duration(duration),
                        text_clip.set_duration(duration)
                    ])
                    
                    return final_clip
        except Exception as e:
            print(f"⚠️ Error creating b-roll visual: {e}")
        
        # Fallback to text-only
        return self._create_fallback_visual(text, "", index, duration)
    
    def _create_fallback_visual(self, text: str, topic: str, index: int, duration: float) -> CompositeVideoClip:
        """Create high-quality text-only visual as fallback"""
        # Create animated background
        bg_clip = self._create_animated_background(index, duration)
        
        # Create kinetic text
        text_clip = self._create_kinetic_text(text, index)
        
        # Composite
        final_clip = CompositeVideoClip([
            bg_clip,
            text_clip
        ])
        
        return final_clip
    
    def _create_animated_background(self, index: int, duration: float) -> ColorClip:
        """Create animated gradient background"""
        # Create gradient colors
        colors = [
            (41, 128, 185),    # Blue
            (142, 68, 173),    # Purple
            (231, 76, 60),     # Red
            (243, 156, 18),    # Orange
            (46, 204, 113),    # Green
            (52, 152, 219),    # Light Blue
        ]
        
        color = colors[index % len(colors)]
        
        # Create color clip with slight animation
        bg_clip = ColorClip(
            size=self.video_size,
            color=color,
            duration=duration
        )
        
        return bg_clip
    
    def _create_kinetic_text(self, text: str, index: int) -> TextClip:
        """Create kinetic text with animations and effects"""
        # Choose font - prefer bold fonts for impact
        font_paths = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]
        font_path = font_paths[index % len(font_paths)]
        font_size = 70  # Consistent, readable size (YouTube Shorts style)
        
        # Limit text to top portion of screen (not full screen)
        max_width = self.video_size[0] - 150  # More margin
        
        # Create text clip with high quality
        try:
            text_clip = TextClip(
                text,
                fontsize=font_size,
                color='white',
                font=font_path,
                stroke_color='black',
                stroke_width=4,  # Thicker outline for readability (YouTube style)
                method='caption',
                size=(max_width, None),
                align='center',
                bg_color='transparent'
            ).set_position(('center', self.video_size[1] * 0.75))  # Position at bottom (YouTube Shorts subtitle style)
            
            # Add entrance animation
            text_clip = text_clip.set_start(0.2).fadein(0.3)
        except Exception as e:
            print(f"⚠️ Font error ({font_path}), using default: {e}")
            # Fallback to default font
            text_clip = TextClip(
                text,
                fontsize=font_size,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(max_width, None),
                align='center'
            ).set_position(('center', self.video_size[1] * 0.75))
            text_clip = text_clip.set_start(0.1).fadein(0.4)
        
        return text_clip
    
    def _download_media(self, url: str, index: int) -> Optional[str]:
        """Download media from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Determine file extension
            ext = '.jpg'
            if 'video' in response.headers.get('content-type', ''):
                ext = '.mp4'
            elif 'png' in response.headers.get('content-type', ''):
                ext = '.png'
            
            # Save file
            media_path = os.path.join(self.temp_dir, f"media_{index}_{random.randint(10000, 99999)}{ext}")
            with open(media_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded media: {media_path}")
            return media_path
            
        except Exception as e:
            print(f"❌ Error downloading media: {e}")
            return None
    
    def _resize_for_shorts(self, clip) -> VideoFileClip:
        """Resize clip to fit 9:16 aspect ratio for YouTube Shorts"""
        # Get current dimensions
        w, h = clip.size
        
        # Calculate target dimensions (9:16 aspect ratio)
        target_w, target_h = self.video_size
        
        # Calculate scale factor to fill the frame
        scale_w = target_w / w
        scale_h = target_h / h
        scale = max(scale_w, scale_h)  # Use larger scale to fill frame
        
        # Resize
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        clip = clip.resize((new_w, new_h))
        
        # Crop to exact size if needed
        if new_w > target_w or new_h > target_h:
            x_center = new_w // 2
            y_center = new_h // 2
            clip = clip.crop(
                x_center=x_center,
                y_center=y_center,
                width=target_w,
                height=target_h
            )
        
        return clip
    
    def _split_script_into_segments(self, script: str) -> List[str]:
        """Split script into visual segments"""
        import re
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', script)
        segments = [s.strip() for s in sentences if s.strip()]
        
        # Group into segments of 1-2 sentences for better pacing
        grouped = []
        for i in range(0, len(segments), 2):
            group = segments[i:i+2]
            grouped.append(' '.join(group))
        
        return grouped if grouped else [script]
    
    def _combine_audio_video(self, video_clips: List, audio_path: str, duration: float, music_path: Optional[str] = None) -> CompositeVideoClip:
        """Combine video clips with audio and optional background music"""
        if not video_clips:
            # Create a simple placeholder if no clips
            blank_clip = ColorClip(size=self.video_size, color=(0, 0, 0), duration=duration)
            video_clips = [blank_clip]
        
        # Concatenate video clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Add voiceover audio
        audio = AudioFileClip(audio_path)
        
        # If we have background music, mix it with voiceover
        if music_path and os.path.exists(music_path):
            try:
                music = AudioFileClip(music_path)
                # Loop music if shorter than duration
                from moviepy.audio.AudioClip import concatenate_audioclips
                if music.duration < duration:
                    music = concatenate_audioclips([music] * int(duration / music.duration + 1))
                music = music.subclip(0, duration)
                
                # Lower music volume (duck under voiceover)
                music = music.volumex(0.15)  # 15% volume
                audio = audio.volumex(1.0)  # 100% voice volume
                
                # Composite audio
                from moviepy.audio.AudioClip import CompositeAudioClip
                final_audio = CompositeAudioClip([audio, music])
                final_video = final_video.set_audio(final_audio)
                
                print("✅ Background music added")
            except Exception as e:
                print(f"⚠️ Error adding music: {e}, using voiceover only")
                final_video = final_video.set_audio(audio)
        else:
            # Just voiceover
            final_video = final_video.set_audio(audio)
        
        # Ensure exact duration
        final_video = final_video.set_duration(min(duration, final_video.duration))
        
        return final_video