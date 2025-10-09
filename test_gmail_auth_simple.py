"""
Simple Gmail OAuth Authentication Test
Uses console-based OAuth flow (no redirect URI needed)
"""

import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / os.getenv('GOOGLE_CREDENTIALS_FILE', 'client_secret_632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com.json')
TOKEN_FILE = BASE_DIR / os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')


def authenticate_console():
    """
    Authenticate using console-based OAuth flow (OOB)
    This method doesn't require redirect URI configuration
    """
    print("\n🔐 Gmail API Console Authentication")
    print("=" * 60)
    
    creds = None
    
    # Check if token already exists
    if TOKEN_FILE.exists():
        print("📝 Found existing token file...")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        
        # Check if token is valid
        if creds and creds.valid:
            print("✅ Existing token is valid!")
            return creds
        elif creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired, refreshing...")
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Token refreshed successfully!")
            return creds
    
    # Need new authentication
    print("\n📋 First-time authentication required")
    print()
    
    if not CREDENTIALS_FILE.exists():
        print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
        print()
        print("💡 Solution:")
        print("   1. Download OAuth credentials JSON from Google Cloud Console")
        print("   2. Save it to project root directory")
        print("   3. Update .env file with correct filename")
        return None
    
    print("🌐 Starting OAuth flow...")
    print()
    print("📝 Steps:")
    print("   1. Browser will open to Google login")
    print("   2. Sign in with your Gmail account")
    print("   3. Grant permissions to send emails")
    print("   4. You'll see an authorization code")
    print("   5. Copy the code and paste it here")
    print()
    
    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES
        )
        
        # Use local server with port 0 (random available port)
        # User will authorize in browser, then browser redirects back
        print("🚀 Opening browser for authorization...")
        print()
        print("⚠️  IMPORTANT: If you see redirect_uri_mismatch error:")
        print("   - Note the redirect URI in the error")
        print("   - Add it to Google Cloud Console")
        print("   - See OAUTH_SETUP_FIX.md for instructions")
        print()
        
        creds = flow.run_local_server(
            port=0,  # Use any available port
            success_message='Authentication successful! You can close this window.',
            open_browser=True
        )
        
        # Save token
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print()
        print("✅ Authentication successful!")
        print(f"📝 Token saved to: {TOKEN_FILE}")
        
        return creds
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_send_email(creds):
    """Test sending email with authenticated credentials"""
    print("\n📧 Testing Email Send")
    print("=" * 60)
    
    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Get sender email from .env
        sender = os.getenv('EMAIL_SENDER_ADDRESS', '')
        
        if not sender:
            print("⚠️  EMAIL_SENDER_ADDRESS not set in .env")
            sender = input("Enter your Gmail address: ").strip()
        
        print(f"📤 Sender: {sender}")
        
        # Get recipient
        recipient = input("Enter recipient email (or press Enter to skip): ").strip()
        
        if not recipient:
            print("⏭️  Skipping email send test")
            return
        
        # Create test message
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText("✅ Test email from GEC Rajkot notification system!\n\nIf you received this, Gmail API is working correctly.")
        message['to'] = recipient
        message['from'] = sender
        message['subject'] = '🧪 Test Email - GEC Rajkot'
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        print(f"\n📨 Sending test email to {recipient}...")
        
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        print(f"✅ Email sent successfully!")
        print(f"📬 Message ID: {result.get('id')}")
        print(f"💡 Check inbox: {recipient}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    print()
    print("=" * 70)
    print("         GEC Rajkot - Simple Gmail Authentication Test")
    print("=" * 70)
    print()
    print("💡 This script uses console-based OAuth (no redirect URI needed)")
    print()
    
    try:
        # Step 1: Authenticate
        creds = authenticate_console()
        
        if not creds:
            print("\n❌ Authentication failed")
            print()
            print("📚 Troubleshooting:")
            print("   - Make sure Google OAuth credentials file exists")
            print("   - Check .env file configuration")
            print("   - See OAUTH_SETUP_FIX.md for help")
            return
        
        # Step 2: Test email
        test_send_email(creds)
        
        print()
        print("=" * 70)
        print("✅ Setup Complete!")
        print("=" * 70)
        print()
        print("📚 Next Steps:")
        print("   1. Token is saved - no need to authenticate again")
        print("   2. Email notification system is ready")
        print("   3. Faculty can now send announcements/events")
        print("   4. Students will receive email notifications")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user (Ctrl+C)")
        print("💡 Run again: python test_gmail_auth_simple.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
