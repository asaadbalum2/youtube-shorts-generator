"""
Verify all Secrets/API keys are correct and working
Tests each API without exposing sensitive data
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_groq():
    """Verify Groq API key"""
    api_key = os.getenv('GROQ_API_KEY', '')
    
    if not api_key:
        return False, "Not set or empty"
    
    # Strip whitespace (common issue)
    api_key = api_key.strip()
    
    # Debug info (first/last chars only)
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"  Debug: Key loaded: {masked} (length: {len(api_key)})")
    
    if api_key.startswith('your_'):
        return False, "Not set or placeholder"
    
    if not api_key.startswith('gsk_'):
        return False, f"Invalid format (should start with 'gsk_')"
    
    try:
        from groq import Groq
        print(f"  Debug: Creating Groq client...")
        client = Groq(api_key=api_key)
        print(f"  Debug: Making API call...")
        # Test API with simple request
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=10
        )
        if response.choices[0].message.content:
            print(f"  Debug: API call succeeded!")
            return True, "Valid"
        return False, "API call succeeded but no content"
    except Exception as e:
        error = str(e)
        print(f"  Debug: Error occurred: {type(e).__name__}")
        print(f"  Debug: Error message: {error}")
        
        if "401" in error or "unauthorized" in error.lower():
            return False, f"Invalid API key (401 Unauthorized) - Check if key is correct in Replit Secrets"
        if "invalid" in error.lower() and "api" in error.lower():
            return False, f"Invalid API key: {error[:80]}"
        if "rate limit" in error.lower():
            return False, f"Rate limited: {error[:50]}"
        
        return False, f"Error: {error[:80]}"

def verify_reddit():
    """Verify Reddit credentials"""
    client_id = os.getenv('REDDIT_CLIENT_ID', '')
    secret = os.getenv('REDDIT_CLIENT_SECRET', '')
    
    if not client_id or not secret or client_id.startswith('your_'):
        return False, "Not set or placeholder"
    
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=secret,
            user_agent=os.getenv('REDDIT_USER_AGENT', 'YShortsGen/1.0')
        )
        # Test by accessing a public subreddit
        sub = reddit.subreddit('test')
        _ = sub.display_name
        return True, "Valid"
    except Exception as e:
        error = str(e)
        if "401" in error:
            return False, "Invalid credentials"
        return False, f"Error: {error[:50]}"
    
    return False, "Unknown error"

def verify_youtube_refresh_token():
    """Verify YouTube refresh token"""
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN', '')
    client_id = os.getenv('YOUTUBE_CLIENT_ID', '')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET', '')
    
    if not refresh_token or refresh_token.startswith('your_'):
        return False, "Not set or placeholder"
    
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        # Try to refresh
        creds.refresh(Request())
        return True, "Valid"
    except Exception as e:
        error = str(e)
        if "invalid_grant" in error.lower():
            return False, "Token expired - needs regeneration"
        if "401" in error:
            return False, "Invalid credentials"
        return False, f"Error: {error[:50]}"
    
    return False, "Unknown error"

def main():
    print("=" * 60)
    print("Secrets Verification")
    print("=" * 60)
    print()
    
    results = {}
    
    # Check Groq
    print("Checking Groq API...")
    valid, msg = verify_groq()
    results['GROQ_API_KEY'] = (valid, msg)
    status = "✅ VALID" if valid else f"❌ {msg}"
    print(f"  {status}")
    print()
    
    # Check Reddit
    print("Checking Reddit API...")
    valid, msg = verify_reddit()
    results['REDDIT'] = (valid, msg)
    status = "✅ VALID" if valid else f"❌ {msg}"
    print(f"  {status}")
    print()
    
    # Check YouTube
    print("Checking YouTube Refresh Token...")
    valid, msg = verify_youtube_refresh_token()
    results['YOUTUBE'] = (valid, msg)
    status = "✅ VALID" if valid else f"❌ {msg}"
    print(f"  {status}")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_valid = True
    for name, (valid, msg) in results.items():
        status = "✅" if valid else "❌"
        print(f"{status} {name}: {msg}")
        if not valid:
            all_valid = False
    
    print()
    if all_valid:
        print("🎉 All secrets are valid!")
        return 0
    else:
        print("⚠️  Some secrets need attention. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

