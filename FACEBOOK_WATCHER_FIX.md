# 🔧 Facebook Watcher Troubleshooting Guide

## Error 1: "FacebookAPI is not defined"

### Cause
The `facebook-business` SDK import is failing.

### Solution
The watcher is using the requests library directly (which works fine), so this error is just a warning. However, to fix it:

**Option A: Install facebook-business SDK**
```bash
pip install facebook-business
```

**Option B: Ignore the error** (Recommended)
The watcher works fine with just the `requests` library. The error is just informational.

---

## Error 2: Facebook Messages 403 Forbidden

### Cause
Your access token doesn't have permission to read Facebook messages/conversations.

### Required Permissions
To read Facebook Page messages, you need:
- ✅ `pages_manage_posts` - Post to pages
- ✅ `pages_read_engagement` - Read page engagement
- ✅ `pages_read_user_content` - **Read page messages** (THIS IS MISSING!)
- ✅ `pages_show_list` - Show page information

### Solution

1. **Go to Graph API Explorer:**
   https://developers.facebook.com/tools/explorer/

2. **Select your app**

3. **Click "Get Token" → "Get Page Access Token"**

4. **Select your Page**

5. **Add ALL these permissions:**
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_read_user_content` ← **IMPORTANT for messages!**
   - `pages_show_list`
   - `pages_manage_metadata`

6. **Click "Continue" → "Allow"**

7. **Copy the new token**

8. **Update .env:**
   ```bash
   FACEBOOK_ACCESS_TOKEN=YOUR_NEW_TOKEN_WITH_ALL_PERMISSIONS
   ```

---

## Error 3: Instagram Not Configured

### Cause
Your `.env` file has the placeholder value:
```bash
INSTAGRAM_ACCOUNT_ID=your_ig_account_id_here
```

### Solution Option A: Configure Instagram (If You Want Instagram Monitoring)

1. **Get Your Instagram Business Account ID:**

   Go to Graph API Explorer and run:
   ```
   GET /me/accounts?fields=instagram_business_account
   ```

   Or use this URL (replace PAGE_ID and TOKEN):
   ```
   https://graph.facebook.com/v18.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN
   ```

2. **Copy the Instagram Account ID** (it's a number like 17841400000000000)

3. **Update .env:**
   ```bash
   INSTAGRAM_ACCOUNT_ID=17841400000000000
   ```

### Solution Option B: Disable Instagram (If You Only Want Facebook)

**Edit `.env`:**
```bash
# Comment out or remove Instagram
# INSTAGRAM_ACCOUNT_ID=your_ig_account_id_here
```

**Or run watcher with Facebook only:**
```bash
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60 --platforms facebook
```

---

## 🚀 Quick Fix Commands

### Fix Facebook Messages Permission

```bash
# 1. Get new token with pages_read_user_content permission
# Go to: https://developers.facebook.com/tools/explorer/
# Get Page Access Token with ALL permissions

# 2. Update .env
# FACEBOOK_ACCESS_TOKEN=new_token_with_all_permissions

# 3. Test
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection
```

### Disable Instagram (Temporary Fix)

```bash
# Run with Facebook only
python watchers/facebook_watcher.py AI_Employee_Vault \
  --interval 60 \
  --platforms facebook
```

---

## ✅ Verify Fixed

After fixing, you should see:
```
[OK] Found 0 new Facebook messages
[OK] Found 0 new Facebook comments
```

Instead of 403/400 errors.

---

## 📋 Complete Permission List

### For Facebook Posting Only
- `pages_manage_posts`
- `pages_read_engagement`

### For Facebook Messages Too (Full Monitoring)
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_read_user_content` ← **Required for messages!**
- `pages_show_list`
- `pages_manage_metadata`

### For Instagram (Optional)
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_comments`
- `instagram_manage_insights`

---

## 🔗 Helpful Links

- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Access Token Debugger:** https://developers.facebook.com/tools/debug/access_token/
- **Facebook Pages API:** https://developers.facebook.com/docs/pages/api
- **Facebook Messages:** https://developers.facebook.com/docs/graph-api/reference/page/conversations

---

**Last Updated:** 2026-03-14
