"""
Gold Tier Verification Script

Tests all Gold Tier components to ensure they are properly installed and configured.

Usage:
    python verify_gold_tier.py
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, List


class GoldTierVerifier:
    """Verifies Gold Tier installation and configuration."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.vault_path = self.project_root / 'AI_Employee_Vault'
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def check(self, name: str, condition: bool, error_msg: str = ""):
        """Check a condition and print result."""
        if condition:
            print(f"  [OK] {name}")
            self.passed += 1
        else:
            print(f"  [FAIL] {name}")
            if error_msg:
                print(f"    Error: {error_msg}")
            self.failed += 1

    def warn(self, name: str, message: str):
        """Print a warning."""
        print(f"  [WARN] {name}: {message}")
        self.warnings += 1

    def verify_python_packages(self):
        """Verify required Python packages are installed."""
        print("\n" + "=" * 60)
        print("1. Verifying Python Packages")
        print("=" * 60)

        packages = {
            'playwright': 'Browser automation (Facebook, LinkedIn)',
            'tweepy': 'Twitter API',
            'google-api-python-client': 'Gmail API',
            'python-dotenv': 'Environment variables',
            'schedule': 'Task scheduling',
            'watchdog': 'File system monitoring',
        }

        for package, description in packages.items():
            try:
                __import__(package.replace('-', '_'))
                self.check(f"{package} ({description})", True)
            except ImportError:
                self.check(f"{package} ({description})", False, 
                          f"Install with: pip install {package}")

    def verify_docker_setup(self):
        """Verify Docker and Docker Compose are available."""
        print("\n" + "=" * 60)
        print("2. Verifying Docker Setup")
        print("=" * 60)

        # Check Docker
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.check("Docker installed", True)
                print(f"    Version: {result.stdout.strip()}")
            else:
                self.check("Docker installed", False)
        except FileNotFoundError:
            self.check("Docker installed", False, "Docker not found")
        except subprocess.TimeoutExpired:
            self.warn("Docker check", "Timeout checking Docker version")

        # Check Docker Compose
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.check("Docker Compose installed", True)
                print(f"    Version: {result.stdout.strip()}")
            else:
                self.check("Docker Compose installed", False)
        except FileNotFoundError:
            # Try new docker compose command
            try:
                result = subprocess.run(
                    ['docker', 'compose', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.check("Docker Compose installed", True)
                    print(f"    Version: {result.stdout.strip()}")
                else:
                    self.check("Docker Compose installed", False)
            except:
                self.check("Docker Compose installed", False, "Docker Compose not found")

        # Check docker-compose.yml
        compose_file = self.project_root / 'docker-compose.yml'
        self.check("docker-compose.yml exists", compose_file.exists(),
                  "Required for Odoo deployment")

    def verify_vault_structure(self):
        """Verify Obsidian vault structure."""
        print("\n" + "=" * 60)
        print("3. Verifying Vault Structure")
        print("=" * 60)

        required_folders = [
            'Inbox',
            'Needs_Action',
            'In_Progress',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'Done',
            'Logs',
            'Briefings',
            'Plans',
            'Accounting',
            'Invoices',
        ]

        for folder in required_folders:
            folder_path = self.vault_path / folder
            exists = folder_path.exists() and folder_path.is_dir()
            self.check(f"{folder}/", exists,
                      f"Run: mkdir {folder_path}")

        # Check key files
        required_files = [
            'Dashboard.md',
            'Company_Handbook.md',
            'Business_Goals.md',
        ]

        for file in required_files:
            file_path = self.vault_path / file
            self.check(f"{file}", file_path.exists(),
                      f"Create file: {file_path}")

    def verify_watchers(self):
        """Verify watcher scripts exist."""
        print("\n" + "=" * 60)
        print("4. Verifying Watcher Scripts")
        print("=" * 60)

        watchers_path = self.project_root / 'watchers'

        watchers = {
            'base_watcher.py': 'Base class for all watchers',
            'filesystem_watcher.py': 'File drop monitoring (Bronze)',
            'gmail_watcher.py': 'Gmail monitoring (Silver)',
            'linkedin_watcher.py': 'LinkedIn monitoring (Silver)',
            'linkedin_poster.py': 'LinkedIn posting (Silver)',
            'facebook_watcher.py': 'Facebook/Instagram monitoring (Gold)',
            'facebook_poster.py': 'Facebook/Instagram posting (Gold)',
            'twitter_watcher.py': 'Twitter monitoring (Gold)',
            'twitter_poster.py': 'Twitter posting (Gold)',
            'odoo_sync_watcher.py': 'Odoo ERP sync (Gold)',
        }

        for watcher, description in watchers.items():
            watcher_path = watchers_path / watcher
            self.check(f"{watcher} ({description})", watcher_path.exists(),
                      "Gold Tier watcher missing")

    def verify_mcp_servers(self):
        """Verify MCP servers exist."""
        print("\n" + "=" * 60)
        print("5. Verifying MCP Servers")
        print("=" * 60)

        mcp_path = self.project_root / 'mcp_servers'

        # Check directory exists
        self.check("mcp_servers/ directory", mcp_path.exists(),
                  "Create directory for MCP servers")

        if mcp_path.exists():
            # Check Odoo MCP server
            odoo_mcp = mcp_path / 'odoo_mcp_server.py'
            self.check("odoo_mcp_server.py (Odoo ERP integration)", 
                      odoo_mcp.exists(),
                      "Gold Tier MCP server missing")

    def verify_gold_tier_files(self):
        """Verify Gold Tier specific files."""
        print("\n" + "=" * 60)
        print("6. Verifying Gold Tier Files")
        print("=" * 60)

        files = {
            'GOLD_TIER.md': 'Gold Tier documentation',
            'ODOO_SETUP.md': 'Odoo setup guide',
            'docker-compose.yml': 'Docker Compose for Odoo',
            '.env.example': 'Environment variables template',
            'requirements.txt': 'Python dependencies',
            'ralph_wiggum_loop.py': 'Ralph Wiggum persistence loop',
        }

        for file, description in files.items():
            file_path = self.project_root / file
            self.check(f"{file} ({description})", file_path.exists(),
                      "Gold Tier file missing")

    def verify_environment(self):
        """Verify environment configuration."""
        print("\n" + "=" * 60)
        print("7. Verifying Environment Configuration")
        print("=" * 60)

        # Check .env file
        env_file = self.project_root / '.env'
        if env_file.exists():
            self.check(".env file exists", True)
            
            # Check for required variables
            content = env_file.read_text()
            required_vars = [
                'ODOO_URL',
                'ODOO_DB',
                'ODOO_USERNAME',
                'ODOO_PASSWORD',
            ]
            
            for var in required_vars:
                exists = var in content
                self.check(f"  {var} configured", exists,
                          "Required for Odoo integration")
        else:
            self.check(".env file exists", False,
                      "Copy .env.example to .env and configure")
            print(f"    Run: cp .env.example .env")

    def verify_claude_code(self):
        """Verify Claude Code is available."""
        print("\n" + "=" * 60)
        print("8. Verifying Claude Code")
        print("=" * 60)

        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.check("Claude Code installed", True)
                print(f"    Version: {result.stdout.strip()}")
            else:
                self.check("Claude Code installed", False,
                          "Claude Code returned error")
        except FileNotFoundError:
            self.check("Claude Code installed", False,
                      "Install Claude Code for reasoning engine")
        except subprocess.TimeoutExpired:
            self.warn("Claude Code check", "Timeout checking version")

    def run_all_checks(self):
        """Run all verification checks."""
        print("\n" + "=" * 70)
        print("           GOLD TIER VERIFICATION")
        print("=" * 70)
        print(f"\nProject Root: {self.project_root}")
        print(f"Vault Path: {self.vault_path}")

        self.verify_python_packages()
        self.verify_docker_setup()
        self.verify_vault_structure()
        self.verify_watchers()
        self.verify_mcp_servers()
        self.verify_gold_tier_files()
        self.verify_environment()
        self.verify_claude_code()

        # Summary
        print("\n" + "=" * 70)
        print("           VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"  [OK] Passed:   {self.passed}")
        print(f"  [FAIL] Failed:   {self.failed}")
        print(f"  [WARN] Warnings: {self.warnings}")
        print()

        if self.failed == 0:
            print("[SUCCESS] All Gold Tier components verified!")
            print("\nNext steps:")
            print("1. Configure .env file with your credentials")
            print("2. Start Odoo: docker-compose up -d odoo postgres")
            print("3. Authenticate services (Gmail, LinkedIn, Facebook, Twitter)")
            print("4. Start watchers and Ralph Wiggum loop")
            print("\nSee GOLD_TIER.md for detailed instructions.")
            return 0
        else:
            print(f"[WARN] {self.failed} issues found. Please fix them before proceeding.")
            print("\nSee GOLD_TIER.md for setup instructions.")
            return 1


def main():
    """Main entry point."""
    verifier = GoldTierVerifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
