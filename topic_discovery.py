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
from config import Config

class TopicDiscoveryAgent:
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
        
        # Initialize Reddit if credentials provided
        self.reddit = None
        if Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                user_agent=Config.REDDIT_USER_AGENT
            )
    
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
            return topics
        
        try:
            # Check multiple popular subreddits
            subreddits = ['todayilearned', 'Showerthoughts', 'mildlyinteresting', 
                         'LifeProTips', 'AskReddit', 'funny', 'interestingasfuck']
            
            for subreddit_name in subreddits[:3]:  # Limit for API rate limits
                subreddit = self.reddit.subreddit(subreddit_name)
                for post in subreddit.hot(limit=5):
                    if post.score > 100:  # Minimum engagement threshold
                        topics.append({
                            'topic': post.title,
                            'source': f'reddit/{subreddit_name}',
                            'score': min(post.score / 100, 10),  # Normalize score
                            'metadata': {
                                'upvotes': post.score,
                                'comments': post.num_comments,
                                'url': post.url
                            }
                        })
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
            print(f"Error fetching Google Trends: {e}")
        
        return topics
    
    def _get_youtube_trending(self) -> List[Dict]:
        """Get trending topics from YouTube"""
        topics = []
        
        try:
            # Try using pyyoutube library (simpler, uses API key)
            from pyyoutube import Api
            
            # Note: YouTube Data API requires an API key for trending (read-only)
            # This is separate from OAuth credentials
            # User can get free API key from Google Cloud Console
            youtube_api_key = Config.YOUTUBE_CLIENT_ID  # Can use API key for read operations
            
            if youtube_api_key:
                api = Api(api_key=youtube_api_key)
                trending = api.get_videos_by_chart(
                    chart='mostPopular',
                    region_code='US',
                    max_results=10
                )
                
                for item in trending.items:
                    title = item.snippet.title
                    stats = item.statistics
                    view_count = int(stats.viewCount) if stats.viewCount else 0
                    
                    # Score based on view count (normalized)
                    score = min(view_count / 100000, 10)  # 1M views = 10 points
                    
                    topics.append({
                        'topic': title,
                        'source': 'youtube_trending',
                        'score': max(score, 7),  # Trending videos get at least 7
                        'metadata': {
                            'views': view_count,
                            'video_id': item.id
                        }
                    })
        except Exception as e:
            print(f"Error fetching YouTube trends (this is optional): {e}")
            # YouTube trending is optional - continue without it
        
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
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying viral content trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                ai_topics_data = json.loads(content)
                
                for item in ai_topics_data:
                    topics.append({
                        'topic': item.get('topic', ''),
                        'source': 'ai_generated',
                        'score': float(item.get('score', 7)),
                        'metadata': {'reason': item.get('reason', '')}
                    })
            except json.JSONDecodeError:
                print(f"Could not parse AI response as JSON: {content}")
        
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

