# 🚀 Quick OAuth Setup - Add Redirect URI

## The Problem
You're getting `redirect_uri_mismatch` error because Google Cloud Console doesn't have the redirect URI that the app is trying to use.

## ✅ Quick Fix (2 minutes)

### Step 1: Go to Google Cloud Console
Open this link in your browser:
```
https://console.cloud.google.com/apis/credentials?project=gec-rajkot
```

### Step 2: Click on your OAuth Client
Look for:
- **Client ID**: `632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com`
- Click the **pencil icon** (Edit) or click on the client name

### Step 3: Add Redirect URIs
Scroll down to **"Authorized redirect URIs"** section

Click **"+ ADD URI"** and add these URIs **one by one**:

```
http://localhost:8080/
http://localhost:8081/
http://localhost:8090/
http://localhost:50000/
http://localhost:51977/
http://localhost:52000/
http://localhost:53000/
http://localhost:54000/
http://localhost:55000/
http://localhost:60000/
http://127.0.0.1:8080/
http://127.0.0.1:8081/
http://127.0.0.1:8090/
```

### Step 4: Save
- Click **"SAVE"** button at the bottom
- Wait **1-2 minutes** for changes to propagate

### Step 5: Try Again
Run the authentication script:
```bash
python test_gmail_auth_simple.py
```

---

## 📸 Visual Guide

### What You'll See:

1. **APIs & Services → Credentials**
   ```
   [Your OAuth Credentials list will be here]
   ```

2. **Click on OAuth 2.0 Client ID**
   ```
   Client name: GEC_Rajkot (or similar)
   Client ID: 632055652735-...
   ```

3. **Authorized redirect URIs section**
   ```
   + ADD URI
   [List of URIs you already have]
   ```

4. **Add each URI** from the list above

5. **Click SAVE**

---

## 🎯 Why These URIs?

The OAuth library (`InstalledAppFlow.run_local_server(port=0)`) chooses a **random available port** on your computer. By adding multiple common ports, we ensure the authentication will work regardless of which port gets selected.

---

## ⚠️ Common Mistakes

1. **Forgetting the trailing slash `/`** 
   - ✅ Correct: `http://localhost:8080/`
   - ❌ Wrong: `http://localhost:8080`

2. **Using https instead of http**
   - ✅ Correct: `http://localhost:8080/`
   - ❌ Wrong: `https://localhost:8080/`

3. **Not waiting for changes to propagate**
   - After saving, wait 1-2 minutes before testing

4. **Editing the wrong OAuth client**
   - Make sure the Client ID matches: `632055652735-3ockdd9un8bodnk9utgd74312ursunbg...`

---

## 🔍 Still Not Working?

### Check OAuth Client Type

Make sure your OAuth client is type **"Desktop app"** or **"Other"**, not "Web application".

If it's "Web application":
1. Delete it
2. Create a new one with type "Desktop app"
3. Download the new credentials JSON
4. Replace your existing JSON file
5. Update .env if filename changed

### Verify Gmail API is Enabled

1. Go to: https://console.cloud.google.com/apis/dashboard?project=gec-rajkot
2. Look for **"Gmail API"**
3. If not enabled, click **"+ ENABLE APIS AND SERVICES"**
4. Search for "Gmail API"
5. Click "Enable"

---

## 📞 Alternative Method (If Console Access is Blocked)

If you can't access Google Cloud Console, ask the person who created the OAuth credentials to add the redirect URIs for you.

Send them this list:
```
http://localhost:8080/
http://localhost:8081/
http://localhost:8090/
http://localhost:50000/
http://localhost:51977/
http://127.0.0.1:8080/
http://127.0.0.1:8081/
```

---

*Last Updated: October 9, 2025*
*Estimated Time: 2 minutes*
*Difficulty: ⭐ Easy*
