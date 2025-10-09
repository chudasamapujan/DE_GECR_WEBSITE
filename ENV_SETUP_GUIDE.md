# 🔐 Environment Variables Setup Guide

This guide explains how to configure the `.env` file for your GEC Rajkot application.

## 📋 Quick Start

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** with your actual values

3. **Never commit `.env` to Git!** (already in `.gitignore`)

---

## 🔑 Required Configuration

### 1. Flask Secret Key

Generate a secure random key:

**PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and set:
```env
SECRET_KEY=<your-generated-key>
```

### 2. Gmail API Configuration

**Step 1: Get Client Secret**

From your Google OAuth credentials JSON file:
```json
{
  "installed": {
    "client_id": "632055652735-...",
    "client_secret": "GOCSPX-...",
    ...
  }
}
```

**Step 2: Set environment variables:**
```env
EMAIL_SENDER_ADDRESS=your-email@gmail.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-secret
```

**Step 3: Keep credentials file:**
```env
GOOGLE_CREDENTIALS_FILE=client_secret_632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com.json
```

### 3. Application URL

For development (default):
```env
BASE_URL=http://localhost:5000
```

For production:
```env
BASE_URL=https://your-domain.com
```

---

## 📊 Configuration Reference

### Flask Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask session encryption key | ⚠️ Change this! | ✅ Yes |
| `FLASK_ENV` | Environment (development/production) | development | No |
| `FLASK_DEBUG` | Enable debug mode | True | No |

### Database Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URI` | Database connection string | sqlite:///instance/gec_rajkot.db | No |

**For PostgreSQL (Production):**
```env
DATABASE_URI=postgresql://username:password@localhost:5432/gec_rajkot
```

### Email Notification Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_SENDER_ADDRESS` | Gmail account for sending | ⚠️ Set your email | ✅ Yes |
| `EMAIL_SENDER_NAME` | Display name in emails | GEC Rajkot | No |
| `EMAIL_NOTIFICATIONS_ENABLED` | Global email toggle | True | No |
| `EMAIL_BATCH_SIZE` | Max emails per batch | 50 | No |
| `EMAIL_MAX_RETRIES` | Retry failed sends | 3 | No |

### Google OAuth Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_CREDENTIALS_FILE` | OAuth credentials JSON | client_secret_...json | ✅ Yes |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret | From JSON file | ✅ Yes |
| `GMAIL_TOKEN_FILE` | Token storage file | token.pickle | No |
| `GOOGLE_SCOPES` | API scopes | gmail.send | No |

### Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BASE_URL` | Application base URL | http://localhost:5000 | ✅ Yes |
| `UPLOAD_FOLDER` | File upload directory | uploads | No |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | 16777216 (16MB) | No |

---

## 🔧 Example Configurations

### Development (Local Testing)

```env
# Flask
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Email
EMAIL_SENDER_ADDRESS=yourname@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=True

# App
BASE_URL=http://localhost:5000
```

### Production (Deployment)

```env
# Flask
SECRET_KEY=<64-character-random-hex-string>
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URI=postgresql://gecuser:securepassword@db.example.com:5432/gec_rajkot

# Email
EMAIL_SENDER_ADDRESS=noreply@gecrajkot.ac.in
EMAIL_NOTIFICATIONS_ENABLED=True
EMAIL_BATCH_SIZE=100

# App
BASE_URL=https://portal.gecrajkot.ac.in

# Security
CORS_ORIGINS=https://portal.gecrajkot.ac.in
```

---

## 🚀 Verification

### Test Configuration Loading

Create a test file `test_env.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

print("✅ Environment Variables Loaded:")
print(f"   SECRET_KEY: {'Set ✓' if os.getenv('SECRET_KEY') else 'Missing ✗'}")
print(f"   EMAIL_SENDER: {os.getenv('EMAIL_SENDER_ADDRESS', 'Not set')}")
print(f"   BASE_URL: {os.getenv('BASE_URL', 'http://localhost:5000')}")
print(f"   EMAIL_ENABLED: {os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'True')}")
print(f"   GOOGLE_CREDS: {'Found ✓' if os.path.exists(os.getenv('GOOGLE_CREDENTIALS_FILE', '')) else 'Missing ✗'}")
```

Run:
```bash
python test_env.py
```

### Expected Output

```
✅ Environment Variables Loaded:
   SECRET_KEY: Set ✓
   EMAIL_SENDER: yourname@gmail.com
   BASE_URL: http://localhost:5000
   EMAIL_ENABLED: True
   GOOGLE_CREDS: Found ✓
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Generate strong random secrets
- Keep `.env` in `.gitignore`
- Use different values for dev/prod
- Rotate secrets periodically
- Use environment-specific files (`.env.development`, `.env.production`)

### ❌ DON'T:
- Commit `.env` to Git
- Share `.env` files via email/chat
- Use default/example secrets in production
- Store `.env` in public locations
- Include credentials in error messages

---

## 📁 File Structure

```
DE_GECR_WEBSITE/
├── .env                    ← Your actual config (NOT in Git)
├── .env.example            ← Template (safe to commit)
├── .gitignore              ← Excludes .env
├── app.py                  ← Loads .env automatically
└── utils/
    └── email_notification.py ← Uses .env values
```

---

## 🐛 Troubleshooting

### Error: "SECRET_KEY not set"

**Solution:**
```env
SECRET_KEY=your-secret-key-here
```

Generate one:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Error: "Google credentials file not found"

**Check:**
1. File exists in project root
2. Filename matches `GOOGLE_CREDENTIALS_FILE` in `.env`
3. Path is correct (relative to project root)

### Error: "Email sender not configured"

**Set:**
```env
EMAIL_SENDER_ADDRESS=your-email@gmail.com
```

### Environment variables not loading

**Ensure:**
1. File is named exactly `.env` (not `env.txt` or `.env.txt`)
2. File is in project root (same folder as `app.py`)
3. `python-dotenv` package is installed:
   ```bash
   pip install python-dotenv
   ```
4. Code includes:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## 📚 Additional Resources

- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Flask Configuration](https://flask.palletsprojects.com/en/2.3.x/config/)
- [Google OAuth Setup](./OAUTH_SETUP_FIX.md)
- [Email Notifications Guide](./EMAIL_NOTIFICATIONS_GUIDE.md)

---

## 🎯 Next Steps

After setting up `.env`:

1. ✅ Run verification: `python test_env.py`
2. ✅ Test Gmail auth: `python test_gmail_auth.py`
3. ✅ Start application: `python app.py`
4. ✅ Check logs for configuration errors

---

*Last Updated: October 9, 2025*
*File: .env*
*Security Level: 🔴 Critical - Never commit to Git!*
