"""
Twitter (X) Watcher Module

Monitors Twitter for:
- Mentions (@yourhandle)
- Direct messages
- Keyword mentions
- Engagement metrics (likes, retweets)

Uses Tweepy library for Twitter API v2.

Usage:
    python twitter_watcher.py /path/to/vault [--interval 300]
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Twitter API imports
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Note: Tweepy not installed.")
    print("Install with: pip install tweepy")


class TwitterWatcher(BaseWatcher):
    """
    Watches Twitter for mentions, DMs, and engagement.

    Attributes:
        api: Tweepy API client
        bearer_token: Twitter API bearer token
        processed_ids: Set of processed tweet/DM IDs
        keywords: Keywords to monitor
    """

    def __init__(self, vault_path: str, check_interval: int = 300,
                 keywords: Optional[List[str]] = None,
                 max_results: int = 10):
        """
        Initialize the Twitter watcher.

        Args:
            vault_path: Path to the Obsidian vault directory
            check_interval: How often to check for updates
            keywords: Keywords to monitor for mentions
            max_results: Maximum results to fetch per check
        """
        super().__init__(vault_path, check_interval)

        # Processed items tracking
        self.processed_ids_file = self.logs / 'twitter_processed_ids.json'
        self.processed_ids = self._load_processed_ids()

        # Keywords to monitor
        self.keywords = keywords or ['your_brand', 'your_product']
        self.max_results = max_results

        # Priority keywords
        self.priority_keywords = [
            'urgent', 'asap', 'help', 'issue', 'problem',
            'complaint', 'question', 'invoice', 'payment'
        ]

        # Twitter API client
        self.api = None
        self.bearer_token = None
        self.client = None

        # Load credentials from environment or .env
        self._load_credentials()

    def _load_credentials(self):
        """Load Twitter API credentials from environment."""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')

        if not self.bearer_token:
            self.logger.warning("TWITTER_BEARER_TOKEN not set in environment")

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

    def _connect(self) -> bool:
        """Connect to Twitter API."""
        if not TWEEPY_AVAILABLE:
            self.logger.error("Tweepy not installed")
            return False

        if not self.bearer_token:
            self.logger.error("Twitter credentials not configured")
            return False

        try:
            # Initialize client with bearer token (for v2 API)
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )

            # Test connection
            me = self.client.get_me()
            if me and me.data:
                self.logger.info(f"Connected to Twitter as @{me.data.username}")
                self.me = me.data
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to connect to Twitter: {e}")
            return False

    def _check_mentions(self) -> List[Dict]:
        """Check for new mentions."""
        mentions = []

        if not self.client:
            return mentions

        try:
            # Get mentions
            mentions_response = self.client.get_users_mentions(
                id=self.me.id,
                max_results=self.max_results,
                tweet_fields=['created_at', 'author_id', 'text', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if mentions_response.data:
                for mention in mentions_response.data:
                    if mention.id not in self.processed_ids:
                        # Get author info
                        author = None
                        if mentions_response.includes and 'users' in mentions_response.includes:
                            for user in mentions_response.includes['users']:
                                if user.id == mention.author_id:
                                    author = user
                                    break

                        # Check priority
                        text_lower = mention.text.lower()
                        priority = 'high' if any(kw in text_lower for kw in self.priority_keywords) else 'normal'

                        mentions.append({
                            'id': mention.id,
                            'type': 'mention',
                            'platform': 'twitter',
                            'from_username': author.username if author else 'Unknown',
                            'from_name': author.name if author else 'Unknown',
                            'text': mention.text,
                            'created_at': mention.created_at.isoformat() if mention.created_at else self.get_timestamp(),
                            'metrics': mention.public_metrics if hasattr(mention, 'public_metrics') else {},
                            'priority': priority
                        })
                        self.processed_ids.add(mention.id)

        except Exception as e:
            self.logger.error(f"Error checking mentions: {e}")

        return mentions

    def _check_keyword_mentions(self) -> List[Dict]:
        """Check for keyword mentions."""
        tweets = []

        if not self.client:
            return tweets

        for keyword in self.keywords:
            try:
                # Search for keyword
                search_response = self.client.search_recent_tweets(
                    query=f"{keyword} -is:retweet",
                    max_results=self.max_results,
                    tweet_fields=['created_at', 'author_id', 'text', 'public_metrics'],
                    expansions=['author_id'],
                    user_fields=['username', 'name']
                )

                if search_response.data:
                    for tweet in search_response.data:
                        if tweet.id not in self.processed_ids:
                            # Get author info
                            author = None
                            if search_response.includes and 'users' in search_response.includes:
                                for user in search_response.includes['users']:
                                    if user.id == tweet.author_id:
                                        author = user
                                        break

                            text_lower = tweet.text.lower()
                            priority = 'high' if any(kw in text_lower for kw in self.priority_keywords) else 'normal'

                            tweets.append({
                                'id': tweet.id,
                                'type': 'keyword_mention',
                                'platform': 'twitter',
                                'keyword': keyword,
                                'from_username': author.username if author else 'Unknown',
                                'from_name': author.name if author else 'Unknown',
                                'text': tweet.text,
                                'created_at': tweet.created_at.isoformat() if tweet.created_at else self.get_timestamp(),
                                'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                                'priority': priority
                            })
                            self.processed_ids.add(tweet.id)

            except Exception as e:
                self.logger.error(f"Error searching for '{keyword}': {e}")

        return tweets

    def check_for_updates(self) -> List[Dict]:
        """
        Check Twitter for new activity.

        Returns:
            List of new activity dictionaries
        """
        if not self.client:
            if not self._connect():
                return []

        all_items = []

        # Check mentions
        mentions = self._check_mentions()
        all_items.extend(mentions)
        if mentions:
            self.logger.info(f"Found {len(mentions)} new mentions")

        # Check keyword mentions
        keyword_tweets = self._check_keyword_mentions()
        all_items.extend(keyword_tweets)
        if keyword_tweets:
            self.logger.info(f"Found {len(keyword_tweets)} keyword mentions")

        # Save processed IDs
        if all_items:
            self._save_processed_ids()

        return all_items

    def create_action_file(self, item: Dict) -> Optional[Path]:
        """
        Create a .md action file for a Twitter activity.

        Args:
            item: Activity dictionary

        Returns:
            Path to the created file
        """
        try:
            item_type = item['type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            username = self.sanitize_filename(item.get('from_username', 'Unknown'))[:30]

            # Create filename
            if item_type == 'mention':
                filename = f"TWITTER_MENTION_{timestamp}_{username}.md"
            elif item_type == 'keyword_mention':
                keyword = item.get('keyword', 'unknown')
                filename = f"TWITTER_KEYWORD_{keyword.upper()}_{timestamp}_{username}.md"
            else:
                filename = f"TWITTER_{item_type.upper()}_{timestamp}.md"

            filepath = self.needs_action / filename

            metrics = item.get('metrics', {})
            metrics_str = f"- **Likes:** {metrics.get('like_count', 0)}\n- **Retweets:** {metrics.get('retweet_count', 0)}\n- **Replies:** {metrics.get('reply_count', 0)}" if metrics else "*Not available*"

            content = f"""---
type: social_media
platform: twitter
notification_type: {item_type}
from: @{item.get('from_username', 'Unknown')}
received: {item['created_at']}
priority: {item['priority']}
status: pending
tweet_id: {item['id']}
---

# Twitter {item_type.title()}: @{item.get('from_username', 'Unknown')}

## Details
- **Platform:** Twitter
- **Type:** {item_type.title()}
- **From:** @{item.get('from_username', 'Unknown')} ({item.get('from_name', 'Unknown')})
- **Received:** {item['created_at']}
- **Priority:** {item['priority'].title()}
- **Tweet ID:** {item['id']}

---

## Tweet Content

{item['text']}

---

## Engagement Metrics

{metrics_str}

---

## Suggested Actions

- [ ] Review tweet
- [ ] Draft response
- [ ] Create approval request
- [ ] Respond via Twitter
- [ ] Archive after processing

---

## Processing Notes

*Add notes here during processing*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________

---
*Created by TwitterWatcher*
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
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Keywords: {self.keywords}')

        if not self._connect():
            self.logger.error("Failed to connect to Twitter API. Check credentials.")
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
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new activity')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self._connect()  # Try to reconnect

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Twitter Watcher')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--keywords', '-k', help='Comma-separated keywords to monitor')
    parser.add_argument('--max-results', '-m', type=int, default=10,
                       help='Maximum results per check')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Twitter API connection')

    args = parser.parse_args()

    if not TWEEPY_AVAILABLE:
        print("Error: Tweepy not installed")
        print("Install with: pip install tweepy")
        sys.exit(1)

    watcher = TwitterWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval,
        keywords=args.keywords.split(',') if args.keywords else None,
        max_results=args.max_results
    )

    if args.test_connection:
        print("Testing Twitter connection...")
        if watcher._connect():
            print("✓ Connected to Twitter API")
            print(f"  Account: @{watcher.me.username}")
        else:
            print("✗ Failed to connect to Twitter API")
        sys.exit(0 if watcher.client else 1)
    elif args.once:
        count = watcher.run_once()
        print(f"Found {count} items")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
