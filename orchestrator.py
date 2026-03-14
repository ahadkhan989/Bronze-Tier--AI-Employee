"""
Orchestrator Module

Master process for the AI Employee system.
Coordinates watchers, processes approvals, and updates the dashboard.

Usage:
    python orchestrator.py /path/to/vault [--status] [--process-approvals]
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class DashboardStats:
    """Statistics for the dashboard."""
    pending_actions: int = 0
    tasks_in_progress: int = 0
    awaiting_approval: int = 0
    completed_today: int = 0
    completed_this_week: int = 0
    last_updated: str = ""


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Responsibilities:
    - Monitor folder states
    - Process approved actions
    - Update dashboard
    - Generate daily briefings
    - Manage logs
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault directory
        """
        self.vault_path = Path(vault_path)
        
        # Define folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        self.accounting = self.vault_path / 'Accounting'
        
        # Define files
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        self.goals = self.vault_path / 'Business_Goals.md'
        
        # Ensure all directories exist
        for folder in [self.inbox, self.needs_action, self.in_progress,
                       self.pending_approval, self.approved, self.rejected,
                       self.done, self.logs, self.briefings, self.accounting]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        self.log_entries: List[Dict] = []
        
    def log_action(self, action_type: str, actor: str, target: str,
                   parameters: Dict = None, approval_status: str = "auto",
                   result: str = "success"):
        """
        Log an action to the daily log file.
        
        Args:
            action_type: Type of action (e.g., 'file_move', 'approval_process')
            actor: Who/what performed the action
            target: What the action was performed on
            parameters: Additional parameters
            approval_status: approved/rejected/auto
            result: success/failure/pending
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters or {},
            "approval_status": approval_status,
            "result": result
        }
        self.log_entries.append(entry)
        
        # Write to log file
        try:
            if self.log_file.exists():
                logs = json.loads(self.log_file.read_text(encoding='utf-8'))
            else:
                logs = []
            logs.append(entry)
            self.log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"Error writing log: {e}")
    
    def count_files(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md'])
    
    def get_stats(self) -> DashboardStats:
        """Get current dashboard statistics."""
        today = datetime.now().strftime('%Y-%m-%d')
        week_start = datetime.now()
        
        stats = DashboardStats(
            pending_actions=self.count_files(self.needs_action),
            tasks_in_progress=self.count_files(self.in_progress),
            awaiting_approval=self.count_files(self.pending_approval),
            last_updated=self.get_timestamp()
        )
        
        # Count completed today and this week
        if self.done.exists():
            for f in self.done.iterdir():
                if f.suffix == '.md':
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime.strftime('%Y-%m-%d') == today:
                            stats.completed_today += 1
                        if mtime >= week_start:
                            stats.completed_this_week += 1
                    except:
                        pass
        
        return stats
    
    def get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        return datetime.now().isoformat()
    
    def update_dashboard(self):
        """Update the Dashboard.md file with current statistics."""
        stats = self.get_stats()

        # Read current dashboard (with UTF-8 encoding for emoji support)
        if self.dashboard.exists():
            content = self.dashboard.read_text(encoding='utf-8')
        else:
            content = "# 📊 AI Employee Dashboard\n\n"
        
        # Update the frontmatter and status table
        lines = content.split('\n')
        new_lines = []
        in_frontmatter = False
        frontmatter_done = False
        in_status_table = False
        status_table_done = False
        
        for line in lines:
            # Handle frontmatter
            if line.strip() == '---' and not frontmatter_done:
                if not in_frontmatter:
                    in_frontmatter = True
                    new_lines.append(line)
                else:
                    # Update last_updated
                    new_lines.append(f'last_updated: {stats.last_updated}')
                    new_lines.append(line)
                    frontmatter_done = True
                    in_frontmatter = False
                continue
            
            if in_frontmatter and not line.strip().startswith('last_updated'):
                new_lines.append(line)
            
            # Handle status table
            if '| **Pending Actions** |' in line:
                new_lines.append(f'| **Pending Actions** | {stats.pending_actions} | - |')
                status_table_done = True
                continue
            elif '| **Tasks in Progress** |' in line:
                new_lines.append(f'| **Tasks in Progress** | {stats.tasks_in_progress} | - |')
                continue
            elif '| **Awaiting Approval** |' in line:
                new_lines.append(f'| **Awaiting Approval** | {stats.awaiting_approval} | - |')
                continue
            elif '| **Completed Today** |' in line:
                new_lines.append(f'| **Completed Today** | {stats.completed_today} | - |')
                continue
            elif '| **Completed This Week** |' in line:
                new_lines.append(f'| **Completed This Week** | {stats.completed_this_week} | - |')
                continue
            
            new_lines.append(line)
        
        # Write updated content
        self.dashboard.write_text('\n'.join(new_lines), encoding='utf-8')
        
        self.log_action('dashboard_update', 'orchestrator', 'Dashboard.md',
                       asdict(stats), 'auto', 'success')
    
    def process_approvals(self):
        """
        Process files in the Approved folder.
        Moves them to Done and logs the action.
        
        Returns:
            Number of files processed
        """
        if not self.approved.exists():
            return 0

        processed = 0
        sent = 0
        failed = 0
        
        for filepath in self.approved.iterdir():
            if filepath.suffix != '.md':
                continue

            try:
                # Read the approval file
                content = filepath.read_text(encoding='utf-8')
                
                # Extract email details
                action_type = self.extract_field(content, 'action')
                to_email = self.extract_field(content, 'to')
                subject = self.extract_field(content, 'subject')
                
                print(f"\nProcessing: {filepath.name}")
                print(f"  Action: {action_type}")
                print(f"  To: {to_email}")
                print(f"  Subject: {subject}")
                
                # Execute the action based on type
                if action_type in ['send_email', 'send_invoice', 'accept_connection']:
                    # Extract the response body from the approval file
                    response_body = self.extract_response_body(content)
                    
                    print(f"  [INFO] Sending email via Gmail API...")
                    
                    # Try to send using email_sender
                    try:
                        from watchers.email_sender import EmailSender
                        
                        sender = EmailSender(
                            credentials_path='credentials.json',
                            token_path=str(self.vault_path / 'token.json')
                        )
                        
                        if sender.connect():
                            success = sender.send_email(
                                to=to_email,
                                subject=subject,
                                body=response_body
                            )
                            
                            if success:
                                print(f"  [OK] Email sent successfully!")
                            else:
                                print(f"  [ERROR] Failed to send email")
                                failed += 1
                                continue
                        else:
                            print(f"  [ERROR] Could not connect to Gmail API")
                            print(f"  [INFO] Run: python watchers/email_sender.py authenticate")
                    except ImportError:
                        print(f"  [INFO] Email sender not available")
                    except Exception as e:
                        print(f"  [ERROR] Email send error: {e}")
                    
                # Move to Done with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest = self.done / f"{timestamp}_{filepath.name}"
                shutil.move(str(filepath), str(dest))
                
                print(f"  [OK] Moved to Done/")
                
                self.log_action('approval_processed', 'orchestrator',
                               filepath.name, {
                                   'destination': str(dest),
                                   'action_type': action_type,
                                   'to': to_email
                               },
                               'approved', 'success')
                processed += 1
                sent += 1

            except Exception as e:
                print(f"  [ERROR] {e}")
                self.log_action('approval_process_error', 'orchestrator',
                               filepath.name, {'error': str(e)},
                               'approved', 'failure')
                failed += 1

        print(f"\n{'='*60}")
        print(f"SUMMARY: Processed={processed}, Sent={sent}, Failed={failed}")
        print(f"{'='*60}")
        return processed
    
    def extract_field(self, content: str, field: str) -> str:
        """Extract a field from markdown frontmatter."""
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue
            
            if in_frontmatter and line.startswith(f'{field}:'):
                return line.split(':', 1)[1].strip()
        
        return ''
    
    def extract_response_body(self, content: str) -> str:
        """Extract the response body from markdown content."""
        lines = content.split('\n')
        
        # Find the "## Draft Response" section
        in_draft = False
        body_lines = []
        
        for i, line in enumerate(lines):
            # Start capturing after "## Draft Response"
            if '## Draft Response' in line:
                in_draft = True
                continue
            
            # Stop capturing at next section
            if in_draft and line.strip().startswith('##'):
                break
            
            # Capture the draft content
            if in_draft:
                # Skip empty lines at the start
                if not body_lines and not line.strip():
                    continue
                body_lines.append(line)
        
        # Clean up and return
        result = '\n'.join(body_lines).strip()
        
        # Remove any remaining markdown artifacts
        if result.startswith('---'):
            end = result.find('---', 3)
            if end > 0:
                result = result[end+3:].strip()
        
        return result

    def process_rejections(self):
        """
        Process files in the Rejected folder.
        Logs the rejection and archives the file.
        
        Returns:
            Number of files processed
        """
        if not self.rejected.exists():
            return 0
        
        processed = 0
        for filepath in self.rejected.iterdir():
            if filepath.suffix != '.md':
                continue
            
            try:
                self.log_action('rejection_processed', 'orchestrator',
                               filepath.name, {}, 'rejected', 'archived')
                processed += 1
                
            except Exception as e:
                self.log_action('rejection_process_error', 'orchestrator',
                               filepath.name, {'error': str(e)},
                               'rejected', 'failure')
        
        return processed
    
    def get_pending_items(self) -> List[Dict]:
        """Get list of pending items with metadata."""
        items = []
        
        if not self.needs_action.exists():
            return items
        
        for filepath in self.needs_action.iterdir():
            if filepath.suffix != '.md':
                continue
            
            try:
                content = filepath.read_text()
                # Extract frontmatter
                if content.startswith('---'):
                    end = content.find('---', 3)
                    if end > 0:
                        frontmatter = content[4:end].strip()
                        items.append({
                            'filename': filepath.name,
                            'path': str(filepath),
                            'frontmatter': frontmatter,
                            'modified': datetime.fromtimestamp(
                                filepath.stat().st_mtime
                            ).isoformat()
                        })
            except Exception as e:
                self.logger.error(f'Error reading {filepath}: {e}')
        
        return items
    
    def generate_daily_briefing(self) -> Optional[Path]:
        """
        Generate a daily briefing file.
        
        Returns:
            Path to the created briefing file
        """
        stats = self.get_stats()
        today = datetime.now().strftime('%Y-%m-%d')
        briefing_file = self.briefings / f'{today}_Daily_Briefing.md'
        
        pending_items = self.get_pending_items()
        
        content = f"""---
generated: {self.get_timestamp()}
date: {today}
type: daily_briefing
---

# 📅 Daily Briefing - {today}

## Summary
- **Pending Actions:** {stats.pending_actions}
- **Tasks in Progress:** {stats.tasks_in_progress}
- **Awaiting Approval:** {stats.awaiting_approval}
- **Completed Today:** {stats.completed_today}

---

## Pending Items Requiring Attention

"""
        
        if pending_items:
            for item in pending_items[:10]:  # Limit to 10 items
                content += f"### {item['filename']}\n"
                content += f"- **Modified:** {item['modified']}\n"
                content += f"- **Path:** `{item['path']}`\n\n"
        else:
            content += "*No pending items*\n\n"
        
        content += f"""---
## Suggested Next Steps

1. Review pending items in /Needs_Action
2. Process any approvals in /Pending_Approval
3. Run Claude Code on high-priority items

## Quick Commands

```bash
# Process pending items
claude "Process all files in /Needs_Action"

# Check status
python orchestrator.py --status
```

---
*Generated by AI Employee Orchestrator*
"""
        
        briefing_file.write_text(content, encoding='utf-8')
        
        self.log_action('briefing_generated', 'orchestrator',
                       str(briefing_file), {'date': today},
                       'auto', 'success')
        
        return briefing_file
    
    def status_report(self) -> str:
        """Generate a status report for CLI output."""
        stats = self.get_stats()

        report = f"""
╔══════════════════════════════════════════════════════╗
║         AI Employee System Status                    ║
╠══════════════════════════════════════════════════════╣
║  Vault: {str(self.vault_path)[:45]:<45} ║
╠══════════════════════════════════════════════════════╣
║  Pending Actions:     {stats.pending_actions:<5}                        ║
║  Tasks in Progress:   {stats.tasks_in_progress:<5}                        ║
║  Awaiting Approval:   {stats.awaiting_approval:<5}                        ║
║  Completed Today:     {stats.completed_today:<5}                        ║
║  Completed This Week: {stats.completed_this_week:<5}                        ║
╠══════════════════════════════════════════════════════╣
║  Last Updated: {stats.last_updated[:19]:<32} ║
╚══════════════════════════════════════════════════════╝
"""
        return report

    def generate_weekly_briefing(self) -> Optional[Path]:
        """
        Generate a weekly CEO briefing file with Odoo data.

        Returns:
            Path to the created briefing file
        """
        from datetime import timedelta
        
        stats = self.get_stats()
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        briefing_file = self.briefings / f'{week_start.strftime("%Y-%m-%d")}_Weekly_CEO_Briefing.md'

        # Get Odoo dashboard summary if available
        odoo_summary = self._get_odoo_summary()

        content = f"""---
generated: {self.get_timestamp()}
period: {week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}
type: weekly_ceo_briefing
---

# 📊 Weekly CEO Briefing

## Week of {week_start.strftime('%B %d, %Y')}

---

## Executive Summary

"""
        if odoo_summary.get('success'):
            revenue = odoo_summary.get('total_revenue', 0)
            content += f"This week's revenue: **${revenue:,.2f}** from Odoo ERP. "
        
        if stats.completed_this_week > 0:
            content += f"Completed **{stats.completed_this_week}** tasks. "
        
        if stats.pending_actions > 0:
            content += f"\n\n⚠️ **{stats.pending_actions}** items require attention."

        content += f"""

---

## 📈 Key Metrics

### Task Completion
- **Completed This Week:** {stats.completed_this_week}
- **Pending Actions:** {stats.pending_actions}
- **Awaiting Approval:** {stats.awaiting_approval}

### 💰 Odoo ERP Summary
- **Total Revenue:** ${odoo_summary.get('total_revenue', 0):,.2f}
- **Total Invoices:** {odoo_summary.get('posted_invoices', 0)}
- **Total Customers:** {odoo_summary.get('total_customers', 0)}
- **Draft Invoices:** {odoo_summary.get('draft_invoices', 0)}

---

## 📋 Proactive Suggestions

1. **Review Pending Actions:** {stats.pending_actions} items need attention
2. **Process Approvals:** {stats.awaiting_approval} items awaiting decision
3. **Odoo Follow-ups:** Check for overdue invoices

---

*Generated by AI Employee Orchestrator (Gold Tier)*
"""

        briefing_file.write_text(content, encoding='utf-8')

        self.log_action('briefing_generated', 'orchestrator',
                       str(briefing_file), {'type': 'weekly'},
                       'auto', 'success')

        return briefing_file

    def _get_odoo_summary(self) -> Dict:
        """Get summary from Odoo ERP."""
        try:
            from watchers.odoo_sync_watcher import OdooSyncWatcher
            
            watcher = OdooSyncWatcher(str(self.vault_path))
            if watcher.odoo:
                data = watcher._get_dashboard_data()
                data['success'] = True
                return data
        except Exception as e:
            self.logger.debug(f"Error getting Odoo summary: {e}")
        
        return {'success': False}


def main():
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', nargs='?', help='Path to the Obsidian vault')
    parser.add_argument('--status', '-s', action='store_true',
                       help='Show system status')
    parser.add_argument('--process-approvals', '-p', action='store_true',
                       help='Process approved files')
    parser.add_argument('--briefing', '-b', action='store_true',
                       help='Generate daily briefing')
    parser.add_argument('--weekly-briefing', '-w', action='store_true',
                       help='Generate weekly CEO briefing')
    parser.add_argument('--update-dashboard', '-u', action='store_true',
                       help='Update dashboard')

    args = parser.parse_args()

    # Get vault path from argument or environment
    vault_path = args.vault_path
    if not vault_path:
        # Try to find vault in current directory
        current_vault = Path.cwd() / 'AI_Employee_Vault'
        if current_vault.exists():
            vault_path = str(current_vault)
        else:
            print("Error: Please specify vault path or run from vault directory")
            sys.exit(1)

    orchestrator = Orchestrator(vault_path)

    if args.status:
        print(orchestrator.status_report())

    if args.process_approvals:
        count = orchestrator.process_approvals()
        print(f"Processed {count} approved file(s)")

    if args.briefing:
        briefing = orchestrator.generate_daily_briefing()
        print(f"Generated daily briefing: {briefing}")

    if args.weekly_briefing:
        briefing = orchestrator.generate_weekly_briefing()
        print(f"Generated weekly briefing: {briefing}")

    if args.update_dashboard or not any([args.status, args.process_approvals, args.briefing, args.weekly_briefing]):
        orchestrator.update_dashboard()
        print("Dashboard updated")
        print(orchestrator.status_report())


if __name__ == '__main__':
    main()
