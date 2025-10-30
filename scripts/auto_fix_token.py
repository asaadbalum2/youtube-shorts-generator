#!/usr/bin/env python3
"""
Automated YouTube token regeneration and Replit secret update
Run this when your token expires - it handles everything automatically
"""
import os
import sys
import webbrowser
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.token_auto_recovery import regenerate_token_auto, update_replit_secret

def main():
    print("="*70)
    print("🤖 AUTOMATED YOUTUBE TOKEN FIX")
    print("="*70)
    print()
    print("This script will:")
    print("1. Open your browser for Google OAuth")
    print("2. Guide you to get an authorization code")
    print("3. Exchange it for a new refresh token")
    print("4. Attempt to update Replit Secrets automatically")
    print()
    print("Starting in 3 seconds...")
    import time
    time.sleep(3)
    print()
    
    # Regenerate token
    new_token = regenerate_token_auto()
    
    if not new_token:
        print("\n❌ Failed to generate new token. Please try again.")
        sys.exit(1)
    
    print()
    print("="*70)
    print("Step 4: Updating Replit Secret...")
    print("="*70)
    print()
    
    # Try to update Replit secret
    if update_replit_secret(new_token):
        print("\n✅✅✅ SUCCESS! ✅✅✅")
        print("Token has been automatically updated in Replit!")
        print("Please restart your app for changes to take effect.")
        sys.exit(0)
    else:
        # Manual instructions
        print()
        print("="*70)
        print("MANUAL UPDATE REQUIRED")
        print("="*70)
        print()
        print("Copy this token:")
        print()
        print(f"YOUTUBE_REFRESH_TOKEN={new_token}")
        print()
        print("Then:")
        print("1. In Replit, click Secrets (🔒 icon)")
        print("2. Find YOUTUBE_REFRESH_TOKEN")
        print("3. Update it with the token above")
        print("4. Restart your app")
        print()
        print("="*70)

if __name__ == "__main__":
    main()

