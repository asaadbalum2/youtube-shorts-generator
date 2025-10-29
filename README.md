# YouTube Shorts Generator 🤖📹

A fully autonomous AI-powered system that generates and uploads YouTube Shorts videos daily, optimized for maximum views and engagement.

## Features

- 🤖 **AI-Powered Content Generation**: Uses Groq AI and multiple data sources to identify viral topics
- 📊 **Multi-Source Trend Analysis**: Aggregates trends from Reddit, Google Trends, YouTube Trending, and AI-generated topics
- 🎬 **Automated Video Creation**: Generates videos with text overlays, TTS narration, and optimized formatting
- 📺 **YouTube Upload Integration**: Automatically uploads videos with optimized titles, descriptions, and tags
- ⏰ **Fully Autonomous**: Runs continuously with scheduled daily video generation
- 📧 **Email Reports**: Sends daily performance reports
- 💰 **100% Free**: Uses only free-tier APIs and services

## Tech Stack

- **AI Services**: Groq API (free tier), Hugging Face (free)
- **Video Processing**: MoviePy, FFmpeg, Pillow
- **Audio**: Google Text-to-Speech (free)
- **Data Sources**: Reddit API (free), Google Trends API (free), YouTube Data API (free)
- **Hosting**: Configurable for Railway, Render, Replit, or self-hosted

## 🚀 Quick Start (Choose Your Path)

### Option A: Deploy to Hosting (Recommended - No Local Install!)

**For hosting deployment**: See [`DEPLOY_FIRST_GUIDE.md`](DEPLOY_FIRST_GUIDE.md)
- ✅ Dependencies install automatically on hosting
- ✅ No Python installation needed locally
- ✅ Just get API keys and deploy
- **Start here if deploying to Railway/Replit/Oracle Cloud**

### Option B: Test Locally First

**For local testing**: Follow steps below
- Install Python 3.8+ on your computer
- Install dependencies locally
- Test before deploying

---

## Setup Instructions (For Local Testing)

### 1. Prerequisites

- Python 3.8+ (only if testing locally)
- Google account with YouTube channel
- Free API keys for:
  - Groq (https://console.groq.com/)
  - Reddit (https://www.reddit.com/prefs/apps)
  - Hugging Face (optional, https://huggingface.co/)

### 2. Install Dependencies (Only for local testing!)

**⚠️ Skip this if deploying to hosting!** Hosting platforms auto-install.

```bash
pip install -r requirements.txt
```

### 3. YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download credentials as `client_secrets.json`
6. Run the setup script:

```bash
python setup_youtube_oauth.py
```

This will:
- Open a browser for OAuth authentication
- Save your credentials to `token.pickle`
- Display your Channel ID (add to .env)

### 4. Configure Environment

1. Copy `.env.example` to `.env`
2. Fill in all required values:

```env
# YouTube (from OAuth setup)
YOUTUBE_CHANNEL_ID=your_channel_id_here

# AI Services
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_hf_key  # Optional

# Reddit API (create at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=YShortsGen/1.0

# Email (for reports)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password  # Use App Password, not regular password
REPORT_RECIPIENT=your_email@gmail.com

# Settings
VIDEOS_PER_DAY=3
```

### 5. Gmail App Password Setup

For email reports, you need a Gmail App Password:

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google Account Settings](https://myaccount.google.com/)
3. Security > 2-Step Verification > App passwords
4. Generate an app password for "Mail"
5. Use this password in `EMAIL_PASSWORD`

## Usage

### Autonomous Mode (Recommended)

Runs continuously with scheduled video generation:

```bash
python main.py autonomous
```

Videos will be generated at optimal times (2pm, 4pm, 8pm, 10pm by default).

### Batch Generation

Generate multiple videos immediately:

```bash
python main.py batch 5  # Generate 5 videos
```

### Single Video

Generate and upload one video:

```bash
python main.py single
```

## Deployment

### Option 1: Railway (Recommended)

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Deploy: `railway up`

Railway provides free tier with $5/month credit.

### Option 2: Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py autonomous`

Note: Free tier spins down after 15min inactivity (may not work for scheduled tasks).

### Option 3: Replit

1. Import this repository to Replit
2. Configure secrets in Replit Secrets tab
3. Run `python main.py autonomous`

### Option 4: Self-Hosted (Oracle Cloud Free Tier)

Oracle Cloud provides a free VPS:

1. Sign up at [Oracle Cloud](https://www.oracle.com/cloud/free/)
2. Create an Always Free Compute instance
3. SSH into the instance
4. Install Python, Git, and dependencies
5. Clone and run this project

## Configuration

Edit `config.py` to customize:

- `VIDEOS_PER_DAY`: Number of videos per day (default: 3)
- `VIDEO_DURATION_SECONDS`: Target video length
- `MIN_TREND_SCORE`: Minimum trend score threshold (0-10)
- `HASHTAG_COUNT`: Number of hashtags per video

## How It Works

1. **Topic Discovery**: AI agent analyzes multiple sources (Reddit, Google Trends, YouTube) to find viral topics
2. **Content Generation**: Groq AI creates optimized scripts, titles, and descriptions
3. **Video Creation**: System generates visuals with text overlays and adds TTS narration
4. **Upload**: Automatically uploads to YouTube with optimized metadata
5. **Reporting**: Sends daily email reports with statistics

## Database

SQLite database tracks:
- Generated videos and their status
- Trending topics discovered
- Daily statistics (views, likes, uploads)

Database file: `shorts_db.sqlite`

## Logging

Logs are written to:
- Console output
- `shorts_generator.log` file

## Troubleshooting

### YouTube Upload Fails
- Check that `token.pickle` exists and is valid
- Verify YouTube API quotas haven't been exceeded
- Ensure video file is valid MP4 format

### No Topics Found
- Check API keys are valid
- Verify internet connection
- Reduce `MIN_TREND_SCORE` in config if needed

### Email Not Sending
- Verify Gmail App Password is correct
- Check 2FA is enabled
- Ensure SMTP isn't blocked by firewall

## Future Enhancements

The system is designed to be easily enhanced. You can request:
- Integration with additional data sources
- Improved video creation (AI-generated images, animations)
- Better trend analysis algorithms
- Performance analytics dashboard
- A/B testing for titles and descriptions

## License

Free to use and modify for your needs.

## Support

For issues or questions, check the logs in `shorts_generator.log`.

## Important Notes

⚠️ **YouTube Terms of Service**: Ensure your content complies with YouTube's policies. Automated uploads are allowed but must follow community guidelines.

⚠️ **Rate Limits**: Free API tiers have rate limits. The system includes delays to respect these limits.

⚠️ **Content Quality**: While optimized for views, always monitor your channel and adjust topics/content as needed.

# youtube-shorts-generator
