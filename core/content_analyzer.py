"""
Content Analyzer - Analyzes video content to determine mood, style, and characteristics
"""
import json
import re
from typing import Dict
from core.config import Config
from groq import Groq


class ContentAnalyzer:
    """Analyzes content to determine mood, music style, and voice characteristics"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
    
    def analyze_content(self, topic: str, script: str) -> Dict:
        """
        Analyze video content to determine appropriate mood, music, and voice style
        
        Returns:
            Dictionary with mood, music_style, voice_style, energy_level, etc.
        """
        try:
            prompt = f"""Analyze this video content and determine the appropriate styling:

Topic: {topic}
Script: {script[:500]}

Return ONLY a valid JSON object with this exact structure:
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
                    {"role": "system", "content": "You are an expert at analyzing video content to determine appropriate audio and visual styling. ALWAYS return ONLY valid JSON, no other text."},
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
            
            # STEP 1: Extract JSON from markdown code blocks if present
            json_content = None
            
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_content = content.split("```")[1].split("```")[0].strip()
            
            # STEP 2: If not in code blocks, extract JSON object from text
            if not json_content:
                # Find the first { which should be the start of the JSON object
                start_idx = content.find('{')
                if start_idx == -1:
                    print("⚠️ Content analysis: No JSON object found, using fallback")
                    return self._fallback_analysis(topic, script)
                
                # Find the matching closing brace
                bracket_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(content)):
                    if content[i] == '{':
                        bracket_count += 1
                    elif content[i] == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx <= start_idx:
                    print("⚠️ Content analysis: Invalid JSON structure, using fallback")
                    return self._fallback_analysis(topic, script)
                
                json_content = content[start_idx:end_idx]
                print(f"🔍 Extracted JSON from text (length: {len(json_content)})")
            
            # STEP 3: Clean the extracted JSON
            if not json_content or not json_content.strip():
                print("⚠️ Content analysis: Extracted JSON is empty, using fallback")
                return self._fallback_analysis(topic, script)
            
            # Clean invalid control characters
            json_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', json_content)
            json_content = ''.join(char for char in json_content if char.isprintable() or char in '\n\r\t' or ord(char) >= 32)
            json_content = json_content.encode('utf-8', errors='ignore').decode('utf-8')
            
            if not json_content or not json_content.strip():
                print("⚠️ Content analysis: JSON content empty after cleaning, using fallback")
                return self._fallback_analysis(topic, script)
            
            # STEP 4: Parse the cleaned JSON
            try:
                analysis = json.loads(json_content)
                print(f"✅ Content analyzed: {analysis.get('mood')} {analysis.get('music_style')} {analysis.get('voice_style')}")
                return analysis
            except json.JSONDecodeError as json_error:
                print(f"⚠️ JSON parse error: {json_error}")
                print(f"⚠️ JSON content (first 300 chars): {json_content[:300]}")
                # Last resort: try to re-extract and parse
                try:
                    start_idx = content.find('{')
                    if start_idx != -1:
                        bracket_count = 0
                        end_idx = start_idx
                        for i in range(start_idx, len(content)):
                            if content[i] == '{':
                                bracket_count += 1
                            elif content[i] == '}':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    end_idx = i + 1
                                    break
                        if end_idx > start_idx:
                            json_str = content[start_idx:end_idx]
                            analysis = json.loads(json_str)
                            print(f"✅ Content analyzed (retry): {analysis.get('mood')} {analysis.get('music_style')} {analysis.get('voice_style')}")
                            return analysis
                except:
                    pass
                return self._fallback_analysis(topic, script)
            
        except Exception as e:
            print(f"⚠️ Content analysis error: {e}, using fallback")
            import traceback
            traceback.print_exc()
            return self._fallback_analysis(topic, script)
    
    def _fallback_analysis(self, topic: str, script: str) -> Dict:
        """Fallback analysis based on keywords"""
        topic_lower = topic.lower() + " " + script.lower()
        
        # Determine mood
        if any(word in topic_lower for word in ["shocking", "dark", "secret", "truth", "hidden", "revealed"]):
            mood = "dramatic"
        elif any(word in topic_lower for word in ["tip", "hack", "trick", "how to", "guide"]):
            mood = "informative"
        elif any(word in topic_lower for word in ["funny", "hilarious", "laugh", "comedy"]):
            mood = "lighthearted"
        else:
            mood = "informative"
        
        # Determine voice style
        if mood == "dramatic":
            voice_style = "authoritative"
        elif mood == "informative":
            voice_style = "professional"
        else:
            voice_style = "casual"
        
        # Determine music style
        if mood == "dramatic":
            music_style = "cinematic"
        elif mood == "informative":
            music_style = "ambient"
        else:
            music_style = "upbeat"
        
        return {
            "mood": mood,
            "genre": "educational",
            "energy_level": "medium",
            "voice_style": voice_style,
            "music_style": music_style,
            "music_tempo": "medium",
            "content_theme": "general",
            "keywords": topic.lower().split()[:5]
        }
