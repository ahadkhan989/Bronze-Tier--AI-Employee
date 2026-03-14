# 📘 Facebook Comment Reply Guide

## How to Reply to Facebook Comments with AI Employee

---

## 🔄 Complete Workflow

### Step 1: Watcher Detects Comment
```
Facebook Comment → Facebook Watcher → Creates file in Needs_Action/
```

### Step 2: Review & Draft Response
1. Open the file from `Needs_Action/`
2. Read the comment
3. Write your response in the `## Draft Response` section
4. Move file to `Pending_Approval/`

### Step 3: Approve & Post
1. Review the file in `Pending_Approval/`
2. Move to `Approved/` folder
3. Run the reply command
4. File moves to `Done/`

---

## 📝 Step-by-Step Instructions

### When a Comment Arrives

The Facebook Watcher creates a file like:
```
AI_Employee_Vault/Needs_Action/FACEBOOK_COMMENT_20260314_120000.md
```

### 1. Open the File

The file will have this structure:
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

## Content

Great post!

---

## Draft Response (for approval)

*Write your response here, then move file to Pending_Approval/*
```

### 2. Write Your Response

Edit the file and add your response:

```markdown
## Draft Response (for approval)

Thank you so much! We're glad you liked it! 😊
```

### 3. Move to Pending_Approval

Move the file from:
- `Needs_Action/FACEBOOK_COMMENT_*.md`
- To: `Pending_Approval/FACEBOOK_COMMENT_*.md`

### 4. Review & Approve

1. Open the file in `Pending_Approval/`
2. Review your drafted response
3. If approved, move to: `Approved/`

### 5. Post the Reply

Run this command:

```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

**Expected Output:**
```
Replying to comment: FACEBOOK_COMMENT_20260314_120000.md
  Comment ID: 123456789_987654321
  Reply: Thank you so much! We're glad you liked it! 😊...
  
  [SUCCESS] Reply posted!
      Reply ID: 123456789_111222333
```

### 6. Done!

The file is automatically moved to `Done/` folder.

Check your Facebook post - the reply should be visible!

---

## 🚀 Quick Commands

### Process Comment Replies
```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

### Check Connection
```bash
python watchers/facebook_poster.py AI_Employee_Vault --test-connection
```

### Monitor Facebook (Continuous)
```bash
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   └── FACEBOOK_COMMENT_*.md     ← New comments arrive here
├── Pending_Approval/
│   └── FACEBOOK_COMMENT_*.md     ← Draft responses waiting for review
├── Approved/
│   └── FACEBOOK_COMMENT_*.md     ← Ready to post
└── Done/
    └── FACEBOOK_COMMENT_*.md     ← Posted replies
```

---

## ⚠️ Important Notes

### Required Fields in File

For replies to work, the file MUST have:
1. ✅ `comment_id:` in frontmatter
2. ✅ `## Draft Response` section with your reply

### File Must Be In Approved Folder

Only files in `Approved/` folder will be processed.

### One Command for All Replies

The `--process-replies` command processes ALL pending replies in the Approved folder.

---

## 🐛 Troubleshooting

### "Processed 0 replies"

**Causes:**
1. No files in `Approved/` folder
2. Files don't have `comment_id` field
3. Files don't have `## Draft Response` section

**Solution:**
- Make sure files are in `Approved/` folder
- Check file has `comment_id: xxx` in frontmatter
- Add your response under `## Draft Response`

### "Failed to post reply"

**Causes:**
1. Invalid access token
2. Missing permissions
3. Comment ID is invalid

**Solution:**
- Run: `python watchers/facebook_poster.py AI_Employee_Vault --test-connection`
- Check your token is valid
- Make sure you have `pages_manage_posts` permission

---

## ✅ Example Workflow

Here's a real example:

**1. Comment arrives:**
```
File created: Needs_Action/FACEBOOK_COMMENT_20260314_120000.md
Comment from: John Doe
Comment text: "Great post!"
```

**2. You write response:**
```markdown
## Draft Response (for approval)

Thanks John! Stay tuned for more updates! 🚀
```

**3. Move file:**
```
Needs_Action/ → Pending_Approval/ → Approved/
```

**4. Post reply:**
```bash
python watchers/facebook_poster.py AI_Employee_Vault --process-replies
```

**5. Result:**
```
Reply posted to Facebook!
Reply ID: 123456789_111222333
File moved to: Done/
```

**6. Check Facebook:**
Your reply is now visible on the post! ✅

---

**Last Updated:** 2026-03-14
