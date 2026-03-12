"""
LinkedIn Watcher Module

Monitors LinkedIn for notifications, messages, and engagement.
Uses Playwright to automate LinkedIn Web.

WARNING: Be aware of LinkedIn's Terms of Service when using automation.

Usage:
    python linkedin_watcher.py /path/to/vault [--interval 300] [--setup-session]
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Note: Playwright not installed.")
    print("Install with: pip install playwright && playwright install chromium")


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for new notifications and messages.
    
    Attributes:
        session_path: Path to store browser session data
        notification_types: Types of notifications to track
        headless: Run browser in headless mode
    """
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    NOTIFICATIONS_URL = 'https://www.linkedin.com/notifications/'
    MESSAGES_URL = 'https://www.linkedin.com/messaging/'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 check_interval: int = 300, notification_types: Optional[List[str]] = None,
                 headless: bool = True):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            session_path: Path to store session data (default: vault/linkedin_session)
            check_interval: How often to check for updates (in seconds)
            notification_types: Types of notifications to track
            headless: Run browser in headless mode
        """
        super().__init__(vault_path, check_interval)
        
        # Set up paths
        self.session_path = Path(session_path or self.vault_path / 'linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Processed notifications tracking
        self.processed_ids_file = self.logs / 'linkedin_processed_ids.json'
        self.processed_ids = self._load_processed_ids()
        
        # Notification types
        self.notification_types = notification_types or [
            'messages', 'connections', 'engagement'
        ]
        
        self.headless = headless
        self.last_check = None
        
    def _load_processed_ids(self) -> set:
        """Load previously processed notification IDs."""
        if self.processed_ids_file.exists():
            try:
                data = json.loads(self.processed_ids_file.read_text())
                return set(data.get('ids', []))
            except:
                pass
        return set()
    
    def _save_processed_ids(self):
        """Save processed notification IDs."""
        ids_list = list(self.processed_ids)[-500:]
        self.processed_ids_file.write_text(
            json.dumps({'ids': ids_list, 'updated': self.get_timestamp()})
        )
    
    def _setup_session(self):
        """Set up LinkedIn session (login)."""
        print("Starting LinkedIn session setup...")
        print("Please log in to your LinkedIn account.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(self.LINKEDIN_URL)
            
            print("\nWaiting for login...")
            print("Press Ctrl+C to cancel")
            
            try:
                # Wait for navigation to feed page (indicates successful login)
                page.wait_for_url('**/feed/**', timeout=120000)
                print("\n[OK] LinkedIn logged in successfully!")
                print("[OK] Session saved. You can now run the watcher normally.")
                
                # Give it a moment to save cookies
                time.sleep(2)
                
            except PlaywrightTimeout:
                print("\n✗ Timeout waiting for login")
            finally:
                browser.close()
        
        return True
    
    def _check_session(self) -> bool:
        """Check if session is valid."""
        if not self.session_path.exists():
            return False
        
        # Check if session directory has content
        if not any(self.session_path.iterdir()):
            return False
        
        return True
    
    def _clear_session(self):
        """Clear stored session."""
        import shutil
        if self.session_path.exists():
            shutil.rmtree(self.session_path)
            print("Session cleared. Run with --setup-session to re-authenticate.")
    
    def _check_notifications(self, page) -> List[Dict]:
        """Check for new notifications."""
        notifications = []
        
        try:
            # Navigate to notifications page
            page.goto(self.NOTIFICATIONS_URL, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)  # Wait for content to load
            
            # Find notification items
            notification_items = page.query_selector_all('li div.notification-item')
            
            for item in notification_items[:10]:  # Limit to 10
                try:
                    # Extract notification data
                    title_elem = item.query_selector('.notification-item__title')
                    subtitle_elem = item.query_selector('.notification-item__subtitle')
                    time_elem = item.query_selector('.notification-item__time')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    subtitle = subtitle_elem.inner_text().strip() if subtitle_elem else ''
                    time_ago = time_elem.inner_text().strip() if time_elem else ''
                    
                    # Determine type
                    notif_type = 'other'
                    if 'message' in title.lower():
                        notif_type = 'messages'
                    elif 'connection' in title.lower() or 'connect' in title.lower():
                        notif_type = 'connections'
                    elif 'liked' in title.lower() or 'commented' in title.lower():
                        notif_type = 'engagement'
                    
                    # Skip if not in our watch list
                    if notif_type not in self.notification_types:
                        continue
                    
                    # Create unique ID
                    notif_id = f"{notif_type}_{title[:30]}_{time_ago}"
                    
                    if notif_id not in self.processed_ids:
                        notifications.append({
                            'id': notif_id,
                            'type': notif_type,
                            'title': title,
                            'subtitle': subtitle,
                            'time_ago': time_ago,
                            'timestamp': datetime.now().isoformat(),
                            'priority': 'high' if notif_type == 'messages' else 'normal'
                        })
                        self.processed_ids.add(notif_id)
                        
                except Exception as e:
                    self.logger.debug(f"Error processing notification: {e}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error checking notifications: {e}")
        
        return notifications
    
    def _check_messages(self, page) -> List[Dict]:
        """Check for new messages."""
        messages = []
        
        try:
            # Navigate to messaging page
            page.goto(self.MESSAGES_URL, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # Find message threads with unread
            message_threads = page.query_selector_all('div.msg-s-message-list__item')
            
            for thread in message_threads[:10]:
                try:
                    # Check if unread
                    if 'unread' not in str(thread.get_attribute('class')):
                        continue
                    
                    # Extract message data
                    name_elem = thread.query_selector('.msg-s-message-list-item__name')
                    preview_elem = thread.query_selector('.msg-s-message-list-item__preview')
                    time_elem = thread.query_selector('.msg-s-message-list-item__time')
                    
                    name = name_elem.inner_text().strip() if name_elem else 'Unknown'
                    preview = preview_elem.inner_text().strip() if preview_elem else ''
                    time_ago = time_elem.inner_text().strip() if time_elem else ''
                    
                    # Create unique ID
                    msg_id = f"message_{name}_{time_ago}"
                    
                    if msg_id not in self.processed_ids:
                        messages.append({
                            'id': msg_id,
                            'type': 'messages',
                            'from': name,
                            'preview': preview,
                            'time_ago': time_ago,
                            'timestamp': datetime.now().isoformat(),
                            'priority': 'high'
                        })
                        self.processed_ids.add(msg_id)
                        
                except Exception as e:
                    self.logger.debug(f"Error processing message: {e}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error checking messages: {e}")
        
        return messages
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check LinkedIn for new notifications and messages.
        
        Returns:
            List of new notification dictionaries
        """
        if not self._check_session():
            self.logger.warning("No valid session found. Run with --setup-session first.")
            return []
        
        all_items = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    # Check notifications
                    if 'notifications' in self.notification_types or 'connections' in self.notification_types or 'engagement' in self.notification_types:
                        notifications = self._check_notifications(page)
                        all_items.extend(notifications)
                        self.logger.info(f"Found {len(notifications)} new notifications")
                    
                    # Check messages
                    if 'messages' in self.notification_types:
                        messages = self._check_messages(page)
                        all_items.extend(messages)
                        self.logger.info(f"Found {len(messages)} new messages")
                    
                    browser.close()
                    
                    # Save processed IDs
                    if all_items:
                        self._save_processed_ids()
                        self.last_check = datetime.now()
                        
                except Exception as e:
                    self.logger.error(f"Error during LinkedIn check: {e}")
                    browser.close()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
            return []
        
        return all_items
    
    def create_action_file(self, notification: Dict) -> Optional[Path]:
        """
        Create a .md action file for a LinkedIn notification.
        
        Args:
            notification: Notification dictionary
            
        Returns:
            Path to the created file
        """
        try:
            notif_type = notification['type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create filename based on type
            if notif_type == 'messages':
                name = self.sanitize_filename(notification.get('from', 'Unknown'))[:30]
                filename = f"LINKEDIN_MSG_{timestamp}_{name}.md"
            else:
                filename = f"LINKEDIN_{notif_type.upper()}_{timestamp}.md"
            
            filepath = self.needs_action / filename
            
            content = f"""---
type: linkedin
notification_type: {notification['type']}
from: {notification.get('from', notification.get('title', 'Unknown'))}
received: {notification['timestamp']}
priority: {notification['priority']}
status: pending
---

# LinkedIn Notification: {notification['type'].title()}

## Details
- **Type:** {notification['type'].title()}
- **From:** {notification.get('from', notification.get('title', 'Unknown'))}
- **Received:** {notification['timestamp']}
- **Priority:** {notification['priority'].title()}

---

## Content

**Title:** {notification['title']}

**Details:** {notification.get('subtitle', notification.get('preview', 'N/A'))}

**Time:** {notification.get('time_ago', 'N/A')}

---

## Suggested Actions

- [ ] Review notification
- [ ] Reply/Respond on LinkedIn
- [ ] Take appropriate action
- [ ] Archive after processing

---

## Processing Notes

*Add notes here during processing*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________

---
*Created by LinkedInWatcher*
"""
            
            filepath.write_text(content, encoding='utf-8')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def run_once(self) -> int:
        """Run a single check and return number of notifications found."""
        notifications = self.check_for_updates()
        if notifications:
            self.logger.info(f'Found {len(notifications)} new notification(s)')
            for notif in notifications:
                filepath = self.create_action_file(notif)
                if filepath:
                    self.logger.info(f'Created: {filepath.name}')
        return len(notifications)
    
    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Notification types: {self.notification_types}')
        
        if not self._check_session():
            self.logger.error("No valid session found. Run with --setup-session first.")
            return
        
        try:
            while True:
                try:
                    notifications = self.check_for_updates()
                    if notifications:
                        self.logger.info(f'Found {len(notifications)} new notification(s)')
                        for notif in notifications:
                            try:
                                filepath = self.create_action_file(notif)
                                if filepath:
                                    priority_str = f" [{notif['priority'].upper()}]"
                                    self.logger.info(f'Created action file: {filepath.name}{priority_str}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new notifications')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault directory')
    parser.add_argument('--session-path', '-s', help='Path to store session data')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--types', '-t', help='Comma-separated notification types')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode (default: True)')
    parser.add_argument('--no-headless', action='store_false', dest='headless',
                       help='Run with visible browser')
    parser.add_argument('--setup-session', action='store_true',
                       help='Set up LinkedIn session')
    parser.add_argument('--check-session', action='store_true',
                       help='Check if session is valid')
    parser.add_argument('--clear-session', action='store_true',
                       help='Clear stored session')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    
    args = parser.parse_args()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Error: Playwright not installed")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    watcher = LinkedInWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval,
        notification_types=args.types.split(',') if args.types else None,
        headless=args.headless
    )
    
    if args.setup_session:
        watcher._setup_session()
    elif args.check_session:
        valid = watcher._check_session()
        print(f"Session valid: {valid}")
        sys.exit(0 if valid else 1)
    elif args.clear_session:
        watcher._clear_session()
    elif args.once:
        count = watcher.run_once()
        print(f"Found {count} notifications")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
