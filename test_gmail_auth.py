"""
Test Gmail API authentication and email sending
Run this script first to authenticate with your Google account
"""

import sys
import os
import signal
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set timeout for the entire script
TIMEOUT = 120  # 2 minutes

def timeout_handler(signum, frame):
    """Handle timeout"""
    print("\n⏱️  Timeout: Script took too long. Exiting...")
    print("\n💡 This usually means:")
    print("   - OAuth redirect URI is not configured correctly")
    print("   - Browser didn't redirect back properly")
    print("   - See OAUTH_SETUP_FIX.md for solution")
    sys.exit(1)

# Set timeout (Windows doesn't support signal.alarm, so we'll handle differently)
try:
    from utils.email_notification import (
        EmailNotificationService,
        send_announcement_email
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the project root directory")
    sys.exit(1)

def test_authentication():
    """Test Gmail API authentication"""
    print("\n🔐 Testing Gmail API Authentication...\n")
    print("=" * 60)
    print("IMPORTANT: First-time setup")
    print("=" * 60)
    print()
    print("📝 Steps:")
    print("1. A browser window will open")
    print("2. Sign in with your Google account")
    print("3. Click 'Allow' to grant permissions")
    print("4. Browser will try to redirect to http://localhost:[PORT]/")
    print()
    print("⚠️  If you see 'redirect_uri_mismatch' error:")
    print("   - Note the port number in the URL")
    print("   - Add that URI to Google Cloud Console")
    print("   - See OAUTH_SETUP_FIX.md for detailed steps")
    print()
    print("⚠️  If you see 'This app isn't verified':")
    print("   - Click 'Advanced'")
    print("   - Click 'Go to GEC Rajkot (unsafe)'")
    print("   - Click 'Allow'")
    print()
    
    print("⏱️  Waiting 10 seconds before starting...")
    print("   (Press Ctrl+C to cancel)")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return None
    
    print("\n🚀 Starting OAuth flow...")
    print("   Browser should open in 3... 2... 1...")
    print()
    
    try:
        # Initialize service (will trigger OAuth flow)
        print("🌐 Initializing EmailNotificationService...")
        service = EmailNotificationService()
        print("\n✅ Authentication successful!")
        print("📝 Token saved to token.pickle")
        print("🎉 You're all set! Gmail API is ready to use.")
        print()
        return service
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print()
        print("📋 To fix this:")
        print("1. Make sure you have the Google OAuth credentials JSON file")
        print("2. File should be in project root directory")
        print("3. Check .env file for GOOGLE_CREDENTIALS_FILE setting")
        return None
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user (Ctrl+C pressed)")
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Authentication failed: {error_msg}")
        
        # Check for specific errors
        if "redirect_uri_mismatch" in error_msg.lower():
            print()
            print("🔧 SOLUTION: Fix OAuth redirect URI")
            print("   See OAUTH_SETUP_FIX.md for step-by-step instructions")
            print()
            print("   Quick fix:")
            print("   1. Go to https://console.cloud.google.com/apis/credentials")
            print("   2. Edit your OAuth client")
            print("   3. Add redirect URIs (see OAUTH_SETUP_FIX.md)")
        elif "invalid_client" in error_msg.lower():
            print()
            print("🔧 SOLUTION: Check OAuth credentials")
            print("   - Make sure credentials JSON file is correct")
            print("   - Verify client ID and secret are valid")
        else:
            print()
            print("📋 Full error details:")
            import traceback
            traceback.print_exc()
        
        return None


def test_send_email(service):
    """Test sending an email"""
    if not service:
        print("❌ Cannot send email - authentication failed")
        return
    
    print("\n📧 Testing Email Send...\n")
    print("=" * 60)
    
    # Get recipient email
    recipient = input("Enter recipient email address: ")
    
    if not recipient:
        print("❌ No recipient provided")
        return
    
    print(f"\n📤 Sending test email to {recipient}...")
    
    # Send test announcement email
    success = send_announcement_email(
        student_email=recipient,
        announcement_title="Test Announcement",
        announcement_message="This is a test email from the GEC Rajkot notification system. If you received this, email notifications are working correctly!",
        faculty_name="Test Faculty"
    )
    
    if success:
        print(f"\n✅ Email sent successfully!")
        print(f"📬 Check your inbox: {recipient}")
        print("\n💡 Tip: If you don't see it, check your spam folder")
    else:
        print("\n❌ Failed to send email")
        print("📋 Check the error messages above for details")


def main():
    """Main test function"""
    print()
    print("=" * 60)
    print("      GEC Rajkot - Gmail API Test Script")
    print("=" * 60)
    
    try:
        # Step 1: Authenticate
        service = test_authentication()
        
        if not service:
            print("\n❌ Setup incomplete. Please fix the errors and try again.")
            print("\n📚 Helpful resources:")
            print("   - OAUTH_SETUP_FIX.md (fix redirect URI errors)")
            print("   - EMAIL_NOTIFICATIONS_GUIDE.md (complete setup guide)")
            print("   - ENV_SETUP_GUIDE.md (environment variables)")
            return
        
        # Step 2: Send test email
        print("\n" + "=" * 60)
        test_send_email(service)
        
        print()
        print("=" * 60)
        print("✅ Test Complete!")
        print("=" * 60)
        print()
        print("📚 Next Steps:")
        print("1. Email notifications are now ready to use")
        print("2. Faculty can create announcements/events")
        print("3. Students will receive email notifications automatically")
        print("4. Students can toggle email notifications in settings")
        print()
    
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user (Ctrl+C)")
        print("💡 To try again, run: python test_gmail_auth.py")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
