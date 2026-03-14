"""
Twitter (X) Poster Module

Posts content to Twitter:
- Single tweets (280 chars)
- Threaded tweets
- Tweets with images
- Scheduled tweets (via approval workflow)

Uses Tweepy library for Twitter API v2.

Usage:
    python twitter_poster.py /path/to/vault --content "Tweet content"
"""

import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent))

# Twitter API imports
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Note: Tweepy not installed.")
    print("Install with: pip install tweepy")


class TwitterPoster:
    """
    Posts content to Twitter.
    
    Attributes:
        vault_path: Path to Obsidian vault
        client: Tweepy client
        max_tweet_length: Maximum characters per tweet
    """

    MAX_TWEET_LENGTH = 280
    MAX_THREAD_LENGTH = 25  # Maximum tweets in a thread

    def __init__(self, vault_path: str):
        """
        Initialize the Twitter poster.

        Args:
            vault_path: Path to the Obsidian vault directory
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.client = None
        self.me = None

        # Load credentials
        self._load_credentials()
        self._connect()

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

    def _connect(self) -> bool:
        """Connect to Twitter API."""
        if not TWEEPY_AVAILABLE:
            print("Tweepy not installed")
            return False

        if not self.bearer_token:
            print("Twitter credentials not configured")
            return False

        try:
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
                print(f"Connected to Twitter as @{me.data.username}")
                self.me = me.data
                return True

            return False

        except Exception as e:
            print(f"Failed to connect to Twitter: {e}")
            return False

    def _split_into_tweets(self, content: str) -> List[str]:
        """
        Split content into tweets for a thread.

        Args:
            content: Full text content

        Returns:
            List of tweet texts
        """
        tweets = []
        
        # If content fits in one tweet
        if len(content) <= self.MAX_TWEET_LENGTH:
            return [content]

        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_tweet = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph fits in current tweet
            if len(current_tweet) + len(para) + 2 <= self.MAX_TWEET_LENGTH:
                if current_tweet:
                    current_tweet += "\n\n" + para
                else:
                    current_tweet = para
            else:
                # If current tweet has content, save it
                if current_tweet:
                    tweets.append(current_tweet)
                
                # If paragraph itself is too long, split it
                if len(para) > self.MAX_TWEET_LENGTH:
                    # Split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_tweet = ""
                    
                    for sentence in sentences:
                        if len(current_tweet) + len(sentence) + 1 <= self.MAX_TWEET_LENGTH:
                            if current_tweet:
                                current_tweet += " " + sentence
                            else:
                                current_tweet = sentence
                        else:
                            if current_tweet:
                                tweets.append(current_tweet)
                            current_tweet = sentence
                    
                    if current_tweet:
                        tweets.append(current_tweet)
                        current_tweet = ""
                else:
                    current_tweet = para

        # Add remaining content
        if current_tweet:
            tweets.append(current_tweet)

        # Limit thread length
        if len(tweets) > self.MAX_THREAD_LENGTH:
            tweets = tweets[:self.MAX_THREAD_LENGTH]
            tweets[-1] = tweets[-1][:self.MAX_TWEET_LENGTH - 3] + "..."

        return tweets

    def post_tweet(self, content: str, image_path: Optional[str] = None) -> Optional[str]:
        """
        Post a single tweet.

        Args:
            content: Tweet text
            image_path: Optional path to image

        Returns:
            Tweet ID if successful
        """
        if not self.client:
            print("Not connected to Twitter")
            return None

        if len(content) > self.MAX_TWEET_LENGTH:
            print(f"Content too long ({len(content)} > {self.MAX_TWEET_LENGTH} chars)")
            return None

        try:
            print(f"Posting tweet ({len(content)} chars)...")

            # Upload media if provided
            media_ids = []
            if image_path:
                print("Uploading image...")
                media = self.client.media_upload(filename=image_path)
                media_ids.append(media.media_id)
                print(f"Image uploaded: {media.media_id}")

            # Post tweet
            if media_ids:
                response = self.client.create_tweet(
                    text=content,
                    media_ids=media_ids
                )
            else:
                response = self.client.create_tweet(text=content)

            tweet_id = response.data['id']
            print(f"Tweet posted successfully: {tweet_id}")
            print(f"URL: https://twitter.com/{self.me.username}/status/{tweet_id}")
            
            return tweet_id

        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None

    def post_thread(self, content: str) -> List[str]:
        """
        Post a thread of tweets.

        Args:
            content: Full thread content

        Returns:
            List of tweet IDs
        """
        if not self.client:
            print("Not connected to Twitter")
            return []

        tweets = self._split_into_tweets(content)
        tweet_ids = []
        previous_tweet_id = None

        print(f"Posting thread of {len(tweets)} tweets...")

        for i, tweet_text in enumerate(tweets):
            try:
                # First tweet
                if i == 0:
                    tweet_id = self.post_tweet(tweet_text)
                else:
                    # Reply to previous tweet
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                    tweet_id = response.data['id']
                    print(f"Thread tweet {i+1}/{len(tweets)} posted: {tweet_id}")

                if tweet_id:
                    tweet_ids.append(tweet_id)
                    previous_tweet_id = tweet_id
                else:
                    print(f"Failed to post tweet {i+1}")
                    break

            except Exception as e:
                print(f"Error posting thread tweet {i+1}: {e}")
                break

        return tweet_ids

    def create_approval_request(self, content: str, hashtags: list = None,
                                image_path: str = None) -> Optional[Path]:
        """Create approval request for Twitter post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"TWITTER_POST_APPROVAL_{timestamp}.md"
        filepath = self.pending_approval / filename

        hashtags_str = ', '.join(hashtags) if hashtags else ''
        content_preview = content[:200] + '...' if len(content) > 200 else content

        # Split into tweets for preview
        tweets = self._split_into_tweets(content)
        tweets_preview = "\n\n".join([f"**Tweet {i+1}:** {t}" for i, t in enumerate(tweets)])

        approval_content = f"""---
type: approval_request
action: twitter_post
created: {datetime.now().isoformat()}
status: pending
hashtags: {hashtags_str}
image: {image_path or 'None'}
tweet_count: {len(tweets)}
---

# Twitter Post Approval Request

## Tweet Preview

{tweets_preview}

---

## Full Content

{content}

---

## Preview

{content_preview}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
"""

        filepath.write_text(approval_content, encoding='utf-8')
        return filepath

    def process_approved_posts(self) -> int:
        """Process approved Twitter posts."""
        if not self.pending_approval.exists():
            return 0

        if not self.client:
            if not self._connect():
                print("Cannot process posts - not connected to Twitter")
                return 0

        processed = 0
        for filepath in self.pending_approval.iterdir():
            if filepath.suffix != '.md' or 'TWITTER_POST_APPROVAL' not in filepath.name:
                continue

            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Extract post content
                if '## Full Content' in content:
                    post_content = content.split('## Full Content')[1].split('---')[0].strip()
                else:
                    continue

                # Extract image path
                image_match = re.search(r'image:\s*(.+)', content)
                image_path = image_match.group(1).strip() if image_match and image_match.group(1).strip() != 'None' else None

                print(f"Posting: {filepath.name}")
                
                # Post (could be thread)
                tweet_ids = self.post_thread(post_content)
                
                if tweet_ids:
                    print(f"Posted {len(tweet_ids)} tweet(s)")
                    
                    # Move to Done
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath.rename(self.done / f"{timestamp}_{filepath.name}")
                    processed += 1
                else:
                    print(f"Failed to post")
                    
            except Exception as e:
                print(f"Error: {e}")

        return processed


def parse_markdown_file(filepath: Path) -> dict:
    """Parse markdown file with frontmatter."""
    content = filepath.read_text(encoding='utf-8')
    result = {'content': content, 'hashtags': [], 'image': None}

    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            frontmatter = content[4:end].strip()
            
            # Extract hashtags
            hashtags_match = re.search(r'hashtags:\s*\[(.*?)\]', frontmatter)
            if hashtags_match:
                result['hashtags'] = [h.strip().strip('"\'') for h in hashtags_match.group(1).split(',')]
            
            # Extract image
            image_match = re.search(r'image:\s*(.+)', frontmatter)
            if image_match:
                result['image'] = image_match.group(1).strip()
            
            result['content'] = content[end+3:].strip()

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Twitter Poster')
    parser.add_argument('vault_path', help='Vault path')
    parser.add_argument('--content', '-c', help='Content to tweet')
    parser.add_argument('--file', '-f', help='Markdown file with content')
    parser.add_argument('--image', '-i', help='Image path')
    parser.add_argument('--require-approval', '-a', action='store_true')
    parser.add_argument('--process-approved', action='store_true')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Twitter connection')

    args = parser.parse_args()

    if not TWEEPY_AVAILABLE:
        print("Error: Tweepy not installed")
        print("Install with: pip install tweepy")
        sys.exit(1)

    poster = TwitterPoster(args.vault_path)

    if args.test_connection:
        if poster.client:
            print(f"✓ Connected as @{poster.me.username}")
            sys.exit(0)
        else:
            print("✗ Not connected")
            sys.exit(1)

    if args.process_approved:
        count = poster.process_approved_posts()
        print(f"Processed {count} posts")
        sys.exit(0)

    content = args.content
    image_path = args.image
    hashtags = []

    if args.file:
        parsed = parse_markdown_file(Path(args.file))
        content = parsed['content']
        hashtags = parsed['hashtags']
        image_path = image_path or parsed['image']

    if not content:
        print("Error: No content provided")
        sys.exit(1)

    # Add hashtags to content
    if hashtags:
        content += '\n\n' + ' '.join(hashtags)

    if args.require_approval:
        filepath = poster.create_approval_request(content, hashtags, image_path)
        if filepath:
            print(f"Approval created: {filepath}")
            print("Move to /Approved to post")
            sys.exit(0)
        sys.exit(1)

    # Post directly
    tweet_ids = poster.post_thread(content)
    if tweet_ids:
        print(f"Posted {len(tweet_ids)} tweet(s)")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
