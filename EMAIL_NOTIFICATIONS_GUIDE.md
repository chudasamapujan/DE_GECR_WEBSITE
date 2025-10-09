# 📧 Email Notifications Setup Guide

## Overview
The GEC Rajkot portal now supports **email notifications** via Gmail API. When faculty members post announcements or create events, students automatically receive beautifully formatted HTML emails.

---

## ✨ Features

### 📬 Automatic Email Notifications
- **Announcements**: Students receive emails when faculty posts announcements
- **Events**: Students receive emails when faculty creates events
- **Beautiful Templates**: Professional HTML emails with GEC Rajkot branding
- **Plain Text Fallback**: Works in all email clients
- **User Preferences**: Students can enable/disable email notifications

### 🎨 Email Templates
- Gradient headers with emojis (📢 for announcements, 📅 for events)
- Clean, modern design using Tailwind-inspired styles
- Responsive layout (works on mobile and desktop)
- Direct links to portal
- Metadata (faculty name, date, time)

---

## 🚀 Setup Instructions

### Step 1: Enable Gmail API in Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create/Select Project**
   - Project name: `gec-rajkot` (already exists)
   - Project ID: `gec-rajkot`

3. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth Credentials** (Already Done ✅)
   - You already have: `client_secret_632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com.json`
   - Location: Project root directory

5. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - User Type: External
   - App name: GEC Rajkot Portal
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/gmail.send`
   - Test users: Add your email and any test accounts

---

### Step 2: Authenticate with Gmail

Run the authentication test script:

```bash
python test_gmail_auth.py
```

**What Happens:**
1. Browser opens automatically
2. Google login page appears
3. Sign in with the account you want to send emails FROM
4. Grant permissions to the app
5. Token is saved to `token.pickle`

**⚠️ Important:**
- Use the email account you want to SEND emails from (e.g., gecrajkot@gmail.com)
- The `token.pickle` file contains authentication credentials
- Keep `token.pickle` secure (already in `.gitignore`)

**If You See "App Not Verified" Warning:**
1. Click "Advanced"
2. Click "Go to GEC Rajkot (unsafe)"
3. Click "Allow"

This is normal for apps in development/testing mode.

---

### Step 3: Test Email Sending

After authentication, the script will ask for a recipient email:

```bash
Enter recipient email address: your-email@example.com
```

You'll receive a test email with:
- Subject: "📢 New Announcement: Test Announcement"
- Beautiful HTML template
- Test message content

**✅ Success Indicators:**
- Console shows: "✅ Email sent successfully!"
- Email arrives in recipient's inbox within seconds
- Email is properly formatted with images and styling

---

### Step 4: Update Database Schema

Recreate the database to add the new `email_notifications_enabled` field:

```bash
python recreate_db.py
```

This adds the `email_notifications_enabled` column to the students table (default: `True`).

---

## 🔧 Configuration

### Email Notification Settings

**Student Model** (`models/gecr_models.py`):
```python
class Student(db.Model):
    ...
    email_notifications_enabled = db.Column(db.Boolean, default=True)
```

**Default Behavior:**
- New students have email notifications **enabled** by default
- Students can disable in their settings page

---

## 📚 How It Works

### End-to-End Flow

#### 1. Faculty Creates Announcement

```
Faculty Dashboard
  ↓
"Manage Announcements" Page
  ↓
Fill form (title, message, expiry)
  ↓
Click "Create Announcement"
  ↓
POST /api/faculty/announcements
```

#### 2. Backend Processing

```python
# routes/faculty_routes.py

def create_announcement():
    # 1. Save announcement to database
    ann = Announcement(title=title, message=message, author_id=author_id)
    db.session.add(ann)
    db.session.commit()
    
    # 2. Create in-app notifications
    create_notifications_for_students(...)
    
    # 3. Send email notifications
    send_announcement_email_notifications(
        title=title,
        message=message,
        faculty_name=faculty.name
    )
```

#### 3. Email Sending

```python
# utils/email_notification.py

def send_announcement_email_notifications(...):
    # 1. Query students with email enabled
    students = Student.query.filter_by(
        email_notifications_enabled=True
    ).all()
    
    # 2. Collect email addresses
    student_emails = [s.email for s in students]
    
    # 3. Send bulk emails via Gmail API
    send_announcement_emails_bulk(...)
```

#### 4. Gmail API

```python
# utils/email_notification.py

class EmailNotificationService:
    def send_email(self, to, subject, body_html, body_text):
        # 1. Create MIME message
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        # 2. Attach HTML and plain text
        message.attach(MIMEText(body_text, 'plain'))
        message.attach(MIMEText(body_html, 'html'))
        
        # 3. Send via Gmail API
        service.users().messages().send(
            userId='me',
            body={'raw': base64_encoded_message}
        ).execute()
```

---

## 📧 Email Templates

### Announcement Email

**Subject:** `📢 New Announcement: {title}`

**HTML Template:**
- Purple gradient header with 📢 icon
- White content box with announcement details
- Faculty name and timestamp
- "View on Portal" button
- Footer with settings link

**Example:**
```html
┌────────────────────────────────────────┐
│  📢                                     │
│  New Announcement                      │
│  Government Engineering College, Rajkot│
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  Mid-term Exam Schedule          │ │
│  │                                  │ │
│  │  Mid-term exams will be         │ │
│  │  conducted from November 15-20.  │ │
│  │  Prepare accordingly.            │ │
│  │                                  │ │
│  │  Posted by: Dr. Sharma           │ │
│  │  Date: Oct 8, 2025 at 10:30 AM   │ │
│  └──────────────────────────────────┘ │
│                                        │
│         [View on Portal]                │
│                                        │
├────────────────────────────────────────┤
│  Automated notification from GEC Rajkot│
│  Manage preferences in Settings         │
└────────────────────────────────────────┘
```

### Event Email

**Subject:** `📅 New Event: {title}`

**HTML Template:**
- Pink/red gradient header with 📅 icon
- Event title and description
- Highlighted event details box (yellow background):
  - 🕐 Start and end time
  - 📍 Location
- Faculty name and timestamp
- "View Event Details" button
- Footer with settings link

---

## 🎯 Usage Examples

### Send Announcement Email (Single Student)

```python
from utils.email_notification import send_announcement_email

send_announcement_email(
    student_email="student@example.com",
    announcement_title="Important Update",
    announcement_message="Classes will resume on Monday.",
    faculty_name="Dr. Sharma"
)
```

### Send Announcement Emails (Bulk)

```python
from utils.email_notification import send_announcement_emails_bulk

results = send_announcement_emails_bulk(
    student_emails=["student1@example.com", "student2@example.com"],
    announcement_title="Holiday Notice",
    announcement_message="College will be closed tomorrow.",
    faculty_name="Dr. Patel"
)

print(f"Sent: {results['sent']}, Failed: {results['failed']}")
```

### Send Event Email (Single Student)

```python
from utils.email_notification import send_event_email
from datetime import datetime

send_event_email(
    student_email="student@example.com",
    event_title="Tech Fest 2025",
    event_description="Annual technical festival with competitions",
    start_time=datetime(2025, 11, 15, 10, 0),
    end_time=datetime(2025, 11, 15, 17, 0),
    location="Main Auditorium",
    faculty_name="Dr. Shah"
)
```

---

## 🔐 Security & Privacy

### OAuth Credentials
- **File:** `client_secret_*.json`
- **Contains:** Client ID, Client Secret, OAuth URLs
- **Security:** Keep secure, don't commit to public repos
- **Already in:** `.gitignore`

### Token Storage
- **File:** `token.pickle`
- **Contains:** Access token, refresh token
- **Security:** Highly sensitive - grants access to Gmail account
- **Already in:** `.gitignore`
- **Expiry:** Tokens auto-refresh when expired

### Best Practices
✅ Use a dedicated Gmail account for sending (e.g., gecrajkot@gmail.com)
✅ Don't use personal Gmail account
✅ Enable 2FA on the sending account
✅ Keep `token.pickle` secure
✅ Rotate credentials periodically
✅ Monitor API quota usage

---

## 📊 Quota & Limits

### Gmail API Quotas (Free Tier)
- **Daily Sending Limit:** 500 emails/day
- **Per-Second Rate:** 250 quota units/second
- **Per-User Rate:** 25 quota units/second/user

### For GEC Rajkot Portal
- **Students:** ~500-1000 students
- **Announcements:** ~5-10 per day
- **Events:** ~2-5 per day
- **Total Emails:** ~50-150 per day

**✅ Well within free tier limits!**

### If You Need More
- Upgrade to Google Workspace
- Use SendGrid/Mailgun for bulk emails
- Implement email batching/queuing

---

## 🐛 Troubleshooting

### Issue: "Authentication failed"
**Fix:**
1. Delete `token.pickle`
2. Run `python test_gmail_auth.py` again
3. Complete OAuth flow

### Issue: "App not verified" warning
**Fix:**
1. Click "Advanced"
2. Click "Go to... (unsafe)"
3. This is normal for test apps

### Issue: "Insufficient permissions"
**Fix:**
1. Go to Google Cloud Console
2. OAuth consent screen → Scopes
3. Add `https://www.googleapis.com/auth/gmail.send`
4. Delete `token.pickle` and re-authenticate

### Issue: "Quota exceeded"
**Fix:**
1. Check API quotas in Google Cloud Console
2. Wait 24 hours for reset
3. Consider upgrading plan

### Issue: Emails go to spam
**Fix:**
1. Add SPF/DKIM records (requires domain)
2. Use dedicated sending domain
3. Improve email content (less spammy words)
4. Ask recipients to mark as "Not Spam"

### Issue: Emails not sending
**Check:**
1. `token.pickle` exists and is valid
2. Internet connection working
3. Gmail API enabled in console
4. Students have `email_notifications_enabled=True`
5. Server logs for error messages

---

## 🧪 Testing Checklist

### Pre-Flight Checks
- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth credentials downloaded
- [ ] Credentials file in project root
- [ ] Python packages installed (`pip install -r requirements.txt`)

### Authentication Test
- [ ] Run `python test_gmail_auth.py`
- [ ] Browser opens automatically
- [ ] Login successful
- [ ] Permissions granted
- [ ] `token.pickle` created
- [ ] Test email sent successfully
- [ ] Email received in inbox

### Integration Test
- [ ] Database recreated with new schema
- [ ] Faculty can create announcements
- [ ] Announcement emails sent automatically
- [ ] Students receive emails
- [ ] Email formatting correct (HTML)
- [ ] Links in email work
- [ ] Plain text fallback works

### User Preference Test
- [ ] Student can toggle email notifications
- [ ] Setting saved to database
- [ ] Disabled students don't receive emails
- [ ] Enabled students receive emails

---

## 📈 Monitoring & Logs

### Server Logs

**Successful Email Send:**
```
INFO: Sending announcement emails to 5 students
✅ Email sent to student1@example.com (Message ID: abc123)
✅ Email sent to student2@example.com (Message ID: def456)
INFO: Email results: 5 sent, 0 failed
```

**Failed Email Send:**
```
WARNING: Email notification failed: HttpError 403
❌ Gmail API error sending to student@example.com: Insufficient permissions
INFO: Email results: 3 sent, 2 failed
```

### API Usage Monitoring

Check quota usage:
1. Go to Google Cloud Console
2. "APIs & Services" → "Dashboard"
3. Click "Gmail API"
4. View "Quotas" tab

---

## 🔄 Updating Email Templates

To customize email templates, edit `utils/email_notification.py`:

### Change Colors
```python
# Announcement header - Purple gradient
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# Event header - Pink/red gradient
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
```

### Change Button Color
```python
.button {
    background: #667eea;  # Change this color
}
```

### Change Font
```python
body {
    font-family: 'Your Font', Arial, sans-serif;
}
```

### Add Logo
```python
<img src="https://your-domain.com/logo.png" alt="GEC Rajkot">
```

---

## 🎓 Best Practices

### For Faculty
✅ Keep announcements concise (emails are truncated at 200 chars)
✅ Use clear, descriptive titles
✅ Include all important details
✅ Schedule announcements during business hours
✅ Avoid sending too many emails in one day

### For Administrators
✅ Monitor email delivery rates
✅ Check spam reports
✅ Keep Google Cloud credentials secure
✅ Rotate tokens periodically
✅ Monitor API quota usage
✅ Have backup email method (SMTP, SendGrid)

### For Students
✅ Check spam folder if emails missing
✅ Whitelist gecrajkot@gmail.com
✅ Update email preferences in settings
✅ Use a valid, active email address

---

## 📚 Next Steps

### Completed ✅
- Gmail API integration
- Email templates (announcement, event)
- Bulk email sending
- Student preference field
- Faculty route integration
- Authentication system

### Pending ⏳
- [ ] Add email notification toggle in student settings UI
- [ ] Create email logs/history
- [ ] Add email delivery status tracking
- [ ] Implement email queue for large batches
- [ ] Add admin dashboard for email analytics
- [ ] Create email templates for other notification types (attendance, assignments)

---

## 🆘 Support

**Issues?**
- Check server logs
- Review troubleshooting section
- Test with `python test_gmail_auth.py`
- Verify Google Cloud Console settings

**Resources:**
- Gmail API Docs: https://developers.google.com/gmail/api
- Google Cloud Console: https://console.cloud.google.com
- OAuth 2.0 Guide: https://developers.google.com/identity/protocols/oauth2

---

*Last Updated: October 8, 2025*
*Version: 1.0.0*
*Status: ✅ Ready for Testing*
