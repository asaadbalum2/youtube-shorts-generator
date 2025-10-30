"""
Setup verification script
Checks if all dependencies and configurations are correct
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'fastapi', 'groq', 'praw', 'moviepy', 'gtts',
        'googleapiclient', 'apscheduler', 'PIL'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'googleapiclient':
                __import__('googleapiclient.discovery')
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("❌ FFmpeg not found. Install FFmpeg and add to PATH")
    print("   Windows: https://ffmpeg.org/download.html")
    print("   Linux: sudo apt-get install ffmpeg")
    print("   Mac: brew install ffmpeg")
    return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Copy env_template.txt to .env and fill in values")
        return False
    
    print("✅ .env file exists")
    
    # Check for critical keys
    required_keys = [
        'GROQ_API_KEY',
        'REDDIT_CLIENT_ID',
        'EMAIL_ADDRESS'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    for key in required_keys:
        value = os.getenv(key)
        if not value or value.startswith('your_'):
            missing.append(key)
        else:
            print(f"✅ {key} configured")
    
    if missing:
        print(f"\n⚠️  Missing or incomplete keys: {', '.join(missing)}")
        return False
    
    return True

def check_youtube_auth():
    """Check YouTube authentication"""
    if os.path.exists('token.pickle'):
        print("✅ YouTube token.pickle exists")
        return True
    elif os.path.exists('client_secrets.json'):
        print("⚠️  client_secrets.json found but token.pickle missing")
        print("   Run: python setup_youtube_oauth.py")
        return False
    else:
        print("❌ YouTube credentials not set up")
        print("   Create client_secrets.json and run setup_youtube_oauth.py")
        return False

def check_directories():
    """Check if required directories exist"""
    dirs = ['temp', 'output', 'assets']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        if os.path.exists(d):
            print(f"✅ Directory '{d}' exists")
        else:
            print(f"⚠️  Could not create directory '{d}'")
    
    return True

def main():
    print("=" * 60)
    print("YouTube Shorts Generator - Setup Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("Environment File", check_env_file),
        ("YouTube Auth", check_youtube_auth),
        ("Directories", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to go!")
        print("   Run: python main.py single (to test)")
        print("   Or: python main.py autonomous (to start)")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("   See SETUP_GUIDE.md for detailed instructions.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

