"""
AI Agent for generating video content (scripts, titles, descriptions)
Optimized for YouTube Shorts engagement based on statistical analysis
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
        
        prompt = f"""You are an expert at creating viral YouTube Shorts content based on statistical analysis and data-backed insights from 2024-2025 research.

Topic: {topic}

Based on research showing viral Shorts have 70-90% higher retention with strong hooks, and rewatch rates spike Diesel payoff moments:

1. Script: Write a 30-35 second script (minimum 30s for monetization, optimized for maximum retention) with DATA-BACKED VIRAL characteristics:
   
   **HOOK (First 3 seconds - STATISTICALLY CRITICAL - 70-90% retention boost):**
   - MUST start with a SHOCKING fact, surprising statistic, or intriguing question
   - Examples that work: "Did you know [shocking fact]?" "This will shock you..." "The truth about [surprising thing]..."
   - Create immediate curiosity with a micro-pause (0.5 seconds) after the hook
   - The first 3 seconds determine if viewers stay (data shows this is the critical retention window)
   
   **EMOTIONAL NARRATIVE BODY (Seconds 3-25):**
   - Tell a STORY, not just facts - emotional connection drives shares (statistically proven)
   - Create an arc: Problem → Revelation → Impact (data shows narrative arcs increase engagement)
   - ACTUALLY STATE each key point clearly (don't say "there are 3 points" - LIST THEM!)
   - Format: "First, [point with emotion]. Here's why this matters: [impact]. Second, [point]. This changes everything because [emotional connection]. Third, [point]. [Why this is shocking/important]."
   - Match pacing rhythmically: Energetic topics = faster, flowing rhythm | Serious topics = measured, impactful rhythm
   - Use simple language (8th grade level) but with emotional weight
   - Include micro-pauses between points (1 second) for visual transitions
   
   **PAYOFF MOMENT (Last 5 seconds - CRITICAL for rewatch loops):**
   - Must end with either:
     a) Surprising reveal that makes viewers rewatch (drives replay rate - key algorithm signal)
     b) Thought-provoking question that drives comments (engagement signal)
     c) Strong CTA that creates saves/shares (algorithm boost)
   - Examples: "Wait until you see point 3 - it'll blow your mind!", "Comment what shocked you most!", "Save this if [value proposition]!"
   - This payoff moment should make viewers want to watch again or share immediately
   
   **RHYTHM & PACING (Data-driven requirement):**
   - Match speech rhythm to content mood (proven to improve retention)
   - Use strategic pauses for visual impact (0.5-1 second between major points)
   - Vary pace to maintain engagement (faster for exciting facts, slower for impact)
   
   Ensure natural visual pause points for b-roll transitions between key segments.

2. Title: Create a YouTube Shorts title (under 60 chars) that:
   - Is clickable and intriguing
   - Uses power words (shocking, secret, amazing, etc.)
   - Includes numbers if relevant
   - Avoids clickbait but is compelling
   - Matches the hook from the script (consistency improves CTR)

3. Description: Write a description (under 200 chars) with:
   - First line is the hook (same as video opening)
   - 5 relevant hashtags (trending if possible)
   - Short, scannable format
   - Includes engagement hook (question or CTA)

4. Tags: Provide 10 relevant tags that:
   - Match the topic/authortopic keywords
   - Include trending variations if possible
   - Cover different search intents

Format your response as JSON:
{{
    "script": "Full script text here...",
    "title": "Title here",
    "description": "Description with hashtags",
    "tags": ["tag1", "tag2", ...]
}}"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a YouTube Shorts content expert specializing in viral videos. Your scripts are backed by statistical analysis showing what makes content go viral."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON - clean content first
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Clean invalid control characters
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            
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
            "description": f"Discover the shocking truth about {topic}. #shorts #facts #viral",
            "tags": [topic.lower().split()[0], "facts", "shorts", "viral", "truth"]
        }
