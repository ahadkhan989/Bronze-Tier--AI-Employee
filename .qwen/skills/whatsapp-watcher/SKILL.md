---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for new messages containing priority keywords.
  Uses Playwright to automate WhatsApp Web and extract messages from chats.
  Creates action files in Obsidian vault for messages requiring attention.
  WARNING: Be aware of WhatsApp's terms of service when using automation.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web for important messages and create action files.

## ⚠️ Important Notice

**This tool uses WhatsApp Web automation. Be aware of:**
- WhatsApp's Terms of Service
- Rate limiting to avoid account bans
- Privacy considerations for message content

## Prerequisites

1. **Python packages**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **WhatsApp Web Account** - Must be able to scan QR code

3. **Existing Playwright MCP** (optional, for advanced features)

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: First-Time Setup (Session Creation)

```bash
# This will open a browser for QR code scanning
python watchers/whatsapp_watcher.py AI_Employee_Vault --setup-session
```

1. Scan the QR code with your WhatsApp mobile app
2. Wait for "Session saved" message
3. Close the browser

### Step 3: Run the Watcher

```bash
# Basic usage
python watchers/whatsapp_watcher.py AI_Employee_Vault

# With custom session path
python watchers/whatsapp_watcher.py AI_Employee_Vault --session-path ./whatsapp_session

# Keyword filtering (only these keywords trigger action files)
python watchers/whatsapp_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment,asap"
```

## Configuration

Create `whatsapp_config.json` in project root:

```json
{
  "whatsapp": {
    "check_interval": 30,
    "keywords": ["urgent", "asap", "invoice", "payment", "help", "pricing"],
    "session_path": "./whatsapp_session",
    "headless": true,
    "max_chats_to_check": 10,
    "ignore_groups": true
  }
}
```

## Priority Keywords

Default keywords that trigger action file creation:
- `urgent`
- `asap`
- `invoice`
- `payment`
- `help`
- `pricing`
- `meeting`
- `deadline`

## How It Works

1. **Session Management**: Uses persistent Chromium context to maintain WhatsApp Web session
2. **Chat Scanning**: Checks recent chats for unread messages
3. **Keyword Matching**: Filters messages containing priority keywords
4. **Action File Creation**: Creates `.md` file in `Needs_Action/` folder

## Action File Format

```markdown
---
type: whatsapp
from: +1234567890
chat_name: John Doe
received: 2026-03-11T10:30:00Z
priority: high
status: pending
---

## WhatsApp Message

**From:** John Doe
**Chat:** +1234567890
**Received:** 2026-03-11T10:30:00Z

### Message Content
Hey, can you send me the invoice for last month? It's urgent.

## Suggested Actions
- [ ] Reply on WhatsApp
- [ ] Prepare invoice
- [ ] Follow up if needed
```

## Usage Examples

### Monitor for Invoice Requests

```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault \
  --keywords "invoice,bill,payment,receipt"
```

### Non-Headless Mode (Debug)

```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault --headless false
```

### Quick Test

```bash
# Check once and exit
python watchers/whatsapp_watcher.py AI_Employee_Vault --once
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code keeps appearing | Session not saved, check permissions |
| No messages detected | Increase check interval, verify keywords |
| Browser won't close | Press Ctrl+C, run cleanup script |
| WhatsApp Web slow | Increase check interval to 60s+ |

## Session Management

### View Session Status

```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault --check-session
```

### Clear Session (Force Re-login)

```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault --clear-session
```

## Security Notes

- Session files contain authentication data - **store securely**
- Add to `.gitignore`:
  ```
  whatsapp_session/
  *.json
  ```
- Consider using a dedicated phone number for automation

## Performance Tips

1. **Increase interval**: Set `--interval 60` or higher
2. **Limit chats**: Use `--max-chats 5` to check fewer conversations
3. **Headless mode**: Run with `--headless true` for production
4. **Keyword filtering**: Narrow down keywords to reduce false positives

## Example Output

```
2026-03-11 12:00:00 - WhatsAppWatcher - INFO - Starting WhatsAppWatcher
2026-03-11 12:00:05 - WhatsAppWatcher - INFO - Session loaded successfully
2026-03-11 12:00:30 - WhatsAppWatcher - INFO - Found 2 new message(s)
2026-03-11 12:00:31 - WhatsAppWatcher - INFO - Created action file: WHATSAPP_20260311_120031_John_Doe.md [HIGH]
```

## Ethical Use Guidelines

1. **Personal use only** - Don't automate business accounts at scale
2. **Respect rate limits** - Don't check more than once per 30 seconds
3. **Privacy** - Don't store sensitive message content unnecessarily
4. **Terms of Service** - Review WhatsApp's ToS before production use

## Alternative: WhatsApp Business API

For production use, consider the official [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/) which provides:
- Official API access
- Better reliability
- Compliance with terms
- Webhook support (no polling needed)
