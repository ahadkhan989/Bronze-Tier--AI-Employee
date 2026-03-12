---
name: plan-reasoning-loop
description: |
  Qwen Code reasoning loop that creates Plan.md files for complex tasks.
  Breaks down multi-step tasks into actionable checkboxes with progress tracking.
  Integrates with the approval workflow for sensitive steps.
---

# Plan.md Reasoning Loop Skill

Systematic task planning with Qwen Code.

## Overview

When Qwen Code encounters complex tasks requiring multiple steps, it creates a `Plan.md` file in the `Plans/` folder to track progress and coordinate actions.

## When to Create Plans

Create a Plan.md when a task requires:
- **3+ steps** to complete
- **Multiple file operations**
- **Human approvals** at intermediate stages
- **Progress tracking** over time
- **Coordination** between different actions

## Plan Template

```markdown
---
created: 2026-03-11T10:30:00Z
status: in_progress
objective: Process client invoice request
priority: high
---

# Plan: Process Client Invoice Request

## Objective

Generate and send invoice to Client A for January 2026 services.

---

## Context

Client A requested invoice via WhatsApp on 2026-03-11.
Services rendered: Consulting (20 hours @ $150/hour)
Total: $3,000

---

## Steps

- [x] Step 1: Identify client details (Client A, client_a@email.com)
- [x] Step 2: Calculate amount (20 hours × $150 = $3,000)
- [ ] Step 3: Generate invoice PDF
- [ ] Step 4: Create approval request for email send
- [ ] Step 5: Wait for human approval
- [ ] Step 6: Send email with invoice
- [ ] Step 7: Log transaction
- [ ] Step 8: Move to /Done

---

## Resources Needed

- [x] Client contact information
- [ ] Invoice template
- [ ] Approval for sending

---

## Approvals Required

- [ ] Email send requires approval (new invoice)

---

## Progress Log

| Timestamp | Action | Actor | Notes |
|-----------|--------|-------|-------|
| 2026-03-11T10:30 | Plan created | Qwen Code | Initial plan |
| 2026-03-11T10:31 | Step 1-2 complete | Qwen Code | Client identified |

---

## Blockers

*None currently*

---

## Completion Criteria

- [ ] Invoice sent to client
- [ ] Transaction logged
- [ ] All files moved to /Done
```

## Qwen Code Workflow

### Step 1: Detect Complex Task

```bash
qwen "Review Needs_Action folder. For any item requiring 
      multiple steps to complete, create a Plan.md file"
```

### Step 2: Create Plan

Qwen Code:
1. Reads the action file
2. Identifies required steps
3. Creates Plan.md in `Plans/` folder
4. Updates Dashboard.md

### Step 3: Execute Steps

For each step:
- If simple: Execute directly
- If sensitive: Create approval request
- Update progress log

### Step 4: Mark Complete

When all steps done:
- Move Plan.md to `Done/`
- Update Dashboard.md
- Log completion

## Integration with Approval Workflow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Qwen      │────▶│  Create      │────▶│   Execute   │
│   Code      │     │  Plan.md     │     │   Steps     │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌──────────────┐
                    │  Approval    │◀────│  Sensitive   │
                    │  Required?   │     │  Step        │
                    └──────────────┘     └──────────────┘
                           │
                    Yes    │    No
                     ▼     │     ▼
              ┌────────────┴──────────┐
              │  Create Approval      │
              │  Request in           │
              │  Pending_Approval/    │
              └───────────────────────┘
```

## Commands

```bash
# Generate plans for complex tasks
python qwen_processor.py plan AI_Employee_Vault

# Check plan status
python qwen_processor.py custom "Review Plans folder and summarize progress" AI_Employee_Vault

# Complete abandoned plans
python qwen_processor.py custom "Find incomplete plans older than 7 days and suggest next steps" AI_Employee_Vault
```

## Plan Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Plan created, not started |
| `in_progress` | Steps being executed |
| `blocked` | Waiting on approval/external |
| `completed` | All steps done |
| `abandoned` | Plan no longer relevant |

## Example: Email Campaign Plan

```markdown
---
created: 2026-03-11
status: in_progress
objective: Send monthly newsletter to 50 clients
---

# Plan: Monthly Newsletter Campaign

## Steps

- [x] 1. Gather content from recent blog posts
- [x] 2. Design email template
- [ ] 3. Create recipient list (50 clients)
- [ ] 4. Generate approval request (bulk send)
- [ ] 5. Human approves recipient list
- [ ] 6. Send emails via Gmail MCP
- [ ] 7. Track open rates
- [ ] 8. Log campaign results

## Approvals

- [ ] Bulk email send (50 recipients)
```

## Best Practices

1. **Clear objective** - One sentence summary
2. **Numbered steps** - Sequential execution
3. **Progress log** - Update after each step
4. **Blockers section** - Note what's stuck
5. **Completion criteria** - Define "done"

## Error Recovery

If Qwen Code stops mid-plan:

```bash
qwen "Review Plans folder for in_progress status.
      Resume execution from last completed step.
      Update progress log with current state."
```
