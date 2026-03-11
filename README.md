# 🤖 Personal AI Employee - Bronze Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is a **Bronze-Tier implementation** of the Personal AI Employee hackathon project. It provides the foundational layer for an autonomous digital FTE (Full-Time Equivalent) that manages personal and business affairs using **Qwen Code** as the reasoning engine and **Obsidian** as the knowledge base/dashboard.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## ✨ Features

### Bronze Tier Deliverables

- ✅ **Obsidian Vault** with Dashboard.md and Company_Handbook.md
- ✅ **File System Watcher** - Monitors a drop folder for new files
- ✅ **Qwen Code Integration** - Reads from and writes to the vault
- ✅ **Basic Folder Structure** - /Inbox, /Needs_Action, /Done, etc.
- ✅ **Orchestrator** - Master process for coordination
- ✅ **Action Templates** - Pre-built templates for common actions

### What It Can Do

1. **File Drop Processing**: Drop any file into the monitored folder → AI creates an action item
2. **Task Tracking**: Organize tasks through pending → in-progress → done workflow
3. **Approval System**: Human-in-the-loop for sensitive actions
4. **Daily Briefings**: Auto-generated summaries of pending work
5. **Audit Logging**: All actions logged for review

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL INPUT                           │
│                    (File Drop)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 PERCEPTION LAYER                            │
│              FileSystemWatcher.py                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  OBSIDIAN VAULT                             │
│  /Needs_Action  →  /Plans  →  /Done                         │
│  /Pending_Approval  →  /Approved  →  /Rejected              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 REASONING LAYER                             │
│                    QWEN CODE                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION                               │
│                 orchestrator.py                             │
│   - Dashboard Updates   - Approval Processing               │
│   - Daily Briefings     - Logging                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Python](https://www.python.org/downloads/) | 3.10+ | Watcher scripts & orchestrator |
| [Qwen Code](https://github.com/anthropics/claude-code) | Active subscription | Reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ (free) | Knowledge base & dashboard |
| [Node.js](https://nodejs.org/) | v18+ LTS | MCP servers (optional for Silver+) |

### Optional (for enhanced functionality)

- **watchdog** (Python package) - Efficient file system monitoring
- **Git** - Version control for your vault

---

## 🚀 Installation

### 1. Clone/Navigate to Project

```bash
cd "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install watchdog
```

### 3. Open Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder
4. You should see Dashboard.md, Company_Handbook.md, etc.

### 4. Verify Qwen Code

```bash
qwen --version
```

---

## ⚡ Quick Start

### Step 1: Initialize the System

```bash
# Update dashboard and check status
python orchestrator.py AI_Employee_Vault --status
```

### Step 2: Start the File Watcher

```bash
# Start watching the drop folder
python watchers/filesystem_watcher.py AI_Employee_Vault
```

Keep this running in a terminal window. It will monitor for new files.

### Step 3: Test with a File Drop

1. Create a test file (e.g., `test_document.txt`)
2. Drop it into `AI_Employee_Vault/Inbox/Drop/`
3. Watch the watcher create an action file in `Needs_Action/`

### Step 4: Process with Qwen Code

```bash
# Navigate to vault directory
cd AI_Employee_Vault

# Run Qwen Code to process pending items
qwen "Review all files in Needs_Action folder. For each file, create a plan and suggest next steps. Move completed items to Done folder."
```

### Step 5: Update Dashboard

```bash
# Back in project root
python orchestrator.py AI_Employee_Vault --update-dashboard
```

---

## 📖 Usage

### Daily Workflow

1. **Morning**: Check Dashboard.md for pending items
2. **Throughout day**: Drop files into `Inbox/Drop/` for processing
3. **Review**: Check `Needs_Action/` folder periodically
4. **Approve**: Move files from `Pending_Approval/` to `Approved/` when ready
5. **Process**: Run Qwen Code on pending items
6. **Evening**: Generate daily briefing

### Key Commands

```bash
# Show system status
python orchestrator.py AI_Employee_Vault --status

# Process approved files
python orchestrator.py AI_Employee_Vault --process-approvals

# Generate daily briefing
python orchestrator.py AI_Employee_Vault --briefing

# Start file watcher (polling mode)
python watchers/filesystem_watcher.py AI_Employee_Vault

# Start file watcher (watchdog mode - more efficient)
python watchers/filesystem_watcher.py AI_Employee_Vault --watchdog

# Process with Qwen Code (using helper script)
python qwen_processor.py process AI_Employee_Vault

# Run custom Qwen Code prompt
python qwen_processor.py custom "Your custom prompt here" AI_Employee_Vault
```

### Qwen Code Prompts

Instead of typing full prompts, use the helper script:

```bash
# Process all pending items
python qwen_processor.py process AI_Employee_Vault

# Generate a plan for complex tasks
python qwen_processor.py plan AI_Employee_Vault

# Daily review
python qwen_processor.py review AI_Employee_Vault

# Approval processing
python qwen_processor.py approvals AI_Employee_Vault

# Full system audit
python qwen_processor.py audit AI_Employee_Vault

# Custom prompt
python qwen_processor.py custom "Your custom prompt here" AI_Employee_Vault
```

---

## 📁 Folder Structure

```
Bronze-Tier--AI-Employee/
├── AI_Employee_Vault/           # Obsidian vault (open this in Obsidian)
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # Objectives and metrics
│   ├── Inbox/                   # Raw incoming items
│   │   └── Drop/                # Drop files here for processing
│   ├── Needs_Action/            # Items requiring processing
│   ├── In_Progress/             # Currently being worked on
│   ├── Pending_Approval/        # Awaiting human approval
│   ├── Approved/                # Approved actions (ready to process)
│   ├── Rejected/                # Rejected items
│   ├── Done/                    # Completed tasks
│   ├── Logs/                    # System logs
│   ├── Briefings/               # Daily/weekly briefings
│   ├── Accounting/              # Financial records
│   ├── Invoices/                # Invoice files
│   └── Templates/               # Action file templates
│       ├── Email_Action_Template.md
│       ├── Approval_Request_Template.md
│       ├── Plan_Template.md
│       └── Task_Template.md
│
├── watchers/
│   ├── base_watcher.py          # Abstract base class
│   └── filesystem_watcher.py    # File drop watcher
│
├── orchestrator.py              # Master coordination script
├── README.md                    # This file
└── QWEN.md                      # Project context for AI assistants
```

### Folder Purposes

| Folder | Purpose |
|--------|---------|
| `/Inbox/Drop` | Drop files here for AI processing |
| `/Needs_Action` | New action items created by watchers |
| `/In_Progress` | Items currently being worked on |
| `/Pending_Approval` | Actions awaiting your decision |
| `/Approved` | Approved actions ready to execute |
| `/Rejected` | Declined actions (archived) |
| `/Done` | Completed tasks |

---

## 🔧 Troubleshooting

### File Watcher Not Detecting Files

```bash
# Check if watchdog is installed
pip install watchdog

# Run with verbose logging
python watchers/filesystem_watcher.py AI_Employee_Vault --interval 2
```

### Orchestrator Can't Find Vault

```bash
# Use absolute path
python orchestrator.py "D:\code\Hackathon Project\Bronze-Tier--AI-Employee\AI_Employee_Vault"
```

### Qwen Code Not Processing Files

1. Ensure you're in the vault directory: `cd AI_Employee_Vault`
2. Check file permissions
3. Verify Qwen Code subscription is active

### Dashboard Not Updating

```bash
# Force update
python orchestrator.py AI_Employee_Vault --update-dashboard

# Check for errors in Logs folder
cat AI_Employee_Vault/Logs/*.log
```

---

## 🎯 Next Steps (Silver Tier Upgrades)

Once you've mastered the Bronze Tier, consider adding:

1. **Gmail Watcher** - Monitor Gmail for important emails
2. **WhatsApp Watcher** - Use Playwright to monitor WhatsApp Web
3. **MCP Servers** - Enable Claude to send emails, make payments
4. **Scheduled Tasks** - Use cron/Task Scheduler for daily briefings
5. **Human-in-the-Loop** - Full approval workflow for sensitive actions

---

## 📚 Resources

- **Full Hackathon Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Agent Skills Docs**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Obsidian Help**: https://help.obsidian.md
- **Qwen Code Docs**: https://github.com/anthropics/claude-code

---

## 🤝 Weekly Meetings

Join the Personal AI Employee research meetings:

- **When**: Wednesdays 10:00 PM PKT
- **Zoom**: [Link in hackathon doc](Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- **YouTube**: https://www.youtube.com/@panaversity

---

## 📄 License

This project is part of the Personal AI Employee Hackathon. Share and build upon it freely.

---

*Built with ❤️ for the future of autonomous work*
