"""Quick script to verify Secrets are loaded"""
import os
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

print("Checking environment variables...")
print()

secrets = {
    'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
    'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
    'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
    'YOUTUBE_CLIENT_ID': os.getenv('YOUTUBE_CLIENT_ID'),
    'YOUTUBE_REFRESH_TOKEN': os.getenv('YOUTUBE_REFRESH_TOKEN'),
}

for key, value in secrets.items():
    if value:
        # Show first/last few chars for security
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✅ {key}: {masked}")
    else:
        print(f"❌ {key}: NOT FOUND")

print()
print("If any are missing, check Replit Secrets tab!")

