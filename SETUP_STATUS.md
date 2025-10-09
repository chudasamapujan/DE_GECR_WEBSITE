# 📊 Email Notifications Setup - Current Status

**Last Updated:** October 9, 2025  
**Status:** 95% Complete - Waiting for OAuth Configuration

---

## ✅ What's Already Done

### 1. Environment Configuration ✓
- ✅ Created `.env` file with all required variables
- ✅ Set `SECRET_KEY` (auto-generated secure key)
- ✅ Set `EMAIL_SENDER_ADDRESS` (pujanraj2005@gmail.com)
- ✅ Set `GOOGLE_CREDENTIALS_FILE` path
- ✅ Installed `python-dotenv` package
- ✅ Updated `app.py` to load environment variables
- ✅ Updated `utils/email_notification.py` to use .env values

### 2. Email System Implementation ✓
- ✅ Created `utils/email_notification.py` with Gmail API integration
- ✅ Beautiful HTML email templates (announcements & events)
- ✅ Email service with OAuth 2.0 authentication
- ✅ Bulk email sending capability
- ✅ Error handling and retry logic

### 3. Database Schema ✓
- ✅ Added `email_notifications_enabled` field to Student model
- ✅ Migrated existing database (1 student updated)
- ✅ Default: Email notifications ENABLED for all students

### 4. Backend Integration ✓
- ✅ Updated `routes/faculty_routes.py`
- ✅ `create_announcement()` sends emails automatically
- ✅ `create_event()` sends emails automatically
- ✅ Non-blocking email sending (announcements still created if email fails)

### 5. Documentation ✓
- ✅ `EMAIL_NOTIFICATIONS_GUIDE.md` - Complete email system guide
- ✅ `ENV_SETUP_GUIDE.md` - Environment variables reference
- ✅ `OAUTH_SETUP_FIX.md` - Detailed OAuth troubleshooting
- ✅ `QUICK_OAUTH_FIX.md` - **Quick 2-minute OAuth fix** ⭐
- ✅ `.env.example` - Template for environment variables
- ✅ `.gitignore` - Protects sensitive files

### 6. Testing Scripts ✓
- ✅ `test_env.py` - Verify environment configuration
- ✅ `test_gmail_auth_simple.py` - Simple OAuth authentication test
- ✅ `test_gmail_auth.py` - Full authentication and email test

---

## ⚠️ What's Blocking You

### The Only Issue: OAuth Redirect URI

**Problem:**  
Google Cloud Console doesn't have the redirect URIs that the OAuth library uses.

**Error You'll See:**  
`Error 400: redirect_uri_mismatch`

**Impact:**  
- Cannot authenticate with Gmail API
- Cannot send emails
- Everything else is ready and waiting

---

## 🚀 How to Fix It (2 Minutes)

### Step 1: Open Google Cloud Console
```
https://console.cloud.google.com/apis/credentials?project=gec-rajkot
```

### Step 2: Edit OAuth Client
- Find client with ID: `632055652735-3ockdd9un8bodnk9utgd74312ursunbg...`
- Click the **pencil icon** to edit

### Step 3: Add Redirect URIs
Click **"+ ADD URI"** and add each of these:

```
http://localhost:8080/
http://localhost:8081/
http://localhost:8090/
http://localhost:51977/
http://localhost:52000/
http://127.0.0.1:8080/
http://127.0.0.1:8081/
```

⚠️ **Important:** Include the trailing slash `/`

### Step 4: Save
- Click **"SAVE"**
- Wait **1-2 minutes** for changes to propagate

### Step 5: Test Authentication
```bash
python test_gmail_auth_simple.py
```

**Expected Result:**
- Browser opens
- You sign in with Google
- Grant permissions
- Browser redirects back
- Terminal shows: "✅ Authentication successful!"
- File created: `token.pickle`

### Step 6: Test Email Sending
The script will ask if you want to send a test email.
- Enter a test email address (or your own)
- Check inbox for test email

---

## 📋 Detailed Instructions

See: **`QUICK_OAUTH_FIX.md`** for step-by-step guide with screenshots explanation.

---

## 🎯 After OAuth is Fixed

Once authentication works:

### 1. Start Your Application
```bash
python app.py
```

### 2. Test End-to-End Flow

**As Faculty:**
1. Login: `http://127.0.0.1:5000/auth/login/faculty`
2. Go to Dashboard
3. Create a new announcement
4. Check terminal logs for "📤 Sending announcement emails..."

**As Student:**
1. Check your email inbox
2. You should receive a beautiful HTML email
3. Email will have:
   - 📢 Announcement icon
   - Purple gradient header
   - Faculty name and timestamp
   - Message content
   - "View on Portal" button
   - Link to manage email preferences

### 3. Verify Email Sending
Check server logs:
```
📤 Sending announcement emails to X students...
✅ Successfully sent 1 emails
❌ Failed to send 0 emails
```

---

## 🔧 Troubleshooting

### Script Hangs / Won't Stop

**Solution:**
1. Press `Ctrl+C` multiple times
2. Or close the terminal window
3. Fix OAuth redirect URIs first
4. Then try again

### "redirect_uri_mismatch" Error

**Solution:**
- You haven't added the redirect URIs yet
- See `QUICK_OAUTH_FIX.md`
- Takes 2 minutes

### "This app isn't verified" Warning

**This is normal!**
1. Click "Advanced"
2. Click "Go to GEC Rajkot (unsafe)"
3. Click "Allow"
4. (Your app is in testing mode - this warning is expected)

### Email Not Sending

**Check:**
1. Token exists: `token.pickle` file should be present
2. Environment: `EMAIL_NOTIFICATIONS_ENABLED=True` in `.env`
3. Student preferences: `email_notifications_enabled=True` in database
4. Logs: Check terminal for error messages

---

## 📁 Important Files

### Configuration
- `.env` - Your actual configuration (NOT in Git)
- `.env.example` - Template for others
- `client_secret_*.json` - Google OAuth credentials (NOT in Git)
- `token.pickle` - Gmail API token (created after auth, NOT in Git)

### Code
- `app.py` - Main Flask application
- `utils/email_notification.py` - Email sending service
- `routes/faculty_routes.py` - Announcement/event creation with emails
- `models/gecr_models.py` - Student model with email preference

### Documentation
- `QUICK_OAUTH_FIX.md` ⭐ **Start here!**
- `EMAIL_NOTIFICATIONS_GUIDE.md` - Complete guide
- `ENV_SETUP_GUIDE.md` - Environment variables
- `OAUTH_SETUP_FIX.md` - Detailed OAuth troubleshooting

### Testing
- `test_env.py` - Verify environment setup
- `test_gmail_auth_simple.py` - **Use this one!**
- `test_gmail_auth.py` - Alternative test script

---

## 📊 System Architecture

```
Faculty creates announcement
         ↓
routes/faculty_routes.py
         ↓
1. Save to database
2. Create in-app notifications
3. Call send_announcement_email_notifications()
         ↓
utils/email_notification.py
         ↓
1. Query students with email_notifications_enabled=True
2. Get student emails
3. Format HTML email from template
4. Send via Gmail API
         ↓
Students receive beautiful HTML emails
```

---

## 🎓 Student Email Preference

Students can control if they receive emails:

### Database Field
```python
class Student:
    email_notifications_enabled = db.Column(db.Boolean, default=True)
```

### Future UI (To Be Added)
In student settings page:
```
[ ✓ ] Receive email notifications
```

When unchecked:
- Student still gets in-app notifications
- Student does NOT receive emails
- Announcements/events still saved in database

---

## 📈 What Happens When Faculty Creates Announcement

### 1. Database Operation
```sql
INSERT INTO announcements (title, message, faculty_id, ...)
```

### 2. In-App Notifications
```python
create_notifications_for_students(announcement_id, "announcement")
```
- All students get in-app notification
- Shows up in student dashboard

### 3. Email Notifications (NEW!)
```python
send_announcement_email_notifications(title, message, faculty_name)
```
- Only sends to students with `email_notifications_enabled=True`
- Uses beautiful HTML template
- Non-blocking (won't fail announcement creation)
- Returns count: `{'sent': 5, 'failed': 0}`

---

## 🔐 Security Notes

### What's Protected
- ✅ `.env` file (in `.gitignore`)
- ✅ `client_secret_*.json` (in `.gitignore`)
- ✅ `token.pickle` (in `.gitignore`)
- ✅ Secret keys and passwords (never committed)

### Gmail API Permissions
- **Scope:** `https://www.googleapis.com/auth/gmail.send`
- **Permission:** Send emails only (cannot read emails)
- **Account:** pujanraj2005@gmail.com
- **Token:** Stored locally in `token.pickle`

### Best Practices
- ✅ Using environment variables for secrets
- ✅ OAuth 2.0 authentication (secure)
- ✅ Token refresh handled automatically
- ✅ Non-blocking email sending
- ✅ Student opt-out capability

---

## 📊 Current Status Summary

| Component | Status | Details |
|-----------|--------|---------|
| Environment Variables | ✅ Complete | .env file configured |
| Google OAuth Credentials | ✅ Complete | JSON file present |
| Email Service Code | ✅ Complete | Full implementation ready |
| Database Schema | ✅ Complete | Migration successful |
| Faculty Routes Integration | ✅ Complete | Emails sent on create |
| OAuth Redirect URIs | ⚠️ **BLOCKED** | Need to add in Console |
| Gmail Authentication | ⏸️ Waiting | Blocked by redirect URIs |
| Email Sending | ⏸️ Waiting | Blocked by authentication |
| Student Settings UI | 📋 Planned | Future enhancement |

---

## 🎯 Your Next Action

**Do this RIGHT NOW (2 minutes):**

1. Open: https://console.cloud.google.com/apis/credentials?project=gec-rajkot
2. Edit OAuth client: `632055652735-3ockdd9un8bodnk9utgd74312ursunbg...`
3. Add redirect URIs (see Step 3 above)
4. Click SAVE
5. Wait 2 minutes
6. Run: `python test_gmail_auth_simple.py`

**You're literally 2 minutes away from having a fully working email notification system!** 🚀

---

## 📞 Need Help?

**If stuck on OAuth:**
- Read: `QUICK_OAUTH_FIX.md` (step-by-step with screenshots explanation)
- Check: OAuth client type should be "Desktop app" not "Web application"
- Verify: Gmail API is enabled in your Google Cloud project

**If OAuth is fixed but emails not working:**
- Check: `token.pickle` file exists
- Verify: `.env` has `EMAIL_SENDER_ADDRESS` set
- Test: Run `python test_env.py` to verify configuration
- Logs: Check terminal output when creating announcements

---

*You've done 95% of the work. Just add those redirect URIs and you're done!* 🎉
