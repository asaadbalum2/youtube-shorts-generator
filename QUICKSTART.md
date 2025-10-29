# Quick Start Guide ⚡

Get up and running in 15 minutes!

## ⚠️ IMPORTANT: Deployment vs Local

**For hosting deployment** (recommended): See `DEPLOY_FIRST_GUIDE.md`
- Dependencies install automatically on hosting
- No local installation needed
- Deploy directly to Railway/Replit/Oracle Cloud

**For local testing** (optional):
- Install Python 3.8+ on your computer
- Then follow steps below

## Prerequisites Checklist

- [ ] Google account with YouTube channel
- [ ] Gmail account (for reports)
- [ ] (Optional) Python 3.8+ if testing locally

## Step 1: Install Dependencies (Only if testing locally!)

**⚠️ Skip this if deploying to hosting!** Hosting platforms auto-install dependencies.

**Only run this if you want to test on your computer first:**

```bash
pip install -r requirements.txt
```

**Windows users**: May need FFmpeg:
- Download from https://ffmpeg.org/download.html
- Add to system PATH

## Step 2: Get API Keys (5 min)

### Groq API (Required)
1. Go to https://console.groq.com/
2. Sign up → API Keys → Create
3. Copy key

### Reddit API (Required - 2 min)
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Type: **script**, Name: **YShortsGen**
4. Redirect URI: `http://localhost:8080`
5. Copy Client ID (small text) and Secret

### YouTube Setup (5 min)
1. Go to https://console.cloud.google.com/
2. New Project → Enable "YouTube Data API v3"
3. Credentials → OAuth Client ID → Desktop app
4. Download JSON → rename to `client_secrets.json`

**For hosting deployment:**
5. Run: `python get_youtube_token.py` (one-time, locally)
6. Copy the 4 tokens shown (for hosting environment variables)

**For local testing:**
5. Run: `python setup_youtube_oauth.py`
6. Copy Channel ID from output

### Gmail App Password (2 min)
1. https://myaccount.google.com/security
2. Enable 2FA (if not done)
3. App passwords → Mail → Generate
4. Copy 16-char password

## Step 3: Configure (1 min)

1. Copy `env_template.txt` to `.env`
2. Fill in all values from Step 2

## Step 4: Test (2 min)

```bash
python main.py single
```

This generates and uploads ONE video. Check:
- `output/` folder for video file
- Your YouTube channel for uploaded video

## Step 5: Go Autonomous! 🚀

```bash
python main.py autonomous
```

The system will now:
- Generate 3 videos daily at optimal times
- Upload automatically to YouTube
- Send you daily email reports
- Run continuously

**Press Ctrl+C to stop**

## Need Help?

- Full setup: See `SETUP_GUIDE.md`
- Deployment: See `DEPLOYMENT.md`
- Issues: Check `shorts_generator.log`

## What's Next?

- Monitor your YouTube channel
- Adjust `VIDEOS_PER_DAY` in `.env` if needed
- Check email reports for daily stats
- Let it run and watch the views! 📈

---

**That's it!** Your autonomous YouTube Shorts generator is running. 🎉

