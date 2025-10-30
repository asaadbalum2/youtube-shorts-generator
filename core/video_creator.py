"""
Video creation module - generates YouTube Shorts videos
Uses FFmpeg/MoviePy for video processing
"""
import os
import random
from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import tempfile
from typing import Dict, Optional
from core.config import Config

class VideoCreator:
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
        self.output_dir = Config.OUTPUT_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_video(self, content: Dict, topic: str) -> str:
        """
        Create a YouTube Shorts video from content
        
        Returns: Path to created video file
        """
        script = content.get('script', '')
        
        # 1. Generate audio (TTS)
        audio_path = self._generate_audio(script)
        
        # 2. Calculate duration
        audio_clip = AudioFileClip(audio_path)
        duration = min(audio_clip.duration, Config.TARGET_DURATION_SECONDS)
        
        # 3. Create visual sequence
        video_clips = self._create_visuals(script, duration, topic)
        
        # 4. Combine audio and visuals
        final_video = self._combine_audio_video(video_clips, audio_path, duration)
        
        # 5. Export video
        video_id = f"short_{topic.replace(' ', '_')[:20]}_{random.randint(1000, 9999)}"
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='slow',  # Better quality
            bitrate='8000k',  # Higher bitrate
            audio_bitrate='192k',  # Better audio quality
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Cleanup
        audio_clip.close()
        final_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return output_path
    
    def _generate_audio(self, script: str) -> str:
        """Generate TTS audio from script with better quality"""
        # Use slower, more natural speech
        tts = gTTS(text=script, lang='en', slow=True)  # Slower for better quality
        audio_path = os.path.join(self.temp_dir, f"audio_{random.randint(10000, 99999)}.mp3")
        tts.save(audio_path)
        return audio_path
    
    def _create_visuals(self, script: str, duration: float, topic: str) -> list:
        """
        Create visual sequence for the video
        Uses AI-generated or styled images with text overlays
        """
        clips = []
        
        # Split script into segments (roughly by sentences)
        segments = self._split_script_into_segments(script)
        segment_duration = duration / len(segments) if segments else duration
        
        for i, segment in enumerate(segments):
            # Create text-based image for each segment
            image_path = self._create_text_image(segment, topic, i)
            
            # Convert to video clip
            img_clip = ImageClip(image_path)
            img_clip = img_clip.set_duration(segment_duration)
            img_clip = img_clip.set_fps(30)
            
            clips.append(img_clip)
            
            # Cleanup temp image
            if os.path.exists(image_path) and i > 0:  # Keep first for debugging
                pass  # Keep for now
        
        return clips
    
    def _create_text_image(self, text: str, topic: str, index: int) -> str:
        """Create a styled image with text overlay"""
        # Canvas size for YouTube Shorts (9:16 aspect ratio)
        width, height = 1080, 1920
        
        # Create image with gradient background
        img = Image.new('RGB', (width, height), color=self._get_gradient_color(index))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            # Try different font paths with larger sizes
            font_sizes = [140, 120, 100, 80]  # Larger fonts
            font = None
            for size in font_sizes:
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                    break
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
                        break
                    except:
                        try:
                            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
                            break
                        except:
                            pass
            
            if not font:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Word wrap text
        lines = self._wrap_text(text, font, width - 200)
        
        # Calculate text positioning (centered)
        # Get line height
        if hasattr(draw, 'textbbox'):
            test_bbox = draw.textbbox((0, 0), 'A', font=font)
            line_height = test_bbox[3] - test_bbox[1]
        else:
            try:
                line_height = font.getsize('A')[1]
            except:
                line_height = 60
        
        total_height = len(lines) * line_height * 1.2
        start_y = (height - total_height) // 2
        
        # Draw text with outline for readability
        y_offset = start_y
        for line in lines:
            # Calculate text width
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                try:
                    text_width = draw.textsize(line, font=font)[0]
                except:
                    text_width = len(line) * 20
            
            x = (width - text_width) // 2
            
            # Draw text shadow/outline
            for adj in range(-2, 3):
                for adjy in range(-2, 3):
                    draw.text((x + adj, y_offset + adjy), line, font=font, fill=(0, 0, 0, 200))
            
            # Draw main text
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255))
            y_offset += int(line_height * 1.2)
        
        # Save image
        image_path = os.path.join(self.temp_dir, f"frame_{index}_{random.randint(10000, 99999)}.png")
        img.save(image_path)
        
        return image_path
    
    def _get_gradient_color(self, index: int) -> tuple:
        """Generate gradient colors for visual variety"""
        colors = [
            (41, 128, 185),    # Blue
            (142, 68, 173),    # Purple
            (231, 76, 60),     # Red
            (243, 156, 18),    # Orange
            (46, 204, 113),    # Green
            (52, 152, 219),    # Light Blue
        ]
        return colors[index % len(colors)]
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Estimate width (rough approximation)
            test_width = len(test_line) * 30  # Rough estimate
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _split_script_into_segments(self, script: str) -> list:
        """Split script into visual segments"""
        # Split by sentences
        import re
        sentences = re.split(r'[.!?]+', script)
        segments = [s.strip() for s in sentences if s.strip()]
        
        # Group into segments of 2-3 sentences for better pacing
        grouped = []
        for i in range(0, len(segments), 2):
            group = segments[i:i+3]
            grouped.append(' '.join(group))
        
        return grouped if grouped else [script]
    
    def _combine_audio_video(self, video_clips: list, audio_path: str, duration: float) -> CompositeVideoClip:
        """Combine video clips with audio"""
        if not video_clips:
            # Create a simple placeholder if no clips
            blank_clip = ImageClip(np.zeros((1920, 1080, 3), dtype=np.uint8))
            blank_clip = blank_clip.set_duration(duration)
            video_clips = [blank_clip]
        
        # Concatenate video clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Add audio
        audio = AudioFileClip(audio_path)
        final_video = final_video.set_audio(audio)
        
        # Ensure exact duration
        final_video = final_video.set_duration(min(duration, final_video.duration))
        
        return final_video

