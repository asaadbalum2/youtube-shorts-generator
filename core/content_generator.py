"""
AI Agent for generating video content (scripts, titles, descriptions)
Optimized for YouTube Shorts engagement based on statistical analysis
"""
from groq import Groq
from typing import Dict, Optional
from core.config import Config
import json
import re
import requests

class ContentGenerator:
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
        self.openrouter_api_key = Config.OPENROUTER_API_KEY
    
    def generate_video_content(self, topic: str) -> Dict:
        """
        Generate complete video content package:
        - Script (text for video)
        - Title (YouTube optimized)
        - Description (with hashtags)
        - Tags
        """
        # Try Groq first, fallback to OpenRouter if needed
        try:
            return self._generate_with_groq(topic)
        except Exception as groq_error:
            print(f"⚠️ Groq failed: {groq_error}, trying OpenRouter fallback...")
            if self.openrouter_api_key:
                try:
                    return self._generate_with_openrouter(topic)
                except Exception as openrouter_error:
                    print(f"⚠️ OpenRouter also failed: {openrouter_error}, using fallback content")
                    return self._generate_fallback_content(topic)
            else:
                print("⚠️ No OpenRouter API key configured, using fallback content")
                return self._generate_fallback_content(topic)
    
    def _generate_with_groq(self, topic: str) -> Dict:
        """Generate content using Groq API"""
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

CRITICAL: Return ONLY raw JSON (no markdown, no code blocks, no text before/after).
Use \\n for newlines inside strings, NOT actual line breaks.

Format (raw JSON only):
{{"script":"Full script text here... use \\n for line breaks","title":"Title here","description":"Description with hashtags","tags":["tag1","tag2"]}}"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a YouTube Shorts content expert. ALWAYS return ONLY valid JSON format with NO markdown, NO code blocks, NO explanations. JSON strings must use \\n for newlines, NOT actual newlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            return self._parse_response(response.choices[0].message.content, topic)
        except Exception as e:
            raise Exception(f"Groq API error: {e}")
    
    def _generate_with_openrouter(self, topic: str) -> Dict:
        """Generate content using OpenRouter API as fallback"""
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")
        
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

3. Description: Write a description (under 200 chars) that:
   - First line is the hook (same as video opening)
   - 5 relevant hashtags (trending if possible)
   - Short, scannable format
   - Includes engagement hook (question or CTA)

4. Tags: Provide 10 relevant tags that:
   - Match the topic/authortopic keywords
   - Include trending variations if possible
   - Cover different search intents

CRITICAL: Return ONLY raw JSON (no markdown, no code blocks, no text before/after).
Use \\n for newlines inside strings, NOT actual line breaks.

Format (raw JSON only):
{{"script":"Full script text here... use \\n for line breaks","title":"Title here","description":"Description with hashtags","tags":["tag1","tag2"]}}"""
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/ViralShortsFactory",
                    "X-Title": "ViralShortsFactory"
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [
                        {"role": "system", "content": "You are a YouTube Shorts content expert. ALWAYS return ONLY valid JSON format with NO markdown, NO code blocks, NO explanations. JSON strings must use \\n for newlines, NOT actual newlines."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return self._parse_response(content, topic)
        except Exception as e:
            raise Exception(f"OpenRouter API error: {e}")
    
    def _parse_response(self, content: str, topic: str) -> Dict:
        """Parse AI response and extract JSON content"""
        # Parse JSON - clean content first
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Check if content is empty before cleaning
            if not content or not content.strip():
                print("⚠️ Content generator: Empty response from AI, using fallback")
                return self._generate_fallback_content(topic)
            
            # EXTRACT JSON FIRST - don't parse the whole response
            # Find JSON object and extract it BEFORE cleaning
            start_idx = content.find('{')
            if start_idx == -1:
                print("⚠️ Content generator: No JSON object found, using fallback")
                return self._generate_fallback_content(topic)
            
            # Find matching closing brace
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
                print("⚠️ Content generator: Invalid JSON structure, using fallback")
                return self._generate_fallback_content(topic)
            
            # Extract JSON string
            json_str = content[start_idx:end_idx]
            
            # Clean invalid control characters from extracted JSON - ULTRA AGGRESSIVE
            # Step 1: Remove ALL control characters (0x00-0x1F, 0x7F-0x9F) except \n, \r, \t
            json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)
            
            # Step 2: Remove any character that's not printable ASCII (32-126) or whitespace
            # But we need to preserve string content inside quotes, so do this carefully
            # First, replace control chars in string values with space
            json_str_clean = ""
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_str):
                if escape_next:
                    json_str_clean += char
                    escape_next = False
                    continue
                
                if char == '\\':
                    json_str_clean += char
                    escape_next = True
                    continue
                
                if char == '"':
                    in_string = not in_string
                    json_str_clean += char
                    continue
                
                # Inside strings: escape newlines and preserve valid characters
                if in_string:
                    if char == '\n':
                        # Escape newlines in strings - JSON requires \n, not actual newline
                        json_str_clean += '\\n'
                    elif char == '\r':
                        # Escape carriage returns
                        json_str_clean += '\\r'
                    elif char == '\t':
                        # Escape tabs
                        json_str_clean += '\\t'
                    elif char == '"':
                        # Escape quotes in strings
                        json_str_clean += '\\"'
                    elif 32 <= ord(char) <= 126:
                        # Printable ASCII - keep as-is
                        json_str_clean += char
                    elif ord(char) < 32 or (127 <= ord(char) <= 159):
                        # Control characters - remove
                        pass  # Skip invalid control chars
                    else:
                        # Other characters - keep but might need escaping
                        json_str_clean += char
                else:
                    # Outside strings: strict ASCII + whitespace
                    if (32 <= ord(char) <= 126) or char in '\n\r\t':
                        json_str_clean += char
            
            json_str = json_str_clean
            
            # Step 3: Clean up any remaining issues
            # Normalize whitespace outside strings (but keep escaped sequences inside strings)
            # This is tricky - we've already escaped newlines in strings, so now we can safely clean outside
            json_str = re.sub(r'[ \t]+', ' ', json_str)  # Multiple spaces to single (outside strings)
            
            # Check if JSON string is empty after cleaning
            if not json_str or not json_str.strip():
                print("⚠️ Content generator: JSON empty after extraction/cleaning, using fallback")
                return self._generate_fallback_content(topic)
            
            # Try parsing the cleaned JSON
            try:
                video_content = json.loads(json_str)
                print(f"✅ JSON parsed successfully")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error: {e}")
                print(f"⚠️ JSON content (first 300 chars): {json_str[:300]}")
                # Last resort: try one more time with raw extraction
                try:
                    # Try direct parse of original content from first {
                    raw_json = content[content.find('{'):]
                    video_content = json.loads(raw_json)
                    print(f"✅ JSON parsed (direct extraction)")
                except:
                    print("⚠️ All JSON parsing attempts failed, using fallback")
                    return self._generate_fallback_content(topic)
            
            # Ensure hashtags are in description
            if video_content.get('description') and '#' not in video_content['description']:
                tags_for_hashtags = video_content.get('tags', [])[:5]
                hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags_for_hashtags])
                video_content['description'] += f'\n\n{hashtags}'
            
            return video_content
    
    def get_post_content_enhancements(self, content: Dict, topic: str) -> Dict:
        """
        Analyze generated content and return enhancement suggestions
        This is called AFTER content generation to suggest improvements
        Uses multiple methods: rule-based, pattern detection, and AI-powered analysis
        """
        enhancements = {
            "script_enhancements": [],
            "title_enhancements": [],
            "description_enhancements": [],
            "tag_enhancements": [],
            "seo_enhancements": [],
            "engagement_enhancements": [],
            "viral_potential_enhancements": [],
            "overall_suggestions": []
        }
        
        script = content.get('script', '')
        title = content.get('title', '')
        description = content.get('description', '')
        tags = content.get('tags', [])
        
        # METHOD 1: Script Quality Analysis
        if len(script) < 200:
            enhancements["script_enhancements"].append("Script is too short - aim for 30-35 seconds of content (minimum 200 chars)")
        elif len(script) > 1500:
            enhancements["script_enhancements"].append("Script may be too long - aim for 30-35 seconds (max ~1500 chars)")
        
        # METHOD 2: Hook Strength Detection
        hook_words = ['did you know', 'shocking', 'truth', 'secret', 'amazing', 'incredible', 'unbelievable', 'wait until', 'this will']
        if not any(word in script.lower()[:100] for word in hook_words):
            enhancements["script_enhancements"].append("Script hook could be stronger - add a shocking fact or intriguing question in first 3 seconds")
        
        # METHOD 3: Awkward Phrase Detection (like "3333 dollars")
        import re
        awkward_numbers = re.findall(r'\b\d{4,}\b', script)
        if awkward_numbers:
            enhancements["script_enhancements"].append(f"Found specific numbers that may sound awkward: {', '.join(awkward_numbers)}. Consider rounding or using 'thousands'")
        
        # METHOD 4: Repetition Detection
        words = script.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        repeated = [word for word, count in word_freq.items() if count > 3]
        if repeated:
            enhancements["script_enhancements"].append(f"High repetition detected: {', '.join(repeated[:3])}. Consider using synonyms for variety")
        
        # METHOD 5: Title Optimization
        if len(title) > 60:
            enhancements["title_enhancements"].append("Title exceeds 60 characters - shorten for better mobile display")
        elif len(title) < 20:
            enhancements["title_enhancements"].append("Title is too short - add more context for better SEO")
        
        power_words = ['shocking', 'secret', 'truth', 'amazing', 'you', 'this', 'how', 'why', 'what', 'top', 'best', 'worst']
        if not any(word in title.lower() for word in power_words):
            enhancements["title_enhancements"].append("Title could be more engaging - add power words to increase CTR")
        
        # METHOD 6: Description Formatting
        if len(description) > 200:
            enhancements["description_enhancements"].append("Description exceeds 200 characters - shorten for better readability")
        elif len(description) < 50:
            enhancements["description_enhancements"].append("Description is too short - add more context and hashtags")
        
        hashtag_count = description.count('#')
        if hashtag_count < 3:
            enhancements["description_enhancements"].append(f"Add more hashtags (currently {hashtag_count}, aim for 5-7) for better discoverability")
        
        # METHOD 7: Tag Validation and SEO
        if len(tags) < 5:
            enhancements["tag_enhancements"].append("Add more tags (aim for 10) for better SEO and discoverability")
        elif len(tags) > 15:
            enhancements["tag_enhancements"].append("Too many tags (YouTube recommends 10-15 max) - remove less relevant ones")
        
        # Check tag relevance to topic
        topic_words = set(topic.lower().split())
        tag_words = set(' '.join(tags).lower().split())
        overlap = len(topic_words.intersection(tag_words))
        if overlap < 2:
            enhancements["tag_enhancements"].append("Tags don't match topic well - add more topic-relevant keywords")
        
        # METHOD 8: SEO Optimization
        if topic.lower() not in title.lower():
            enhancements["seo_enhancements"].append("Topic keyword not in title - add it for better SEO")
        
        if topic.lower() not in description.lower()[:100]:
            enhancements["seo_enhancements"].append("Topic keyword not in first 100 chars of description - add it early for SEO")
        
        # METHOD 9: Engagement Optimization
        question_words = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        has_question = any(word in script.lower() for word in question_words) or '?' in script
        if not has_question:
            enhancements["engagement_enhancements"].append("Add a question to script to encourage comments and engagement")
        
        cta_words = ['comment', 'like', 'subscribe', 'share', 'save', 'follow']
        has_cta = any(word in script.lower()[-200:] for word in cta_words)
        if not has_cta:
            enhancements["engagement_enhancements"].append("Add a call-to-action at the end (e.g., 'Comment below!', 'Save this!') to boost engagement")
        
        # METHOD 10: Viral Potential Analysis
        emotional_words = ['shocking', 'amazing', 'incredible', 'unbelievable', 'mind-blowing', 'jaw-dropping']
        emotional_count = sum(1 for word in emotional_words if word in script.lower())
        if emotional_count < 2:
            enhancements["viral_potential_enhancements"].append("Add more emotional/impactful words to increase shareability")
        
        # Check for numbers/statistics (viral content often has stats)
        has_stats = bool(re.search(r'\d+%|\d+\s+(million|billion|thousand)', script.lower()))
        if not has_stats:
            enhancements["viral_potential_enhancements"].append("Add statistics or numbers to make content more shareable and credible")
        
        # METHOD 11: AI-Powered Analysis (if API available)
        try:
            ai_suggestions = self._get_ai_enhancement_suggestions(content, topic)
            if ai_suggestions:
                enhancements["overall_suggestions"].extend(ai_suggestions)
        except Exception as e:
            # Silently fail - AI suggestions are optional
            pass
        
        # Overall suggestions
        total_issues = sum(len(v) for k, v in enhancements.items() if k != "overall_suggestions")
        if total_issues == 0:
            enhancements["overall_suggestions"].append("✅ Content quality looks excellent! All checks passed.")
        elif total_issues <= 2:
            enhancements["overall_suggestions"].append(f"✅ Content is good with {total_issues} minor improvements suggested")
        else:
            enhancements["overall_suggestions"].append(f"⚠️ Content has {total_issues} areas for improvement - review suggestions above")
        
        return enhancements
    
    def _get_ai_enhancement_suggestions(self, content: Dict, topic: str) -> list:
        """Use AI to provide additional enhancement suggestions"""
        try:
            prompt = f"""Analyze this YouTube Shorts content and provide 2-3 specific improvement suggestions:

Topic: {topic}
Title: {content.get('title', '')}
Script (first 200 chars): {content.get('script', '')[:200]}

Provide 2-3 specific, actionable suggestions to improve viral potential and engagement.
Return as a simple list, one suggestion per line."""
            
            # Try Groq first
            if self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a YouTube Shorts optimization expert. Provide concise, actionable suggestions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    suggestions = response.choices[0].message.content.strip().split('\n')
                    return [s.strip('- •') for s in suggestions if s.strip()][:3]
                except:
                    pass
            
            # Fallback to OpenRouter
            if self.openrouter_api_key:
                import requests
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/llama-3.1-8b-instruct:free",
                        "messages": [
                            {"role": "system", "content": "You are a YouTube Shorts optimization expert. Provide concise, actionable suggestions."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 200
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    suggestions = response.json()['choices'][0]['message']['content'].strip().split('\n')
                    return [s.strip('- •') for s in suggestions if s.strip()][:3]
        except:
            pass
        
        return []
    
    def _generate_fallback_content(self, topic: str) -> Dict:
        """Fallback if AI generation fails"""
        return {
            "script": f"Today we're talking about {topic}. This is something you probably didn't know. First, let me explain the key details about this topic and why it matters to you. Second, there are important implications that affect your daily life in ways you might not realize. Third, understanding this can change how you see the world around you. That's why this topic is so important and worth learning about. What do you think? Comment below!",
            "title": f"The Truth About {topic[:30]}",
            "description": f"Discover the shocking truth about {topic}. #shorts #facts #viral",
            "tags": [topic.lower().split()[0], "facts", "shorts", "viral", "truth"]
        }
