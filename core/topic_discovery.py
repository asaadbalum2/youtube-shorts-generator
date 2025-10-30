"""
AI Agent for discovering trending topics from multiple sources
Optimized for maximum views potential
"""
import praw
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from groq import Groq
import json
from core.config import Config

class TopicDiscoveryAgent:
    def __init__(self):
        # Check if Groq API key is valid (not empty)
        if Config.GROQ_API_KEY and Config.GROQ_API_KEY.strip() and not Config.GROQ_API_KEY.startswith('your_'):
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                print("✅ Groq client initialized")
            except Exception as e:
                print(f"⚠️ Groq client initialization failed: {e}")
                self.groq_client = None
        else:
            print("⚠️ Groq API key not configured")
            self.groq_client = None
        
        # Initialize Reddit if credentials provided
        self.reddit = None
        if (Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_ID.strip() and 
            Config.REDDIT_CLIENT_SECRET and Config.REDDIT_CLIENT_SECRET.strip() and
            not Config.REDDIT_CLIENT_ID.startswith('your_')):
            try:
                self.reddit = praw.Reddit(
                    client_id=Config.REDDIT_CLIENT_ID,
                    client_secret=Config.REDDIT_CLIENT_SECRET,
                    user_agent=Config.REDDIT_USER_AGENT
                )
                # Test with a simple read-only operation
                try:
                    _ = list(self.reddit.subreddit('test').hot(limit=1))
                    print("✅ Reddit client initialized and tested")
                except Exception as test_error:
                    # Reddit API may require valid credentials - this is expected if not configured
                    self.reddit = None
            except Exception as e:
                print(f"⚠️ Reddit client initialization failed: {e}")
                self.reddit = None
        else:
            print("⚠️ Reddit credentials not configured")
            self.reddit = None
    
    def discover_trending_topics(self) -> List[Dict]:
        """
        Discover trending topics from multiple sources
        Returns list of topics with scores (0-10)
        """
        all_topics = []
        
        # 1. Reddit Trending
        reddit_topics = self._get_reddit_trending()
        all_topics.extend(reddit_topics)
        
        # 2. Google Trends (using API)
        trends_topics = self._get_google_trends()
        all_topics.extend(trends_topics)
        
        # 3. YouTube Trending
        youtube_topics = self._get_youtube_trending()
        all_topics.extend(youtube_topics)
        
        # 4. AI-generated viral topics
        ai_topics = self._get_ai_generated_topics()
        all_topics.extend(ai_topics)
        
        # Score and rank all topics
        scored_topics = self._score_topics(all_topics)
        
        # Sort by score and return top ones
        scored_topics.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_topics[:Config.MAX_TOPICS_TO_ANALYZE]
    
    def _get_reddit_trending(self) -> List[Dict]:
        """Get trending topics from Reddit"""
        topics = []
        
        if not self.reddit:
            # Reddit not available - this is OK, we use AI generation as primary source
            pass
            return topics
        
        try:
            # Check multiple popular subreddits
            subreddits = ['todayilearned', 'Showerthoughts', 'mildlyinteresting', 
                         'LifeProTips', 'AskReddit', 'funny', 'interestingasfuck']
            
            for subreddit_name in subreddits[:2]:  # Reduce to 2 to avoid rate limits
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts = list(subreddit.hot(limit=3))  # Reduce to 3 posts per subreddit
                    
                    for post in posts:
                        if post.score > 50:  # Lower threshold to get more results
                            topics.append({
                                'topic': post.title,
                                'source': f'reddit/{subreddit_name}',
                                'score': min(post.score / 50, 10),  # Adjust normalization
                                'metadata': {
                                    'upvotes': post.score,
                                    'comments': post.num_comments,
                                    'url': post.url
                                }
                            })
                            
                except Exception as subreddit_error:
                    print(f"⚠️ Error accessing subreddit {subreddit_name}: {subreddit_error}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Reddit trends: {e}")
        
        return topics
    
    def _get_google_trends(self) -> List[Dict]:
        """Get trending topics from Google Trends"""
        topics = []
        
        try:
            # Use pytrends library (we'll install it)
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-US', tz=360)
            trending_searches = pytrends.trending_searches(pn='united_states')
            
            for i, trend in enumerate(trending_searches.head(10).values):
                topic_text = str(trend[0])
                # Score based on position (higher position = higher score)
                score = 10 - (i * 0.5)
                
                topics.append({
                    'topic': topic_text,
                    'source': 'google_trends',
                    'score': max(score, 5),  # Minimum 5
                    'metadata': {'position': i + 1}
                })
        except Exception as e:
            # Google Trends API issues are common - silently skip, we have other sources
            pass
        
        return topics
    
    def _get_youtube_trending(self) -> List[Dict]:
        """Get trending topics from YouTube"""
        topics = []
        
        # Skip YouTube trending (pyyoutube not available, and not critical)
        # We have Reddit, Google Trends, and AI generation which is enough
        return topics
    
    def _get_ai_generated_topics(self) -> List[Dict]:
        """Use AI to generate potentially viral topics"""
        topics = []
        
        if not self.groq_client:
            return topics
        
        try:
            prompt = """Generate 5 viral YouTube Shorts topic ideas that are currently trending or likely to go viral. 
            Focus on:
            - Educational facts people don't know
            - Mind-blowing statistics
            - Life hacks or tips
            - Interesting comparisons
            - Shocking revelations
            
            Format as JSON array: [{"topic": "...", "reason": "why it's viral", "score": 1-10}]"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated: using current Groq model
                messages=[
                    {"role": "system", "content": "You are an expert at identifying viral content trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response - handle text-wrapped JSON arrays
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Clean invalid control characters
                import re
                content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
                content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
                
                # Try direct JSON parsing first
                try:
                    ai_topics_data = json.loads(content)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON array from text
                    # Look for JSON array pattern: [{...}]
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        try:
                            ai_topics_data = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            # Try cleaning point by point - find individual objects
                            # Look for all {topic: ...} objects in the text
                            objects = re.findall(r'\{[^{}]*"topic"[^{}]*\}', content)
                            if objects:
                                ai_topics_data = []
                                for obj_str in objects:
                                    try:
                                        obj = json.loads(obj_str)
                                        ai_topics_data.append(obj)
                                    except:
                                        continue
                            else:
                                raise json.JSONDecodeError("No JSON array or objects found", content, 0)
                    else:
                        raise json.JSONDecodeError("No JSON array found", content, 0)
                
                # Process topics
                if isinstance(ai_topics_data, list):
                    for item in ai_topics_data:
                        if isinstance(item, dict) and 'topic' in item:
                            topics.append({
                                'topic': item.get('topic', ''),
                                'source': 'ai_generated',
                                'score': float(item.get('score', 7)),
                                'metadata': {'reason': item.get('reason', '')}
                            })
                
                if topics:
                    print(f"✅ Generated {len(topics)} AI topics")
                else:
                    print(f"⚠️ No valid topics extracted from AI response")
                    
            except json.JSONDecodeError as e:
                print(f"Could not parse AI response as JSON: {e}")
                print(f"⚠️ Raw content (first 500 chars): {content[:500]}")
            except Exception as parse_error:
                print(f"⚠️ Error parsing topics: {parse_error}")
                print(f"⚠️ Raw content (first 500 chars): {content[:500]}")
        
        except Exception as e:
            print(f"Error generating AI topics: {e}")
        
        return topics
    
    def _score_topics(self, topics: List[Dict]) -> List[Dict]:
        """Intelligently score topics based on multiple factors"""
        scored = []
        
        for topic in topics:
            base_score = topic.get('score', 5)
            
            # Additional scoring factors
            title = topic.get('topic', '').lower()
            
            # Boost for engaging keywords
            engagement_keywords = ['secret', 'hidden', 'shocking', 'amazing', 'incredible', 
                                 'you won\'t believe', 'top 10', 'vs', 'comparison', 'never knew']
            keyword_boost = sum(1 for keyword in engagement_keywords if keyword in title) * 0.5
            
            # Boost for question format (higher engagement)
            if '?' in topic.get('topic', ''):
                keyword_boost += 1
            
            # Boost for numbers (lists perform well)
            import re
            if re.search(r'\d+', topic.get('topic', '')):
                keyword_boost += 0.5
            
            final_score = min(base_score + keyword_boost, 10)
            
            scored.append({
                **topic,
                'score': round(final_score, 2)
            })
        
        return scored
    
    def select_best_topic(self, min_score: float = Config.MIN_TREND_SCORE) -> Optional[Dict]:
        """Select the best topic from discovered trends"""
        topics = self.discover_trending_topics()
        
        # Filter by minimum score
        filtered = [t for t in topics if t['score'] >= min_score]
        
        if not filtered:
            # If no topics meet threshold, take top one anyway
            filtered = topics[:1]
        
        return filtered[0] if filtered else None

