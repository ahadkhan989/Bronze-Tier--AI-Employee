"""
Ralph Wiggum Persistence Loop

Keeps Claude Code working autonomously until tasks are complete.
Implements the "Ralph Wiggum" pattern from the hackathon blueprint.

How it works:
1. Creates a state file with the task
2. Runs Claude with the prompt
3. Checks if task is complete (file in /Done or completion promise)
4. If not complete, re-injects prompt with previous output
5. Repeats until complete or max iterations reached

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    python ralph_wiggum_loop.py /path/to/vault "Your task description"
"""

import sys
import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class RalphWiggumLoop:
    """
    Ralph Wiggum persistence loop for autonomous task completion.
    
    Attributes:
        vault_path: Path to Obsidian vault
        task: Task description
        max_iterations: Maximum iterations before stopping
        completion_promise: String to look for indicating completion
        logs_path: Path to log directory
        state_file: Current state file path
    """

    def __init__(self, vault_path: str, task: str,
                 max_iterations: int = 10,
                 completion_promise: str = None,
                 verbose: bool = False):
        """
        Initialize Ralph Wiggum loop.

        Args:
            vault_path: Path to the Obsidian vault directory
            task: Task description for Claude
            max_iterations: Maximum iterations (default: 10)
            completion_promise: String indicating task completion
            verbose: Enable verbose logging
        """
        self.vault_path = Path(vault_path)
        self.task = task
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise or "TASK_COMPLETE"
        self.verbose = verbose

        # Paths
        self.logs = self.vault_path / 'Logs'
        self.done = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'

        for folder in [self.logs, self.done, self.in_progress]:
            folder.mkdir(parents=True, exist_ok=True)

        # State file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.state_file = self.logs / f"ralph_wiggum_state_{timestamp}.json"
        self.log_file = self.logs / f"ralph_wiggum_{datetime.now().strftime('%Y-%m-%d')}.log"

        # State
        self.iteration = 0
        self.start_time = datetime.now()
        self.last_output = ""
        self.task_complete = False

    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)

        # Append to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Error writing to log: {e}")

    def save_state(self):
        """Save current state to file."""
        state = {
            'task': self.task,
            'iteration': self.iteration,
            'max_iterations': self.max_iterations,
            'start_time': self.start_time.isoformat(),
            'last_output_length': len(self.last_output),
            'task_complete': self.task_complete,
            'vault_path': str(self.vault_path),
            'state_file': str(self.state_file)
        }

        try:
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception as e:
            self.log(f"Error saving state: {e}", "ERROR")

    def load_state(self, state_file: Path) -> bool:
        """Load state from file."""
        try:
            state = json.loads(state_file.read_text(encoding='utf-8'))
            self.task = state.get('task', self.task)
            self.iteration = state.get('iteration', 0)
            self.max_iterations = state.get('max_iterations', self.max_iterations)
            self.task_complete = state.get('task_complete', False)
            return True
        except Exception as e:
            self.log(f"Error loading state: {e}", "ERROR")
            return False

    def check_task_complete(self) -> bool:
        """
        Check if task is complete.
        
        Strategies:
        1. Look for completion promise in output
        2. Check if files moved to /Done
        3. Check if /Needs_Action is empty (if task was to process it)
        
        Returns:
            True if task appears complete
        """
        # Check for completion promise in last output
        if self.completion_promise and self.completion_promise in self.last_output:
            self.log(f"Completion promise found: {self.completion_promise}")
            return True

        # Check if all files processed (if task involves Needs_Action)
        if 'Needs_Action' in self.task and self.needs_action.exists():
            pending_files = list(self.needs_action.glob('*.md'))
            if len(pending_files) == 0:
                self.log("All files in Needs_Action processed")
                return True

        # Check if files moved to Done
        if self.done.exists():
            recent_done = [
                f for f in self.done.glob('*.md')
                if datetime.fromtimestamp(f.stat().st_mtime) > self.start_time
            ]
            if recent_done:
                self.log(f"{len(recent_done)} files moved to Done since start")

        return False

    def build_prompt(self) -> str:
        """
        Build the prompt for Claude.
        
        Returns:
            Prompt string
        """
        if self.iteration == 0:
            # First iteration - use original task
            prompt = f"""{self.task}

IMPORTANT: When you have completed this task, output the exact phrase: {self.completion_promise}

Work on this task step by step. If you need to process files, move them to the Done folder when complete."""
        else:
            # Subsequent iterations - include previous output
            prompt = f"""Continue working on this task. Previous iteration output:

{self.last_output[-5000:]}  # Last 5000 chars

IMPORTANT: 
- Continue from where you left off
- Don't repeat work already done
- When complete, output: {self.completion_promise}

Current task: {self.task}"""

        return prompt

    def run_claude(self, prompt: str) -> str:
        """
        Run Claude Code with the given prompt.
        
        Args:
            prompt: Prompt to send to Claude
            
        Returns:
            Claude's output
        """
        self.log(f"Running Claude (iteration {self.iteration + 1}/{self.max_iterations})")

        try:
            # Change to vault directory
            original_dir = os.getcwd()
            os.chdir(str(self.vault_path))

            # Build Claude command
            # Note: This assumes 'claude' command is available
            cmd = ['claude', prompt]

            # Run Claude
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per iteration
            )

            output = result.stdout
            if result.stderr:
                self.log(f"Claude stderr: {result.stderr}", "WARN")

            os.chdir(original_dir)
            return output

        except subprocess.TimeoutExpired:
            self.log("Claude timed out (10 minutes)", "ERROR")
            os.chdir(original_dir)
            return "ERROR: Timeout expired"
        except FileNotFoundError:
            self.log("'claude' command not found. Make sure Claude Code is installed.", "ERROR")
            os.chdir(original_dir)
            return "ERROR: Claude not found"
        except Exception as e:
            self.log(f"Error running Claude: {e}", "ERROR")
            os.chdir(original_dir)
            return f"ERROR: {e}"

    def run(self):
        """Run the Ralph Wiggum loop."""
        self.log("=" * 60)
        self.log("Ralph Wiggum Persistence Loop - Starting")
        self.log("=" * 60)
        self.log(f"Task: {self.task}")
        self.log(f"Max iterations: {self.max_iterations}")
        self.log(f"Completion promise: {self.completion_promise}")
        self.log(f"Vault: {self.vault_path}")

        # Save initial state
        self.save_state()

        while self.iteration < self.max_iterations and not self.task_complete:
            self.iteration += 1
            self.log(f"\n{'='*40}")
            self.log(f"ITERATION {self.iteration}/{self.max_iterations}")
            self.log(f"{'='*40}")

            # Build prompt
            prompt = self.build_prompt()

            # Run Claude
            output = self.run_claude(prompt)
            self.last_output = output

            # Check if task is complete
            if self.check_task_complete():
                self.task_complete = True
                self.log("\n✓ TASK COMPLETE!")
                break

            # Check for errors
            if output.startswith("ERROR:"):
                self.log(f"Error in Claude execution: {output}", "ERROR")
                # Continue anyway - might be transient

            # Save state
            self.save_state()

            # Brief pause between iterations
            time.sleep(2)

        # Final state
        self.save_state()

        # Summary
        elapsed = datetime.now() - self.start_time
        self.log("\n" + "=" * 60)
        self.log("Ralph Wiggum Loop - Summary")
        self.log("=" * 60)
        self.log(f"Task: {self.task}")
        self.log(f"Iterations: {self.iteration}")
        self.log(f"Completed: {self.task_complete}")
        self.log(f"Elapsed time: {elapsed}")
        self.log(f"State file: {self.state_file}")
        self.log(f"Log file: {self.log_file}")
        self.log("=" * 60)

        return self.task_complete


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Persistence Loop')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('task', help='Task description for Claude')
    parser.add_argument('--max-iterations', '-m', type=int, default=10,
                       help='Maximum iterations (default: 10)')
    parser.add_argument('--completion-promise', '-p', default='TASK_COMPLETE',
                       help='String indicating task completion')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--resume', '-r', help='Resume from state file')

    args = parser.parse_args()

    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)

    # Create loop
    if args.resume:
        # Resume from state file
        loop = RalphWiggumLoop(str(vault_path), "")
        if loop.load_state(Path(args.resume)):
            print(f"Resuming from state file: {args.resume}")
            print(f"Task: {loop.task}")
            print(f"Iteration: {loop.iteration}")
            loop.run()
        else:
            print("Failed to load state file")
            sys.exit(1)
    else:
        # New loop
        loop = RalphWiggumLoop(
            str(vault_path),
            args.task,
            max_iterations=args.max_iterations,
            completion_promise=args.completion_promise,
            verbose=args.verbose
        )
        success = loop.run()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
