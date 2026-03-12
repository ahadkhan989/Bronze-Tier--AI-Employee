---
name: scheduling
description: |
  Schedule automated tasks using cron (Linux/Mac) or Task Scheduler (Windows).
  Automate daily briefings, periodic checks, and recurring AI Employee tasks.
  Includes templates for common scheduling scenarios.
---

# Scheduling Skill

Automate AI Employee tasks with system schedulers.

## Overview

Run AI Employee tasks on a schedule:
- **Daily briefings** at 8:00 AM
- **Hourly checks** for new emails
- **Weekly audits** every Monday
- **Monthly reports** on the 1st

## Scheduling Options

| Platform | Tool | Complexity |
|----------|------|------------|
| Linux/Mac | cron | Simple |
| Windows | Task Scheduler | Medium |
| Cross-platform | Python schedule library | Simple |
| Production | systemd timers | Advanced |

---

## Option 1: Cron (Linux/Mac)

### Setup

```bash
# Edit crontab
crontab -e

# Add entries (examples below)
```

### Common Schedules

```bash
# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --briefing

# Process approvals every hour
0 * * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --process-approvals

# Update dashboard every 15 minutes
*/15 * * * * cd /path/to/project && python orchestrator.py AI_Employee_Vault --update-dashboard

# Weekly audit every Monday at 9:00 AM
0 9 * * 1 cd /path/to/project && python qwen_processor.py audit AI_Employee_Vault

# Monthly report on 1st of month at 10:00 AM
0 10 1 * * cd /path/to/project && python qwen_processor.py review AI_Employee_Vault
```

### Cron Format

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Cron Examples

```bash
# Every 5 minutes
*/5 * * * *

# Every hour at :30
30 * * * *

# Every weekday at 9:00 AM
0 9 * * 1-5

# Every day at 6:00 PM
0 18 * * *

# First day of every month
0 0 1 * *
```

---

## Option 2: Windows Task Scheduler

### Create Scheduled Task (PowerShell)

```powershell
# Daily briefing at 8:00 AM
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "orchestrator.py AI_Employee_Vault --briefing" `
  -WorkingDirectory "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger -Description "Generate daily briefing"
```

### Common Windows Tasks

```powershell
# Hourly approval processing
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "AI_Employee_Process_Approvals" `
  -Action $action -Trigger $trigger
```

### Task Scheduler GUI

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: `AI Employee Daily Briefing`
4. Trigger: `Daily` at `8:00 AM`
5. Action: `Start a program`
   - Program: `python`
   - Arguments: `orchestrator.py AI_Employee_Vault --briefing`
   - Start in: `D:\code\Hackathon Project\Bronze-Tier--AI-Employee`

---

## Option 3: Python Schedule Library

### Installation

```bash
pip install schedule
```

### Example Script

```python
# scheduler.py
import schedule
import time
import subprocess
from pathlib import Path

VAULT = "AI_Employee_Vault"
PROJECT = Path(__file__).parent

def run_command(cmd):
    """Run a shell command."""
    subprocess.run(cmd, shell=True, cwd=PROJECT)

def daily_briefing():
    print("Running daily briefing...")
    run_command(f"python orchestrator.py {VAULT} --briefing")

def process_approvals():
    print("Processing approvals...")
    run_command(f"python orchestrator.py {VAULT} --process-approvals")

def update_dashboard():
    print("Updating dashboard...")
    run_command(f"python orchestrator.py {VAULT} --update-dashboard")

# Schedule tasks
schedule.every().day.at("08:00").do(daily_briefing)
schedule.every().hour.do(process_approvals)
schedule.every(15).minutes.do(update_dashboard)
schedule.every().monday.at("09:00").do(
    lambda: run_command(f"python qwen_processor.py audit {VAULT}")
)

print("Scheduler started. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Run Scheduler

```bash
# Start the scheduler (runs continuously)
python scheduler.py

# Or as background service
nohup python scheduler.py &
```

---

## Option 4: systemd Timer (Linux Production)

### Service File

```ini
# /etc/systemd/system/ai-employee-briefing.service
[Unit]
Description=AI Employee Daily Briefing
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python orchestrator.py AI_Employee_Vault --briefing
```

### Timer File

```ini
# /etc/systemd/system/ai-employee-briefing.timer
[Unit]
Description=Run AI Employee Briefing Daily

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable Timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-briefing.timer
sudo systemctl start ai-employee-briefing.timer
```

---

## Scheduled Task Templates

### Daily Briefing (8:00 AM)

```bash
# Generates summary of pending items, completed tasks, and suggestions
python orchestrator.py AI_Employee_Vault --briefing
```

### Hourly Approval Check

```bash
# Process any approved files
python orchestrator.py AI_Employee_Vault --process-approvals
```

### Dashboard Update (Every 15 min)

```bash
# Keep dashboard current
python orchestrator.py AI_Employee_Vault --update-dashboard
```

### Weekly Audit (Monday 9:00 AM)

```bash
# Full system audit
python qwen_processor.py audit AI_Employee_Vault
```

### Monthly Review (1st of month)

```bash
# Generate monthly report
python qwen_processor.py review AI_Employee_Vault
```

---

## Logging Scheduled Tasks

### Cron Logging

```bash
# View cron logs
grep CRON /var/log/syslog

# Or log to file
0 8 * * * cd /path && python orchestrator.py AI_Employee_Vault --briefing >> logs/briefing.log 2>&1
```

### Windows Task History

1. Open **Task Scheduler**
2. Select your task
3. View **History** tab

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task doesn't run | Check working directory |
| Python not found | Use full path: `/usr/bin/python` |
| Permission denied | Run as correct user |
| Environment variables | Source .bashrc or set explicitly |

## Best Practices

1. **Log output** - Capture stdout/stderr
2. **Error handling** - Don't fail silently
3. **Overlap prevention** - Ensure tasks don't overlap
4. **Monitoring** - Alert if tasks fail
5. **Testing** - Test manually before scheduling
