# Complete Setup Guide

This guide will walk you through setting up all required accounts and API keys (all free).

## Step 1: Groq API (AI Content Generation)

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key - you'll need it for `GROQ_API_KEY` in .env

**Note**: Groq free tier is very generous with fast inference.

## Step 2: Reddit API (Trending Topics)

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down and click "create another app..." or "create app"
3. Fill in:
   - **Name**: YShortsGen (or any name)
   - **Type**: script
   - **Description**: YouTube Shorts Generator
   - **About URL**: (leave blank or use a placeholder)
   - **Redirect URI**: http://localhost:8080 (required but not used)
4. Click "create app"
5. You'll see:
   - **Client ID**: The string under your app name (small text)
   - **Client Secret**: The "secret" field
6. Copy both - you'll need them for .env

**Note**: Reddit API is completely free with no quotas for this use case.

## Step 3: Google Cloud / YouTube Setup

### 3a. Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" > "New Project"
3. Name it "YouTube Shorts Generator" (or any name)
4. Click "Create"

### 3b. Enable YouTube Data API v3

1. In your project, go to "APIs & Services" > "Library"
2. Search for "YouTube Data API v3"
3. Click on it and press "Enable"

### 3c. Create OAuth Credentials (for uploading)

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: YouTube Shorts Generator
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue through all steps
4. Back to credentials, create OAuth client ID:
   - Application type: **Desktop app**
   - Name: YouTube Shorts Generator
   - Click "Create"
5. Download the JSON file
6. Rename it to `client_secrets.json` and place in project root

### 3d. Get Channel ID (Optional - for YouTube API key)

For trending data, you can also create an API key:

1. In "Credentials", click "Create Credentials" > "API key"
2. Copy the API key (optional - for trending videos)
3. You can use this for `YOUTUBE_CLIENT_ID` (it serves dual purpose)

### 3e. Run OAuth Setup

1. Make sure `client_secrets.json` is in your project root
2. Run: `python setup_youtube_oauth.py`
3. Browser will open - authorize the app
4. Copy your Channel ID from the output
5. Add to `.env` as `YOUTUBE_CHANNEL_ID`

## Step 4: Hugging Face (Optional)

1. Go to https://huggingface.co/
2. Sign up for free account
3. Go to Settings > Access Tokens
4. Create a new token (read access is enough)
5. Copy token - use for `HUGGINGFACE_API_KEY` in .env (optional)

## Step 5: Gmail App Password (for Email Reports)

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to "App passwords"
4. Select app: "Mail"
5. Select device: "Other (Custom name)" > "YouTube Shorts Generator"
6. Click "Generate"
7. Copy the 16-character password
8. Use this for `EMAIL_PASSWORD` in .env (NOT your regular Gmail password)

## Step 6: Configure .env File

1. Copy `.env.example` to `.env`
2. Fill in all values:

```env
# YouTube (from OAuth setup)
YOUTUBE_CLIENT_ID=your_oauth_client_id_or_api_key
YOUTUBE_CLIENT_SECRET=your_oauth_client_secret
YOUTUBE_REFRESH_TOKEN=auto_generated_when_you_run_setup
YOUTUBE_CHANNEL_ID=your_channel_id_from_setup_script

# AI Services
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_hf_key  # Optional

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=YShortsGen/1.0

# Email
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
REPORT_RECIPIENT=your_email@gmail.com

# Settings
VIDEOS_PER_DAY=3
LOG_LEVEL=INFO
```

## Step 7: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On some systems, you may need to install FFmpeg separately:
- Windows: Download from https://ffmpeg.org/download.html, add to PATH
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## Step 8: Test Run

1. Generate a single video: `python main.py single`
2. Check the output folder for the generated video
3. If successful, start autonomous mode: `python main.py autonomous`

## Troubleshooting

### "No module named 'moviepy'"
- Run: `pip install -r requirements.txt`

### "FFmpeg not found"
- Install FFmpeg and ensure it's in your system PATH
- Test: `ffmpeg -version` should work

### YouTube upload fails
- Check that `token.pickle` exists
- Re-run `python setup_youtube_oauth.py` if needed
- Verify OAuth credentials are correct

### "API key invalid"
- Double-check all API keys in `.env`
- Ensure no extra spaces or quotes
- Verify accounts are activated

### Email not sending
- Use App Password, not regular password
- Check 2FA is enabled on Google account
- Try generating a new app password

## Next Steps

Once everything is set up:

1. The system will generate 3 videos per day automatically
2. You'll receive email reports each evening
3. Videos are uploaded to your YouTube channel
4. Monitor your channel and adjust topics as needed

## Free Tier Limits

All services used are truly free with no payment required:

- **Groq**: Very generous free tier
- **Reddit API**: No limits for this use case
- **Google/YouTube API**: 10,000 units/day free quota (plenty for this)
- **gTTS (Google TTS)**: Free, unlimited
- **Hugging Face**: Free tier with generous limits

Enjoy your autonomous YouTube Shorts generator! 🚀

