---
name: linkedin-poster
description: |
  Automatically post to LinkedIn about business updates to generate sales.
  Uses Playwright to automate LinkedIn posting with text, images, and hashtags.
  Supports scheduled posts, approval workflow, and engagement tracking.
---

# LinkedIn Poster Skill

Automatically post content to LinkedIn for business growth.

## ⚠️ Important Notice

**This tool uses LinkedIn Web automation. Be aware of:**
- LinkedIn's Terms of Service
- Posting frequency limits (max 5 posts/day recommended)
- Content guidelines

## Prerequisites

1. **Python packages**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **LinkedIn Account** with session already set up

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: Ensure LinkedIn Session Exists

```bash
# If you haven't set up LinkedIn session yet
python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session
```

### Step 3: Create Content Template

Create `linkedin_content.md` in your vault:

```markdown
---
type: linkedin_post
scheduled: 2026-03-11T09:00:00Z
hashtags: ["#AI", "#Automation", "#Business"]
---

# Exciting News!

We just launched our new AI Employee system that helps businesses automate their daily operations 24/7.

🤖 Bronze Tier: Starting at $500
🥈 Silver Tier: Starting at $1000
🥇 Gold Tier: Custom pricing

Want to learn more? DM me!

#AI #Automation #Business #Productivity
```

## Usage

### Post Immediately

```bash
python watchers/linkedin_poster.py AI_Employee_Vault --content "Your post content here"
```

### Post from File

```bash
python watchers/linkedin_poster.py AI_Employee_Vault --file AI_Employee_Vault/linkedin_content.md
```

### With Approval Workflow

```bash
# Creates approval request first
python watchers/linkedin_poster.py AI_Employee_Vault --file content.md --require-approval
```

### Scheduled Post

```bash
python watchers/linkedin_poster.py AI_Employee_Vault --file content.md --schedule "2026-03-11T09:00:00"
```

## Content Templates

### Business Update Template

```markdown
---
hashtags: ["#Business", "#Update", "#Growth"]
image: path/to/image.png
---

📈 Business Update

We're excited to share our latest milestone: [achievement]!

Key highlights:
• [Point 1]
• [Point 2]
• [Point 3]

Thank you to our amazing clients and partners!

#Business #Growth #Milestone
```

### Lead Generation Template

```markdown
---
hashtags: ["#AI", "#Automation", "#LeadGen"]
---

🤖 Are you spending too much time on repetitive tasks?

Our AI Employee system can help you:
✅ Process emails automatically
✅ Monitor WhatsApp & LinkedIn
✅ Generate reports 24/7
✅ Reduce manual work by 80%

Ready to transform your business? Let's talk!

#AI #Automation #Productivity #Business
```

## Posting Best Practices

1. **Frequency**: Max 1-2 posts per day
2. **Timing**: Best times are 8-10 AM and 12-1 PM
3. **Content**: Mix of educational, promotional, and engagement posts
4. **Hashtags**: 3-5 relevant hashtags
5. **Images**: Posts with images get 2x engagement

## Approval Workflow

For business posts, use the approval workflow:

1. **Create draft** in `Pending_Approval/`
2. **Human reviews** content
3. **Move to `Approved/`** to post
4. **Orchestrator posts** automatically

## Example: Automated Business Posting

```bash
# Create content
cat > AI_Employee_Vault/Plans/linkedin_post_draft.md << EOF
---
type: linkedin_post
status: draft
---

🚀 Just completed a Bronze Tier AI Employee setup!

Our client can now:
• Auto-process emails
• Monitor WhatsApp 24/7  
• Generate daily briefings

Want your own AI Employee? DM me!

#AI #Automation #Business
EOF

# Post with approval
python watchers/linkedin_poster.py AI_Employee_Vault \
  --file AI_Employee_Vault/Plans/linkedin_post_draft.md \
  --require-approval
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Run --setup-session first |
| Post failed | Check content length (<3000 chars) |
| Rate limited | Wait 24 hours before posting again |

## Analytics

Track post performance:

```bash
# Check recent posts
python watchers/linkedin_poster.py AI_Employee_Vault --analytics
```
