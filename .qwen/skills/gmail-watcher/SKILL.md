---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files in Obsidian vault.
  Watches for unread, important messages and converts them into actionable Markdown files
  for Qwen Code to process. Supports priority keywords and sender filtering.
---

# Gmail Watcher Skill

Monitor Gmail inbox and create action files for important emails.

## Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth 2.0 Credentials** (credentials.json)
3. **Python packages**:
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

## Setup Instructions

### Step 1: Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API: `APIs & Services > Library > Gmail API`
4. Create OAuth 2.0 credentials: `APIs & Services > Credentials`
5. Download `credentials.json` to project root

### Step 2: First-Time Authentication

Run the watcher once to authenticate:

```bash
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate
```

This will:
- Open browser for Google login
- Request Gmail permissions
- Save token to `token.json`

### Step 3: Run the Watcher

```bash
# Basic usage
python watchers/gmail_watcher.py AI_Employee_Vault

# With custom check interval (30 seconds)
python watchers/gmail_watcher.py AI_Employee_Vault --interval 30

# Only watch high-priority emails
python watchers/gmail_watcher.py AI_Employee_Vault --priority-only
```

## Configuration

Create `config.json` in project root:

```json
{
  "gmail": {
    "check_interval": 120,
    "priority_keywords": ["urgent", "asap", "invoice", "payment", "important"],
    "watch_labels": ["INBOX", "IMPORTANT"],
    "ignore_senders": ["noreply@", "notifications@"],
    "max_results": 10
  }
}
```

## How It Works

1. **Polling**: Checks Gmail every N seconds (default: 120)
2. **Filtering**: Only processes unread, important messages
3. **Action File Creation**: Creates `.md` file in `Needs_Action/` folder
4. **Tracking**: Remembers processed message IDs to avoid duplicates

## Action File Format

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-03-11T10:30:00Z
priority: high
status: pending
message_id: abc123xyz
---

## Email Content
{message snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Priority Keywords

Default priority keywords (configurable):
- `urgent`
- `asap`
- `invoice`
- `payment`
- `important`
- `help`
- `deadline`

Emails containing these keywords in subject or body are marked as **high priority**.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `token.json` not created | Run with `--authenticate` flag |
| No emails detected | Check Gmail API quota, verify labels |
| Duplicate action files | Delete `processed_ids.json` and restart |
| API quota exceeded | Reduce check frequency or upgrade quota |

## Security Notes

- `credentials.json` contains API secrets - **never commit to Git**
- `token.json` contains OAuth token - **store securely**
- Add to `.gitignore`:
  ```
  credentials.json
  token.json
  ```

## Example Output

```
2026-03-11 12:00:00 - GmailWatcher - INFO - Starting GmailWatcher
2026-03-11 12:02:00 - GmailWatcher - INFO - Found 2 new email(s)
2026-03-11 12:02:01 - GmailWatcher - INFO - Created action file: EMAIL_abc123_Invoice_Request.md
2026-03-11 12:02:02 - GmailWatcher - INFO - Created action file: EMAIL_def456_Urgent_Meeting.md
```

## Stop the Watcher

Press `Ctrl+C` to stop gracefully.
