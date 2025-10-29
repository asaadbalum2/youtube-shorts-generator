# Replit Deployment Guide - Truly Free, No Credit Card! 🎉

**Replit is 100% free with no credit card required - perfect for autonomous operation!**

## ✅ What You Get:
- Free hosting with no credit card
- Runs 24/7 (doesn't sleep if you have Replit Hacker plan, or use "Always On" feature)
- Easy setup - all in browser
- Perfect for our YouTube Shorts generator

---

## Step 1: Create Replit Account

1. **Go to**: https://replit.com/
2. **Click**: "Sign up" (top right)
3. **Sign up** with:
   - Google account (easiest)
   - Or email
4. **No credit card needed!**

---

## Step 2: Create GitHub Repository (or use existing)

1. **Go to**: https://github.com/
2. **Sign in** (create account if needed - free)
3. **Click**: "+" → "New repository"
4. **Name**: `youtube-shorts-generator` (or any name)
5. **Choose**: Private (recommended)
6. **Click**: "Create repository"

---

## Step 3: Upload Your Code to GitHub

### Option A: Using GitHub Web Interface

1. In your new repository, click "uploading an existing file"
2. **Drag and drop ALL your project files**:
   - All `.py` files
   - `requirements.txt`
   - `config.py`
   - `README.md`
   - Everything EXCEPT:
     - `.env` (don't upload this - contains secrets!)
     - `token.pickle`
     - `temp/` folder
     - `output/` folder
3. **Click**: "Commit changes"

### Option B: Using Git (if you have it)

```bash
cd C:\Users\SoulsTaker7\YShortsGen
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

---

## Step 4: Import to Replit

1. **Go to**: https://replit.com/
2. **Click**: "Create Repl" (or "+" button)
3. **Select**: "Import from GitHub"
4. **Paste**: Your GitHub repository URL
5. **Language**: Select "Python"
6. **Name**: `youtube-shorts-generator`
7. **Click**: "Import from GitHub"

---

## Step 5: Add Environment Variables (API Keys)

1. **In Replit**, look for the "Secrets" icon (🔒) in the left sidebar
   - Or click the "Secrets" tab
2. **Click**: "New secret"
3. **Add each secret one by one**:

```
Name: GROQ_API_KEY
Value: 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
```

```
Name: REDDIT_CLIENT_ID
Value: xYQpnTvdFazG5Kj4NAYJ_Q
```

```
Name: REDDIT_CLIENT_SECRET
Value: YE-cUcxK8CZ3GN0ubS9SuIC-8n059Q
```

```
Name: REDDIT_USER_AGENT
Value: YShortsGen/1.0
```

```
Name: YOUTUBE_CLIENT_ID
Value: 545895166701-g9qft1iae4tb24mf0t2br3dm2j89deip.apps.googleusercontent.com
```

```
Name: YOUTUBE_CLIENT_SECRET
Value: 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
```

```
Name: YOUTUBE_REFRESH_TOKEN
Value: 1//03jBFWhalGDg2CgYIARAAGAMSNwF-L9IrqF8PhucH0z4c3fLJQ8bL10d27Mj17b4Aa4qAvGJ7mbFH2w7V9KOWqePnsjdVglVfJxs
```

```
Name: YOUTUBE_CHANNEL_ID
Value: 4Y6O0ubwl0_ZQsLq2EteTQ
```

```
Name: VIDEOS_PER_DAY
Value: 3
```

```
Name: LOG_LEVEL
Value: INFO
```

**Add all of them!** Click "New secret" for each one.

---

## Step 6: Install FFmpeg

1. **In Replit**, open the **Shell** tab (bottom panel)
2. **Run**:
```bash
pkg install ffmpeg
```

Or if that doesn't work:
```bash
apt-get update && apt-get install -y ffmpeg
```

---

## Step 7: Install Python Dependencies

**In Replit Shell**, run:
```bash
pip install -r requirements.txt
```

This may take 5-10 minutes.

---

## Step 8: Create .env File (or use Replit Secrets)

Since we're using Replit Secrets, the environment variables are automatically available!
But if needed, you can create `.env`:
```bash
touch .env
```

Then add content (but Secrets method above is better).

---

## Step 9: Configure for Always-On (Important!)

Replit free tier can "sleep" after inactivity. To keep it running:

### Option A: Replit Hacker Plan (Free for students/education)
- Apply at: https://replit.com/learn/getting-started-with-replit-hacker
- Gets you "Always On"

### Option B: Use a Keep-Alive Script

Create `keep_alive.py`:
```python
from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "YouTube Shorts Generator is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

keep_alive()

# Now run your main app
from main import YouTubeShortsGenerator
generator = YouTubeShortsGenerator()
generator.start_autonomous_mode()
```

### Option C: Use UptimeRobot (External Ping)

1. Sign up at: https://uptimerobot.com/ (free)
2. Add monitor pointing to your Repl URL
3. Pings every 5 minutes to keep it awake

---

## Step 10: Run Your App

**In Replit Shell**, run:
```bash
python main.py autonomous
```

**Or** modify `.replit` file to auto-run:
```toml
run = "python main.py autonomous"
```

---

## Step 11: Keep It Running

### Method 1: Replit Always-On (If you have Hacker plan)
- Just run and leave it - it stays on

### Method 2: UptimeRobot Ping (Free)
- Keeps pinging your Repl every 5 minutes
- Prevents it from sleeping

### Method 3: External Cron Job
- Use a free service like cron-job.org
- Pings your Repl URL every 5 minutes

---

## Monitoring

### View Logs:
- Check Replit console/output panel
- Or check `shorts_generator.log` file

### Check Your YouTube Channel:
- Videos will appear automatically!

---

## Important Notes:

⚠️ **Replit Free Tier Limitations:**
- May sleep after 1 hour of inactivity (unless pinged)
- Use UptimeRobot or similar to keep it alive
- Or upgrade to Hacker plan (free for students)

✅ **Solution**: Use UptimeRobot (completely free) to ping your Repl every 5 minutes - keeps it awake!

---

## Alternative: If Replit Doesn't Work

**Other truly free options (no credit card):**

1. **Glitch.com** - Free, but can sleep
2. **Heroku** - Free tier discontinued
3. **PythonAnywhere** - Free tier with limitations
4. **Fly.io** - Free tier, requires credit card (won't charge)

**Best option for you**: **Replit + UptimeRobot** = Completely free, runs 24/7!

---

## That's It!

Your YouTube Shorts generator is now running on Replit!

- ✅ 100% free (no credit card)
- ✅ Runs 24/7 (with UptimeRobot ping)
- ✅ Fully autonomous
- ✅ All error recovery included

**Just set up UptimeRobot to ping your Repl every 5 minutes and you're done!** 🚀

