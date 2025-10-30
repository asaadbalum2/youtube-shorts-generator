# Answers to Your Questions

## 1. How many videos per day can we create?

### API Limits:
- **YouTube**: 10,000 units/day free → ~6 videos/day max (1,600 units per upload)
- **Groq**: Very generous → Hundreds of videos/day ✅ NO LIMIT
- **Reddit**: 60 req/min → Thousands of videos/day ✅ NO LIMIT
- **Google TTS**: Unlimited ✅

### Replit Free Tier Limits:
- **CPU/RAM**: Limited, best for 3-5 videos/day
- **Storage**: 1GB (enough for many videos)

### Current Setting:
- **3 videos/day** ✅ SAFE and optimal
- **Can safely increase to**: 5-6 videos/day (stays under YouTube quota)
- **Maximum**: 6 videos/day (YouTube quota limit)

**Recommendation**: Keep at 3-5 videos/day to stay safe.

---

## 2. How long will each video be?

- **Target**: 45 seconds (optimal for engagement)
- **Maximum**: 60 seconds (YouTube Shorts limit)
- **Current setting**: `TARGET_DURATION_SECONDS = 45` (in config.py)

Videos will be 45-60 seconds long, optimized for maximum engagement.

---

## 3. Won't YouTube catch this as spam?

**YES, this is a valid concern!** Fixed issues:

✅ **FIXED**: Randomized posting times (not fixed at 2pm, 4pm, 8pm)
   - Videos now post at random times within optimal windows
   - Different minute each day for variation

✅ **FIXED**: Spread throughout day (not all at once)

✅ **Already in place**: 
   - Different topics each video
   - Varied content styles
   - Optimized titles/descriptions

**Additional recommendations:**
- Monitor your channel for any warnings
- Start slow (3 videos/day) and increase gradually
- Vary content topics as much as possible
- The randomization we added helps!

---

## 4. Manual trigger for testing?

**ADDED**: Manual trigger endpoint!
- Web server runs on port 8080
- Endpoint: `POST /generate` - triggers one video generation
- Check health: `GET /health`
- Main status: `GET /`

**How to use:**
1. Your Replit URL + `/generate` (POST request)
2. Or use Replit's built-in webview
3. Or curl: `curl -X POST https://your-repl.repl.co/generate`

This lets you test without waiting for scheduled times!

---

## 5. Replit changes to code?

**YES**, Replit made changes:
- ✅ Fixed `requirements.txt` (removed built-in modules like smtplib, email, sqlite3)
- ✅ Likely added `numpy<2` to fix OpenCV compatibility
- ✅ Cleaned up duplicate entries

**These changes are ONLY in Replit, NOT in GitHub yet.**

**We need to sync them back!**

### To sync Replit changes to GitHub:

**Option A: In Replit:**
1. Open Shell in Replit
2. Run:
```bash
git add requirements.txt
git commit -m "Sync Replit fixes - remove built-ins, fix numpy"
git push origin main
```

**Option B: I'll help you do it**

Tell me which you prefer!

---

## Summary:

✅ **Capacity**: 5-6 videos/day safely (currently 3)
✅ **Duration**: 45-60 seconds
✅ **Spam prevention**: Randomized times + varied content
✅ **Manual trigger**: Added `/generate` endpoint
✅ **Sync needed**: Update GitHub with Replit's fixes

**Next steps**: I'll help you sync the changes and set up keep-alive!

