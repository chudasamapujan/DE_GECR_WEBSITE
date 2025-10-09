"""
Environment Variables Verification Script
Tests if .env file is properly configured
"""

from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

def check_env_var(name, required=True, is_file=False):
    """Check if environment variable is set"""
    value = os.getenv(name)
    
    if value:
        if is_file:
            file_exists = Path(value).exists()
            status = '✓ Found' if file_exists else '✗ File Missing'
            print(f"   {name}: {status} ({value})")
            return file_exists
        else:
            # Hide sensitive values
            if 'SECRET' in name or 'PASSWORD' in name:
                display = '***hidden***'
            else:
                display = value[:50] + '...' if len(value) > 50 else value
            print(f"   {name}: ✓ Set ({display})")
            return True
    else:
        status = '✗ REQUIRED' if required else '○ Optional (using default)'
        print(f"   {name}: {status}")
        return not required

print("=" * 60)
print("🔍 GEC Rajkot - Environment Configuration Check")
print("=" * 60)

print("\n📋 Flask Configuration:")
all_good = True
all_good &= check_env_var('SECRET_KEY', required=True)
all_good &= check_env_var('FLASK_ENV', required=False)
all_good &= check_env_var('FLASK_DEBUG', required=False)

print("\n📧 Email Configuration:")
all_good &= check_env_var('EMAIL_SENDER_ADDRESS', required=True)
all_good &= check_env_var('EMAIL_SENDER_NAME', required=False)
all_good &= check_env_var('EMAIL_NOTIFICATIONS_ENABLED', required=False)

print("\n🔐 Google OAuth Configuration:")
all_good &= check_env_var('GOOGLE_CREDENTIALS_FILE', required=True, is_file=True)
all_good &= check_env_var('GOOGLE_CLIENT_SECRET', required=False)
all_good &= check_env_var('GMAIL_TOKEN_FILE', required=False)

print("\n🌐 Application Configuration:")
all_good &= check_env_var('BASE_URL', required=True)
all_good &= check_env_var('DATABASE_URI', required=False)

print("\n📁 File Paths:")
check_env_var('UPLOAD_FOLDER', required=False)
check_env_var('LOG_FILE', required=False)

print("\n" + "=" * 60)
if all_good:
    print("✅ All required configuration is set!")
    print("✅ Application is ready to run")
    print("\n💡 Next steps:")
    print("   1. Run: python test_gmail_auth.py (authenticate Gmail)")
    print("   2. Run: python app.py (start the application)")
else:
    print("⚠️  Some required configuration is missing!")
    print("⚠️  Please check .env file and set missing values")
    print("\n💡 Quick fix:")
    print("   1. Copy .env.example to .env")
    print("   2. Edit .env with your values")
    print("   3. Run this script again")

print("=" * 60)

# Additional checks
print("\n🔍 Additional Checks:")

# Check if .env file exists
env_file = Path('.env')
if env_file.exists():
    print(f"   .env file: ✓ Found")
else:
    print(f"   .env file: ✗ Missing (create from .env.example)")
    all_good = False

# Check if credentials file exists
creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'client_secret_632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com.json')
if Path(creds_file).exists():
    print(f"   Google credentials: ✓ Found")
else:
    print(f"   Google credentials: ✗ Missing ({creds_file})")
    all_good = False

# Check if token file exists (optional)
token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
if Path(token_file).exists():
    print(f"   Gmail token: ✓ Found (already authenticated)")
else:
    print(f"   Gmail token: ○ Not found (need to authenticate)")

# Check if uploads folder exists
upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
if Path(upload_folder).exists():
    print(f"   Upload folder: ✓ Exists")
else:
    print(f"   Upload folder: ○ Will be created automatically")

print("\n" + "=" * 60)
print(f"📊 Overall Status: {'✅ READY' if all_good else '⚠️  NEEDS SETUP'}")
print("=" * 60)
