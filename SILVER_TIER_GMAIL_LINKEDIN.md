# 🥈 Silver Tier - Gmail + LinkedIn Edition

Complete Silver Tier implementation with focus on **Gmail Watcher** and **LinkedIn Automation** for business growth.

---

## 📋 Silver Tier Requirements (Completed)

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| 2+ Watcher scripts | ✅ | Gmail + LinkedIn + Filesystem |
| Auto-post to LinkedIn | ✅ | LinkedIn Poster |
| Plan.md reasoning loop | ✅ | Qwen Processor |
| MCP server for actions | ✅ | Email Sender |
| Approval workflow | ✅ | File-based approvals |
| Scheduling | ✅ | Python scheduler + cron templates |

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install playwright schedule
playwright install chromium

# Gmail API (if not already installed)
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 2: Authenticate Gmail

Your `credentials.json` is already in place. Now authenticate:

```bash
# This will open a browser for Google login
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate
```

**Steps:**
1. Browser opens automatically
2. Sign in to your Google account
3. Grant Gmail API permissions
4. Token saved to `AI_Employee_Vault/token.json`

### Step 3: Authenticate LinkedIn

```bash
# This will open a browser for LinkedIn login
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session
```

**Steps:**
1. Browser opens to LinkedIn
2. Log in to your account
3. Wait for "Session saved" message
4. Close the browser

### Step 4: Start Watchers

```bash
# Start Gmail Watcher (Terminal 1)
python watchers/gmail_watcher.py AI_Employee_Vault --interval 60

# Start LinkedIn Watcher (Terminal 2)
python watchers/linkedin_watcher.py AI_Employee_Vault --interval 300

# Start File Watcher (Terminal 3 - optional)
python watchers/filesystem_watcher.py AI_Employee_Vault
```

### Step 5: Process with Qwen Code

```bash
# Process all pending items
python qwen_processor.py process AI_Employee_Vault

# Or run manually
cd AI_Employee_Vault
qwen "Review all files in Needs_Action folder and take appropriate action"
```

---

## 📧 Gmail Watcher

### Features

- Monitors Gmail for **unread, important** emails
- Filters by **priority keywords** (urgent, invoice, payment, etc.)
- Creates action files in `Needs_Action/` folder
- Tracks processed emails to avoid duplicates

### Commands

```bash
# Basic usage (checks every 2 minutes)
python watchers/gmail_watcher.py AI_Employee_Vault

# Priority emails only
python watchers/gmail_watcher.py AI_Employee_Vault --priority-only

# Custom interval (30 seconds)
python watchers/gmail_watcher.py AI_Employee_Vault --interval 30

# Re-authenticate
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate
```

### Configuration

Edit `watchers/gmail_watcher.py` to customize:

```python
# Priority keywords (line ~85)
self.priority_keywords = [
    'urgent', 'asap', 'invoice', 'payment', 'important',
    'help', 'deadline', 'action required', 'immediate'
]

# Check interval (default: 120 seconds)
check_interval = 120
```

### Expected Output

```
2026-03-11 12:00:00 - GmailWatcher - INFO - Starting GmailWatcher
2026-03-11 12:02:00 - GmailWatcher - INFO - Found 2 new email(s)
2026-03-11 12:02:01 - GmailWatcher - INFO - Created action file: EMAIL_20260311_120201_Invoice_Request.md [HIGH]
```

### Troubleshooting

```bash
# Check if token exists
ls AI_Employee_Vault/token.json

# Check credentials
cat credentials.json

# Re-authenticate if needed
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate
```

---

## 💼 LinkedIn Watcher

### Features

- Monitors LinkedIn for **notifications** and **messages**
- Tracks connection requests, engagement, mentions
- Creates action files for important notifications
- Session-based authentication (secure)

### Commands

```bash
# Basic usage (checks every 5 minutes)
python watchers/linkedin_watcher.py AI_Employee_Vault

# Messages only
python watchers/linkedin_watcher.py AI_Employee_Vault --types "messages"

# Custom interval (2 minutes)
python watchers/linkedin_watcher.py AI_Employee_Vault --interval 120

# Quick test (check once)
python watchers/linkedin_watcher.py AI_Employee_Vault --once
```

### Notification Types

| Type | Description |
|------|-------------|
| `messages` | Direct messages from connections |
| `connections` | New connection requests |
| `engagement` | Likes, comments on your posts |
| `mentions` | When you're mentioned |

### Expected Output

```
2026-03-11 12:00:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-03-11 12:05:00 - LinkedInWatcher - INFO - Found 3 new notification(s)
2026-03-11 12:05:01 - LinkedInWatcher - INFO - Created action file: LINKEDIN_MSG_20260311_120501_John_Doe.md [HIGH]
```

---

## 📢 LinkedIn Poster

### Features

- Auto-post content to LinkedIn
- Support for text + images
- Approval workflow for business posts
- Scheduled posting support

### Commands

```bash
# Post content directly
python watchers/linkedin_poster.py AI_Employee_Vault \
  --content "🚀 Exciting news! Our AI Employee system is now live..."

# Post from file
python watchers/linkedin_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/linkedin_post.md

# With approval workflow
python watchers/linkedin_poster.py AI_Employee_Vault \
  --file content.md --require-approval

# Process approved posts
python watchers/linkedin_poster.py AI_Employee_Vault --process-approved
```

### Content Template

Create `AI_Employee_Vault/Plans/linkedin_post.md`:

```markdown
---
hashtags: ["#AI", "#Automation", "#Business"]
---

🤖 Exciting News!

Our AI Employee system helps businesses automate:
✅ Email processing
✅ WhatsApp monitoring
✅ LinkedIn engagement
✅ Daily briefings

Want to learn more? DM me!

#AI #Automation #Business #Productivity
```

### Posting Schedule

**Best times to post:**
- 8:00 AM - 10:00 AM (morning commute)
- 12:00 PM - 1:00 PM (lunch break)
- 5:00 PM - 6:00 PM (end of work day)

**Frequency:** Max 1-2 posts per day

---

## 🔄 Complete Workflow Example

### Scenario: Client inquiry via Gmail → LinkedIn follow-up

**Step 1: Gmail Watcher detects email**
```bash
# Running in background
python watchers/gmail_watcher.py AI_Employee_Vault

# Email received: "Interested in AI automation services"
# Creates: Needs_Action/EMAIL_20260311_120000_Interested_in_AI.md
```

**Step 2: Qwen Code processes email**
```bash
python qwen_processor.py process AI_Employee_Vault

# Qwen Code:
# 1. Reads the email
# 2. Identifies as lead
# 3. Creates follow-up plan
# 4. Drafts reply for approval
```

**Step 3: Human approves reply**
```bash
# Review in Obsidian: Pending_Approval/EMAIL_REPLY_...md
# Move to Approved/ to send
```

**Step 4: Email sent**
```bash
python orchestrator.py AI_Employee_Vault --process-approvals
```

**Step 5: LinkedIn post about new client**
```bash
# Create post content
cat > AI_Employee_Vault/Plans/client_win_post.md << EOF
---
hashtags: ["#ClientWin", "#AI", "#Automation"]
---

🎉 Welcome to our new client!

Just helped another business automate their email processing.
They're now saving 10+ hours per week!

Ready to transform your business? Let's talk!

#ClientWin #AI #Automation
EOF

# Post with approval
python watchers/linkedin_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/client_win_post.md \
  --require-approval
```

---

## ⚙️ Scheduling

### Option 1: Python Scheduler

```bash
# Run continuously
python scheduler.py

# Test scheduled tasks
python scheduler.py --once
```

### Option 2: Windows Task Scheduler

```powershell
# Gmail Watcher at startup
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "watchers/gmail_watcher.py AI_Employee_Vault --interval 60" `
  -WorkingDirectory "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"

$trigger = New-ScheduledTaskTrigger -AtStartup

Register-ScheduledTask -TaskName "AI_Employee_Gmail_Watcher" `
  -Action $action -Trigger $trigger
```

### Option 3: Cron (Linux/Mac)

```bash
crontab -e

# Gmail Watcher every hour
0 * * * * cd /path/to/project && python watchers/gmail_watcher.py AI_Employee_Vault --interval 3600

# LinkedIn Post at 9 AM daily
0 9 * * * cd /path/to/project && python watchers/linkedin_poster.py AI_Employee_Vault --process-approved
```

---

## 📁 File Structure

```
Bronze-Tier--AI-Employee/
├── credentials.json                 # Your Gmail OAuth credentials
├── AI_Employee_Vault/
│   ├── token.json                   # Gmail OAuth token (created after auth)
│   ├── linkedin_session/            # LinkedIn session (created after setup)
│   ├── Needs_Action/
│   │   ├── EMAIL_*.md              # Gmail action files
│   │   └── LINKEDIN_*.md           # LinkedIn action files
│   ├── Pending_Approval/
│   │   ├── EMAIL_REPLY_*.md        # Email replies awaiting approval
│   │   └── LINKEDIN_POST_APPROVAL_*.md  # LinkedIn posts awaiting approval
│   ├── Approved/                    # Approved actions ready to execute
│   ├── Done/                        # Completed actions
│   └── Plans/
│       └── linkedin_post.md        # LinkedIn post templates
│
├── watchers/
│   ├── gmail_watcher.py            # Gmail monitoring
│   ├── linkedin_watcher.py         # LinkedIn monitoring
│   ├── linkedin_poster.py          # LinkedIn posting
│   ├── email_sender.py             # Email sending
│   └── filesystem_watcher.py       # File drop monitoring
│
├── orchestrator.py                 # Approval processing
├── qwen_processor.py               # Qwen Code helper
└── scheduler.py                    # Task scheduler
```

---

## 🔒 Security

### Credentials Management

```bash
# NEVER commit these files
echo "credentials.json" >> .gitignore
echo "AI_Employee_Vault/token.json" >> .gitignore
echo "AI_Employee_Vault/linkedin_session/" >> .gitignore
```

### Approval Rules

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Gmail read | ✅ Yes | N/A |
| Email reply | ❌ No | ✅ Always |
| LinkedIn post | ❌ No | ✅ Always |
| Connection request | ❌ No | ✅ For new accounts |

---

## 📊 Silver Tier Checklist

- [ ] Gmail Watcher authenticated and running
- [ ] LinkedIn Watcher authenticated and running
- [ ] Action files created in `Needs_Action/`
- [ ] Qwen Code processing items
- [ ] Approval workflow functional
- [ ] LinkedIn Poster tested
- [ ] Scheduler running

---

## 🐛 Troubleshooting

### Gmail Issues

```bash
# Check authentication
ls -la AI_Employee_Vault/token.json

# Re-authenticate
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate

# Check API quota (Google Cloud Console)
# https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas
```

### LinkedIn Issues

```bash
# Clear session and re-setup
rm -rf AI_Employee_Vault/linkedin_session
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session
```

### Posting Issues

```bash
# Test with simple content
python watchers/linkedin_poster.py AI_Employee_Vault \
  --content "Test post from AI Employee" --require-approval
```

---

## 📚 Resources

- **Gmail API Docs**: https://developers.google.com/gmail/api
- **LinkedIn Marketing**: https://business.linkedin.com/marketing-solutions
- **Playwright Docs**: https://playwright.dev/python

---

*Silver Tier complete! Ready for business automation with Gmail + LinkedIn.*
