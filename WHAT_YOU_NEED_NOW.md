# 🚀 What You Need Right Now - Quick Guide

## ✅ **REQUIRED** (App won't work without these):

### 1. **Groq API Key** ⚠️ **REQUIRED**
- **What it does:** Generates video scripts, titles, descriptions
- **Get it:** https://console.groq.com/ → Sign up (free) → API Keys → Create
- **Where to add:** Replit Secrets → `GROQ_API_KEY`
- **No fallback** - app will crash without it

### 2. **YouTube OAuth** ⚠️ **REQUIRED** (if you want to upload videos)
- **What it does:** Uploads videos to your YouTube channel
- **Get it:** https://console.cloud.google.com/
- **Steps:**
  1. Create project → Enable "YouTube Data API v3"
  2. Create OAuth Client ID (Desktop app)
  3. Download JSON or copy Client ID/Secret
  4. Run token setup script (see YouTube setup guides)
- **Where to add:** Replit Secrets → `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CHANNEL_ID`
- **Note:** If you skip this, videos will generate but won't upload (they'll be saved locally)

---

## ⏭️ **OPTIONAL** (Has fallbacks, but improves quality):

### 3. **ElevenLabs API** ⭐ **RECOMMENDED** (Better voice quality)
- **What it does:** High-quality text-to-speech (better than gTTS)
- **Get it:** https://elevenlabs.io/ → Sign up (free 10K chars/month)
- **Where to add:** Replit Secrets → `ELEVENLABS_API_KEY`
- **Fallback:** Uses gTTS (free but lower quality) if not configured
- **Status:** Videos work without it, just lower quality voice

### 4. **Reddit API** ⭐ **RECOMMENDED** (Topic discovery)
- **What it does:** Finds trending topics from Reddit
- **Get it:** https://www.reddit.com/prefs/apps → Create app (type: script)
- **Where to add:** Replit Secrets → `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- **Fallback:** Uses built-in topic list if not configured
- **Status:** Videos work without it,orical topics

### 5. **Pexels/Pixabay API** ⭐ **RECOMMENDED** (Better b-roll)
- **What it does:** Fetches real images/videos for background
- **Get Pexels:** https://www.pexels.com/api/ (free)
- **Get Pixabay:** https://pixabay.com/api/docs/ (free)
- **Where to add:** Replit Secrets → `PEXELS_API_KEY` or `PIXABAY_API_KEY`
- **Fallback:** Uses gradient backgrounds if not configured
- **Status:** Videos work without it, just gradient backgrounds instead of real images

### 6. **Hugging Face API** (Future feature)
- **What it does:** AI image generation (not implemented yet)
- **Get it:** https://huggingface.co/ → Settings → Access Tokens
- **Where to add:** Replit Secrets → `HUGGINGFACE_API_KEY`
- **Status:** Not needed yet, future feature

### 7. **YouTube Audio Library Music** (100% FREE, NO API!)
- **What it does:** Background music for videos
- **How to set up:** See `docs/FREE_MUSIC_SETUP.md`
- **Note:** You manually download music files, no API needed
- **Fallback:** Videos work without music (voiceover only)
- **Status:** Optional but recommended for better videos

---

## 🎯 **Minimum Setup to Test:**

**To test RIGHT NOW (minimum):**
1. ✅ Add `GROQ_API_KEY` to Replit Secrets
2. ✅ Restart app
3. ✅ Click "Generate (No Upload)" button in dashboard

**Result:** Video will generate with:
- ✅ AI-generated script (Groq)
- ✅ Basic TTS voice (gTTS - free, no key needed)
- ✅ Gradient backgrounds (no b-roll APIs needed)
- ❌ No music (unless you add YouTube Audio Library files)
- ❌ Won't upload (unless you add YouTube OAuth)

---

## 📋 **Recommended Setup (For Full Experience):**

**Minimum recommended:**
1. ✅ Groq API (REQUIRED)
2. ✅ ElevenLabs API (better voice)
3. ✅ Reddit API (trending topics)
4. ✅ YouTube OAuth (if you want uploads)

**Best experience:**
- All of the above +
- Pexels API (better visuals)
- YouTube Audio Library music (background music)

---

## 🧪 **Quick Test Plan:**

**Step 1:** Add Groq API key only
- Add `GROQ_API_KEY` to Replit Secrets
- Restart app
- Click "Generate (No Upload)"
- **Expected:** Video generates successfully (basic quality)

**Step 2:** Add ElevenLabs for better voice
- Add `ELEVENLABS_API_KEY`
- Restart app
- Generate another video
- **Expected:** Better voice quality

**Step 3:** Add YouTube OAuth for uploads
- Set up YouTube OAuth (follow guides)
- Add all 4 YouTube secrets
- Click "Generate" (not "No Upload")
- **Expected:** Video generates AND uploads to YouTube

---

## ❓ **What Should You Do Now?**

**Option A: Quick Test (2 minutes)**
- Add Groq API key only
- Test if video generation works
- Add more APIs later

**Option B: Full Setup (15 minutes)**
- Add Groq + ElevenLabs + Reddit + YouTube OAuth
- Get full experience immediately

**Recommendation:** Start with Option A, test, then add more APIs one by one.

