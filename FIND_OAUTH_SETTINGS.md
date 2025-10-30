# How to Find and Edit OAuth Client Settings in Google Cloud Console

## Method 1: Direct Navigation

1. **Go to**: https://console.cloud.google.com/apis/credentials

2. **If you see a list of credentials:**
   - Look for entries that say **"OAuth 2.0 Client ID"** (not API Key, not Service Account)
   - You might see multiple - look for one that matches your YOUTUBE_CLIENT_ID
   - Click on the **name** of the client (the blue link), OR click the **pencil icon** (✏️) to edit

3. **If you don't see any OAuth clients:**
   - Click **"CREATE CREDENTIALS"** at the top
   - Select **"OAuth client ID"**
   - Application type: **"Desktop app"** (or Web application)
   - Name: YouTube Shorts Generator
   - Click **"CREATE"**

## Method 2: Step-by-Step Navigation

1. **Go to**: https://console.cloud.google.com/
2. **Select your project** from the dropdown at the top (if you have multiple)
3. **Search for "Credentials"** in the top search bar, OR
4. **Navigate manually:**
   - Click the **hamburger menu** (☰) in the top left
   - Click **"APIs & Services"**
   - Click **"Credentials"** in the left sidebar

5. **In the Credentials page:**
   - Look for **"OAuth 2.0 Client IDs"** section
   - You should see your client listed there

## Method 3: Create New OAuth Client (If You Can't Find It)

If you can't find an existing client:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, **configure OAuth consent screen first:**
   - User type: **External** (for personal use)
   - Fill in app name: "YouTube Shorts Generator"
   - User support email: Your email
   - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"**
   - Scopes: Add `https://www.googleapis.com/auth/youtube.upload`
   - Click **"SAVE AND CONTINUE"**
   - Test users: Add your email (asaadbalum2@gmail.com)
   - Click **"SAVE AND CONTINUE"**

4. **Now create OAuth client:**
   - Application type: **"Desktop app"** (recommended)
   - Name: YouTube Shorts Generator
   - Click **"CREATE"**

5. **After creation:**
   - A popup will show your Client ID and Client Secret
   - **Copy both of these**
   - Update them in Replit Secrets

6. **Then edit the redirect URI:**
   - You'll see the client in the list
   - Click the **pencil icon** (✏️) to edit
   - Under "Authorized redirect URIs", add: `urn:ietf:wg:oauth:2.0:oob`
   - Click **"SAVE"**

---

## What to Look For

When you're in the right place, you should see:
- **Client ID** (starts with something like `545895166701-...`)
- **Client secret** (starts with `GOCSPX-...`)
- **Authorized redirect URIs** (this is what we need to edit)

---

## Quick Check: What Do You See?

When you go to https://console.cloud.google.com/apis/credentials, what exactly do you see?

1. A list with "API keys", "OAuth 2.0 Client IDs", etc.?
2. An empty page?
3. A page asking you to create credentials?
4. Something else?

Let me know what you see and I'll guide you from there!

