# Fix OAuth Error 400: invalid_request

## Problem
Getting "Error 400: invalid_request" when trying to authorize YouTube access.

## Solution: Add Redirect URI to Google Cloud Console

### Step 1: Go to OAuth Client Settings

1. **Go to**: https://console.cloud.google.com/apis/credentials
2. **Select your project**: `youtube-shorts-generator`
3. **Find your OAuth 2.0 Client ID** (it should be visible in the list)
4. **Click on the Client ID** (not the edit icon, click the name/link)

### Step 2: Add Redirect URI

1. Scroll down to **"Authorized redirect URIs"** section
2. **Click "ADD URI"**
3. **Add this exact URI**: `urn:ietf:wg:oauth:2.0:oob`
4. **Click "SAVE"**

**Important**: Make sure you add it exactly as shown above (copy-paste to avoid typos)

### Step 3: Wait a Few Minutes

Google changes can take 1-5 minutes to propagate.

### Step 4: Try Again

Run the token fix script again:
```bash
python scripts/auto_fix_token.py
```

---

## Alternative: Use HTTP Redirect URI

If the out-of-band URI doesn't work, we can use `http://localhost`:

1. In Google Cloud Console, add redirect URI: `http://localhost`
2. Update the token script to use `http://localhost` instead

But try the `urn:ietf:wg:oauth:2.0:oob` method first - it's better for headless environments.

