# Facebook Graph API Setup Guide

Complete guide for setting up Facebook and Instagram integration using the official Facebook Graph API.

---

## 📋 Prerequisites

- **Facebook Page** (you must be an admin)
- **Facebook Developer Account** at https://developers.facebook.com/
- **Instagram Business Account** (optional, for Instagram posting)
- **Python 3.10+**

---

## 🚀 Quick Start

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select **Business** as the app type
4. Fill in app details:
   - **App Name:** AI Employee
   - **App Contact Email:** your@email.com
5. Click **Create App**

### Step 2: Configure App Permissions

Add these products to your app:

1. **Pages API**
   - Go to App Dashboard → Add Product → Pages
   - Click **Set Up**

2. **Instagram Graph API** (optional)
   - Go to App Dashboard → Add Product → Instagram
   - Click **Set Up**

3. **Required Permissions:**
   - `pages_manage_posts` - Create posts on Pages
   - `pages_read_engagement` - Read Page engagement
   - `pages_read_user_content` - Read Page content
   - `instagram_basic` - Basic Instagram info
   - `instagram_content_publish` - Post to Instagram
   - `instagram_manage_comments` - Read/write comments
   - `instagram_manage_insights` - Read Instagram insights

### Step 3: Get Page Access Token

#### Option A: Graph API Explorer (Quick Setup)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Get Token** → **Get Page Access Token**
4. Select your Page
5. Check required permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
6. Click **Generate Token**
7. Copy the **Access Token**

#### Option B: Long-Lived Token (Recommended for Production)

1. Get a short-lived token from Graph API Explorer
2. Exchange for long-lived token:

```bash
curl -G \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=YOUR_SHORT_LIVED_TOKEN" \
  "https://graph.facebook.com/v18.0/oauth/access_token"
```

3. Long-lived tokens last ~60 days

### Step 4: Get Page ID and Instagram Account ID

#### Get Page ID

1. Go to your Facebook Page
2. Click **About**
3. Find **Page ID** (e.g., `123456789012345`)

Or use Graph API:
```bash
curl "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_TOKEN"
```

#### Get Instagram Account ID

1. Make sure Instagram is a **Business Account**
2. Connect Instagram to your Facebook Page
3. Use Graph API to get ID:

```bash
curl -G \
  -d "fields=instagram_business_account" \
  -d "access_token=YOUR_TOKEN" \
  "https://graph.facebook.com/v18.0/YOUR_PAGE_ID"
```

The response will include:
```json
{
  "instagram_business_account": {
    "id": "17841400000000000"
  }
}
```

### Step 5: Configure Environment Variables

Create/update `.env` file:

```bash
# Facebook Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token
FACEBOOK_PAGE_ID=your_page_id_here
INSTAGRAM_ACCOUNT_ID=your_ig_business_account_id
```

### Step 6: Test Connection

```bash
# Test Facebook connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# Test posting
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Test post from AI Employee" \
  --require-approval
```

---

## 📁 File Structure

```
Bronze-Tier--AI-Employee/
├── .env                              # Facebook credentials
├── watchers/
│   ├── facebook_watcher.py           # Facebook/Instagram monitoring
│   └── facebook_poster.py            # Facebook/Instagram posting
└── AI_Employee_Vault/
    ├── Needs_Action/
    │   ├── FACEBOOK_MSG_*.md        # Facebook messages
    │   └── INSTAGRAM_MSG_*.md       # Instagram messages
    └── Pending_Approval/
        └── SOCIAL_POST_APPROVAL_*.md # Posts awaiting approval
```

---

## 🔧 Available Commands

### Facebook Watcher

```bash
# Run continuously (check every 5 minutes)
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

# Run once and exit
python watchers/facebook_watcher.py AI_Employee_Vault --once

# Test connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# Monitor only Facebook (not Instagram)
python watchers/facebook_watcher.py AI_Employee_Vault --platforms facebook

# Monitor both platforms
python watchers/facebook_watcher.py AI_Employee_Vault --platforms facebook,instagram
```

### Facebook Poster

```bash
# Post to Facebook
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --platform facebook

# Post to Instagram (requires image)
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --image path/to/image.jpg \
  --platform instagram

# Post to both
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --platform both

# With approval workflow
python watchers/facebook_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/social_post.md \
  --require-approval

# Process approved posts
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

---

## 📝 Content Templates

### Facebook Post Template

Create `AI_Employee_Vault/Plans/facebook_post.md`:

```markdown
---
platforms: facebook
hashtags: ["#AI", "#Automation", "#Business"]
---

🤖 Exciting News!

Our AI Employee system helps businesses automate:
✅ Email processing
✅ Social media monitoring
✅ Customer communications

Want to learn more? DM us!

#AI #Automation #Business
```

### Instagram Post Template

```markdown
---
platforms: instagram
image: /path/to/image.jpg
hashtags: ["#AI", "#Automation"]
---

🚀 Transform your business with AI automation!

Our AI Employee works 24/7 to:
• Monitor customer messages
• Process inquiries automatically  
• Generate reports and briefings

Link in bio to learn more!

#AI #BusinessAutomation #Productivity
```

---

## 🔒 Security Best Practices

### Token Management

1. **Never commit tokens to Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use long-lived tokens** (60 days vs 1 hour)

3. **Rotate tokens regularly**
   - Set calendar reminder to refresh tokens
   - Update `.env` file with new token

4. **Limit token permissions**
   - Only request permissions you need
   - Review permissions in App Dashboard

### App Review

For production use, your app must pass **Facebook App Review**:

1. Go to App Dashboard → App Review
2. Submit each permission for review
3. Provide:
   - Detailed use case description
   - Screen recording of your app
   - Step-by-step testing instructions

**Note:** Development mode allows unlimited testing with your own Page.

---

## 🐛 Troubleshooting

### "Invalid Access Token"

```bash
# Check token expiration
curl "https://graph.facebook.com/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_APP_ID|YOUR_APP_SECRET"
```

**Solution:** Generate new long-lived token

### "Permissions Not Granted"

**Error:** `(#200) Requires pages_manage_posts permission`

**Solution:**
1. Go to Graph API Explorer
2. Generate new token with required permissions
3. Or submit for App Review

### "Instagram Account Not Connected"

**Solution:**
1. Make sure Instagram is a **Business Account**
2. Connect Instagram to Facebook Page:
   - Page Settings → Instagram → Connect
3. Get new Instagram Account ID

### "Image Upload Failed for Instagram"

Instagram requires images at **public URLs**.

**Solutions:**
1. Upload to cloud storage (S3, Cloudinary)
2. Host on your own server
3. Use image hosting service (Imgur)

---

## 📊 API Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| Page Posts | 200 posts per hour |
| Instagram Posts | 25 posts per hour |
| Comments Read | 200 requests per hour |
| Messages Read | 200 requests per hour |

---

## 🔗 Resources

- **Facebook Graph API Docs:** https://developers.facebook.com/docs/graph-api
- **Instagram Graph API:** https://developers.facebook.com/docs/instagram-api
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Access Token Tool:** https://developers.facebook.com/tools/access_token/
- **App Review Guide:** https://developers.facebook.com/docs/app-review

---

*Facebook/Instagram integration complete! Your AI Employee can now monitor and post to social media.*
