"""
Scheduler Module

Run AI Employee tasks on a schedule using Python.
Alternative to cron/Task Scheduler for cross-platform scheduling.

Usage:
    python scheduler.py  # Run continuously
    python scheduler.py --once  # Run scheduled tasks once (for testing)
"""

import schedule
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# Configuration
VAULT = "AI_Employee_Vault"
PROJECT = Path(__file__).parent


def run_command(cmd: str, description: str = ""):
    """Run a shell command and log the result."""
    desc = f" ({description})" if description else ""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {cmd}{desc}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=PROJECT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed: {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def daily_briefing():
    """Generate daily briefing at 8:00 AM."""
    return run_command(
        f"python orchestrator.py {VAULT} --briefing",
        "Daily Briefing"
    )


def process_approvals():
    """Process approved files every hour."""
    return run_command(
        f"python orchestrator.py {VAULT} --process-approvals",
        "Process Approvals"
    )


def update_dashboard():
    """Update dashboard every 15 minutes."""
    return run_command(
        f"python orchestrator.py {VAULT} --update-dashboard",
        "Update Dashboard"
    )


def weekly_audit():
    """Run weekly audit every Monday at 9:00 AM."""
    return run_command(
        f"python qwen_processor.py audit {VAULT}",
        "Weekly Audit"
    )


def check_watchers():
    """Check if watchers are running."""
    return run_command(
        f"python orchestrator.py {VAULT} --status",
        "Check Status"
    )


def setup_schedule():
    """Configure all scheduled tasks."""
    
    # Daily briefing at 8:00 AM
    schedule.every().day.at("08:00").do(daily_briefing)
    
    # Process approvals every hour
    schedule.every().hour.do(process_approvals)
    
    # Update dashboard every 15 minutes
    schedule.every(15).minutes.do(update_dashboard)
    
    # Weekly audit every Monday at 9:00 AM
    schedule.every().monday.at("09:00").do(weekly_audit)
    
    # Check watchers every 30 minutes
    schedule.every(30).minutes.do(check_watchers)
    
    print("Schedule configured:")
    print("  - Daily briefing: 8:00 AM")
    print("  - Process approvals: Every hour")
    print("  - Update dashboard: Every 15 minutes")
    print("  - Weekly audit: Monday 9:00 AM")
    print("  - Check watchers: Every 30 minutes")


def run_pending():
    """Run any pending scheduled tasks."""
    schedule.run_pending()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Scheduler')
    parser.add_argument('--once', action='store_true',
                       help='Run scheduled tasks once (for testing)')
    parser.add_argument('--list', action='store_true',
                       help='List scheduled tasks')
    
    args = parser.parse_args()
    
    if args.list:
        setup_schedule()
        print("\nNext scheduled runs:")
        for job in schedule.get_jobs():
            print(f"  {job}")
        return
    
    if args.once:
        print("Running all scheduled tasks once for testing...\n")
        daily_briefing()
        process_approvals()
        update_dashboard()
        print("\nTest run complete.")
        return
    
    # Start scheduler
    print("=" * 50)
    print("AI Employee Scheduler")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {PROJECT}")
    print(f"Vault: {VAULT}")
    print("=" * 50)
    
    setup_schedule()
    print("\nScheduler running. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")


if __name__ == '__main__':
    main()
