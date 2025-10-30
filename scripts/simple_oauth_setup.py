#!/usr/bin/env python3
"""
Simplified OAuth setup - creates new OAuth client with correct settings
Or helps you find existing one
"""
import os

print("="*70)
print("SIMPLE OAUTH SETUP HELPER")
print("="*70)
print()

# Get current client ID from secrets
client_id = os.getenv('YOUTUBE_CLIENT_ID', '')

if client_id:
    print(f"✅ Your current Client ID: {client_id[:30]}...")
    print()
    print("Let's find this in Google Cloud Console:")
    print()
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print()
    print("2. Look for this Client ID in the list")
    print()
    print("3. If you see it:")
    print("   - Click the ✏️ (pencil/edit) icon next to it")
    print("   - OR click on the name/ID itself")
    print()
    print("4. Scroll down to find 'Authorized redirect URIs'")
    print("   - It might be under 'Advanced settings' or similar")
    print("   - Click 'ADD URI' or '+ ADD URI'")
    print("   - Add: urn:ietf:wg:oauth:2.0:oob")
    print("   - Click SAVE")
    print()
else:
    print("❌ YOUTUBE_CLIENT_ID not found")
    print()
    print("Let's create a new OAuth client:")
    print()
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print()
    print("2. Click: 'CREATE CREDENTIALS' (top of page)")
    print()
    print("3. Select: 'OAuth client ID'")
    print()
    print("4. Application type: 'Desktop app'")
    print()
    print("5. Name: YouTube Shorts Generator")
    print()
    print("6. Click CREATE")
    print()
    print("7. Copy the Client ID and Client Secret shown")
    print()
    print("8. Add them to Replit Secrets")
    print()

print("="*70)
print("ALTERNATIVE: What screen are you seeing?")
print("="*70)
print()
print("A) A list of API keys and OAuth clients?")
print("B) An empty page that says 'Create Credentials'?")
print("C) A page asking about OAuth consent screen?")
print("D) Something else?")
print()
print("Tell me which one and I'll give specific instructions!")
print()

