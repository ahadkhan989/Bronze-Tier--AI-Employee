"""
WhatsApp Watcher Module

Monitors WhatsApp Web for new messages containing priority keywords.
Uses Playwright to automate WhatsApp Web and extract messages.

WARNING: Be aware of WhatsApp's Terms of Service when using automation.

Usage:
    python whatsapp_watcher.py /path/to/vault [--interval 30] [--setup-session]
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


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages with priority keywords.
    
    Attributes:
        session_path: Path to store browser session data
        keywords: List of keywords that trigger action files
        headless: Run browser in headless mode
    """
    
    WHATSAPP_URL = 'https://web.whatsapp.com'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 check_interval: int = 30, keywords: Optional[List[str]] = None,
                 headless: bool = True, max_chats: int = 10):
        """
        Initialize the WhatsApp watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            session_path: Path to store session data (default: vault/whatsapp_session)
            check_interval: How often to check for updates (in seconds)
            keywords: List of priority keywords
            headless: Run browser in headless mode
            max_chats: Maximum number of chats to check
        """
        super().__init__(vault_path, check_interval)
        
        # Set up paths
        self.session_path = Path(session_path or self.vault_path / 'whatsapp_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Processed messages tracking
        self.processed_ids_file = self.logs / 'whatsapp_processed_ids.json'
        self.processed_ids = self._load_processed_ids()
        
        # Keywords
        self.keywords = keywords or [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'pricing', 'meeting', 'deadline', 'important'
        ]
        
        self.headless = headless
        self.max_chats = max_chats
        self.last_check = None
        
    def _load_processed_ids(self) -> set:
        """Load previously processed message IDs."""
        if self.processed_ids_file.exists():
            try:
                data = json.loads(self.processed_ids_file.read_text())
                return set(data.get('ids', []))
            except:
                pass
        return set()
    
    def _save_processed_ids(self):
        """Save processed message IDs."""
        ids_list = list(self.processed_ids)[-500:]
        self.processed_ids_file.write_text(
            json.dumps({'ids': ids_list, 'updated': self.get_timestamp()})
        )
    
    def _setup_session(self):
        """Set up WhatsApp Web session (scan QR code)."""
        print("Starting WhatsApp Web session setup...")
        print("Please scan the QR code with your WhatsApp mobile app.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(self.WHATSAPP_URL)
            
            print("\nWaiting for QR code scan...")
            print("Press Ctrl+C to cancel")
            
            try:
                # Wait for main chat list to appear (indicates successful login)
                page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                print("\n✓ WhatsApp Web loaded successfully!")
                print("✓ Session saved. You can now run the watcher normally.")
            except PlaywrightTimeout:
                print("\n✗ Timeout waiting for QR code scan")
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
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check WhatsApp Web for new messages.
        
        Returns:
            List of new message dictionaries
        """
        new_messages = []
        
        if not self._check_session():
            self.logger.warning("No valid session found. Run with --setup-session first.")
            return []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    page.goto(self.WHATSAPP_URL, wait_until='domcontentloaded')
                    
                    # Wait for chat list
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                    except PlaywrightTimeout:
                        self.logger.warning("WhatsApp Web not loaded, session may be invalid")
                        browser.close()
                        return []
                    
                    # Get recent chats
                    chats = page.query_selector_all('[data-testid="chat-list"] > div')
                    
                    for i, chat in enumerate(chats[:self.max_chats]):
                        try:
                            # Extract chat info
                            name_elem = chat.query_selector('[data-testid="chat-info"]')
                            msg_elem = chat.query_selector('[data-testid="message"]')
                            
                            if not msg_elem:
                                continue
                            
                            chat_name = name_elem.inner_text() if name_elem else "Unknown"
                            message_text = msg_elem.inner_text()
                            
                            # Check for keywords
                            message_lower = message_text.lower()
                            if any(kw in message_lower for kw in self.keywords):
                                # Create unique ID
                                msg_id = f"{chat_name}_{message_text[:20]}_{time.time()}"
                                
                                if msg_id not in self.processed_ids:
                                    new_messages.append({
                                        'id': msg_id,
                                        'chat_name': chat_name,
                                        'message': message_text,
                                        'timestamp': datetime.now().isoformat(),
                                        'priority': 'high' if any(kw in message_lower for kw in ['urgent', 'asap', 'help']) else 'normal'
                                    })
                                    self.processed_ids.add(msg_id)
                                    
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue
                    
                    browser.close()
                    
                    # Save processed IDs
                    if new_messages:
                        self._save_processed_ids()
                        self.last_check = datetime.now()
                        
                except Exception as e:
                    self.logger.error(f"Error during WhatsApp check: {e}")
                    browser.close()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
            return []
        
        return new_messages
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create a .md action file for a WhatsApp message.
        
        Args:
            message: Message dictionary
            
        Returns:
            Path to the created file
        """
        try:
            chat_name = self.sanitize_filename(message['chat_name'])[:30]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"WHATSAPP_{timestamp}_{chat_name}.md"
            filepath = self.needs_action / filename
            
            content = f"""---
type: whatsapp
from: {message['chat_name']}
chat_name: {message['chat_name']}
received: {message['timestamp']}
priority: {message['priority']}
status: pending
message_id: {message['id']}
---

# WhatsApp Message: {message['chat_name']}

## Message Information
- **From:** {message['chat_name']}
- **Received:** {message['timestamp']}
- **Priority:** {message['priority'].title()}

---

## Message Content

{message['message']}

---

## Suggested Actions

- [ ] Reply on WhatsApp
- [ ] Take appropriate action
- [ ] Follow up if needed
- [ ] Archive after processing

---

## Processing Notes

*Add notes here during processing*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________

---
*Created by WhatsAppWatcher*
"""
            
            filepath.write_text(content, encoding='utf-8')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def run_once(self) -> int:
        """Run a single check and return number of messages found."""
        messages = self.check_for_updates()
        if messages:
            self.logger.info(f'Found {len(messages)} new message(s)')
            for msg in messages:
                filepath = self.create_action_file(msg)
                if filepath:
                    self.logger.info(f'Created: {filepath.name}')
        return len(messages)
    
    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Keywords: {self.keywords}')
        
        if not self._check_session():
            self.logger.error("No valid session found. Run with --setup-session first.")
            return
        
        try:
            while True:
                try:
                    messages = self.check_for_updates()
                    if messages:
                        self.logger.info(f'Found {len(messages)} new message(s)')
                        for msg in messages:
                            try:
                                filepath = self.create_action_file(msg)
                                if filepath:
                                    priority_str = f" [{msg['priority'].upper()}]"
                                    self.logger.info(f'Created action file: {filepath.name}{priority_str}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new messages')
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
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault directory')
    parser.add_argument('--session-path', '-s', help='Path to store session data')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--keywords', '-k', help='Comma-separated keywords to watch')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode (default: True)')
    parser.add_argument('--no-headless', action='store_false', dest='headless',
                       help='Run with visible browser')
    parser.add_argument('--max-chats', type=int, default=10,
                       help='Maximum chats to check (default: 10)')
    parser.add_argument('--setup-session', action='store_true',
                       help='Set up WhatsApp Web session')
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
    
    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval,
        keywords=args.keywords.split(',') if args.keywords else None,
        headless=args.headless,
        max_chats=args.max_chats
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
        print(f"Found {count} messages")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
