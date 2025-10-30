"""
AI Agent for generating video content (scripts, titles, descriptions)
Optimized for YouTube Shorts engagement
"""
from groq import Groq
from typing import Dict, Optional
from core.config import Config
import json
import re

class ContentGenerator:
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
    
    def generate_video_content(self, topic: str) -> Dict:
        """
        Generate complete video content package:
        - Script (text for video)
        - Title (YouTube optimized)
        - Description (with hashtags)
        - Tags
        """
        if not self.groq_client:
            raise ValueError("Groq API key not configured")
        
        prompt = f"""You are an expert at creating viral YouTube Shorts content.

Topic: {topic}

Create a complete YouTube Short video package that maximizes views and engagement:

1. Script: Write a 45-60 second script that:
   - Hooks viewers in the first 3 seconds
   - Is engaging, fast-paced, and easy to follow
   - Uses simple language (8th grade level)
   - Includes 2-3 key points or facts
   - Ends with a call to action or engaging question
   - Has natural pauses for visuals

2. Title: Create a YouTube Shorts title (under 60 chars) that:
   - Is clickable and intriguing
   - Uses power words (shocking, secret, amazing, etc.)
   - Includes numbers if relevant
   - Avoids clickbait but is compelling

3. Description: Write a description (under 200 chars) with:
   - First line is the hook
   - 5 relevant hashtags (trending if possible)
   - Short, scannable format

4. Tags: Provide 10 relevant tags

Format your response as JSON:
{{
    "script": "Full script text here...",
    "title": "Title here",
    "description": "Description with hashtags",
    "tags": ["tag1", "tag2", ...]
}}"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated: using current Groq model
                messages=[
                    {"role": "system", "content": "You are a YouTube Shorts content expert specializing in viral videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            video_content = json.loads(content)
            
            # Ensure hashtags are in description
            if video_content.get('description') and '#' not in video_content['description']:
                tags_for_hashtags = video_content.get('tags', [])[:5]
                hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags_for_hashtags])
                video_content['description'] += f'\n\n{hashtags}'
            
            return video_content
        
        except Exception as e:
            print(f"Error generating content: {e}")
            # Fallback content
            return self._generate_fallback_content(topic)
    
    def _generate_fallback_content(self, topic: str) -> Dict:
        """Fallback if AI generation fails"""
        return {
            "script": f"Today we're talking about {topic}. This is something you probably didn't know. Let me break it down for you. First point, second point, third point. That's why this is so important. What do you think? Comment below!",
            "title": f"The Truth About {topic[:30]}",
            "description": f"Learn about {topic}. #Shorts #Viral #Trending #Education #Facts",
            "tags": ["shorts", "viral", "trending", "education", "facts", "interesting", "amazing", "mindblowing", "top10", "lifestyle"]
        }
    
    def optimize_for_shorts(self, script: str) -> str:
        """Optimize script for YouTube Shorts format"""
        # Split into shorter sentences if needed
        sentences = re.split(r'[.!?]+', script)
        optimized = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Keep sentences under 15 words for better pacing
                words = sentence.split()
                if len(words) > 15:
                    # Split long sentences
                    mid_point = len(words) // 2
                    optimized.append(' '.join(words[:mid_point]) + '.')
                    optimized.append(' '.join(words[mid_point:]) + '.')
                else:
                    optimized.append(sentence + '.')
        
        return ' '.join(optimized)
    
    def generate_hashtags(self, topic: str, count: int = Config.HASHTAG_COUNT) -> list:
        """Generate optimized hashtags for the topic"""
        if not self.groq_client:
            return ["#Shorts", "#Viral", "#Trending", "#Facts", "#Education"]
        
        try:
            prompt = f"""Generate {count} trending hashtags for a YouTube Short about: {topic}
            
            Requirements:
            - Include popular Shorts hashtags (#Shorts, #Viral, etc.)
            - Add topic-specific hashtags
            - Use currently trending tags if possible
            - Return as JSON array: ["#hashtag1", "#hashtag2", ...]"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated: using current Groq model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            hashtags = json.loads(content)
            return hashtags
        
        except Exception as e:
            print(f"Error generating hashtags: {e}")
            return ["#Shorts", "#Viral", "#Trending", "#Facts", "#Education"]

