# Personal AI Employee (Bronze Tier)

## Project Overview

This is a **Bronze-Tier hackathon project** for building a "Personal AI Employee" — an autonomous digital FTE (Full-Time Equivalent) that manages personal and business affairs 24/7. The project uses **Claude Code** as the reasoning engine and **Obsidian** as the knowledge base/dashboard.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine, task execution |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, long-term memory, task tracking |
| **Senses** | Python Watcher Scripts | Monitor Gmail, WhatsApp, filesystem for triggers |
| **Hands** | MCP Servers | External actions (browser automation, email, payments) |

### Key Concepts

- **Watchers:** Lightweight Python scripts that monitor inputs and create `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop:** A persistence pattern that keeps Claude working until tasks are complete
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Agent Skills:** All AI functionality implemented as reusable [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## Directory Structure

```
Bronze-Tier--AI-Employee/
├── .qwen/skills/              # Qwen Agent Skills configuration
│   └── browsing-with-playwright/
│       ├── SKILL.md           # Playwright browser automation skill
│       ├── scripts/           # MCP server management scripts
│       └── references/        # Tool documentation
├── .git/                      # Git repository
├── .gitattributes             # Git attributes
├── skills-lock.json           # Skills dependency lock file
├── Personal AI Employee Hackathon 0_*.md  # Full hackathon blueprint
└── QWEN.md                    # This file
```

### Expected Obsidian Vault Structure (to be created)

```
AI_Employee_Vault/
├── Dashboard.md               # Real-time summary
├── Company_Handbook.md        # Rules of engagement
├── Business_Goals.md          # Q1/Q2 objectives
├── Inbox/                     # Raw incoming items
├── Needs_Action/              # Items requiring processing
├── In_Progress/               # Currently being worked on
├── Pending_Approval/          # Awaiting human approval
├── Approved/                  # Approved actions
├── Done/                      # Completed tasks
└── Plans/                     # Multi-step task plans
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers |
| [GitHub Desktop](https://desktop.github.com/download/) | Latest | Version control |

### Hardware Requirements

- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage
- **For 24/7:** Dedicated mini-PC or cloud VM

### Setup Commands

```bash
# Verify Claude Code installation
claude --version

# Start Playwright MCP server (for browser automation)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify Playwright server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop Playwright server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### Running the AI Employee

1. **Create Obsidian Vault:**
   ```bash
   mkdir AI_Employee_Vault
   cd AI_Employee_Vault
   mkdir Inbox Needs_Action In_Progress Pending_Approval Approved Done Plans
   ```

2. **Start Watchers (Python scripts to be created):**
   ```bash
   python gmail_watcher.py &
   python filesystem_watcher.py &
   ```

3. **Run Claude Code with Ralph Wiggum Loop:**
   ```bash
   claude "Process all files in /Needs_Action, move to /Done when complete" \
     --completion-promise "TASK_COMPLETE" \
     --max-iterations 10
   ```

## Development Conventions

### Coding Style

- **Python Watchers:** Follow the `BaseWatcher` abstract class pattern (see hackathon doc)
- **Markdown Files:** Use YAML frontmatter for metadata
- **Agent Skills:** Document in `SKILL.md` format with usage examples

### Testing Practices

- Verify MCP servers before running tasks: `verify.py`
- Test watcher scripts individually before enabling continuous monitoring
- Use human-in-the-loop approval for sensitive actions (payments, sending messages)

### File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email Actions | `EMAIL_{message_id}.md` | `EMAIL_abc123.md` |
| File Drops | `FILE_{original_name}` | `FILE_invoice.pdf` |
| Approval Requests | `APPROVAL_{type}_{description}_{date}.md` | `APPROVAL_Payment_ClientA_2026-01-07.md` |
| Plans | `Plan_{task_name}.md` | `Plan_Q1_Tax_Prep.md` |

### Markdown Template (Action Items)

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---

## Email Content
{message snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Available Tools

### Playwright MCP (Browser Automation)

The `browsing-with-playwright` skill provides 22 tools for web automation:

| Category | Tools |
|----------|-------|
| Navigation | `browser_navigate`, `browser_navigate_back` |
| Interaction | `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option` |
| Inspection | `browser_snapshot`, `browser_take_screenshot` |
| Advanced | `browser_evaluate`, `browser_run_code`, `browser_wait_for` |

**Usage Example:**
```bash
# Navigate to URL
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Get page snapshot
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot -p '{}'
```

See `.qwen/skills/browsing-with-playwright/SKILL.md` for full documentation.

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 watcher, Claude reading/writing |
| **Silver** | 20-30 hrs | 2+ watchers, MCP server, approval workflow |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, Ralph Wiggum loop |
| **Platinum** | 60+ hrs | Cloud deployment, 24/7 operation, A2A sync |

## Resources

- **Full Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Agent Skills Docs:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Weekly Meeting:** Wednesdays 10:00 PM PKT on Zoom (see hackathon doc for link)
