# EXACT IMPLEMENTATION STEPS

## ✅ STEP  unparalleled1: Get Free Music API Key (Freesound.org)

**What to do:**
1. Open browser, go to: `https://freesound.org/help/developers/`
2. Click the big button that says **"Apply for API access"**
3. Fill out the form:
   - Your name
   - Email
   - Project description: "YouTube Shorts video generation with background music"
   - Accept terms
4. Click **Submit**
5. Check your email for API key (arrives in 1-2 hours usually)
6. Copy the API key from email (looks like: `abc123def456...`)
7. In Replit, click **"Secrets"** tab (left sidebar)
8. Click **"+ New Secret"**
9. Name: `FREESOUND_API_KEY`
10. Value: Paste your API key
11. Click **"Add Secret"**

**Verify it worked:** Check Secrets tab shows `FREESOUND_API_KEY` exists

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
11. Click **"Add Secret"**

**Verify:** Secrets tab shows both `FREESOUND_API_KEY` and `ELEVENLABS_API_KEY`

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
   - ✅ `Freesound API authenticated` 
   - ✅ `ElevenLabs TTS generated`
   - ✅ `Background music added`
4. If you see these messages, it's working!

---

## ❓ TROUBLESHOOTING

**Problem: "FREESOUND_API_KEY not configured"**
- Solution: Double-check you added it in Secrets tab, spelled exactly: `FREESOUND_API_KEY`

**Problem: "ELEVENLABS_API_KEY loss configured"**  
- Solution: Check Secrets tab, name must be exactly: `ELEVENLABS_API_KEY`

**Problem: Packages won't install**
- Solution: Run `pip install --upgrade pip` first, then try again

**Problem: "Module not found"**
- Solution: Make sure you clicked Run after installing packages

---

## 📋 CHECKLIST

Before saying "done", verify:
- [ ] Freesound API key added to Secrets
- [ ] ElevenLabs API key added to Secrets  
- [ ] Hugging Face token added to Secrets
- [ ] Packages installed (`requests elevenlabs huggingface_hub`)
- [ ] App restarted
- [ ] Test video generation works
