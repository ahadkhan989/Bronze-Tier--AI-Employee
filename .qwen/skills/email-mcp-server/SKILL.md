---
name: email-mcp-server
description: |
  Model Context Protocol (MCP) server for sending emails via Gmail API.
  Provides tools for composing, drafting, and sending emails.
  Supports attachments, HTML content, and human-in-the-loop approval workflow.
---

# Email MCP Server Skill

Send emails via Gmail API using Model Context Protocol (MCP).

## Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth 2.0 Credentials** with send permissions
3. **Node.js** v18+ for MCP server
4. **Python** for helper scripts

## Scope

This skill provides:
- **Send emails** via Gmail API
- **Draft emails** for review before sending
- **Search emails** in Gmail
- **Label management** for organization

## Setup Instructions

### Step 1: Enable Gmail API with Send Scope

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Add OAuth scope: `https://www.googleapis.com/auth/gmail.send`
4. Download `credentials.json`

### Step 2: Install Dependencies

```bash
# Python packages
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Node.js packages (for MCP server)
npm install @modelcontextprotocol/server-gmail
```

### Step 3: Configure MCP Server

Create `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-gmail"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

### Step 4: Authenticate

```bash
# Run authentication flow
python scripts/email_mcp_auth.py
```

## Available Tools

### `gmail_send_email`

Send an email immediately.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body text",
  "html": "<p>Optional HTML body</p>",
  "attachments": ["/path/to/file.pdf"],
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"]
}
```

### `gmail_create_draft`

Create a draft email for review.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body text"
}
```

**Returns:** Draft ID for later sending

### `gmail_search_emails`

Search Gmail for emails.

**Parameters:**
```json
{
  "query": "is:unread from:boss@company.com",
  "maxResults": 10
}
```

### `gmail_get_email`

Get full content of an email.

**Parameters:**
```json
{
  "message_id": "abc123xyz"
}
```

### `gmail_mark_read`

Mark emails as read.

**Parameters:**
```json
{
  "message_ids": ["abc123", "def456"]
}
```

## Usage Examples

### Send Simple Email

```bash
python scripts/mcp_client.py call -u http://localhost:8809 \
  -t gmail_send_email \
  -p '{"to": "client@example.com", "subject": "Meeting Tomorrow", "body": "Hi, see you at 3pm."}'
```

### Send Email with Attachment

```bash
python scripts/mcp_client.py call -u http://localhost:8809 \
  -t gmail_send_email \
  -p '{
    "to": "client@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached invoice.",
    "attachments": ["/path/to/invoice.pdf"]
  }'
```

### Create Draft for Review

```bash
python scripts/mcp_client.py call -u http://localhost:8809 \
  -t gmail_create_draft \
  -p '{"to": "client@example.com", "subject": "Proposal", "body": "Here is our proposal..."}'
```

### Search Emails

```bash
python scripts/mcp_client.py call -u http://localhost:8809 \
  -t gmail_search_emails \
  -p '{"query": "is:unread subject:invoice", "maxResults": 5}'
```

## Human-in-the-Loop Pattern

For sensitive actions, use the approval workflow:

### Step 1: Create Approval Request

```python
# When Qwen Code detects email needs approval:
approval_content = f"""---
type: approval_request
action: send_email
to: {recipient}
subject: {subject}
created: {timestamp}
---

# Email Approval Request

## Email Details
- **To:** {recipient}
- **Subject:** {subject}
- **Body:** {body_preview}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""
```

### Step 2: Human Reviews

- Review email content in Obsidian
- Move file from `Pending_Approval/` to `Approved/`

### Step 3: Orchestrator Sends

```python
# orchestrator.py detects approved file
# Calls Gmail MCP to send
# Logs result
# Moves to /Done
```

## Integration with Qwen Code

### Example Prompt

```
You have access to the Gmail MCP server. When the user asks to send an email:

1. Compose the email content
2. If it's a new recipient or sensitive topic, create an approval request
3. For routine emails to known contacts, you may send directly
4. Log all sent emails to the Dashboard
```

### Qwen Code Workflow

```bash
qwen "Check the approved emails in /Approved folder and send them using the Gmail MCP server"
```

## Error Handling

| Error | Solution |
|-------|----------|
| `403 Forbidden` | Check OAuth scopes include gmail.send |
| `429 Rate Limit` | Wait and retry, implement backoff |
| `Invalid credentials` | Re-run authentication |
| `Attachment not found` | Verify file path is absolute |

## Security Best Practices

1. **Never log email content** to console
2. **Store credentials securely** - use environment variables
3. **Implement rate limiting** - max 10 emails/minute
4. **Require approval** for:
   - First-time recipients
   - Emails with attachments
   - Bulk sends (>5 recipients)
   - Sensitive topics (payments, legal)

## Testing

```bash
# Test connection
python scripts/test_email_mcp.py

# Send test email to self
python scripts/test_email_mcp.py --send-test
```

## Troubleshooting

### MCP Server Won't Start

```bash
# Check if port is available
netstat -an | grep 8809

# Check credentials path
ls -la /path/to/credentials.json

# Run with debug
DEBUG=* npx @modelcontextprotocol/server-gmail
```

### Authentication Errors

```bash
# Clear old tokens
rm ~/.gmail_tokens.json

# Re-authenticate
python scripts/email_mcp_auth.py
```

## Reference Implementation

See the official MCP Gmail server:
- GitHub: https://github.com/modelcontextprotocol/servers
- NPM: https://www.npmjs.com/package/@modelcontextprotocol/server-gmail
