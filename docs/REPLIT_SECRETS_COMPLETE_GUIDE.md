# 📋 Complete Replit Secrets Setup Guide

## ✅ Required Secrets (All Must Be Set)

### 1. **Groq API** - AI Content Generation
```
GROQ_API_KEY=your_groq_api_key_here
```
- **Get it:** https://console.groq.com/ → Sign up (free) → API Keys → Create
- **Required:** YES - App won't work without it

### 2. **YouTube OAuth** - Video Uploads
```
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
YOUTUBE_CHANNEL_ID=your_channel_id_here
```
- **Get it:** Google Cloud Console → Create OAuth 2.0 credentials
- **Required:** YES - Videos won't upload without these
- **Setup Guide:** See `docs/guides/SIMPLE_YOUTUBE_SETUP.md`

### 3. **Pexels/Pixabay** - B-Roll Visuals (CRITICAL!)
```
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
```
- **Get Pexels:** https://www.pexels.com/api/ → Sign up (free)
- **Get Pixabay:** https://pixabay.com/api/docs/ → Sign up (free)
- **Required:** YES - Without these, videos will have only color backgrounds
- **Note:** You need AT LEAST ONE of these

### 4. **Jamendo** - Trending Music (Automatic)
```
JAMENDO_CLIENT_ID=your_jamendo_client_id
JAMENDO_CLIENT_SECRET=your_jamendo_client_secret
```
- **Get it:** https://developer.jamendo.com/ → Register (free, no credit card)
- **Required:** NO - But recommended for trending music
- **Benefit:** Gets trending tracks automatically (updated weekly)

---

## ⭐ Optional Secrets (Improve Quality)

### 5. **Reddit API** - Trending Topics
```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=YShortsGen/1 OP
```
- **Get it:** https://www.reddit.com/prefs/apps → Create app (type: script)
- **Required:** NO - System uses AI topic描述 if not configured
- **Benefit:** Finds trending topics from Reddit

### 6. **Email Reports** - Daily Statistics
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
REPORT_RECIPIENT=your_email@gmail.com
```
- **Setup:** Enable 2FA on Google → Generate App Password
- **Required:** NO - Reports won't be sent if not configured
- **Default:** `REPORT_RECIPIENT` defaults to `asaadbalum2@gmail.com`

---

## ⚙️ Configuration Secrets

### 7. **Video Settings**
```
VIDEOS_PER_DAY=3
LOG_LEVEL=INFO
```
- **Required:** NO - Has defaults
- **VIDEOS_PER_DAY:** Number of videos to generate daily (default: 3)
- **LOG_LEVEL:** INFO, DEBUG, WARNING, ERROR (default: INFO)

### 8. **Web Dashboard** (If Using Dashboard)
```
SESSION_SECRET=random_secret_string_here
```
- **Required:** NO - Only if using web dashboard
- **Generate:** Any random string (for session encryption)

---

## 📊 Complete Checklist

Copy this to verify you have everything:

### ✅ Required (Must Have):
- [ ] `GROQ_API_KEY`
- [ ] `YOUTUBE_CLIENT_ID`
- [ ] `YOUTUBE_CLIENT_SECRET`
- [ ] `YOUTUBE_REFRESH_TOKEN`
- [ ] `YOUTUBE_CHANNEL_ID`
- [ ] `PEXELS_API_KEY` OR `PIXABAY_API_KEY` (at least one!)

### ⭐ Recommended (Improves Quality):
- [ ] `JAMENDO_CLIENT_ID`
- [ ] `JAMENDO_CLIENT_SECRET`
- [ ] `REDDIT_CLIENT_ID`
- [ ] `REDDIT_CLIENT_SECRET`
- [ ] `REDDIT_USER_AGENT`

### ⚙️ Optional (Nice to Have):
- [ ] `VIDEOS_PER_DAY` (default: 3)
- [ ] `LOG_LEVEL` (default: INFO)
- [ ] `EMAIL_ADDRESS`
- [ ] `EMAIL_PASSWORD`
- [ ] `REPORT_RECIPIENT`
- [ ] `SESSION_SECRET`

---

## 🔍 How to Verify Secrets

### In Replit:
1. Go to **Secrets** tab (🔒 icon)
2. Check that all secrets above are listed
3. Make sure values are correct (not empty)

### In Code:
When app starts, you should see:
- ✅ `"✅ Groq client initialized"`
- ✅ `"✅ Pexels provider initialized"` OR `"✅ Pixabay provider initialized"`
- ✅ `"✅ Reddit client initialized"` (if Reddit secrets are set)

### Test Generation:
1. Generate a test video
2. Check console logs for errors
3. Verify b-roll visuals appear (not just colors)
4. Verify music is added

---

## ⚠️ Common Issues

### "No visuals, only color backgrounds"
- **Cause:** Missing `PEXELS_API_KEY` or `PIXABAY_API_KEY`
- **Fix:** Add at least one of these secrets

### "Error generating content"
- **Cause:** Missing or invalid `GROQ_API_KEY`
- **Fix:** Verify Groq API key is correct

### "Upload failed: invalid token"
- **Cause:** Missing or expired `YOUTUBE_REFRESH_TOKEN`
- **Fix:** Regenerate refresh token (see token setup guide)

---

## 📚 Related Documentation

- **YouTube Setup:** `docs/guides/SIMPLE_YOUTUBE_SETUP.md`
- **Quick Start:** `docs/guides/QUICKSTART.md`
- **Full Setup:** `docs/guides/SETUP_GUIDE.md`
- **API Keys Guide:** `API_KEYS_NEEDED.md`

---

## ✅ You're Done!

Once all required secrets are set, your app is ready to generate and upload videos automatically! 🚀

