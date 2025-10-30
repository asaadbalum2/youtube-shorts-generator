# EXACT IMPLEMENTATION STEPS

## ✅ STEP 1: Download Free Music (YouTube Audio Library - 100% FREE, No API!)

**READ THIS FIRST:**
- ✅ **100% FREE** - No API keys, no subscriptions, no trials
- ✅ Just download music files and organize in folders
- ✅ See `docs/FREE_MUSIC_SETUP.md` for detailed instructions

**Quick steps:**
1. Go to: `https://studio.youtube.com/` → **Audio Library** → **Free Music**
2. Download 5-10 tracks for each style (upbeat, dramatic, ambient, etc.)
3. In Replit, create folders: `assets/music/upbeat/`, `assets/music/dramatic/`, etc.
4. Upload your downloaded music files to the appropriate folders
5. Done! System automatically finds and uses them.

**Detailed guide:** See `docs/FREE_MUSIC_SETUP.md` in the repo.

**SKIP THIS STEP IF:** You want videos without music for now (they'll still work!)

---

## ✅ STEP 2: Get Better TTS API Key (ElevenLabs - FREE 10,000 chars/month)

**What to do:**
1. Open browser, go to: `https://elevenlabs.io/`
2. Click **"Sign Up"** (top right)
3. Create account with email (free tier is automatic)
4. After signup, click your **profile icon** (top right)
5. Click **"Profile"** → **"API Key"** tab
6. Copy your API key (starts with something like `sk_...`)
7. In Replit, click **"Secrets"** tab
8. Click **"+ New Secret"**
9. Name: `ELEVENLABS_API_KEY`
10. Value: Paste your API key
11. Click **"Add Secret"`

**Verify:** Secrets tab shows `ELEVENLABS_API_KEY`

---

## ✅ STEP 3: Get AI Image Generation (Hugging Face - FREE)

**What to do:**
1. Open browser, go to: `https://huggingface.co/`
2. Click **"Sign Up"** (top right)
3. Create account
4. Verify email if needed
5. Click your **profile icon** (top right) → **"Settings"**
6. Click **"Access Tokens"** in left menu
7. Click **"New token"** button
8. Name: `youtube-shorts-gen`
9. Type: Select **"Read"** (don't need write)
10. Click **"Generate token"**
11. **COPY THE TOKEN IMMEDIATELY** (you can't see it again!)
12. In Replit, click **"Secrets"** tab
13. Click **"+ New Secret"**
14. Name: `HUGGINGFACE_API_KEY`
15. Value: Paste your token
16. Click **"Add Secret"**

---

## ✅ STEP 4: Install Required Python Packages

**What to do:**
1. In Replit, click **"Shell"** tab (bottom panel)
2. Type this command exactly (press Enter after):
   ```
   pip install requests elevenlabs huggingface_hub
   ```
3. Wait for installation to complete (you'll see "Successfully installed...")
4. If you see errors, copy the error message and tell me

**Note:** Music uses YouTube Audio Library (no package needed - just download files!)

---

## ✅ STEP 5: Restart Your App

**What to do:**
1. In Replit, click the **"Stop"** button (top center, square icon)
2. Wait 2 seconds
3. Click the **"Run"** button (triangle icon)
4. Your app restarts with new API keys loaded

---

## ✅ STEP 6: Test It Works

**What to do:**
1. Go to your dashboard: `https://your-replit-url.replit.dev/dashboard`
2. Click **"⚡ Generate (No Upload)"** button
3. Watch the Replit console for:
   - ✅ `ElevenLabs TTS generated` (or gTTS if ElevenLabs not configured)
   - ✅ `Found YouTube Audio Library music` (if you added music files)
   - ✅ `Background music added`
4. If you see these messages, it's working!

---

## ❓ TROUBLESHOOTING

**Problem: "ELEVENLABS_API_KEY not configured"**  
- Solution: Check Secrets tab, name must be exactly: `ELEVENLABS_API_KEY`

**Problem: Packages won't install**
- Solution: Run `pip install --upgrade pip` first, then try again

**Problem: "Module not found"**
- Solution: Make sure you clicked Run after installing packages

**Problem: "No music available"**
- Solution: Music is optional. Videos work fine without it. To add music, see `docs/FREE_MUSIC_SETUP.md`

---

## 📋 CHECKLIST

Before saying "done", verify:
- [ ] Music downloaded from YouTube Audio Library (optional but recommended)
- [ ] Music organized in `assets/music/{style}/` folders (optional)
- [ ] ElevenLabs API key added to Secrets (optional - gTTS works as fallback)
- [ ] Hugging Face token added to Secrets (optional - for AI image generation)
- [ ] Packages installed (`requests elevenlabs huggingface_hub`)
- [ ] App restarted
- [ ] Test video generation works
