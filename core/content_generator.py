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

Based on research showing viral Shorts have 70-90% higher retention with strong hooks, and rewatch rates spike with payoff moments:

1. Script: Write a 30-35 second script (minimum 30s for monetization, optimized for maximum retention) with DATA-BACKED VIRAL characteristics:
   
   **HOOK (First 3 seconds - STATISTICALLY CRITICAL - 70-90% retention boost):**
   - MUST start with a SHOCKING fact, surprising statistic, or intriguing question
   - Examples that work: "Did you know [shocking fact]?" "This will shock you..." "The truth about [surprising thing]..."
   - Create immediate curiosity with a micro-pause (0.5 seconds) after the hook
   - The first 3 seconds determine if viewers stay (data shows this is the critical retention window)
   
   **EMOTIONAL NARRATIVE BODY (Seconds 3-28):**
   - Tell a STORY, not just facts - emotional connection drives shares (statistically proven)
   - Create an arc: Problem → Revelation → Impact (data shows narrative arcs increase engagement)
   - ABSOLUTELY CRITICAL: You MUST write out the COMPLETE, FULL explanation of each point. NEVER say "first point" or "point 1" without immediately following with the actual detailed explanation.
   - MANDATORY Format Example: "First, [STATE THE COMPLETE POINT WITH ALL DETAILS]. For example, if talking about eggs: 'First, eating eggs daily boosts brain function because they contain choline, a nutrient 90% of people are deficient in. This improves memory and cognitive processing within just 2 weeks of consistent consumption.'"
   - ANOTHER MANDATORY Example: "Second, [FULL DETAILED POINT]. 'Second, eggs increase muscle mass significantly. Research shows people who eat eggs daily gain 30% more muscle mass during workouts because eggs provide complete protein with all essential amino acids in the perfect ratio for muscle synthesis.'"
   - THIRD MANDATORY Example: "Third, [FULL DETAILED POINT]. 'Third, eggs improve eye health dramatically. They contain lutein and zeaxanthin, antioxidants that reduce age-related vision loss by up to 40% and protect against macular degeneration, the leading cause of blindness.'"
   - WRONG Example (NEVER DO THIS): "There are three benefits of eating eggs. First benefit. Second benefit. Third benefit." 
   - WRONG Example (NEVER DO THIS): "First point. Second point. Third point."
   - Each point MUST be 7-10 seconds when read aloud, with full explanations, examples, and context
   - Script MUST be 30-35 seconds when read aloud (test it mentally - it should fill the full duration)
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
            
            # Clean invalid control characters MORE AGGRESSIVELY
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            # Also remove any remaining control chars
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
            
            # Try parsing with retry if it fails
            try:
                video_content = json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON if it's wrapped in text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        video_content = json.loads(json_match.group(0))
                    except:
                        raise e
                else:
                    raise e
            
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
