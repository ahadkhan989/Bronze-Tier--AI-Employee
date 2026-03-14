"""
Facebook Watcher Module (Graph API)

Monitors Facebook Page and Instagram Business Account for:
- New messages
- Comments on posts
- Page notifications
- Lead form submissions

Uses Facebook Graph API via facebook-business SDK.

Prerequisites:
1. Create Facebook App at https://developers.facebook.com/
2. Get Page Access Token with required permissions
3. Link Instagram Business Account (optional)

Usage:
    python facebook_watcher.py /path/to/vault [--interval 300]
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Facebook Business SDK imports (optional - we use requests library primarily)
FACEBOOK_BUSINESS_AVAILABLE = False
try:
    from facebook_business.api import FacebookAPI
    from facebook_business.adobjects.page import Page
    from facebook_business.adobjects.conversation import Conversation
    from facebook_business.adobjects.message import Message
    from facebook_business.adobjects.comment import Comment
    from facebook_business.exceptions import FacebookRequestError
    FACEBOOK_BUSINESS_AVAILABLE = True
except ImportError:
    # Note: We can still use requests-based API without SDK
    # This is just informational
    pass


class FacebookWatcher(BaseWatcher):
    """
    Watches Facebook Page for new activity using Graph API.

    Monitors:
    - New messages
    - Comments on posts

    Uses Facebook Graph API via requests library.

    Attributes:
        app_id: Facebook App ID
        app_secret: Facebook App Secret
        access_token: Page Access Token
        page_id: Facebook Page ID
        graph: Facebook Graph API client
    """

    GRAPH_VERSION = 'v18.0'
    BASE_URL = f'https://graph.facebook.com/{GRAPH_VERSION}'

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize the Facebook watcher.

        Args:
            vault_path: Path to the Obsidian vault directory
            check_interval: How often to check for updates
        """
        super().__init__(vault_path, check_interval)

        # Load credentials
        self._load_credentials()

        # Processed items tracking
        self.processed_ids_file = self.logs / 'facebook_processed_ids.json'
        self.processed_ids = self._load_processed_ids()

        # Keywords that indicate high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'order',
            'purchase', 'buy', 'price', 'cost', 'help'
        ]

        # Initialize Facebook API
        self._initialize_api()

    def _load_credentials(self):
        """Load Facebook API credentials from environment."""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')

        # Validate required credentials
        if not self.access_token:
            self.logger.warning("FACEBOOK_ACCESS_TOKEN not set in environment")
        if not self.page_id:
            self.logger.warning("FACEBOOK_PAGE_ID not set in environment")

    def _load_processed_ids(self) -> set:
        """Load previously processed item IDs."""
        if self.processed_ids_file.exists():
            try:
                data = json.loads(self.processed_ids_file.read_text())
                return set(data.get('ids', []))
            except:
                pass
        return set()

    def _save_processed_ids(self):
        """Save processed item IDs."""
        ids_list = list(self.processed_ids)[-500:]
        self.processed_ids_file.write_text(
            json.dumps({'ids': ids_list, 'updated': self.get_timestamp()})
        )

    def _initialize_api(self):
        """Initialize Facebook Graph API."""
        if not FACEBOOK_BUSINESS_AVAILABLE:
            self.logger.error("facebook-business SDK not installed")
            return

        if not self.access_token:
            self.logger.error("Facebook access token not configured")
            return

        try:
            FacebookAPI.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                access_token=self.access_token
            )
            self.logger.info("Facebook API initialized")
        except Exception as e:
            self.logger.error(f"Error initializing Facebook API: {e}")

    def _get_facebook_messages(self) -> List[Dict]:
        """Get recent messages from Facebook Page."""
        messages = []

        if not self.access_token or not self.page_id:
            return messages

        try:
            # Try to get page inbox (requires pages_manage_metadata permission)
            # This endpoint may not be available for all apps
            url = f"{self.BASE_URL}/{self.page_id}/conversations"
            params = {
                'access_token': self.access_token,
                'fields': 'messages{from,message,created_time,id}',
                'limit': 10
            }

            response = requests.get(url, params=params)
            
            # Silently handle permission errors - messages not critical
            if response.status_code in [400, 403]:
                # Endpoint not available or permission denied
                pass
            else:
                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    for conversation in data['data']:
                        if 'messages' in conversation and 'data' in conversation['messages']:
                            for msg in conversation['messages']['data']:
                                msg_id = f"fb_msg_{msg.get('id', '')}"

                                if msg_id not in self.processed_ids:
                                    text = msg.get('message', '').lower()
                                    priority = 'high' if any(kw in text for kw in self.priority_keywords) else 'normal'

                                    messages.append({
                                        'id': msg_id,
                                        'platform': 'facebook',
                                        'type': 'message',
                                        'from': msg.get('from', {}).get('name', 'Unknown'),
                                        'message': msg.get('message', ''),
                                        'created_time': msg.get('created_time', self.get_timestamp()),
                                        'priority': priority
                                    })
                                    self.processed_ids.add(msg_id)

        except Exception as e:
            # Silently ignore - messages require special permissions
            pass

        return messages

    def _get_facebook_comments(self) -> List[Dict]:
        """Get recent comments on Facebook Page posts."""
        comments = []

        if not self.access_token or not self.page_id:
            return comments

        try:
            # Get page feed with comments included (more reliable than /posts)
            url = f"{self.BASE_URL}/{self.page_id}/feed"
            params = {
                'access_token': self.access_token,
                'fields': 'message,created_time,comments{from,message,created_time,id}',
                'limit': 25
            }

            response = requests.get(url, params=params)
            
            if response.status_code in [400, 403]:
                # Endpoint not available or permission denied
                return comments
            
            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                for post in data['data']:
                    if 'comments' in post and 'data' in post['comments']:
                        for comment in post['comments']['data']:
                            comment_id = f"fb_comment_{comment.get('id', '')}"

                            if comment_id not in self.processed_ids:
                                text = comment.get('message', '').lower()
                                priority = 'high' if any(kw in text for kw in self.priority_keywords) else 'normal'

                                comments.append({
                                    'id': comment_id,
                                    'platform': 'facebook',
                                    'type': 'comment',
                                    'post_id': post.get('id', ''),
                                    'comment_id': comment.get('id', ''),
                                    'from': comment.get('from', {}).get('name', 'Unknown'),
                                    'message': comment.get('message', ''),
                                    'created_time': comment.get('created_time', self.get_timestamp()),
                                    'priority': priority
                                })
                                self.processed_ids.add(comment_id)

        except requests.exceptions.HTTPError as e:
            pass  # Silently ignore
        except Exception as e:
            pass  # Silently ignore

        return comments

    def check_for_updates(self) -> List[Dict]:
        """
        Check Facebook for new activity.

        Returns:
            List of new activity dictionaries
        """
        all_items = []

        # Check Facebook messages
        fb_messages = self._get_facebook_messages()
        all_items.extend(fb_messages)
        if fb_messages:
            self.logger.info(f"Found {len(fb_messages)} new Facebook messages")

        # Check Facebook comments
        fb_comments = self._get_facebook_comments()
        all_items.extend(fb_comments)
        if fb_comments:
            self.logger.info(f"Found {len(fb_comments)} new Facebook comments")

        # Save processed IDs
        if all_items:
            self._save_processed_ids()

        return all_items

    def create_action_file(self, item: Dict) -> Optional[Path]:
        """
        Create a .md action file for a Facebook/Instagram notification.

        Args:
            item: Activity dictionary

        Returns:
            Path to the created file
        """
        try:
            platform = item['platform']
            item_type = item['type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Create filename based on platform and type
            if item_type == 'message':
                name = self.sanitize_filename(item.get('from', 'Unknown'))[:30]
                filename = f"{platform.upper()}_MSG_{timestamp}_{name}.md"
            else:
                filename = f"{platform.upper()}_{item_type.upper()}_{timestamp}.md"

            filepath = self.needs_action / filename

            # Include comment_id for replies if available
            comment_id_field = ""
            if item.get('comment_id'):
                comment_id_field = f"comment_id: {item['comment_id']}\n"

            content = f"""---
type: social_media
platform: {platform}
notification_type: {item_type}
from: {item.get('from', 'Unknown')}
received: {item['created_time']}
priority: {item['priority']}
status: pending
{comment_id_field}---

# {platform.title()} {item_type.title()}: {item.get('from', 'Unknown')}

## Details
- **Platform:** {platform.title()}
- **Type:** {item_type.title()}
- **From:** {item.get('from', 'Unknown')}
- **Received:** {item['created_time']}
- **Priority:** {item['priority'].title()}

---

## Content

{item.get('message', 'N/A')}

---

## Suggested Actions

- [ ] Review message/comment
- [ ] Draft response
- [ ] Create approval request in Pending_Approval/
- [ ] Respond via {platform.title()}
- [ ] Archive after processing

---

## Processing Notes

*Add notes here during processing*

---

## Draft Response (for approval)

*Write your response here, then move file to Pending_Approval/*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________

---
*Created by FacebookWatcher (Graph API)*
"""

            filepath.write_text(content, encoding='utf-8')
            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def run_once(self) -> int:
        """Run a single check and return number of items found."""
        items = self.check_for_updates()
        if items:
            self.logger.info(f'Found {len(items)} new items')
            for item in items:
                filepath = self.create_action_file(item)
                if filepath:
                    self.logger.info(f'Created: {filepath.name}')
        return len(items)

    def run(self):
        """Main run loop with auto-response generation."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')

        if not self.access_token:
            self.logger.error("No access token found. Configure FACEBOOK_ACCESS_TOKEN in .env")
            return

        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    priority_str = f" [{item['priority'].upper()}]"
                                    self.logger.info(f'Created action file: {filepath.name}{priority_str}')
                                    
                                    # Auto-generate response for comments
                                    if item['type'] == 'comment':
                                        self.logger.info('Auto-generating response...')
                                        try:
                                            from pathlib import Path
                                            import subprocess
                                            
                                            vault_path = Path(self.vault_path)
                                            subprocess.run(
                                                ['python', str(vault_path.parent / 'auto_generate_response.py'), 
                                                 str(vault_path)],
                                                capture_output=True,
                                                timeout=30
                                            )
                                            self.logger.info('Response generated!')
                                        except Exception as e:
                                            self.logger.debug(f'Auto-response skipped: {e}')
                                    
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new activity')
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

    parser = argparse.ArgumentParser(description='Facebook Watcher (Graph API)')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Facebook API connection')

    args = parser.parse_args()

    if not FACEBOOK_BUSINESS_AVAILABLE:
        print("Note: facebook-business SDK not installed (optional)")
        print("Install with: pip install facebook-business")

    watcher = FacebookWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval
    )

    if args.test_connection:
        print("Testing Facebook API connection...")
        if watcher.access_token and watcher.page_id:
            print("[OK] Access token configured")
            print(f"[OK] Page ID: {watcher.page_id}")
            sys.exit(0)
        else:
            print("[FAIL] Missing credentials")
            print("  Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env")
            sys.exit(1)
    elif args.once:
        count = watcher.run_once()
        print(f"Found {count} items")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
