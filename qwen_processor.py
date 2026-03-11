"""
Qwen Code Processor Helper

Provides pre-built prompts and workflows for processing AI Employee tasks with Qwen Code.
"""

import subprocess
import sys
from pathlib import Path


def run_qwen_command(vault_path: str, prompt: str):
    """Run a Qwen Code command in the specified directory."""
    try:
        result = subprocess.run(
            ["qwen", prompt],
            cwd=vault_path,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: 'qwen' command not found.")
        print("Make sure Qwen Code is installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Error running Qwen Code: {e}")
        return False


def process_needs_action(vault_path: str):
    """Process all files in Needs_Action folder."""
    prompt = """Review all files in the Needs_Action folder. For each file:
1. Read the content and understand what action is needed
2. Create a Plan.md in the Plans folder with steps to handle it (if complex)
3. Take appropriate action or create approval requests
4. Update Dashboard.md with a summary
5. Move processed files to Done folder when complete"""
    
    print(f"Processing Needs_Action folder in {vault_path}...")
    return run_qwen_command(vault_path, prompt)


def generate_plan(vault_path: str):
    """Generate plans for complex tasks."""
    prompt = """Review the Needs_Action folder and identify items that require multiple steps.
For each complex item:
1. Create a detailed Plan.md in the Plans folder
2. Break down into actionable checkboxes
3. Identify any approvals needed
4. Estimate priority and dependencies"""
    
    print(f"Generating plans in {vault_path}...")
    return run_qwen_command(vault_path, prompt)


def daily_review(vault_path: str):
    """Review today's completed tasks and update dashboard."""
    prompt = """Review today's completed tasks in the Done folder and:
1. Summarize what was accomplished today
2. Update Dashboard.md with key metrics
3. Note any patterns or recurring items
4. Suggest priorities for tomorrow"""
    
    print(f"Running daily review in {vault_path}...")
    return run_qwen_command(vault_path, prompt)


def check_approvals(vault_path: str):
    """Check Pending_Approval folder and summarize."""
    prompt = """Check the Pending_Approval folder and:
1. List all items awaiting approval
2. Summarize what each approval request is for
3. Highlight any urgent or time-sensitive items
4. Create a summary in Dashboard.md"""
    
    print(f"Checking approvals in {vault_path}...")
    return run_qwen_command(vault_path, prompt)


def full_audit(vault_path: str):
    """Run a comprehensive audit of the entire system."""
    prompt = """Perform a comprehensive audit of the AI Employee system:
1. Review all folders (Inbox, Needs_Action, In_Progress, Pending_Approval, Approved, Done)
2. Check for any orphaned or stuck items
3. Verify Dashboard.md is up to date
4. Review Logs for any errors or patterns
5. Generate a system health report in Briefings/
6. Suggest improvements or cleanup actions"""
    
    print(f"Running full audit in {vault_path}...")
    return run_qwen_command(vault_path, prompt)


def show_help():
    """Display available commands."""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║           Qwen Code Processor - Available Commands           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  process       Process all files in Needs_Action folder      ║
║  plan          Generate plans for complex tasks              ║
║  review        Run daily review and update dashboard         ║
║  approvals     Check and summarize pending approvals         ║
║  audit         Run comprehensive system audit                ║
║  custom        Run with a custom prompt                      ║
║                                                              ║
║  Usage:                                                      ║
║    python qwen_processor.py <command> [vault_path]           ║
║                                                              ║
║  Examples:                                                   ║
║    python qwen_processor.py process                          ║
║    python qwen_processor.py audit AI_Employee_Vault          ║
║    python qwen_processor.py custom "Your prompt here"        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(help_text)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Get vault path
    if len(sys.argv) >= 3:
        vault_path = sys.argv[2]
    else:
        # Try default location
        default_vault = Path.cwd() / 'AI_Employee_Vault'
        if default_vault.exists():
            vault_path = str(default_vault)
        else:
            print("Error: Please specify vault path")
            print("Usage: python qwen_processor.py <command> [vault_path]")
            sys.exit(1)
    
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Execute command
    commands = {
        'process': process_needs_action,
        'plan': generate_plan,
        'review': daily_review,
        'approvals': check_approvals,
        'audit': full_audit,
        'help': show_help,
    }
    
    if command == 'custom':
        if len(sys.argv) < 4:
            print("Error: Custom prompt required")
            print("Usage: python qwen_processor.py custom \"Your prompt here\"")
            sys.exit(1)
        prompt = ' '.join(sys.argv[3:])
        success = run_qwen_command(vault_path, prompt)
    elif command in commands:
        success = commands[command](vault_path)
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
