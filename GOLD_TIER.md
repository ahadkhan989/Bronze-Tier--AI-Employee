# 🥇 Gold Tier - AI Employee Complete Implementation

Complete Gold Tier implementation with **Facebook/Instagram Integration**, **Odoo ERP Integration**, **Docker Compose**, and **Ralph Wiggum Persistence Loop**.

---

## 📋 Gold Tier Requirements (All Completed)

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| All Silver requirements | ✅ | Gmail + LinkedIn + WhatsApp + File watchers |
| Full cross-domain integration | ✅ | Personal + Business systems |
| **Odoo ERP Integration** | ✅ | Docker Compose + MCP Server |
| **Facebook/Instagram Integration** | ✅ | Watcher + Poster |
| **Twitter (X) Integration** | ✅ | Watcher + Poster |
| Multiple MCP servers | ✅ | Email + Browser + Odoo |
| Weekly Business Audit | ✅ | CEO Briefing generation |
| Error recovery | ✅ | Retry logic + graceful degradation |
| Comprehensive audit logging | ✅ | Daily JSON logs |
| **Ralph Wiggum Loop** | ✅ | Autonomous multi-step completion |
| Architecture documentation | ✅ | This document |

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install playwright schedule docker-compose
playwright install chromium

# Facebook/Meta dependencies
pip install facebook-business

# Odoo dependencies
pip install xmlrpc-client requests

# Additional utilities
pip install python-dotenv retry
```

### Step 2: Set Up Docker Compose for Odoo

```bash
# Navigate to project
cd "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"

# Start Odoo with Docker Compose
docker-compose up -d odoo postgres

# Check Odoo status
docker-compose ps

# View Odoo logs
docker-compose logs odoo
```

**Access Odoo:**
- URL: http://localhost:8069
- Database: `odoo-db`
- Email: `admin`
- Password: `admin`

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```bash
# .env - NEVER commit this file
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo-db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Facebook Configuration
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_ig_account_id

# Twitter Configuration
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret

# Gmail Configuration (from Silver)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Security
DRY_RUN=false
MAX_EMAILS_PER_HOUR=10
MAX_POSTS_PER_DAY=5
```

### Step 4: Authenticate Services

```bash
# Gmail (from Silver)
python watchers/gmail_watcher.py AI_Employee_Vault --authenticate

# LinkedIn (from Silver)
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session

# Facebook
python watchers/facebook_watcher.py AI_Employee_Vault --setup-session

# Twitter
python watchers/twitter_watcher.py AI_Employee_Vault --setup-session
```

### Step 5: Start All Watchers

```bash
# Terminal 1 - Gmail Watcher
python watchers/gmail_watcher.py AI_Employee_Vault --interval 60

# Terminal 2 - LinkedIn Watcher
python watchers/linkedin_watcher.py AI_Employee_Vault --interval 300

# Terminal 3 - Facebook Watcher
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

# Terminal 4 - Twitter Watcher
python watchers/twitter_watcher.py AI_Employee_Vault --interval 300

# Terminal 5 - File Watcher
python watchers/filesystem_watcher.py AI_Employee_Vault

# Terminal 6 - Odoo Sync Watcher
python watchers/odoo_sync_watcher.py AI_Employee_Vault --interval 600
```

### Step 6: Start Ralph Wiggum Loop

```bash
# Start the autonomous processing loop
python ralph_wiggum_loop.py AI_Employee_Vault "Process all files in Needs_Action"
```

---

## 📘 Facebook/Instagram Integration (Graph API)

### Facebook Watcher

Monitors Facebook Page and Instagram Business Account for:
- New messages
- Comments on posts
- Page notifications

Uses **Facebook Graph API** (not Playwright) for reliable, production-ready integration.

### Facebook Poster

Posts content to:
- Facebook Page (text, images, links)
- Instagram Business Account (images with captions)
- Both simultaneously (cross-posting)

### Setup Guide

See **FACEBOOK_SETUP.md** for complete setup instructions.

### Commands

```bash
# Facebook Watcher
python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

# Test Facebook connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# Facebook Poster
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --platform facebook

# Instagram Poster (requires image)
python watchers/facebook_poster.py AI_Employee_Vault \
  --content "Your post content here" \
  --image path/to/image.jpg \
  --platform instagram

# Cross-post to both
python watchers/facebook_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/social_post.md \
  --platform both

# With approval workflow
python watchers/facebook_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/social_post.md \
  --require-approval
```

### Required Permissions

- `pages_manage_posts` - Create posts on Pages
- `pages_read_engagement` - Read Page engagement
- `instagram_basic` - Basic Instagram info
- `instagram_content_publish` - Post to Instagram

---

## 🐦 Twitter (X) Integration

### Twitter Watcher

Monitors Twitter for:
- Mentions (@yourhandle)
- Direct messages
- Keyword mentions
- Engagement metrics

### Twitter Poster

Posts tweets and threads:
- Single tweets (280 chars)
- Threaded tweets
- Tweets with images
- Scheduled tweets

### Commands

```bash
# Twitter Watcher
python watchers/twitter_watcher.py AI_Employee_Vault --interval 300

# Twitter Poster
python watchers/twitter_poster.py AI_Employee_Vault \
  --content "Your tweet content here"

# Thread poster
python watchers/twitter_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/twitter_thread.md

# With image
python watchers/twitter_poster.py AI_Employee_Vault \
  --content "Check this out!" \
  --image path/to/image.jpg
```

---

## 🏢 Odoo ERP Integration

### Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  AI Employee    │────▶│  Odoo MCP    │────▶│  Odoo ERP    │
│  (Claude Code)  │     │   Server     │     │  (Docker)    │
└─────────────────┘     └──────────────┘     └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   PostgreSQL │
                        │   Database   │
                        └──────────────┘
```

### Odoo MCP Server Features

| Feature | Description |
|---------|-------------|
| **Invoice Management** | Create, send, track invoices |
| **Customer Management** | Create/update customer records |
| **Accounting** | Record payments, reconcile transactions |
| **Inventory** | Track stock levels, create products |
| **Sales Orders** | Create and manage sales orders |
| **Reporting** | Generate financial reports |

### Commands

```bash
# Start Odoo MCP Server
python mcp_servers/odoo_mcp_server.py

# Test Odoo connection
python watchers/odoo_sync_watcher.py AI_Employee_Vault --test-connection

# Sync customers from Odoo
python watchers/odoo_sync_watcher.py AI_Employee_Vault --sync-customers

# Create invoice in Odoo
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --create-invoice \
  --customer "Client Name" \
  --amount 1500 \
  --description "Consulting services"

# Generate financial report
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --generate-report \
  --type monthly_revenue \
  --month 2026-01
```

### Docker Compose Configuration

The `docker-compose.yml` sets up:

1. **Odoo Community Edition** (latest v19+)
2. **PostgreSQL Database** (persistent storage)
3. **Odoo Addons Volume** (for custom modules)
4. **PostgreSQL Data Volume** (for data persistence)

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: ai-employee-odoo
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    environment:
      - ODOO_DB_NAME=odoo-db
      - ODOO_DB_USER=odoo
      - ODOO_DB_PASSWORD=odoo_password
      - ODOO_ADMIN_PASSWORD=admin_password
    volumes:
      - ./odoo/addons:/mnt/extra-addons
      - ./odoo/data:/var/lib/odoo
      - ./odoo/logs:/var/log/odoo
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: ai-employee-postgres
    environment:
      - POSTGRES_DB=odoo-db
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo_password
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
    restart: unless-stopped
```

---

## 🔄 Ralph Wiggum Persistence Loop

### Overview

The Ralph Wiggum loop keeps Claude Code working autonomously until tasks are complete:

1. **State File**: Orchestrator creates a state file with the task
2. **Claude Works**: Claude processes the task
3. **Completion Check**: Stop hook checks if task is in `/Done`
4. **Loop or Exit**: If not done, re-inject prompt and continue
5. **Max Iterations**: Prevent infinite loops

### Usage

```bash
# Basic usage
python ralph_wiggum_loop.py AI_Employee_Vault \
  "Process all files in Needs_Action folder"

# With max iterations
python ralph_wiggum_loop.py AI_Employee_Vault \
  "Process all files in Needs_Action folder" \
  --max-iterations 10

# With completion promise
python ralph_wiggum_loop.py AI_Employee_Vault \
  "Generate weekly CEO briefing" \
  --completion-promise "TASK_COMPLETE"
```

### How It Works

```python
# Simplified Ralph Wiggum logic
while iteration < max_iterations:
    # Run Claude with prompt
    output = run_claude(prompt)
    
    # Check if task is complete
    if is_task_complete():
        print("Task completed!")
        break
    
    # Check for completion promise
    if "TASK_COMPLETE" in output:
        print("Task completed!")
        break
    
    # Re-inject prompt with previous output
    prompt = f"Continue working. Previous output:\n{output}\n\nCurrent task: {task}"
    iteration += 1
```

---

## 📊 Weekly Business Audit

### CEO Briefing Generation

Every Monday at 8:00 AM, the system generates a comprehensive briefing:

```markdown
# Monday Morning CEO Briefing
## Week of 2026-03-09 to 2026-03-13

### Executive Summary
Strong week with revenue ahead of target.

### Revenue (from Odoo)
- **This Week**: $5,450
- **MTD**: $12,500 (62% of $20,000 target)
- **Trend**: On track

### Completed Tasks
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone delivered
- [x] Social media posts scheduled

### Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

### Proactive Suggestions

#### Cost Optimization
- **Software X**: No activity in 45 days. Cost: $50/month.
  - [ACTION] Cancel subscription?

#### Upcoming Deadlines
- Project Alpha final: March 20
- Tax filing: March 31

### Odoo Accounting Summary
- **Outstanding Invoices**: 3 ($2,500)
- **Paid This Week**: 5 ($7,200)
- **Pending Payments**: 2 ($1,800)
```

### Commands

```bash
# Generate weekly briefing
python orchestrator.py AI_Employee_Vault --weekly-briefing

# Generate monthly audit
python orchestrator.py AI_Employee_Vault --monthly-audit

# Odoo financial report
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --generate-report \
  --type weekly_revenue
```

---

## 📁 Gold Tier File Structure

```
Bronze-Tier--AI-Employee/
├── .env                              # Environment variables (NEVER commit)
├── docker-compose.yml                # Odoo + PostgreSQL setup
├── ralph_wiggum_loop.py              # Ralph Wiggum persistence
├── GOLD_TIER.md                      # This documentation
│
├── .qwen/skills/
│   ├── browsing-with-playwright/     # From Bronze
│   ├── gmail-watcher/                # From Silver
│   ├── linkedin-watcher/             # From Silver
│   ├── linkedin-poster/              # From Silver
│   ├── email-mcp-server/             # From Silver
│   ├── approval-workflow/            # From Silver
│   ├── plan-reasoning-loop/          # From Silver
│   ├── scheduling/                   # From Silver
│   ├── facebook-watcher/             # NEW: Gold
│   ├── facebook-poster/              # NEW: Gold
│   ├── twitter-watcher/              # NEW: Gold
│   ├── twitter-poster/               # NEW: Gold
│   ├── odoo-mcp-server/              # NEW: Gold
│   └── ralph-wiggum-loop/            # NEW: Gold
│
├── watchers/
│   ├── base_watcher.py               # From Bronze
│   ├── filesystem_watcher.py         # From Bronze
│   ├── gmail_watcher.py              # From Silver
│   ├── linkedin_watcher.py           # From Silver
│   ├── linkedin_poster.py            # From Silver
│   ├── email_sender.py               # From Silver
│   ├── facebook_watcher.py           # NEW: Gold
│   ├── facebook_poster.py            # NEW: Gold
│   ├── twitter_watcher.py            # NEW: Gold
│   ├── twitter_poster.py             # NEW: Gold
│   ├── odoo_sync_watcher.py          # NEW: Gold
│   └── whatsapp_watcher.py           # From Silver
│
├── mcp_servers/
│   ├── odoo_mcp_server.py            # NEW: Gold
│   └── email_mcp_server/             # From Silver
│
├── orchestrator.py                   # Updated for Gold
├── qwen_processor.py                 # From Silver
├── scheduler.py                      # From Silver
│
└── AI_Employee_Vault/
    ├── Dashboard.md
    ├── Company_Handbook.md
    ├── Business_Goals.md
    ├── Odoo_Config.md                # NEW: Gold
    ├── Social_Media_Strategy.md      # NEW: Gold
    ├── Inbox/
    ├── Needs_Action/
    ├── In_Progress/
    ├── Pending_Approval/
    ├── Approved/
    ├── Rejected/
    ├── Done/
    ├── Logs/
    ├── Briefings/
    ├── Plans/
    ├── Accounting/
    ├── Invoices/
    ├── Templates/
    └── linkedin_session/             # From Silver
```

---

## 🔒 Security Best Practices

### Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo-db
ODOO_USERNAME=admin
ODOO_PASSWORD=CHANGE_THIS_PASSWORD

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id

# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret

# Security
DRY_RUN=false
MAX_EMAILS_PER_HOUR=10
MAX_POSTS_PER_DAY=5
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### Approval Rules (Gold Tier)

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email replies | ❌ | ✅ Always |
| Social posts (draft) | ✅ | ✅ Before posting |
| Odoo invoice creation | ❌ | ✅ Always |
| Odoo payment recording | ❌ | ✅ Always |
| Odoo customer creation | ❌ | ✅ For new customers |
| Facebook/Instagram post | ❌ | ✅ Always |
| Twitter post | ❌ | ✅ Always |
| Bulk operations (>10) | ❌ | ✅ Always |

---

## 🐛 Troubleshooting

### Docker/Odoo Issues

```bash
# Check Docker status
docker-compose ps

# View Odoo logs
docker-compose logs odoo

# Restart Odoo
docker-compose restart odoo

# Reset Odoo (WARNING: deletes data)
docker-compose down -v
docker-compose up -d odoo postgres

# Access Odoo database
docker-compose exec postgres psql -U odoo -d odoo-db
```

### Facebook API Issues

```bash
# Test Facebook connection
python watchers/facebook_watcher.py AI_Employee_Vault --test-connection

# Re-authenticate Facebook
python watchers/facebook_watcher.py AI_Employee_Vault --setup-session

# Check token expiration
python -c "from facebook_business.api import FacebookAPI; print(FacebookAPI.get_access_token())"
```

### Twitter API Issues

```bash
# Test Twitter connection
python watchers/twitter_watcher.py AI_Employee_Vault --test-connection

# Re-authenticate Twitter
python watchers/twitter_watcher.py AI_Employee_Vault --setup-session
```

### Ralph Wiggum Loop Issues

```bash
# Check loop status
cat AI_Employee_Vault/Logs/ralph_wiggum_status.json

# Reset loop state
rm AI_Employee_Vault/Logs/ralph_wiggum_*.json

# Run with verbose logging
python ralph_wiggum_loop.py AI_Employee_Vault "Your task" --verbose
```

---

## 📊 Gold Tier Checklist

Use this to verify your Gold Tier completion:

### Core Infrastructure
- [ ] Docker Compose running Odoo + PostgreSQL
- [ ] Odoo accessible at http://localhost:8069
- [ ] Environment variables configured
- [ ] All secrets in .gitignore

### Social Media Integration
- [ ] Facebook Watcher detecting messages/comments
- [ ] Facebook Poster publishing to Page
- [ ] Instagram Poster publishing photos
- [ ] Twitter Watcher detecting mentions/DMs
- [ ] Twitter Poster publishing tweets
- [ ] All social posts require approval

### Odoo Integration
- [ ] Odoo MCP server running
- [ ] Can create invoices in Odoo
- [ ] Can create customers in Odoo
- [ ] Can record payments in Odoo
- [ ] Can generate financial reports
- [ ] All Odoo actions require approval

### Ralph Wiggum Loop
- [ ] Loop starts successfully
- [ ] Processes multiple iterations
- [ ] Detects task completion
- [ ] Respects max iterations
- [ ] Logs all iterations

### Business Audit
- [ ] Weekly CEO briefing generates
- [ ] Odoo data included in briefing
- [ ] Social media metrics included
- [ ] Action items tracked
- [ ] Suggestions generated

### Security & Logging
- [ ] All credentials in environment variables
- [ ] Approval workflow functional
- [ ] Daily JSON logs created
- [ ] Error recovery working
- [ ] Graceful degradation tested

---

## 📚 Resources

### Facebook/Meta
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **Facebook Business SDK**: https://github.com/facebook/facebook-business-sdk-codegen

### Twitter
- **Twitter API v2**: https://developer.twitter.com/en/docs/twitter-api
- **Tweepy Library**: https://docs.tweepy.org

### Odoo
- **Odoo Documentation**: https://www.odoo.com/documentation
- **Odoo External API**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **Odoo Docker Image**: https://hub.docker.com/_/odoo

### Docker
- **Docker Compose**: https://docs.docker.com/compose/
- **Docker for Windows**: https://docs.docker.com/desktop/install/windows-install/

### Ralph Wiggum Pattern
- **Reference Implementation**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

---

*Gold Tier complete! Your AI Employee now has full business automation capabilities with Odoo ERP integration and comprehensive social media management.*
