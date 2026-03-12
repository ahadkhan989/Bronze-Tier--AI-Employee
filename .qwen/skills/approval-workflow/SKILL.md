---
name: approval-workflow
description: |
  Human-in-the-Loop approval workflow for sensitive actions.
  Files requiring approval are placed in /Pending_Approval folder.
  Humans move files to /Approved or /Rejected to indicate decision.
  Orchestrator processes approved files and logs all actions.
---

# Human-in-the-Loop Approval Workflow

Safe automation with human oversight for sensitive actions.

## Overview

This workflow ensures sensitive actions (payments, emails to new contacts, file deletions) require human approval before execution.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/    ← AI creates approval requests here
├── Approved/            ← Human moves files here to approve
├── Rejected/            ← Human moves files here to reject
└── Logs/                ← All actions logged here
```

## Workflow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│   Qwen      │────▶│  Pending_    │────▶│   Human     │────▶│ Approved │
│   Code      │     │  Approval/   │     │   Review    │     │    /     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│    Done     │◀────│    Logs/     │◀────│  Execute    │◀────│  Action  │
│   Folder    │     │   Action     │     │   Action    │     │  Server  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
```

## Approval Request Template

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123
amount: 0
created: 2026-03-11T10:30:00Z
expires: 2026-03-12T10:30:00Z
status: pending
---

# Approval Request: Send Email

## Request Details

| Field | Value |
|-------|-------|
| **Action** | Send Email |
| **To** | client@example.com |
| **Subject** | Invoice #123 |
| **Created** | 2026-03-11T10:30:00Z |

---

## Email Content

Dear Client,

Please find attached invoice #123 for services rendered.

Best regards,
[Your Name]

---

## To Approve
**Move this file to `/Approved` folder.**

## To Reject
**Move this file to `/Rejected` folder with reason below.**

---

## Decision

- [ ] Approved → Moved to /Approved on ___________
- [ ] Rejected → Moved to /Rejected on ___________

**Rejection Reason (if applicable):**

```

## Action Types Requiring Approval

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email send | Known contacts | New contacts, bulk |
| Payment | Never | Always |
| File delete | Never | Always |
| Social post | Scheduled | Immediate |
| API calls | Read-only | Write operations |

## Orchestrator Integration

### Processing Approved Files

```python
# orchestrator.py
def process_approvals(self):
    """Process files in Approved folder."""
    for filepath in self.approved.iterdir():
        if filepath.suffix != '.md':
            continue
        
        # Read approval request
        content = filepath.read_text()
        
        # Execute the approved action
        if 'send_email' in content:
            send_approved_email(filepath)
        elif 'payment' in content:
            process_approved_payment(filepath)
        
        # Move to Done
        dest = self.done / f"{timestamp}_{filepath.name}"
        shutil.move(str(filepath), str(dest))
        
        # Log action
        self.log_action('approval_processed', 'orchestrator', filepath.name)
```

### Logging Format

```json
{
  "timestamp": "2026-03-11T10:30:00Z",
  "action_type": "approval_processed",
  "actor": "orchestrator",
  "target": "EMAIL_Invoice_123.md",
  "parameters": {
    "action": "send_email",
    "recipient": "client@example.com"
  },
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

## Qwen Code Integration

### Creating Approval Requests

```bash
qwen "For any email to new contacts or payments over $100, 
      create an approval request in Pending_Approval folder 
      instead of taking direct action"
```

### Checking Pending Approvals

```bash
qwen "Review all files in Pending_Approval folder and 
      summarize what actions are awaiting my decision"
```

## Commands

```bash
# List pending approvals
python orchestrator.py AI_Employee_Vault --list-approvals

# Process approved files
python orchestrator.py AI_Employee_Vault --process-approvals

# Show approval statistics
python orchestrator.py AI_Employee_Vault --approval-stats
```

## Timeout Handling

Approval requests can have expiration:

```markdown
---
expires: 2026-03-12T10:30:00Z
---
```

Orchestrator can:
- Alert if approvals expire
- Auto-reject expired approvals
- Move to `Rejected/Expired/`

## Security Considerations

1. **Never auto-approve payments** to new recipients
2. **Always log** approval decisions
3. **Require fresh approval** for modified actions
4. **Audit trail** - keep all approval files in Done

## Best Practices

1. **Clear descriptions** - Explain what the action does
2. **Preview content** - Show email body, payment details
3. **Easy decision** - Clear approve/reject instructions
4. **Expiry dates** - Time-sensitive actions should expire
5. **Audit logging** - Record who approved what and when
