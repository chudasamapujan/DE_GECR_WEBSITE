# 🔧 Fix OAuth Error: redirect_uri_mismatch

## Error Message
```
Error 400: redirect_uri_mismatch
Access blocked: GEC_Rajkot's request is invalid
```

This error occurs when the redirect URI in your OAuth request doesn't match what's configured in Google Cloud Console.

---

## 🛠️ Solution: Update OAuth Redirect URIs

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com
2. Select project: **gec-rajkot**
3. In the left menu, go to **"APIs & Services"** → **"Credentials"**

### Step 2: Edit OAuth 2.0 Client ID

1. Find your OAuth 2.0 Client ID:
   - Client ID: `632055652735-3ockdd9un8bodnk9utgd74312ursunbg.apps.googleusercontent.com`
   
2. Click on the **pencil icon** (Edit) next to your OAuth client

3. Scroll down to **"Authorized redirect URIs"**

### Step 3: Add Redirect URIs

**IMPORTANT: Add the EXACT URI from your error!**

Based on your OAuth request, add this URI first:

```
http://localhost:51977/
```

**Then add these common ports** (click "+ ADD URI" for each):

```
http://localhost:8080/
http://localhost:8081/
http://localhost:8090/
http://localhost:51977/
http://127.0.0.1:8080/
http://127.0.0.1:8081/
http://127.0.0.1:8090/
http://127.0.0.1:51977/
urn:ietf:wg:oauth:2.0:oob
```

> **Note:** The port (51977) is randomly chosen by the OAuth library. Adding multiple common ports ensures it works on different runs.

### Step 4: Save Changes

1. Click **"SAVE"** at the bottom
2. Wait 1-2 minutes for changes to propagate

### Step 5: Test Again

Now run the authentication script again:

```bash
python test_gmail_auth.py
```

---

## 📝 Why This Happens

When you use `InstalledAppFlow.run_local_server()`, Google's library:
1. Starts a temporary local web server (on a random port like 8080, 8081, etc.)
2. Opens your browser to Google's OAuth page
3. After you grant permission, Google redirects back to `http://localhost:[PORT]/`

If the redirect URI isn't in the allowed list, you get the `redirect_uri_mismatch` error.

---

## 🔒 Alternative: Use Out-of-Band (OOB) Flow

If you can't edit the OAuth client, use the OOB flow instead:

### Update `utils/email_notification.py`

Find this code (around line 44):

```python
flow = InstalledAppFlow.from_client_secrets_file(
    str(CREDENTIALS_FILE), SCOPES
)
creds = flow.run_local_server(port=0)
```

Replace with:

```python
flow = InstalledAppFlow.from_client_secrets_file(
    str(CREDENTIALS_FILE), SCOPES
)
# Use OOB flow (manual code entry)
creds = flow.run_console()
```

**How OOB works:**
1. Opens browser to Google OAuth page
2. You grant permission
3. Google shows you a code
4. You copy/paste the code back into the terminal
5. Authentication completes

**No redirect URI needed!**

---

## ✅ Verification Steps

After fixing, verify:

1. **Run test script:**
   ```bash
   python test_gmail_auth.py
   ```

2. **Expected behavior:**
   - Browser opens to Google login
   - You sign in
   - Permission screen appears
   - You click "Allow"
   - Browser redirects back OR shows code (depending on method)
   - Script continues
   - `token.pickle` file created
   - Test email sent successfully

3. **Check for success messages:**
   ```
   ✅ Authentication successful!
   📝 Token saved to token.pickle
   ✅ Email sent successfully!
   ```

---

## 🐛 Troubleshooting

### Error: "This app isn't verified"

**Solution:**
1. Click **"Advanced"**
2. Click **"Go to GEC Rajkot (unsafe)"**
3. Click **"Allow"**

This is normal for apps in development/testing mode.

### Error: "Invalid request" (after adding URIs)

**Wait 1-2 minutes** - changes to OAuth configuration take time to propagate.

### Error: Still getting redirect_uri_mismatch

**Double-check:**
1. You edited the **correct** OAuth client (check client ID matches)
2. URIs are **exactly** as shown (including trailing slashes where specified)
3. You clicked **SAVE**
4. You waited 1-2 minutes

### Token file already exists but still getting errors

**Delete old token:**
```bash
del token.pickle
python test_gmail_auth.py
```

---

## 📚 Additional Configuration (Optional)

### For Production Deployment

When deploying to a web server (e.g., Render, Heroku):

1. Add production redirect URI:
   ```
   https://your-domain.com/oauth2callback
   ```

2. Update code to use web server flow instead of installed app flow

3. Store tokens securely (database, environment variables, secrets manager)

### For Desktop Application

If building a desktop app:

1. Keep OOB flow (`run_console()`)
2. OR implement custom redirect server
3. OR use device flow for better UX

---

## 🎯 Quick Fix Summary

**Fastest solution:**

1. Go to https://console.cloud.google.com/apis/credentials
2. Edit OAuth client
3. Add redirect URIs (especially `http://localhost:8080/` and `http://localhost:8081/`)
4. Save
5. Wait 2 minutes
6. Run `python test_gmail_auth.py` again

**Alternative (no console access):**

1. Edit `utils/email_notification.py`
2. Change `run_local_server(port=0)` to `run_console()`
3. Run `python test_gmail_auth.py`
4. Copy/paste the authorization code

---

## 📞 Need Help?

If you're still stuck:

1. **Check your OAuth client type:**
   - Should be **"Desktop app"** or **"Other"**
   - NOT "Web application"

2. **Verify scopes:**
   - Make sure `https://www.googleapis.com/auth/gmail.send` is in the OAuth consent screen scopes

3. **Check test users:**
   - If app is in testing mode, add your email to test users list

4. **Review Google Cloud Console:**
   - APIs & Services → Dashboard
   - Verify Gmail API is enabled
   - Check quota usage

---

*Last Updated: October 8, 2025*
*Issue: OAuth redirect_uri_mismatch*
*Status: 🔧 Fixable in 2 minutes*
