# Fix Redirect URI - Step-by-Step Instructions

## Problem
Desktop-type OAuth clients don't show "Authorized redirect URIs" field. We need a **Web application** type instead.

---

## Solution: Create NEW Web Application Client

### Step 1: Go Back to Credentials Page
1. Click the **back arrow** (←) at the top left, OR
2. Go directly to: https://console.cloud.google.com/apis/credentials

### Step 2: Create NEW OAuth Client (Web Application Type)
1. Click the **"+ CREATE CREDENTIALS"** button (top of the page)
2. Select **"OAuth client ID"** from the dropdown
3. If asked about OAuth consent screen:
   - Click **"CONFIGURE CONSENT SCREEN"**
   - User type: **External**
   - App name: **YouTube Shorts Generator**
   - User support email: Your email (asaadbalum2@gmail.com)
   - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"**
   - Scopes: Click **"ADD OR REMOVE SCOPES"**
     - Check: `https://www.googleapis.com/auth/youtube.upload`
     - Click **"UPDATE"**
   - Click **"SAVE AND CONTINUE"**
   - Test users: Click **"ADD USERS"**
     - Add: **asaadbalum2@gmail.com**
     - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**
   - Click **"BACK TO DASHBOARD"**

4. **Create the OAuth Client:**
   - **Application type**: Select **"Web application"** ⚠️ (NOT Desktop!)
   - **Name**: YouTube Shorts Generator
   - **Authorized redirect URIs**: Click **"ADD URI"**
     - Add: `http://localhost:8080`
   - Click **"CREATE"**

5. **Copy the credentials:**
   - A popup will show:
     - **Client ID** (copy this)
     - **Client secret** (copy this - click "Show" if hidden)

### Step 3: Update Replit Secrets
1. In Replit, click **Secrets** (🔒 icon)
2. Update these secrets:
   - `YOUTUBE_CLIENT_ID` → Paste the new Client ID
   - `YOUTUBE_CLIENT_SECRET` → Paste the new Client Secret

### Step 4: Generate New Token
1. Wait 2-3 minutes (for Google to update)
2. In Replit Shell, run:
   ```bash
   python scripts/regenerate_token_modern.py
   ```
3. Follow the prompts - it should work now!

---

## Alternative: Edit Existing Client (If Possible)

If you want to try editing the existing Desktop client:

1. On the edit page (second screenshot), look for any of these:
   - "Show advanced settings" or "Advanced" link
   - A dropdown to change "Application type"
   - Any settings/options button

If you see an option to change it to "Web application", do that, then you'll see redirect URIs appear.

---

## Quick Summary

**The key issue**: Desktop app type doesn't show redirect URI settings.
**The solution**: Create a NEW OAuth client with **"Web application"** type, then you'll see the redirect URI field.

After creating the Web application client and adding `http://localhost:8080` as redirect URI, everything will work!

