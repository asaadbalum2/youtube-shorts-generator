"""
Manual YouTube token generator - shows URL clearly
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

print("=" * 70)
print("YouTube OAuth - Get Your Tokens")
print("=" * 70)
print()

# Read credentials
with open('client_secrets.json', 'r') as f:
    secrets = json.load(f)
    client_data = secrets.get('installed', {})
    client_id = client_data.get('client_id', '')
    client_secret = client_data.get('client_secret', '')

print("Your Client ID and Secret:")
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
print()
print("=" * 70)
print("STEP 1: Go to this URL in your browser:")
print("=" * 70)
print()

# Build the authorization URL manually
auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    "redirect_uri=http://localhost:8080&"
    "response_type=code&"
    "scope=https://www.googleapis.com/auth/youtube.upload&"
    "access_type=offline&"
    "prompt=consent"
)

print(auth_url)
print()
print("=" * 70)
print("STEP 2: After authorizing, you'll see an error page.")
print("That's OK! Look at the URL in your browser.")
print("It will look like: http://localhost:8080/?code=...&scope=...")
print()
print("STEP 3: Copy the ENTIRE URL and paste it below:")
print("=" * 70)
print()

# Get the redirect URL from user
redirect_url = input("Paste the redirect URL here: ").strip()

# Extract code from URL
if "code=" in redirect_url:
    code = redirect_url.split("code=")[1].split("&")[0]
    print(f"\n✅ Got authorization code: {code[:20]}...")
    print("\nNow we need to exchange this for tokens.")
    print("Run this command next:")
    print()
    print(f'python -c "from google_auth_oauthlib.flow import InstalledAppFlow; import json; flow = InstalledAppFlow.from_client_secrets_file(\'client_secrets.json\', [\'https://www.googleapis.com/auth/youtube.upload\']); creds = flow.fetch_token(authorization_response=\'{redirect_url}\'); print(\'Refresh Token:\', creds.refresh_token)"')
else:
    print("❌ Could not find authorization code in URL")

