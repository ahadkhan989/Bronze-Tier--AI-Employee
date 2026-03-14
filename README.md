# 🤖 Personal AI Employee -- FTEs

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.
>
> **Build a Digital FTE (Full-Time Equivalent) that works 24/7 for you!**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Tier Comparison](#-tier-comparison)
- [🥉 Bronze Tier - Foundation](#-bronze-tier---foundation)
- [🥈 Silver Tier - Functional Assistant](#-silver-tier---functional-assistant)
- [🥇 Gold Tier - Autonomous Employee](#-gold-tier---autonomous-employee)
- [Getting Started](#-getting-started)
- [Documentation](#-documentation)
- [Resources & Meetings](#-resources--meetings)

---

## 🎯 Overview

The **Personal AI Employee** is an autonomous digital FTE (Full-Time Equivalent) that manages your personal and business affairs 24/7. Built with **Claude Code/Qwen Code** as the reasoning engine and **Obsidian** as the knowledge base/dashboard.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT SOURCES                            │
│  Gmail  │  WhatsApp  │  Facebook  │  Twitter  │  Files     │
└────┬────┴─────┬──────┴─────┬──────┴────┬──────┴─────┬──────┘
     │          │            │          │            │
     ▼          ▼            ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                    WATCHERS (Continuous)                    │
│  Monitor inputs → Create action files in Needs_Action/      │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                  QWEN CODE (Reasoning)                      │
│  Read → Think → Plan → Write → Request Approval             │
└─────────────────────────────────────────────────────────────┘
     │
     ├─────────────┬─────────────────┐
     ▼             ▼                 ▼
┌─────────┐  ┌────────────┐   ┌──────────────┐
│ Simple  │  │  Pending_  │   │    Plans/    │
│ Actions │  │  Approval/ │   │  Multi-step  │
│ → Done  │  │            │   │  tracking    │
└─────────┘  └─────┬──────┘   └──────────────┘
                  │
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
    │ & Post  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Done/  │
    │  Logs/  │
    └─────────┘
```

---

## 📊 Tier Comparison

| Feature | 🥉 Bronze | 🥈 Silver | 🥇 Gold |
|---------|-----------|-----------|---------|
| **File Monitoring** | ✅ | ✅ | ✅ |
| **Gmail Integration** | ❌ | ✅ | ✅ |
| **LinkedIn Automation** | ❌ | ✅ | ✅ |
| **WhatsApp Monitoring** | ❌ | ✅ | ✅ |
| **Facebook/Instagram** | ❌ | ❌ | ✅ |
| **Twitter Integration** | ❌ | ❌ | ✅ |
| **Odoo ERP Integration** | ❌ | ❌ | ✅ |
| **Auto-Response Generation** | ❌ | ❌ | ✅ |
| **Docker Support** | ❌ | ❌ | ✅ |
| **Ralph Wiggum Loop** | ❌ | ❌ | ✅ |
| **Weekly CEO Briefing** | ❌ | ✅ | ✅ |
| **Estimated Setup Time** | 8-12 hrs | 20-30 hrs | 40+ hrs |

---

## 🥉 Bronze Tier - Foundation

**Estimated Time:** 8-12 hours

### ✨ Features

- ✅ **Obsidian Vault** with Dashboard & Company Handbook
- ✅ **File System Watcher** - Monitor drop folder for new files
- ✅ **Qwen Code Integration** - AI reads/writes to vault
- ✅ **Basic Folder Structure** - Inbox, Needs_Action, Done, etc.
- ✅ **Orchestrator** - Master coordination process
- ✅ **Approval Workflow** - Human-in-the-loop for sensitive actions
- ✅ **Daily Briefings** - Auto-generated summaries

### 📁 What You Get

| Component | Purpose |
|-----------|---------|
| `watchers/filesystem_watcher.py` | Monitor file drop folder |
| `orchestrator.py` | Coordinate all processes |
| `qwen_processor.py` | Qwen Code helper |
| `AI_Employee_Vault/` | Obsidian vault structure |

### 🚀 Quick Start

```bash
# 1. Install dependencies
pip install watchdog

# 2. Start file watcher
python watchers/filesystem_watcher.py AI_Employee_Vault

# 3. Process with Qwen Code
cd AI_Employee_Vault
claude "Review all files in Needs_Action folder"

# 4. Update dashboard
cd ..
python orchestrator.py AI_Employee_Vault --update-dashboard
```

### 📖 Key Commands

```bash
# Show system status
python orchestrator.py AI_Employee_Vault --status

# Generate daily briefing
python orchestrator.py AI_Employee_Vault --briefing

# Process with Qwen Code
python qwen_processor.py process AI_Employee_Vault

# Custom Qwen prompt
python qwen_processor.py custom "Your prompt here" AI_Employee_Vault
```

---

## 🥈 Silver Tier - Functional Assistant

**Estimated Time:** 20-30 hours

### ✨ Features (Everything in Bronze +)

- ✅ **Gmail Watcher** - Monitor Gmail for important emails
- ✅ **LinkedIn Watcher** - Monitor LinkedIn notifications & messages
- ✅ **LinkedIn Poster** - Auto-post content to LinkedIn
- ✅ **Email Sender** - Send emails via Gmail API
- ✅ **WhatsApp Watcher** - Monitor WhatsApp Web (Playwright)
- ✅ **Scheduler** - Automated tasks via cron/Task Scheduler
- ✅ **Weekly Briefings** - CEO briefing generation

### 📁 What You Get

| Component | Purpose |
|-----------|---------|
| `watchers/gmail_watcher.py` | Monitor Gmail |
| `watchers/linkedin_watcher.py` | Monitor LinkedIn |
| `watchers/linkedin_poster.py` | Post to LinkedIn |
| `watchers/email_sender.py` | Send emails |
| `watchers/whatsapp_watcher.py` | Monitor WhatsApp |
| `scheduler.py` | Task scheduling |

### 🚀 Quick Start

```bash
# 1. Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install playwright
playwright install chromium
pip install schedule

# 2. Authenticate Gmail
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate

# 3. Setup LinkedIn session
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session

# 4. Start watchers
python watchers/gmail_watcher.py AI_Employee_Vault --interval 120
python watchers/linkedin_watcher.py AI_Employee_Vault --interval 300

# 5. Start scheduler
python scheduler.py
```

### 📖 Key Commands

```bash
# Gmail Watcher
python watchers/gmail_watcher.py AI_Employee_Vault --interval 120

# LinkedIn Poster
python watchers/linkedin_poster.py AI_Employee_Vault \
  --content "Your post content" \
  --require-approval

# Process approved emails
python orchestrator.py AI_Employee_Vault --process-approvals

# Weekly briefing
python orchestrator.py AI_Employee_Vault --weekly-briefing
```

### 🔐 Required Setup

1. **Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Download `credentials.json`
   - Run: `python watchers/gmail_watcher.py AI_Employee_Vault --authenticate`

2. **LinkedIn:**
   - Run: `python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session`
   - Login to LinkedIn in the browser window
   - Session saved automatically

---

## 🥇 Gold Tier - Autonomous Employee

**Estimated Time:** 40+ hours

### ✨ Features (Everything in Silver +)

- ✅ **Facebook/Instagram Integration** - Graph API (not Playwright)
- ✅ **Twitter (X) Integration** - Monitor & post tweets
- ✅ **Odoo ERP Integration** - Docker Compose setup
- ✅ **Odoo MCP Server** - Invoice/customer management
- ✅ **Auto-Response Generation** - AI drafts responses automatically
- ✅ **Ralph Wiggum Loop** - Autonomous multi-step task completion
- ✅ **Weekly CEO Briefing** - With Odoo financial data
- ✅ **Error Recovery** - Retry logic & graceful degradation
- ✅ **Comprehensive Logging** - Full audit trail

### 📁 What You Get

| Component | Purpose |
|-----------|---------|
| `watchers/facebook_watcher.py` | Facebook monitoring (Graph API) |
| `watchers/facebook_poster.py` | Facebook/Instagram posting |
| `watchers/twitter_watcher.py` | Twitter monitoring |
| `watchers/twitter_poster.py` | Twitter posting |
| `watchers/odoo_sync_watcher.py` | Odoo ERP sync |
| `mcp_servers/odoo_mcp_server.py` | Odoo MCP server |
| `ralph_wiggum_loop.py` | Persistence loop |
| `auto_generate_response.py` | Auto-response generator |
| `docker-compose.yml` | Odoo + PostgreSQL setup |

### 🚀 Quick Start

```bash
# 1. Install dependencies
pip install facebook-business tweepy python-dotenv
pip install docker-compose

# 2. Start Odoo with Docker
docker-compose up -d odoo postgres

# 3. Configure .env file
# Copy .env.example to .env and fill in your credentials

# 4. Authenticate Facebook
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# 5. Start all watchers
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
python watchers/twitter_watcher.py AI_Employee_Vault --interval 300
python watchers/odoo_sync_watcher.py AI_Employee_Vault --interval 600

# 6. Start Ralph Wiggum loop
python ralph_wiggum_loop.py AI_Employee_Vault "Process all files"
```

### 📖 Key Commands

```bash
# Facebook Watcher
python watchers/facebook_watcher.py AI_Employee_Vault --interval 60

# Facebook Poster (with auto-generated responses)
python watchers/facebook_poster.py AI_Employee_Vault --process-replies

# Twitter Poster
python watchers/twitter_poster.py AI_Employee_Vault \
  --content "Your tweet" \
  --platform twitter

# Odoo Sync
python watchers/odoo_sync_watcher.py AI_Employee_Vault --sync-customers
python watchers/odoo_sync_watcher.py AI_Employee_Vault --generate-report

# Auto-generate responses
python auto_generate_response.py AI_Employee_Vault

# Ralph Wiggum Loop
python ralph_wiggum_loop.py AI_Employee_Vault "Process all files in Needs_Action"

# Weekly CEO Briefing (with Odoo data)
python orchestrator.py AI_Employee_Vault --weekly-briefing
```

### 🔐 Required Setup

1. **Facebook Graph API:**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create app & get Page Access Token
   - Add permissions: `pages_manage_posts`, `pages_read_engagement`
   - Update `.env` with `FACEBOOK_ACCESS_TOKEN`

2. **Twitter API:**
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Create app & get API keys
   - Update `.env` with Twitter credentials

3. **Odoo ERP:**
   ```bash
   docker-compose up -d odoo postgres
   # Access at: http://localhost:8069
   # Login: admin / admin
   ```

---

## 🎯 Getting Started

### Step 1: Choose Your Tier

| If you want to... | Start with... |
|-------------------|---------------|
| Learn the basics | 🥉 Bronze Tier |
| Automate email & social media | 🥈 Silver Tier |
| Full business automation | 🥇 Gold Tier |

### Step 2: Install Prerequisites

**Required:**
- Python 3.10+
- Qwen Code / Claude Code subscription
- Obsidian (free)
- Git

**Optional (for Silver/Gold):**
- Node.js v18+
- Docker Desktop (for Odoo)

### Step 3: Setup Your Tier

**Bronze Tier:**
```bash
pip install watchdog
python watchers/filesystem_watcher.py AI_Employee_Vault
```

**Silver Tier:**
```bash
# Complete Bronze setup first, then:
pip install google-api-python-client playwright schedule
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session
```

**Gold Tier:**
```bash
# Complete Silver setup first, then:
pip install facebook-business tweepy
docker-compose up -d odoo postgres
# Configure .env with your API credentials
```

### Step 4: Start Using

1. **Open Obsidian** → Load `AI_Employee_Vault` folder
2. **Check Dashboard.md** for status
3. **Drop files** in `Inbox/Drop/` for processing
4. **Review** `Needs_Action/` folder regularly
5. **Approve** actions by moving files to `Approved/`

---

## 📚 Documentation

### Tier-Specific Guides

| Tier | Guide | Description |
|------|-------|-------------|
| 🥉 Bronze | `README.md` (this file) | Basic setup & usage |
| 🥈 Silver | `SILVER_TIER.md` | Silver Tier guide |
| 🥈 Silver | `SILVER_TIER_GMAIL_LINKEDIN.md` | Gmail + LinkedIn setup |
| 🥇 Gold | `GOLD_TIER.md` | Gold Tier complete guide |
| 🥇 Gold | `FACEBOOK_COMPLETE_GUIDE.md` | Facebook integration |
| 🥇 Gold | `AUTO_RESPONSE_GUIDE.md` | Auto-response system |
| 🥇 Gold | `ODOO_SETUP.md` | Odoo ERP setup |
| 🥇 Gold | `GITHUB_PUSH_GUIDE.md` | Push to GitHub guide |

### Quick Reference

| Topic | File |
|-------|------|
| Security Audit | `SECURITY_REPORT.md` |
| Facebook Setup | `FACEBOOK_SETUP.md` |
| Facebook Workflow | `FACEBOOK_WORKFLOW.md` |
| Facebook Reply Guide | `FACEBOOK_REPLY_GUIDE.md` |
| Facebook Troubleshooting | `FACEBOOK_WATCHER_FIX.md` |
| Token Debugging | `fix_facebook_token.py` |
| Cleanup Script | `cleanup_security.bat` |

---

## 🤝 Resources & Meetings

### Hackathon Blueprint

- **Full Document:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Agent Skills Docs:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

### Weekly Meetings

Join the Personal AI Employee research meetings:

- **When:** Wednesdays 10:00 PM PKT
- **Zoom:** [Link in hackathon doc](Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- **YouTube:** https://www.youtube.com/@panaversity

### Learning Resources

| Topic | Resource |
|-------|----------|
| Claude Code Fundamentals | [Textbook Chapter](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) |
| Obsidian Fundamentals | [Official Help](https://help.obsidian.md) |
| Facebook Graph API | [Developer Docs](https://developers.facebook.com/docs/graph-api) |
| Odoo ERP | [Official Docs](https://www.odoo.com/documentation) |
| Docker Compose | [Official Docs](https://docs.docker.com/compose/) |

---

## 🏆 Hackathon Tiers

### Submission Requirements

- ✅ GitHub repository (public or private)
- ✅ README.md with setup instructions
- ✅ Demo video (5-10 minutes)
- ✅ Security disclosure
- ✅ Tier declaration

### Judging Criteria

| Criterion | Weight |
|-----------|--------|
| Functionality | 30% |
| Innovation | 25% |
| Practicality | 20% |
| Security | 15% |
| Documentation | 10% |

---

## 📄 License

This project is part of the Personal AI Employee Hackathon. Share and build upon it freely.

---

## 🌟 Ready to Build Your AI Employee?

**Choose your tier and start building!**

- 🥉 **Bronze:** Perfect for learning the basics
- 🥈 **Silver:** Great for email & social media automation
- 🥇 **Gold:** Complete business automation with ERP integration

**Good luck with your hackathon!** 🚀🎉

---

*Built with ❤️ for the future of autonomous work*

**Last Updated:** 2026-03-14  
**Status:** ✅ Gold Tier Complete
