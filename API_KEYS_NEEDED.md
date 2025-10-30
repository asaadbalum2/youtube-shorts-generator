# API Keys You Need - What Fixes What

## 🔴 **REQUIRED for B-roll (No Visuals Issue)**

### PEXELS_API_KEY or PIXABAY_API_KEY
**Why:** Without these, you'll get NO b-roll visuals - only color backgrounds

**Get Pexels (Recommended):**
1. Go to: `https://www.pexels.com/api/`
2. Sign up (free)
3. Copy your API key
4. In Replit Secrets: `PEXELS_API_KEY` = your key

**Get Pixabay (Alternative):**
1. Go to: `https://pixabay.com/api/docs/`
2. Sign up (free)
3. Copy your API key
4. In Replit Secrets: `PIXABAY_API_KEY` = your key

**Note:** You need AT LEAST ONE of these, preferably both for better variety.

---

## 🟡 **OPTIONAL but Recommended**

### ELEVENLABS_API_KEY
**Why:** Better voice quality (American accent, more natural)
- Currently using gTTS (lower quality)
- With ElevenLabs: Professional voice quality
- **Get it:** https://elevenlabs.io/ → Sign up (free 10K chars/month)

### JAMENDO_API_KEY
**Why:** For trending music (currently not finding music)
- **Get it:** https://developer.jamendo.com/ → Register (free)
- Adds your API key to Secrets: `JAMENDO_API_KEY`
- **Note:** Can work without key but registration helps

---

## ✅ **ALREADY HAVE**

- ✅ Groq API (you have this - for content generation)
- ✅ YouTube OAuth (for uploads)

---

## 📋 **What Each Key Fixes**

| API Key | Fixes This Issue |
|---------|-----------------|
| PEXELS_API_KEY | ❌ No visuals (only color backgrounds) |
| PIXABAY_API_KEY | ❌ No visuals (only color backgrounds) |
| ELEVENLABS_API_KEY | ⚠️ Better voice quality (American accent) |
| JAMENDO_API_KEY | ⚠️ Music not found |

---

## 🎯 **Priority Order**

1. **PEXELS_API_KEY** - Fixes "no visuals" issue (CRITICAL)
2. **ELEVENLABS_API_KEY** - Fixes voice quality (nice to have)
3. **JAMENDO_API_KEY** - Helps with music (optional)

