# 📘 Complete Facebook Integration Guide
## AI Employee Gold Tier - Facebook Automation

**Last Updated:** 2026-03-14  
**Status:** ✅ Fully Functional

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Setup & Configuration](#setup--configuration)
3. [Facebook Watcher - Monitoring Comments & Messages](#facebook-watcher---monitoring-comments--messages)
4. [Facebook Poster - Posting & Replying](#facebook-poster---posting--replying)
5. [Complete Workflow Examples](#complete-workflow-examples)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Your AI Employee now has **complete Facebook integration**:

| Feature | Status | Description |
|---------|--------|-------------|
| **Monitor Comments** | ✅ Working | Automatically detects new comments on your posts |
| **Monitor Messages** | ⚠️ Permission Required | Requires `pages_read_user_content` permission |
| **Create Action Files** | ✅ Working | Creates markdown files for each comment/message |
| **Draft Responses** | ✅ Working | AI drafts responses for your review |
| **Auto-Post Replies** | ✅ Working | Posts approved replies automatically |
| **Create Posts** | ✅ Working | Creates new Facebook posts |

---

## 🛠️ Setup & Configuration

### Prerequisites

1. **Facebook Page** - You must be an admin
2. **Facebook Developer Account** - https://developers.facebook.com/
3. **Facebook App** - Created in Facebook Developer Portal

### Step 1: Get Facebook Access Token

1. **Go to Graph API Explorer:**
   https://developers.facebook.com/tools/explorer/

2. **Select Your App** from dropdown

3. **Click "Get Token" → "Get Page Access Token"**

4. **Select Your Page** (e.g., 1023318870863610)

5. **Add Permissions:**
   - ✅ `pages_manage_posts` - Create posts
   - ✅ `pages_read_engagement` - Read engagement
   - ✅ `pages_show_list` - Show page info
   - ⚠️ `pages_read_user_content` - Read messages (optional)

6. **Copy the Token** (starts with `EAAn...`)

### Step 2: Configure .env File

Open `.env` in your project root:

```bash
# Facebook Configuration
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=EAAn...YOUR_TOKEN_HERE...
FACEBOOK_PAGE_ID=your_page_id
```

### Step 3: Test Connection

```bash
# Test Facebook connection
python watchers/facebook_poster.py AI_Employee_Vault --test-connection
```

**Expected Output:**
```
[OK] Access token configured
[OK] Page ID: 1023318870863610
```

---

## 👁️ Facebook Watcher - Monitoring Comments & Messages

### What It Does

The Facebook Watcher:
- ✅ Monitors your Facebook Page 24/7
- ✅ Detects new comments on posts
- ✅ Detects new messages (if permission granted)
- ✅ Creates action files in `Needs_Action/` folder
- ✅ Includes comment ID for replies
- ✅ Runs continuously in background

### Start the Watcher

```bash
# Monitor every 60 seconds
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60

# Monitor every 5 minutes
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

# Run once (test)
python watchers/facebook_watcher.py AI_Employee_Vault --once
```

### What Happens When a Comment Arrives

**Step 1: Comment on Facebook**
```
User "John Doe" comments: "Great post! How much does this cost?"
```

**Step 2: Watcher Detects It**
```
[OK] Found 1 new Facebook comment
[OK] Created action file: FACEBOOK_COMMENT_20260314_120000.md
```

**Step 3: File Created in Needs_Action/**

Location: `AI_Employee_Vault/Needs_Action/FACEBOOK_COMMENT_20260314_120000.md`

```markdown
---
type: social_media
platform: facebook
notification_type: comment
from: John Doe
comment_id: 123456789_987654321  ← Important for replies!
received: 2026-03-14T12:00:00+0000
priority: normal
status: pending
---

# Facebook Comment: John Doe

## Details
- **Platform:** Facebook
- **Type:** Comment
- **From:** John Doe
- **Received:** 2026-03-14T12:00:00+0000

---

## Content

Great post! How much does this cost?

---

## Suggested Actions

- [ ] Review message/comment
- [ ] Draft response
- [ ] Create approval request in Pending_Approval/
- [ ] Respond via Facebook
- [ ] Archive after processing

---

## Draft Response (for approval)

*Write your response here, then move file to Pending_Approval/*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________
```

---

## 📢 Facebook Poster - Posting & Replying

### What It Does

The Facebook Poster:
- ✅ Posts new content to Facebook
- ✅ Posts replies to comments
- ✅ Processes approved files
- ✅ Moves processed files to Done/

### Command Reference

```bash
# Post new content
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --platform facebook

# Post with approval workflow
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Draft post" \
  --require-approval

# Process approved posts
python watchers/facebook_poster.py AI_Employee_Vault --process-approved

# Process comment replies (NEW!)
python watchers/facebook_poster.py AI_Employee_Vault --process-replies

# Test connection
python watchers/facebook_poster.py AI_Employee_Vault --test-connection
```

---

## 🔄 Complete Workflow Examples

### Workflow 1: Reply to Facebook Comment (Automated)

**Scenario:** Someone comments on your post asking about pricing.

#### Step 1: Watcher Detects Comment

```bash
# Watcher running in background
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
```

**Output:**
```
[OK] Found 1 new Facebook comment
[OK] Created: FACEBOOK_COMMENT_20260314_120000.md
```

#### Step 2: Review the Comment

Open the file:
```
AI_Employee_Vault/Needs_Action/FACEBOOK_COMMENT_20260314_120000.md
```

Read the comment content.

#### Step 3: Draft Your Response

Edit the file, add your response:

```markdown
## Draft Response (for approval)

Hi John! Thanks for your interest! The price is $99/month. 
DM us for a special discount! 😊
```

#### Step 4: Move to Pending_Approval

Move the file:
```
From: AI_Employee_Vault/Needs_Action/
To:   AI_Employee_Vault/Pending_Approval/
```

#### Step 5: Review & Approve

1. Open file in `Pending_Approval/`
2. Review your drafted response
3. If approved, move to: `AI_Employee_Vault/Approved/`

#### Step 6: Post the Reply

```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

**Expected Output:**
```
Replying to comment: FACEBOOK_COMMENT_20260314_120000.md
  Comment ID: 123456789_987654321
  Reply: Hi John! Thanks for your interest! The price is $99/month...
  
  [SUCCESS] Reply posted!
      Reply ID: 123456789_111222333
  File moved to Done/
```

#### Step 7: Verify on Facebook

Go to your Facebook post - your reply is now visible! ✅

---

### Workflow 2: Create New Facebook Post

#### Step 1: Create Post Content

Create file: `AI_Employee_Vault/Plans/facebook_post.md`

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

#### Step 2: Post with Approval

```bash
python watchers/facebook_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/facebook_post.md \
  --require-approval
```

**Creates:** `Pending_Approval/SOCIAL_POST_APPROVAL_20260314_120000.md`

#### Step 3: Review & Approve

1. Open file in `Pending_Approval/`
2. Review the post content
3. Move to: `Approved/`

#### Step 4: Post to Facebook

```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

**Output:**
```
Posting: SOCIAL_POST_APPROVAL_20260314_120000.md
  Platforms: ['facebook']
  
[SUCCESS] Post published to Facebook!
  Post ID: 1023318870863610_122100931605124242
  URL: https://facebook.com/1023318870863610_122100931605124242
```

---

### Workflow 3: Daily Monitoring Routine

#### Morning Check (9:00 AM)

```bash
# Check what's pending
ls AI_Employee_Vault/Needs_Action/

# Process any comments
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

#### Throughout the Day

Watcher runs automatically:
```bash
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
```

#### Evening Review (5:00 PM)

```bash
# Check approved files
ls AI_Employee_Vault/Approved/

# Process any pending posts
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── FACEBOOK_COMMENT_*.md      ← New comments arrive here
│   └── FACEBOOK_MSG_*.md          ← New messages arrive here
│
├── Pending_Approval/
│   ├── FACEBOOK_COMMENT_*.md      ← Draft replies waiting review
│   └── SOCIAL_POST_APPROVAL_*.md  ← Draft posts waiting review
│
├── Approved/
│   ├── FACEBOOK_COMMENT_*.md      ← Replies ready to post
│   └── SOCIAL_POST_APPROVAL_*.md  ← Posts ready to publish
│
└── Done/
    ├── FACEBOOK_COMMENT_*.md      ← Posted replies
    └── SOCIAL_POST_APPROVAL_*.md  ← Published posts
```

---

## 🔧 Configuration Options

### Watcher Intervals

| Interval | Command | Use Case |
|----------|---------|----------|
| 30 seconds | `--interval 30` | High-volume pages |
| 1 minute | `--interval 60` | Active business pages |
| 5 minutes | `--interval 300` | Normal pages (recommended) |
| 15 minutes | `--interval 900` | Low-volume pages |

### Permission Levels

| Permission | What It Enables | Required For |
|------------|-----------------|--------------|
| `pages_manage_posts` | Create posts | ✅ Posting |
| `pages_read_engagement` | Read reactions | Reading comments |
| `pages_read_user_content` | Read messages | ⚠️ Private messages |
| `pages_show_list` | Show page info | Basic functionality |

---

## 🐛 Troubleshooting

### Problem: "Processed 0 replies"

**Causes:**
1. No files in `Approved/` folder
2. Files missing `comment_id` field
3. Files missing `## Draft Response` section

**Solution:**
```bash
# Check files exist
ls AI_Employee_Vault/Approved/

# Check file format
cat AI_Employee_Vault/Approved/FACEBOOK_COMMENT_*.md

# Ensure file has:
# 1. comment_id: xxx in frontmatter
# 2. ## Draft Response section with content
```

### Problem: "403 Forbidden" when posting

**Causes:**
1. Invalid access token
2. Missing permissions
3. Token expired

**Solution:**
```bash
# Test connection
python watchers/facebook_poster.py AI_Employee_Vault --test-connection

# If fails, get new token:
# 1. Go to: https://developers.facebook.com/tools/explorer/
# 2. Get new Page Access Token
# 3. Update .env with new token
```

### Problem: Watcher not detecting comments

**Causes:**
1. Token missing `pages_read_engagement` permission
2. No new comments since last check
3. Watcher not running

**Solution:**
```bash
# Check watcher is running
ps aux | grep facebook_watcher

# Check permissions
# Go to: https://developers.facebook.com/tools/debug/access_token/
# Verify pages_read_engagement is checked

# Test with manual run
python watchers/facebook_watcher.py AI_Employee_Vault --once
```

---

## 📊 Quick Reference Card

### Start Monitoring
```bash
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
```

### Post Reply to Comment
```bash
# 1. Write response in Needs_Action file
# 2. Move to Pending_Approval/
# 3. Move to Approved/
# 4. Run:
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

### Create New Post
```bash
# 1. Create content in Plans/
# 2. Run with --require-approval
# 3. Move to Approved/
# 4. Run:
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

### Test Everything
```bash
# Test connection
python watchers/facebook_poster.py AI_Employee_Vault --test-connection

# Test watcher
python watchers/facebook_watcher.py AI_Employee_Vault --once

# Test posting
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Test post" \
  --platform facebook
```

---

## ✅ Success Checklist

- [ ] Facebook access token configured in .env
- [ ] Connection test passes
- [ ] Watcher running (or scheduled)
- [ ] Can create action files from comments
- [ ] Can draft responses
- [ ] Can post replies with --process-replies
- [ ] Can create new posts with --process-approved
- [ ] Files moving through workflow correctly

---

## 📚 Additional Resources

- **Facebook Graph API:** https://developers.facebook.com/docs/graph-api
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Access Token Debugger:** https://developers.facebook.com/tools/debug/access_token/
- **Facebook Reply Guide:** FACEBOOK_REPLY_GUIDE.md (in your project)

---

**Your Facebook integration is complete and ready for automation!** 🎉
