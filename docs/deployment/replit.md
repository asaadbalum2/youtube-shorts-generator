# YouTube Shorts Generator

## Project Overview

This is an AI-powered YouTube Shorts generator that autonomously creates and uploads short-form videos to YouTube. The system discovers trending topics from multiple sources (Reddit, Google Trends, AI analysis), generates engaging content, creates videos with text overlays and TTS narration, and automatically uploads them to YouTube.

## Current State

The project has been successfully imported and configured for Replit:

- ✅ Python 3.11 installed and configured
- ✅ All Python dependencies installed (with version compatibility fixes)
- ✅ FFmpeg installed for video processing
- ✅ Workflow configured to run in autonomous mode
- ✅ Directory structure created (temp/, output/, assets/)
- ⚠️ **Requires API keys and credentials to run** (see Setup Required below)

## Project Architecture

### Core Components

1. **main.py** - Main orchestrator
   - Manages the video generation workflow
   - Coordinates all components
   - Handles scheduling and autonomous operation

2. **topic_discovery.py** - AI-powered topic discovery
   - Aggregates trending topics from Reddit, Google Trends, YouTube
   - Uses Groq AI to generate viral topic ideas
   - Scores and ranks topics by viral potential

3. **content_generator.py** - AI content creation
   - Generates video scripts using Groq AI
   - Creates optimized titles, descriptions, and tags
   - Formats content for maximum engagement

4. **video_creator.py** - Video production
   - Creates videos with text overlays
   - Adds TTS narration using Google Text-to-Speech
   - Uses MoviePy and FFmpeg for video processing

5. **youtube_uploader.py** - YouTube integration
   - Handles OAuth authentication
   - Uploads videos to YouTube
   - Manages video metadata and publishing

6. **scheduler.py** - Autonomous scheduling
   - Schedules video generation at optimal times
   - Spreads videos throughout the day for maximum reach

7. **database.py** - SQLite database
   - Tracks generated videos and their performance
   - Stores trending topics and statistics

## Setup Required

### 1. API Keys and Credentials

You need to configure the following environment variables in Replit Secrets:

#### Required Credentials:

**Groq AI** (for content generation):
- `GROQ_API_KEY` - Get from https://console.groq.com/ (free tier available)

**Reddit API** (for trending topics):
- `REDDIT_CLIENT_ID` - From https://www.reddit.com/prefs/apps
- `REDDIT_CLIENT_SECRET` - From https://www.reddit.com/prefs/apps
- `REDDIT_USER_AGENT` - e.g., "YShortsGen/1.0"

**YouTube OAuth** (for uploading videos):
- `YOUTUBE_CLIENT_ID` - From Google Cloud Console
- `YOUTUBE_CLIENT_SECRET` - From Google Cloud Console
- `YOUTUBE_REFRESH_TOKEN` - Generated via OAuth flow
- `YOUTUBE_CHANNEL_ID` - Your YouTube channel ID

#### Optional Credentials:

**Email Reporting** (for daily reports):
- `EMAIL_ADDRESS` - Gmail address
- `EMAIL_PASSWORD` - Gmail app password (not regular password)
- `REPORT_RECIPIENT` - Email to receive reports

**Hugging Face** (optional AI fallback):
- `HUGGINGFACE_API_KEY` - From https://huggingface.co/

#### Configuration:
- `VIDEOS_PER_DAY` - Number of videos to generate daily (default: 3)
- `LOG_LEVEL` - Logging level (default: INFO)

### 2. YouTube OAuth Setup

To get YouTube credentials, follow these steps:

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download credentials as `client_secrets.json`
6. Run the setup script locally to get the refresh token
7. Add the credentials to Replit Secrets

**Note**: The YouTube OAuth flow requires interactive browser authentication, which is typically done locally first. See the project's `SETUP_GUIDE.md` for detailed instructions.

### 3. Directory Structure

```
.
├── main.py                 # Main entry point
├── config.py              # Configuration management
├── topic_discovery.py     # Topic discovery agent
├── content_generator.py   # AI content generator
├── video_creator.py       # Video creation
├── youtube_uploader.py    # YouTube upload handler
├── scheduler.py           # Scheduling system
├── database.py            # Database management
├── email_reporter.py      # Email reporting
├── error_recovery.py      # Error handling
├── requirements.txt       # Python dependencies
├── temp/                  # Temporary files (gitignored)
├── output/                # Generated videos (gitignored)
└── assets/                # Video assets (gitignored)
```

## How to Run

The project has 3 operating modes:

### 1. Autonomous Mode (Default)
Runs continuously with scheduled video generation:
```bash
python main.py autonomous
```

This is the default workflow configured in Replit. Videos are generated at optimal times throughout the day.

### 2. Batch Mode
Generate multiple videos immediately:
```bash
python main.py batch 5
```

### 3. Single Video Mode
Generate one video immediately:
```bash
python main.py single
```

## Recent Changes

**2025-10-29**: Initial Replit setup
- Fixed requirements.txt compatibility issues:
  - Updated groq package to >=0.33.0 (was 0.3.1)
  - Updated pytrends to >=4.9.2 (was 5.0.3)
  - Removed pyyoutube (package not available)
  - Removed built-in modules from requirements (smtplib, email, sqlite3)
- Fixed NumPy compatibility issue (downgraded to <2 for OpenCV)
- Added type hints to fix LSP errors (Optional imports)
- Updated .gitignore for Python and Replit environment
- Created workflow for autonomous mode

## Tech Stack

- **Language**: Python 3.11
- **AI/ML**: Groq API, Hugging Face, OpenAI (optional)
- **Video Processing**: MoviePy, FFmpeg, Pillow, OpenCV
- **Audio**: Google Text-to-Speech (gTTS)
- **Data Sources**: Reddit API (PRAW), Google Trends (pytrends)
- **YouTube**: Google API Python Client, OAuth 2.0
- **Scheduling**: APScheduler
- **Database**: SQLite

## User Preferences

(To be updated as you work with the project)

## Troubleshooting

### Common Issues

1. **"No refresh token available"** - This is expected on first run. You need to:
   - Set up YouTube OAuth credentials
   - Run the OAuth flow to get a refresh token
   - Add credentials to Replit Secrets

2. **NumPy compatibility errors** - Already fixed (using numpy<2)

3. **Missing API keys** - Add all required credentials to Replit Secrets

4. **Video generation fails** - Check:
   - All API keys are valid
   - FFmpeg is installed (already done)
   - Temp and output directories exist (already created)

## Next Steps

To get this project running:

1. **Add API credentials** to Replit Secrets (see Setup Required above)
2. **Set up YouTube OAuth** following the project's documentation
3. **Test with single video mode** first: `python main.py single`
4. **Switch to autonomous mode** once working: `python main.py autonomous`

## Notes

- This is a console application (not a web server)
- Workflow is configured to run in console mode
- The app will fail until you provide the required API credentials
- All generated videos and temporary files are automatically gitignored
- The database (shorts_db.sqlite) tracks all generated content and statistics
