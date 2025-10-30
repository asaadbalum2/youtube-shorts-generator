# Fix Token in Replit - Step by Step

## Where to Run: **Replit Shell** ✅

Run the script in **Replit Shell** (not locally).

---

## Quick Fix Steps:

### Step 1: In Replit Shell, run:
```bash
python scripts/auto_fix_token.py
```

### Step 2: If you get the redirect URI error:
This means we need to fix Google Cloud Console first. Here's the easiest way:

#### Option A: Create NEW OAuth Client (Easiest!)

1. **Go to**: https://console.cloud.google.com/apis/credentials
2. **Click**: "CREATE CREDENTIALS" button (top of page)
3. **Select**: "OAuth client ID"
4. **If prompted about OAuth consent screen**:
   - Click "CONFIGURE CONSENT SCREEN"
   - User type: **External**
   - App name: YouTube Shorts Generator
   - User support email: Your email (asaadbalum2@gmail.com)
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE"
   - Scopes: Click "ADD OR REMOVE SCOPES"
     - Search for: `youtube.upload`
     - Check the box
     - Click "UPDATE"
   - Click "SAVE AND CONTINUE"
   - Test users: Click "ADD USERS"
     - Add: asaadbalum2@gmail.com
     - Click "ADD"
   - Click "SAVE AND CONTINUE"
   - Click "BACK TO DASHBOARD"

5. **Now create OAuth client:**
   - Application type: **Desktop app** (or Web application)
   - Name: YouTube Shorts Generator
   - Click "CREATE"

6. **Copy the credentials:**
   - Client ID: Copy this
   - Client secret: Copy this
   - Update them in Replit Secrets
     - Replace YOUTUBE_CLIENT_ID
     - Replace YOUTUBE_CLIENT_SECRET

7. **Edit the client (add redirect URI):**
   - You should see your new client in the list
   - Click the **pencil icon (✏️)** next to it
   - Look for "Authorized redirect URIs"
   - Click "ADD URI"
   - Add: `urn:ietf:wg:oauth:2.0:oob`
   - Click "SAVE"

8. **Wait 2 minutes, then run:**
   ```bash
   python scripts/auto_fix_token.py
   ```

---

## Summary:

**In Replit Shell:**
```bash
python scripts/auto_fix_token.py
```

If it fails with redirect URI error:
1. Create a new OAuth client in Google Cloud
2. Add redirect URI: `urn:ietf:wg:oauth:2.0:oob`
3. Update Client ID/Secret in Replit Secrets
4. Try the script again

---

The script opens a browser window where you authorize, then you paste the code back into Replit Shell.

