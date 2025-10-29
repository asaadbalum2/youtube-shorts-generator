# Deployment-First Guide 🚀

**No local installation needed!** Deploy directly to free hosting.

## Where Dependencies Are Installed

✅ **On the hosting platform** - All hosting platforms automatically install dependencies during deployment
✅ **You don't install anything locally** - Just push code and configure

## Step-by-Step: Deploy Without Local Setup

### Step 1: Get All API Keys (Do this first - 10 minutes)

You'll need these API keys/credentials. Get them all before deploying:

#### 🔑 Groq API Key
1. Go to https://console.groq.com/
2. Sign up (free)
3. API Keys → Create API Key
4. **Copy and save this key**

#### 🔑 Reddit API Credentials  
1. Go to https://www.reddit.com/prefs/apps
2. Scroll down → "create another app..." or "create app"
3. Fill in:
   - **Name**: YShortsGen
   - **Type**: script
   - **Redirect URI**: `http://localhost:8080` (any placeholder works)
4. Click "create app"
5. **Copy these**:
   - Client ID (the small text under your app name)
   - Secret (click "secret" to reveal)
6. **Save both**

#### 🔑 Google Cloud / YouTube Setup
1. Go to https://console.cloud.google.com/
2. Create new project (or use existing)
3. Enable "YouTube Data API v3":
   - APIs & Services → Library
   - Search "YouTube Data API v3"
   - Click → Enable
4. Create OAuth credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - If first time, configure consent screen:
     * User Type: External
     * App name: YouTube Shorts Generator
     * Your email for support
     * Save and Continue (skip optional steps)
   - Back to credentials:
     * Application type: **Desktop app**
     * Name: YouTube Shorts Generator
     * Create
   - **Download the JSON file** - save it somewhere, you'll upload it

**⚠️ SPECIAL NOTE FOR YOUTUBE OAUTH:**
- For hosting, we'll use a method that works without local browser
- Save the downloaded JSON - we'll convert it to environment variables

#### 🔑 Gmail App Password (for email reports)
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" (if not already)
3. Go to "App passwords"
4. Select: App = "Mail", Device = "Other" (name it "Shorts Generator")
5. Generate → **Copy the 16-character password**

---

### Step 2: Choose Your Hosting Platform

Pick one:

#### **Option A: Railway (Easiest, Recommended)** ⭐
- Free tier: $5/month credit (enough for this project)
- Auto-installs dependencies
- Best for beginners

#### **Option B: Replit (Truly Free, No Card)**
- Completely free
- No credit card needed
- Good for testing

#### **Option C: Oracle Cloud (Best for 24/7, Truly Free)**
- Always free VPS
- No credit card needed
- Runs 24/7 continuously

---

### Step 3: Deploy to Railway (Recommended)

#### 3a. Upload Your Code

**Option 1: Via GitHub (Recommended)**
1. Create a GitHub account if you don't have one
2. Create a new repository
3. Upload all project files:
   - Either use GitHub Desktop, or
   - Use Git: `git init`, `git add .`, `git commit -m "Initial commit"`, `git push`

**Option 2: Via Railway CLI**
1. Install Railway CLI: `npm i -g @railway/cli` (if you have Node.js)
2. Run `railway login`
3. Run `railway init` in your project folder

#### 3b. Deploy on Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project"
4. Choose "Deploy from GitHub repo" (or "Empty Project" if using CLI)
5. Select your repository
6. Railway will detect Python and start building automatically

#### 3c. Configure Environment Variables

In Railway dashboard:

1. Click on your project
2. Go to "Variables" tab
3. Add these variables one by one (from the API keys you collected):

```
GROQ_API_KEY=your_groq_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=YShortsGen/1.0
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_gmail_app_password
REPORT_RECIPIENT=your_email@gmail.com
VIDEOS_PER_DAY=3
LOG_LEVEL=INFO
```

#### 3d. Set Up YouTube OAuth (For Hosting)

Since we can't open a browser on the server, we'll use a token-based approach:

**Method 1: Pre-generate Token (Easier)**

1. **Temporarily run locally** (one-time only):
   - You need Python installed just for this one step
   - Place the `client_secrets.json` file in project folder
   - Run: `python setup_youtube_oauth.py`
   - This creates `token.pickle`
   - Open `token.pickle` → extract the refresh token
   
2. **OR use this helper script** (I'll create it):
   - Run: `python get_youtube_token.py`
   - Follow browser prompts
   - It will output your refresh token and channel ID

3. Add to Railway variables:
   ```
   YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
   YOUTUBE_CHANNEL_ID=your_channel_id_here
   ```

**Method 2: Direct Token Generation**

I'll create a web-based tool URL you can use, or you can run one local command.

4. Also add from your `client_secrets.json`:
   ```json
   // Open client_secrets.json and find:
   {
     "installed": {
       "client_id": "...",
       "client_secret": "..."
     }
   }
   ```
   ```
   YOUTUBE_CLIENT_ID=the_client_id_value
   YOUTUBE_CLIENT_SECRET=the_client_secret_value
   ```

#### 3e. Watch It Deploy

1. Railway will automatically:
   - ✅ Install Python dependencies (`pip install -r requirements.txt`)
   - ✅ Install FFmpeg
   - ✅ Start your application
   
2. Check "Deployments" tab for build logs
3. Check "Logs" tab for runtime logs

4. You should see: "Starting autonomous mode..."

---

### Step 4: Deploy to Replit (Alternative - No Card)

1. Go to https://replit.com/
2. Sign up (free)
3. Click "Create Repl"
4. Choose "Import from GitHub"
5. Enter your GitHub repo URL
6. Click "Import"

**Configure:**
1. Click the "Secrets" (🔒) tab on the left
2. Add all environment variables (same as Railway above)
3. Click "Run" button
4. In the shell, run: `python main.py autonomous`

**Note**: Replit may sleep after inactivity. For always-on, you might need to keep the tab open or upgrade.

---

### Step 5: Deploy to Oracle Cloud (Best Free VPS)

See detailed steps in `DEPLOYMENT.md` under "Option 4: Oracle Cloud"

**Quick version:**
1. Sign up at https://www.oracle.com/cloud/free/
2. Create a VM instance (free tier)
3. SSH into it
4. Install Python, Git, FFmpeg
5. Clone your repo
6. Install dependencies: `pip3 install -r requirements.txt`
7. Configure `.env` file with all API keys
8. Run: `python3 main.py autonomous`

---

## Summary: What Happens Where

| Step | Where It Happens |
|------|----------------|
| Get API Keys | Your web browser (groq.com, reddit.com, etc.) |
| Upload Code | GitHub or hosting platform |
| **Install Dependencies** | **Automatically on hosting platform** |
| Configure Variables | Hosting platform dashboard |
| YouTube OAuth | One-time: local OR via helper script |
| App Runs | On hosting platform 24/7 |

## Dependencies Installation - YOU DON'T DO THIS!

The hosting platform does this automatically when you deploy:

- Railway: Reads `requirements.txt` → runs `pip install -r requirements.txt` automatically
- Replit: Same - auto-installs on first run
- Render: Uses `buildCommand` from config → auto-installs
- Oracle Cloud: You run `pip3 install -r requirements.txt` once via SSH

**You never run `pip install` locally unless you want to test first.**

---

## Troubleshooting

**"Where do I run pip install?"**
→ You don't! The hosting platform does it automatically.

**"How do I test before deploying?"**
→ If you want to test locally first, install Python 3.8+, then `pip install -r requirements.txt` in the project folder. But it's not required.

**"YouTube OAuth won't work on server"**
→ I'll create a helper script that generates tokens you can copy-paste. Or use the method in Step 3d above.

**"Which hosting is truly free?"**
→ Replit and Oracle Cloud are 100% free. Railway gives $5/month free credit.

---

## Next Steps After Deployment

1. ✅ Check hosting platform logs - should see "Starting autonomous mode"
2. ✅ Wait for first video generation (depends on schedule)
3. ✅ Check your YouTube channel for uploaded videos
4. ✅ Check email for daily reports
5. ✅ Monitor logs if something seems wrong

Your app is now running in the cloud! 🎉

---

Need the YouTube OAuth helper script? Let me know and I'll create it!

