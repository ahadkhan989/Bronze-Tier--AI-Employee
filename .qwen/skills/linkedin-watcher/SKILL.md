---
name: linkedin-watcher
description: |
  Monitor LinkedIn for notifications, messages, and engagement opportunities.
  Uses Playwright to automate LinkedIn and extract notifications about:
  - Connection requests
  - Messages
  - Post engagement (likes, comments)
  - Job opportunities
  Creates action files in Obsidian vault for important notifications.
---

# LinkedIn Watcher Skill

Monitor LinkedIn for important notifications and messages.

## ⚠️ Important Notice

**This tool uses LinkedIn Web automation. Be aware of:**
- LinkedIn's Terms of Service
- Rate limiting to avoid account restrictions
- Privacy considerations

## Prerequisites

1. **Python packages**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **LinkedIn Account** - Must have valid credentials

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: First-Time Setup (Session Creation)

```bash
# This will open a browser for login
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session
```

1. Log in to LinkedIn
2. Wait for "Session saved" message
3. Close the browser

### Step 3: Run the Watcher

```bash
# Basic usage
python watchers/linkedin_watcher.py AI_Employee_Vault

# With custom session path
python watchers/linkedin_watcher.py AI_Employee_Vault --session-path ./linkedin_session

# Check specific notification types
python watchers/linkedin_watcher.py AI_Employee_Vault --types "messages,connections"
```

## Configuration

Create `linkedin_config.json` in project root:

```json
{
  "linkedin": {
    "check_interval": 300,
    "session_path": "./linkedin_session",
    "headless": true,
    "notification_types": ["messages", "connections", "engagement"],
    "min_engagement_threshold": 5
  }
}
```

## Notification Types

| Type | Description |
|------|-------------|
| `messages` | Direct messages from connections |
| `connections` | New connection requests |
| `engagement` | Likes, comments on your posts |
| `jobs` | Job recommendations |
| `mentions` | When you're mentioned |

## How It Works

1. **Session Management**: Uses persistent Chromium context
2. **Notification Check**: Visits LinkedIn notifications page
3. **Filtering**: Filters by type and importance
4. **Action File Creation**: Creates `.md` file in `Needs_Action/`

## Action File Format

```markdown
---
type: linkedin
notification_type: message
from: John Doe
received: 2026-03-11T10:30:00Z
priority: high
status: pending
---

# LinkedIn Notification: Message

## Details
- **From:** John Doe
- **Type:** Direct Message
- **Received:** 2026-03-11T10:30:00Z

### Content
Hi! I saw your post about AI automation. Would love to connect...

## Suggested Actions
- [ ] Reply on LinkedIn
- [ ] Send connection request
- [ ] Follow up
```

## Usage Examples

### Monitor Messages Only

```bash
python watchers/linkedin_watcher.py AI_Employee_Vault \
  --types "messages"
```

### Non-Headless Mode (Debug)

```bash
python watchers/linkedin_watcher.py AI_Employee_Vault --headless false
```

### Quick Test

```bash
# Check once and exit
python watchers/linkedin_watcher.py AI_Employee_Vault --once
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login page keeps showing | Session not saved, check permissions |
| No notifications found | Increase check interval |
| Browser won't close | Press Ctrl+C |

## Security Notes

- Session files contain authentication data - **store securely**
- Add to `.gitignore`:
  ```
  linkedin_session/
  *.json
  ```

## Example Output

```
2026-03-11 12:00:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-03-11 12:05:00 - LinkedInWatcher - INFO - Found 3 new notification(s)
2026-03-11 12:05:01 - LinkedInWatcher - INFO - Created action file: LINKEDIN_20260311_120501_John_Doe.md
```
