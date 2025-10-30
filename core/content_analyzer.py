"""
Content Analyzer - Analyzes video topic/script to determine mood, theme, and style
Used to dynamically select music and voice that matches the content
"""
from typing import Dict, List
from groq import Groq
from core.config import Config
import json
import re

class ContentAnalyzer:
    """Analyzes content to determine appropriate music and voice characteristics"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
    
    def analyze_content(self, topic: str, script: str = "") -> Dict:
        """
        Analyze content to determine:
        - Mood (serious, fun, mysterious, upbeat, dramatic, etc.)
        - Genre (educational, entertainment, news, storytelling, etc.)
        - Energy level (low, medium, high)
        - Voice characteristics (formal, casual, energetic, calm, etc.)
        - Music style (ambient, upbeat, dramatic, minimalist, etc.)
        """
        if not self.groq_client:
            # Fallback analysis without AI
            return self._fallback_analysis(topic, script)
        
        try:
            prompt = f"""Analyze this video content and determine the appropriate style characteristics.

Topic: {topic}
Script: {script[:500] if script else "Not provided"}

Analyze and provide:
1. Mood: (serious, fun, mysterious, upbeat, dramatic, calm, energetic, informative, dramatic, inspirational)
2. Genre: (educational, entertainment, news, storytelling, documentary, viral, lifestyle)
3. Energy Level: (low, medium, high)
4. Voice Style: (formal, casual, energetic, calm, authoritative, friendly, dramatic)
5. Music Style: (ambient, upbeat, dramatic, minimalist, cinematic, electronic, acoustic, orchestral, suspenseful, inspiring)
6. Music Tempo: (slow, medium, fast)
7. Content Theme: (medical, business, history, science, lifestyle, technology, nature, society)

Return JSON format:
{{
    "mood": "mood_name",
    "genre": "genre_name",
    "energy_level": "low/medium/high",
    "voice_style": "voice_style_name",
    "music_style": "music_style_name",
    "music_tempo": "slow/medium/fast",
    "content_theme": "theme_name",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing video content to determine appropriate audio and visual styling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Check if content is empty
            if not content or not content.strip():
                print("⚠️ Content analysis: Empty response from AI, using fallback")
                return self._fallback_analysis(topic, script)
            
            # FIRST: Check if content starts with JSON or is wrapped in text
            content_original = content.strip()
            
            # Check if content is empty
            if not content_original:
                print("⚠️ Content analysis: Empty response from AI, using fallback")
                return self._fallback_analysis(topic, script)
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content_original:
                content_original = content_original.split("```json")[1].split("```")[0].strip()
            elif "```" in content_original:
                content_original = content_original.split("```")[1].split("```")[0].strip()
            
            # Clean invalid control characters
            content_original = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content_original)
            content_original = ''.join(char for char in content_original if char.isprintable() or char in '\n\r\t' or ord(char) >= 32)
            content_original = content_original.encode('utf-8', errors='ignore').decode('utf-8')
            
            # SMART EXTRACTION: If content doesn't start with { or [, extract JSON first
            json_content = content_original.strip()
            
            # Check if content starts with JSON
            if not json_content.startswith('{') and not json_content.startswith('['):
                # Content has text prefix - extract JSON object
                start_idx = json_content.find('{')
                if start_idx == -1:
                    start_idx = json_content.find('[')
                
                if start_idx != -1:
                    # Find matching closing brace/bracket
                    bracket_count = 0
                    end_idx = start_idx
                    open_char = json_content[start_idx]
                    close_char = '}' if open_char == '{' else ']'
                    
                    for i in range(start_idx, len(json_content)):
                        if json_content[i] == open_char:
                            bracket_count += 1
                        elif json_content[i] == close_char:
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx > start_idx:
                        json_content = json_content[start_idx:end_idx]
                        print(f"🔍 Extracted JSON from wrapped text (length: {len(json_content)})")
            
            # Try to parse JSON
            try:
                analysis = json.loads(json_content)
                print(f"✅ Content analyzed: {analysis.get('mood')} {analysis.get('music_style')} {analysis.get('voice_style')}")
                return analysis
            except json.JSONDecodeError as json_error:
                # Last resort: try to find and parse any JSON object in the content
                print(f"⚠️ JSON parse error: {json_error}")
                print(f"⚠️ Attempted JSON content (first 300 chars): {json_content[:300]}")
                
                # Try to find ANY valid JSON object
                start_idx = content_original.find('{')
                if start_idx != -1:
                    bracket_count = 0
                    end_idx = start_idx
                    for i in range(start_idx, len(content_original)):
                        if content_original[i] == '{':
                            bracket_count += 1
                        elif content_original[i] == '}':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx > start_idx:
                        json_str = content_original[start_idx:end_idx]
                        try:
                            analysis = json.loads(json_str)
                            print(f"✅ Content analyzed (fallback extraction): {analysis.get('mood')} {analysis.get('music_style')} {analysis.get('voice_style')}")
                            return analysis
                        except Exception as extract_error:
                            print(f"⚠️ Fallback extraction also failed: {extract_error}")
                
                return self._fallback_analysis(topic, script)
            
        except Exception as e:
            print(f"⚠️ Content analysis error: {e}, using fallback")
            return self._fallback_analysis(topic, script)
    
    def _fallback_analysis(self, topic: str, script: str) -> Dict:
        """Fallback analysis based on keywords"""
        topic_lower = topic.lower() + " " + script.lower()
        
        # Mood detection
        if any(word in topic_lower for word in ['medical', 'health', 'condition', 'disease', 'treatment']):
            mood = "serious"
            music_style = "ambient"
            voice_style = "calm"
        elif any(word in topic_lower for word in ['wealth', 'money', 'rich', 'success', 'millionaire']):
            mood = "inspirational"
            music_style = "upbeat"
            voice_style = "energetic"
        elif any(word in topic_lower for word in ['dark', 'history', 'secret', 'truth', 'hidden']):
            mood = "mysterious"
            music_style = "dramatic"
            voice_style = "dramatic"
        elif any(word in topic_lower for word in ['weird', 'amazing', 'shocking', 'incredible']):
            mood = "energetic"
            music_style = "upbeat"
            voice_style = "energetic"
        else:
            mood = "informative"
            music_style = "minimalist"
            voice_style = "casual"
        
        # Energy level
        if any(word in topic_lower for word in ['amazing', 'shocking', 'incredible', 'wow']):
            energy = "high"
            tempo = "fast"
        elif any(word in topic_lower for word in ['calm', 'peaceful', 'meditation', 'relax']):
            energy = "low"
            tempo = "slow"
        else:
            energy = "medium"
            tempo = "medium"
        
        return {
            "mood": mood,
            "genre": "educational",
            "energy_level": energy,
            "voice_style": voice_style,
            "music_style": music_style,
            "music_tempo": tempo,
            "content_theme": "general",
            "keywords": topic.split()[:5]
        }

