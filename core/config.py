"""
Configuration management for YouTube Shorts Generator
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Video Generation Settings
    VIDEOS_PER_DAY = int(os.getenv("VIDEOS_PER_DAY", "3"))
    VIDEO_DURATION_SECONDS = 60  # YouTube Shorts max is 60 seconds
    TARGET_DURATION_SECONDS = 35  # Minimum 30s for monetization, target 35s
    MIN_DURATION_SECONDS = 30  # Minimum duration for monetization eligibility
    
    # YouTube Settings
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")
    
    # AI Services (All Free Tier)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Free tier, fast
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # Free tier
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Optional backup
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")  # Fallback for Groq
    
    # Reddit API (Free)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "YShortsGen/1.0")
    
    # Email Reporting
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # App password if Gmail
    REPORT_RECIPIENT = os.getenv("REPORT_RECIPIENT", "asaadbalum2@gmail.com")
    
    # Media Providers (Free APIs)
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    
    # Music APIs (All Free, no credit card)
    JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID", "")  # Free tier - no credit card
    JAMENDO_CLIENT_SECRET = os.getenv("JAMENDO_CLIENT_SECRET", "")  # Free tier - no credit card
    JAMENDO_API_KEY = os.getenv("JAMENDO_API_KEY", "")  # Legacy support
    
    # Advanced APIs (Optional)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # Free tier
    # Note: TTS uses Edge TTS (100% free, unlimited) - see core/edge_tts.py
    # Note: Music uses YouTube Audio Library (100% free, no API needed - see docs/FREE_MUSIC_SETUP.md)
    
    # Video Settings
    MAX_TOPICS_TO_ANALYZE = 20
    MIN_TREND_SCORE = 7.0  # Out of 10
    HASHTAG_COUNT = 5  # Optimal for Shorts
    
    # Paths
    TEMP_DIR = "./temp"
    OUTPUT_DIR = "./output"
    ASSETS_DIR = "./assets"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_PATH = "./shorts_db.sqlite"

