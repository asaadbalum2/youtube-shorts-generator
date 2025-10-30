#!/usr/bin/env python3
"""
Helper to check and fix OAuth redirect URI configuration
"""
import os
import sys

print("="*70)
print("OAuth Redirect URI Configuration Helper")
print("="*70)
print()

# Check if we're using the correct redirect URI
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

print("Current configuration uses redirect URI:")
print(f"  {redirect_uri}")
print()

print("="*70)
print("STEP-BY-STEP INSTRUCTIONS TO FIX")
print("="*70)
print()
print("1. Go to: https://console.cloud.google.com/apis/credentials")
print()
print("2. Select your project (youtube-shorts-generator)")
print()
print("3. Find your OAuth 2.0 Client ID in the list")
print("   (Look for one that matches your YOUTUBE_CLIENT_ID)")
print()
print("4. CLICK ON THE CLIENT ID NAME (not just the edit icon)")
print()
print("5. Scroll down to 'Authorized redirect URIs' section")
print()
print("6. Click 'ADD URI' button")
print()
print("7. Add this EXACT URI (copy-paste to avoid typos):")
print(f"   {redirect_uri}")
print()
print("8. Click 'SAVE'")
print()
print("9. Wait 2-3 minutes for Google to update")
print()
print("10. Try running again: python scripts/auto_fix_token.py")
print()
print("="*70)

# Verify client ID is set
client_id = os.getenv('YOUTUBE_CLIENT_ID', '')
if client_id:
    print()
    print(f"Your Client ID (first part): {client_id[:20]}...")
    print("Make sure this matches the OAuth client you're editing!")
else:
    print()
    print("⚠️ YOUTUBE_CLIENT_ID not found in environment")
    print("Make sure Replit Secrets are configured correctly")

print()
print("="*70)

