# Facebook Integration - How It Works

Complete guide on how Facebook auto-posting and comment/message detection works in your AI Employee system.

---

## 📋 Overview

The Facebook integration has two main components:

1. **Facebook Watcher** - Detects new messages and comments
2. **Facebook Poster** - Posts content to Facebook/Instagram

Both use the **Facebook Graph API** for reliable, production-ready integration.

---

## 🔄 How Facebook Watcher Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Facebook API   │────▶│ Facebook Watcher │────▶│  Needs_Action/  │
│  (Graph API)    │     │  (Polling)       │     │  (Action Files) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │  Qwen Code       │
                                              │  (Processing)    │
                                              └──────────────────┘
```

### Step-by-Step Process

#### Step 1: Watcher Polls Facebook API

The watcher runs continuously and polls the Facebook Graph API at regular intervals:

```python
# Every 5 minutes (300 seconds)
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300
```

**What it checks:**
- Facebook Page messages
- Facebook Page post comments
- Instagram direct messages (if configured)
- Instagram media comments (if configured)

#### Step 2: API Returns New Activity

Facebook Graph API returns new messages and comments:

**Facebook Messages Endpoint:**
```
GET /{page-id}/conversations?fields=messages{from,message,created_time,id}
```

**Facebook Comments Endpoint:**
```
GET /{post-id}/comments?fields=from,message,created_time,id
```

#### Step 3: Watcher Creates Action Files

For each new message/comment, the watcher creates a `.md` file in `Needs_Action/`:

**Example: New Facebook Message**

File: `AI_Employee_Vault/Needs_Action/FACEBOOK_MSG_20260313_143022_John_Doe.md`

```markdown
---
type: social_media
platform: facebook
notification_type: message
from: John Doe
received: 2026-03-13T14:30:22+0000
priority: high
status: pending
---

# Facebook Message: John Doe

## Details
- **Platform:** Facebook
- **Type:** Message
- **From:** John Doe
- **Received:** 2026-03-13T14:30:22+0000
- **Priority:** High

---

## Content

Hi, I need an invoice for last month's services. Can you send it to me?

---

## Suggested Actions

- [ ] Review message
- [ ] Draft response
- [ ] Create approval request
- [ ] Respond via Facebook
- [ ] Archive after processing
```

**Example: New Facebook Comment**

File: `AI_Employee_Vault/Needs_Action/FACEBOOK_COMMENT_20260313_150045_Jane_Smith.md`

```markdown
---
type: social_media
platform: facebook
notification_type: comment
from: Jane Smith
received: 2026-03-13T15:00:45+0000
priority: normal
status: pending
---

# Facebook Comment: Jane Smith

## Details
- **Platform:** Facebook
- **Type:** Comment
- **From:** Jane Smith
- **Received:** 2026-03-13T15:00:45+0000
- **Priority:** Normal

---

## Content

Great post! How much does your service cost?

---

## Suggested Actions

- [ ] Review comment
- [ ] Draft response
- [ ] Create approval request
- [ ] Respond via Facebook
```

#### Step 4: AI Employee Processes Action Files

Now Qwen Code (Claude) processes the action files:

```bash
# Process all pending items
cd AI_Employee_Vault
claude "Review all files in Needs_Action folder. For each Facebook message/comment, draft a response and create an approval request."
```

**Qwen Code will:**
1. Read each action file
2. Understand the context
3. Draft an appropriate response
4. Create an approval request in `Pending_Approval/`

#### Step 5: Human Reviews and Approves

You review the drafted responses in Obsidian:

1. Open `AI_Employee_Vault/Pending_Approval/`
2. Review each approval request
3. If approved, move file to `Approved/`
4. If rejected, move file to `Rejected/`

#### Step 6: Poster Sends Response

The Facebook Poster processes approved responses:

```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

**What happens:**
- Reads approved files
- Posts responses to Facebook via Graph API
- Moves files to `Done/`

---

## 📢 How Facebook Auto-Posting Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Content Plan   │────▶│ Facebook Poster  │────▶│  Facebook Page  │
│  (Markdown)     │     │  (Graph API)     │     │  (Published)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Pending_Approval│
                        │  (Human Review)  │
                        └──────────────────┘
```

### Step-by-Step Auto-Posting

#### Step 1: Create Post Content

Create a markdown file with your post content:

**File: `AI_Employee_Vault/Plans/facebook_post.md`**

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

#### Step 2: Create Approval Request

```bash
python watchers/facebook_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/facebook_post.md \
  --require-approval
```

**This creates:** `AI_Employee_Vault/Pending_Approval/SOCIAL_POST_APPROVAL_20260313_140000.md`

```markdown
---
type: approval_request
action: social_media_post
platforms: facebook
created: 2026-03-13T14:00:00
status: pending
hashtags: #AI, #Automation, #Business
---

# Social Media Post Approval Request

## Platforms
facebook

## Post Content

🤖 Exciting News!

Our AI Employee system helps businesses automate:
✅ Email processing
✅ Social media monitoring
✅ Customer communications

Want to learn more? DM us!

#AI #Automation #Business

---

## Preview

🤖 Exciting News!

Our AI Employee system helps businesses automate...

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
```

#### Step 3: Human Reviews

Open the file in Obsidian and review:
- Check content accuracy
- Verify hashtags
- Ensure tone is appropriate

If approved: **Move file to `Approved/`**

#### Step 4: Post to Facebook

```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

**Output:**
```
Posting: SOCIAL_POST_APPROVAL_20260313_140000.md
  Platforms: ['facebook']
============================================================
Facebook Poster - Starting (Graph API)
============================================================

[Step 2/2] Posting to Facebook...
      Content length: 187 chars

[SUCCESS] Post published to Facebook!
      Post ID: 123456789012345_987654321098765
      URL: https://facebook.com/123456789012345_987654321098765
```

---

## 🚀 Quick Start Commands

### Start Facebook Watcher

```bash
# Basic usage (check every 5 minutes)
python watchers/facebook_watcher.py AI_Employee_Vault

# Custom interval (check every 2 minutes)
python watchers/facebook_watcher.py AI_Employee_Vault --interval 120

# Facebook only (no Instagram)
python watchers/facebook_watcher.py AI_Employee_Vault --platforms facebook

# Run once (for testing)
python watchers/facebook_watcher.py AI_Employee_Vault --once

# Test connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection
```

### Post to Facebook

```bash
# Simple text post
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Hello from AI Employee!" \
  --platform facebook

# Post with image
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Check out our new product!" \
  --image /path/to/image.jpg \
  --platform facebook

# Post with link
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Read our latest blog post" \
  --link https://yourwebsite.com/blog \
  --platform facebook

# With approval workflow
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Test post" \
  --require-approval
```

### Process Pending Items

```bash
# 1. Check what's in Needs_Action
ls AI_Employee_Vault/Needs_Action/

# 2. Process with Qwen Code
cd AI_Employee_Vault
claude "Review all Facebook messages in Needs_Action and draft responses"

# 3. Check approvals
ls AI_Employee_Vault/Pending_Approval/

# 4. Process approved posts
python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

---

## 📊 Complete Workflow Example

### Scenario: Customer asks about pricing via Facebook message

**Timeline:**

| Time | Action | File Created |
|------|--------|--------------|
| 10:00 AM | Customer sends Facebook message | - |
| 10:05 AM | Facebook Watcher detects message | `Needs_Action/FACEBOOK_MSG_...md` |
| 10:10 AM | Qwen Code processes message | `Plans/PLAN_response_...md` |
| 10:15 AM | Qwen drafts response | `Pending_Approval/FACEBOOK_REPLY_...md` |
| 10:20 AM | Human reviews and approves | Move to `Approved/` |
| 10:25 AM | Facebook Poster sends response | File moved to `Done/` |

**Step-by-Step:**

```bash
# 10:05 AM - Watcher creates action file
# Running in background:
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

# Output:
# [OK] Found 1 new item(s)
# [OK] Created action file: FACEBOOK_MSG_20260313_100500_Customer_Name.md

# 10:10 AM - Process with Qwen Code
cd AI_Employee_Vault
claude "Review the new Facebook message in Needs_Action. Draft a polite response with pricing information."

# Qwen creates:
# - Plans/PLAN_response_customer.md
# - Pending_Approval/FACEBOOK_REPLY_20260313_101000.md

# 10:20 AM - Human reviews in Obsidian
# Open: AI_Employee_Vault/Pending_Approval/FACEBOOK_REPLY_...md
# Review the drafted response
# Move to: AI_Employee_Vault/Approved/

# 10:25 AM - Send response
python watchers/facebook_poster.py AI_Employee_Vault --process-approved

# Output:
# [SUCCESS] Response sent to Facebook!
```

---

## 🔧 Advanced Configuration

### Priority Keywords

The watcher flags messages with priority keywords as **high priority**:

```python
# In facebook_watcher.py (line ~85)
self.priority_keywords = [
    'urgent', 'asap', 'invoice', 'payment', 'order',
    'purchase', 'buy', 'price', 'cost', 'help'
]
```

**High priority messages get:**
- `[HIGH]` tag in logs
- `priority: high` in action file frontmatter

### Custom Check Intervals

| Interval | Use Case | Command |
|----------|----------|---------|
| 60 seconds | High-volume pages | `--interval 60` |
| 5 minutes | Normal business | `--interval 300` |
| 15 minutes | Low-volume pages | `--interval 900` |

### Scheduling Posts

Use the scheduler for automated posting:

```bash
# Start scheduler
python scheduler.py

# Or use cron/Task Scheduler
# Post every day at 9:00 AM
0 9 * * * python watchers/facebook_poster.py AI_Employee_Vault --process-approved
```

---

## 📝 Example Action Files

### Facebook Message (High Priority)

```markdown
---
type: social_media
platform: facebook
notification_type: message
from: John Doe
received: 2026-03-13T14:30:22+0000
priority: high
status: pending
---

# Facebook Message: John Doe

## Details
- **From:** John Doe
- **Received:** 2026-03-13T14:30:22+0000
- **Priority:** High

---

## Content

URGENT: I need an invoice for last month ASAP!

---

## Suggested Actions

- [ ] Review message
- [ ] Draft response
- [ ] Create approval request
- [ ] Respond via Facebook
```

### Instagram Comment

```markdown
---
type: social_media
platform: instagram
notification_type: comment
from: Jane Smith
received: 2026-03-13T15:00:45+0000
priority: normal
status: pending
---

# Instagram Comment: Jane Smith

## Details
- **Platform:** Instagram
- **Type:** Comment
- **From:** Jane Smith
- **Received:** 2026-03-13T15:00:45+0000
- **Priority:** Normal

---

## Content

Love this! How can I sign up?

---

## Suggested Actions

- [ ] Review comment
- [ ] Draft response
- [ ] Create approval request
```

---

## 🐛 Troubleshooting

### Watcher Not Detecting Messages

```bash
# 1. Test connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# 2. Check credentials in .env
cat .env | grep FACEBOOK

# 3. Run with verbose output
python watchers/facebook_watcher.py AI_Employee_Vault --interval 30
```

### Poster Not Posting

```bash
# 1. Test connection
python watchers/facebook_poster.py AI_Employee_Vault --test-connection

# 2. Check token permissions
# Go to: https://developers.facebook.com/tools/explorer/
# Generate token with pages_manage_posts permission

# 3. Try simple post
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Test post" \
  --platform facebook
```

### Action Files Not Being Processed

```bash
# Check files exist
ls -la AI_Employee_Vault/Needs_Action/

# Check file content
cat AI_Employee_Vault/Needs_Action/FACEBOOK_MSG_*.md

# Process with Qwen Code
cd AI_Employee_Vault
claude "Process all Facebook messages in Needs_Action folder"
```

---

## 📚 Resources

- **Facebook Setup Guide:** FACEBOOK_SETUP.md
- **Gold Tier Documentation:** GOLD_TIER.md
- **Graph API Docs:** https://developers.facebook.com/docs/graph-api
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/

---

*Your AI Employee is now ready to automate Facebook and Instagram!*
