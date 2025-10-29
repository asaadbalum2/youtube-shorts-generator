# Simple YouTube Token Setup

Since the automatic script isn't working well, here's a manual method:

## Method: Use Google OAuth Playground (Easiest!)

This is the simplest way to get your refresh token:

1. **Go to**: https://developers.google.com/oauthplayground/

2. **Click the gear icon** (⚙️) in top right
   - Check "Use your own OAuth credentials"
   - OAuth Client ID: Paste your Client ID
   - OAuth Client secret: Paste your Client Secret
   - Click "Close"

3. **In the left panel**, scroll and find:
   - `https://www.googleapis.com/auth/youtube.upload`
   - Check the box next to it

4. **Click "Authorize APIs"** (blue button)
   - Sign in with your Google account
   - Click "Allow"

5. **Click "Exchange authorization code for tokens"**
   - This will show your tokens

6. **Copy these values**:
   - **Refresh token**: Look for "refresh_token" in the JSON shown
   - It will be a long string

7. **Get your Channel ID**:
   - Go to https://www.youtube.com/account_advanced
   - Your Channel ID is shown there (or look at any video URL on your channel, the channel ID is in the URL)

---

## Alternative: Manual URL Method

Run this in your terminal:
```
python get_tokens_manual.py
```

Then follow the instructions it prints.

