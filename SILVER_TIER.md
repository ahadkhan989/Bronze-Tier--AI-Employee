# 🥈 Silver Tier - AI Employee Upgrade Guide

Upgrade from Bronze to Silver Tier for advanced automation capabilities.

---

## 📋 Silver Tier Requirements

Based on the hackathon blueprint, Silver Tier includes:

1. ✅ **Two or more Watcher scripts** (Gmail + WhatsApp)
2. ✅ **Claude/Qwen reasoning loop** that creates Plan.md files
3. ✅ **One working MCP server** for external action (Email)
4. ✅ **Human-in-the-loop approval workflow** for sensitive actions
5. ✅ **Basic scheduling** via cron or Task Scheduler
6. ✅ **All AI functionality as Agent Skills**

---

## 🚀 Installation

### Step 1: Install Additional Dependencies

```bash
# For Gmail Watcher
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# For WhatsApp Watcher
pip install playwright
playwright install chromium

# For Email Sending
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# For Scheduling
pip install schedule
```

### Step 2: Set Up Google API (for Gmail)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to project root
6. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` (for watcher)
   - `https://www.googleapis.com/auth/gmail.send` (for sending)

### Step 3: Authenticate Services

```bash
# Gmail authentication
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate

# Email sender authentication
python watchers/email_sender.py authenticate

# WhatsApp session setup
python watchers/whatsapp_watcher.py AI_Employee_Vault --setup-session
```

---

## 📁 New File Structure

```
Bronze-Tier--AI-Employee/
├── .qwen/skills/
│   ├── browsing-with-playwright/    # From Bronze
│   ├── gmail-watcher/               # NEW: Silver
│   ├── whatsapp-watcher/            # NEW: Silver
│   ├── email-mcp-server/            # NEW: Silver
│   ├── approval-workflow/           # NEW: Silver
│   ├── plan-reasoning-loop/         # NEW: Silver
│   └── scheduling/                  # NEW: Silver
│
├── watchers/
│   ├── base_watcher.py              # From Bronze
│   ├── filesystem_watcher.py        # From Bronze
│   ├── gmail_watcher.py             # NEW: Silver
│   ├── whatsapp_watcher.py          # NEW: Silver
│   └── email_sender.py              # NEW: Silver
│
├── orchestrator.py                  # Updated for Silver
├── qwen_processor.py                # From Bronze
├── scheduler.py                     # NEW: Silver
└── AI_Employee_Vault/
    ├── Plans/                       # NEW: For Plan.md files
    ├── Pending_Approval/            # From Bronze (now actively used)
    ├── Approved/                    # From Bronze (now actively used)
    └── ...
```

---

## 📖 Available Commands

### Watcher Commands

```bash
# Gmail Watcher
python watchers/gmail_watcher.py AI_Employee_Vault
python watchers/gmail_watcher.py AI_Employee_Vault --priority-only
python watchers/gmail_watcher.py AI_Employee_Vault --interval 60

# WhatsApp Watcher
python watchers/whatsapp_watcher.py AI_Employee_Vault
python watchers/whatsapp_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment"
python watchers/whatsapp_watcher.py AI_Employee_Vault --once

# File Watcher (from Bronze)
python watchers/filesystem_watcher.py AI_Employee_Vault
```

### Qwen Processor Commands

```bash
# Process pending items
python qwen_processor.py process AI_Employee_Vault

# Generate plans for complex tasks
python qwen_processor.py plan AI_Employee_Vault

# Daily review
python qwen_processor.py review AI_Employee_Vault

# Check approvals
python qwen_processor.py approvals AI_Employee_Vault

# Full system audit
python qwen_processor.py audit AI_Employee_Vault

# Custom prompt
python qwen_processor.py custom "Your prompt here" AI_Employee_Vault
```

### Scheduler Commands

```bash
# Run scheduler (continuous)
python scheduler.py

# Test scheduled tasks
python scheduler.py --once

# List scheduled tasks
python scheduler.py --list
```

### Orchestrator Commands

```bash
# Status
python orchestrator.py AI_Employee_Vault --status

# Process approvals
python orchestrator.py AI_Employee_Vault --process-approvals

# Generate briefing
python orchestrator.py AI_Employee_Vault --briefing

# Update dashboard
python orchestrator.py AI_Employee_Vault --update-dashboard
```

---

## 🔄 Silver Tier Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      INPUT SOURCES                              │
│  Gmail  │  WhatsApp  │  File Drop  │  Scheduled Tasks           │
└────┬────┴─────┬──────┴──────┬──────┴─────────┬─────────────────┘
     │          │             │                │
     ▼          ▼             ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WATCHERS (Continuous)                        │
│  gmail_watcher.py  │  whatsapp_watcher.py  │  filesystem_...   │
└─────────────────────────────────────────────────────────────────┘
     │          │             │
     ▼          ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Needs_Action/ Folder                           │
│  Action files created by watchers                               │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│              QWEN CODE (Reasoning Engine)                       │
│  - Reads action files                                           │
│  - Creates Plan.md for complex tasks                            │
│  - Creates approval requests for sensitive actions              │
└─────────────────────────────────────────────────────────────────┘
     │
     ├─────────────┬─────────────────┐
     ▼             ▼                 ▼
┌─────────┐  ┌────────────┐   ┌──────────────┐
│ Simple  │  │  Pending_  │   │    Plans/    │
│ Actions │  │  Approval/ │   │              │
│ → Done  │  │            │   │  Multi-step  │
└─────────┘  └─────┬──────┘   │  tracking    │
                  │          └──────────────┘
                  ▼
            ┌─────────┐
            │ Human   │
            │ Review  │
            └────┬────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
     ┌────────┐   ┌──────────┐
     │Approved│   │ Rejected │
     └───┬────┘   └──────────┘
         │
         ▼
    ┌─────────┐
    │ Execute │
    │ Action  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Done/  │
    │  Logs/  │
    └─────────┘
```

---

## 📝 Example: End-to-End Silver Flow

### Scenario: Client sends urgent invoice request via WhatsApp

**Step 1: WhatsApp Watcher detects message**
```bash
# Watcher running in background
python watchers/whatsapp_watcher.py AI_Employee_Vault

# Message received: "Hey, need invoice for last month ASAP!"
# Creates: Needs_Action/WHATSAPP_20260311_120000_Client_Name.md
```

**Step 2: Qwen Code processes the action file**
```bash
python qwen_processor.py process AI_Employee_Vault

# Qwen Code:
# 1. Reads the WhatsApp message
# 2. Identifies this needs multiple steps
# 3. Creates: Plans/PLAN_invoice_client_name.md
```

**Step 3: Plan created with steps**
```markdown
---
objective: Generate and send invoice to Client
status: in_progress
---

## Steps
- [x] 1. Identify client details
- [x] 2. Calculate amount
- [ ] 3. Generate invoice PDF
- [ ] 4. Create approval request
- [ ] 5. Send email
```

**Step 4: Approval request created**
```bash
# Qwen Code creates:
# Pending_Approval/EMAIL_Invoice_Client.md
```

**Step 5: Human reviews and approves**
```bash
# You review in Obsidian
# Move file from Pending_Approval/ to Approved/
```

**Step 6: Orchestrator processes approval**
```bash
python orchestrator.py AI_Employee_Vault --process-approvals

# Email sent via Gmail API
# File moved to Done/
# Log entry created
```

**Step 7: Dashboard updated**
```bash
python orchestrator.py AI_Employee_Vault --update-dashboard
```

---

## ⚙️ Scheduling Setup

### Windows Task Scheduler

```powershell
# Daily briefing at 8:00 AM
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "orchestrator.py AI_Employee_Vault --briefing" `
  -WorkingDirectory "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger
```

### Linux/Mac Cron

```bash
crontab -e

# Add these lines:
0 8 * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --briefing
0 * * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --process-approvals
*/15 * * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --update-dashboard
```

### Python Scheduler (Cross-platform)

```bash
# Run continuously
python scheduler.py

# Or as background service
nohup python scheduler.py &
```

---

## 🔒 Security Best Practices

### Credentials Management

```bash
# NEVER commit these files
echo "credentials.json" >> .gitignore
echo "token.json" >> .gitignore
echo "whatsapp_session/" >> .gitignore
echo "*.log" >> .gitignore
```

### Approval Rules

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email to known contact | ❌ | ✅ Draft only |
| Email to new contact | ❌ | ✅ Always |
| Payment any amount | ❌ | ✅ Always |
| Bulk email (>10) | ❌ | ✅ Always |
| File operations | ✅ Read | ❌ Write/Delete |

---

## 📊 Silver Tier Checklist

Use this to verify your Silver Tier completion:

- [ ] Gmail Watcher running and creating action files
- [ ] WhatsApp Watcher running and detecting keywords
- [ ] Qwen Code creating Plan.md files for complex tasks
- [ ] Approval workflow functional (Pending → Approved → Done)
- [ ] Email sending working via Gmail API
- [ ] Scheduler running (cron, Task Scheduler, or Python)
- [ ] All skills documented in `.qwen/skills/`
- [ ] Dashboard updating automatically

---

## 🐛 Troubleshooting

### Gmail Watcher Issues

```bash
# Re-authenticate
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate

# Check token
ls -la AI_Employee_Vault/token.json
```

### WhatsApp Watcher Issues

```bash
# Clear session and re-setup
python watchers/whatsapp_watcher.py AI_Employee_Vault --clear-session
python watchers/whatsapp_watcher.py AI_Employee_Vault --setup-session
```

### Approval Not Processing

```bash
# Check orchestrator logs
cat AI_Employee_Vault/Logs/*.json | tail -20

# Manually process
python orchestrator.py AI_Employee_Vault --process-approvals
```

### Scheduler Not Running

```bash
# Test scheduled tasks
python scheduler.py --once

# Check if Python is in PATH
where python  # Windows
which python  # Linux/Mac
```

---

## 📚 Resources

- **Gmail API Docs**: https://developers.google.com/gmail/api
- **Playwright Docs**: https://playwright.dev/python
- **Google OAuth**: https://developers.google.com/identity/protocols/oauth2
- **Schedule Library**: https://schedule.readthedocs.io

---

*Silver Tier completes the core AI Employee functionality. Ready for Gold Tier with Odoo integration and advanced MCP servers!*
