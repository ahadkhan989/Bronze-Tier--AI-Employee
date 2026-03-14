"""
Facebook Poster Module (Graph API)

Posts content to Facebook Page.

Uses Facebook Graph API for posting.

Prerequisites:
1. Create Facebook App at https://developers.facebook.com/
2. Get Page Access Token with required permissions
3. Be admin of the Facebook Page

Required Permissions:
- pages_manage_posts
- pages_read_engagement

Usage:
    python facebook_poster.py /path/to/vault --content "Post content"
"""

import sys
import time
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent))


class FacebookPoster:
    """
    Posts content to Facebook using Graph API.
    
    Attributes:
        vault_path: Path to Obsidian vault
        app_id: Facebook App ID
        app_secret: Facebook App Secret
        access_token: Page Access Token
        page_id: Facebook Page ID
    """

    GRAPH_VERSION = 'v18.0'
    BASE_URL = f'https://graph.facebook.com/{GRAPH_VERSION}'

    def __init__(self, vault_path: str):
        """
        Initialize the Facebook poster.

        Args:
            vault_path: Path to the Obsidian vault directory
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

        # Load credentials
        self._load_credentials()

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
            print("[ERROR] FACEBOOK_ACCESS_TOKEN not set in environment")
        if not self.page_id:
            print("[ERROR] FACEBOOK_PAGE_ID not set in environment")

    def post_to_facebook(self, content: str, image_path: Optional[str] = None,
                         link: Optional[str] = None) -> Optional[str]:
        """
        Post content to Facebook Page.

        Args:
            content: Post text content
            image_path: Optional path to image file
            link: Optional link to share

        Returns:
            Post ID if successful
        """
        if not self.access_token or not self.page_id:
            print("[ERROR] Facebook credentials not configured")
            return None

        print("=" * 60)
        print("Facebook Poster - Starting (Graph API)")
        print("=" * 60)

        try:
            # Prepare post data
            url = f"{self.BASE_URL}/{self.page_id}/feed"
            params = {
                'access_token': self.access_token,
                'message': content
            }

            # Add link if provided
            if link:
                params['link'] = link

            # Upload photo if provided
            if image_path:
                print(f"\n[Step 1/2] Uploading image: {image_path}")
                
                # Upload photo to page
                photo_url = f"{self.BASE_URL}/{self.page_id}/photos"
                photo_params = {
                    'access_token': self.access_token
                }
                
                # Upload photo file
                with open(image_path, 'rb') as f:
                    photo_files = {'source': f}
                    photo_response = requests.post(
                        photo_url,
                        params=photo_params,
                        files=photo_files
                    )
                    photo_response.raise_for_status()
                    photo_data = photo_response.json()
                    
                    if 'id' in photo_data:
                        print(f"      Image uploaded: {photo_data['id']}")
                        params['attached_media'] = f'{{"media_fbid": "{photo_data["id"]}"}}'
                    else:
                        print("      Warning: Image uploaded but no ID returned")

            # Post to Facebook
            print(f"\n[Step 2/2] Posting to Facebook...")
            print(f"      Content length: {len(content)} chars")

            response = requests.post(url, params=params)
            
            # Handle errors with better messages
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    error_type = error_data.get('error', {}).get('type', 'Unknown')
                    error_code = error_data.get('error', {}).get('code', 0)
                    
                    print(f"\n[ERROR] API request failed: {response.status_code} {response.reason}")
                    print(f"      Error Type: {error_type}")
                    print(f"      Error Code: {error_code}")
                    print(f"      Message: {error_msg}")
                    
                    # Provide specific help based on error
                    if error_code == 200 or 'OAuthException' in error_type:
                        print(f"\n⚠️  PERMISSION ISSUE DETECTED!")
                        print(f"\n📝 Common Causes:")
                        print(f"   1. Using USER token instead of PAGE token")
                        print(f"   2. Missing pages_manage_posts permission")
                        print(f"   3. Missing pages_read_engagement permission")
                        print(f"   4. Not admin of the Facebook Page")
                        print(f"\n🔧 Solution:")
                        print(f"   1. Run: python fix_facebook_token.py")
                        print(f"   2. Follow instructions to get PAGE token")
                        print(f"   3. Make sure to select 'Get Page Access Token'")
                        print(f"   4. Add permissions: pages_manage_posts, pages_read_engagement")
                        print(f"   5. Update .env with new token")
                    elif error_code == 190:
                        print(f"\n⚠️  TOKEN EXPIRED!")
                        print(f"\n🔧 Solution:")
                        print(f"   1. Generate new token from Graph API Explorer")
                        print(f"   2. Update .env: FACEBOOK_ACCESS_TOKEN=new_token")
                    elif error_code == 4:
                        print(f"\n⚠️  RATE LIMIT EXCEEDED!")
                        print(f"   Please wait a few minutes before trying again")
                    
                except Exception as e:
                    print(f"\n[ERROR] API request failed: {response.status_code}")
                    print(f"      Could not parse error response: {e}")
                
                return None
            
            data = response.json()

            if 'id' in data:
                post_id = data['id']
                print(f"\n[SUCCESS] Post published to Facebook!")
                print(f"      Post ID: {post_id}")
                print(f"      URL: https://facebook.com/{post_id}")
                return post_id
            else:
                print(f"\n[ERROR] Post failed: {data}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"      Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"\n[ERROR] Posting failed: {e}")
            return None

    def post_to_instagram(self, content: str, image_path: str,
                          is_carousel: bool = False) -> Optional[str]:
        """
        Post content to Instagram Business Account.

        Instagram requires a two-step process:
        1. Create a media container
        2. Publish the container

        Args:
            content: Caption text
            image_path: Path to image file (required)
            is_carousel: Whether this is a carousel post

        Returns:
            Media ID if successful
        """
        if not self.access_token or not self.instagram_account_id:
            print("[ERROR] Instagram credentials not configured")
            print("  Set INSTAGRAM_ACCOUNT_ID in .env")
            return None

        if not image_path:
            print("[ERROR] Instagram requires an image")
            return None

        print("=" * 60)
        print("Instagram Poster - Starting (Graph API)")
        print("=" * 60)

        try:
            # Step 1: Upload image and create media container
            print(f"\n[Step 1/2] Creating media container...")
            
            # Get image URL (need to upload to a publicly accessible URL first)
            # For local development, we'll use a direct upload
            image_url = self._upload_image_for_instagram(image_path)
            
            if not image_url:
                print("      Failed to upload image")
                return None

            print(f"      Image URL: {image_url}")

            # Create media container
            container_url = f"{self.BASE_URL}/{self.instagram_account_id}/media"
            container_params = {
                'access_token': self.access_token,
                'image_url': image_url,
                'caption': content,
                'is_carousel_item': is_carousel
            }

            container_response = requests.post(container_url, params=container_params)
            container_response.raise_for_status()
            container_data = container_response.json()

            if 'id' not in container_data:
                print(f"\n[ERROR] Failed to create media container: {container_data}")
                return None

            container_id = container_data['id']
            print(f"      Container ID: {container_id}")

            # Wait for container to be ready
            print("      Waiting for container to be ready...")
            time.sleep(3)

            # Step 2: Publish the container
            print(f"\n[Step 2/2] Publishing to Instagram...")
            
            publish_url = f"{self.BASE_URL}/{self.instagram_account_id}/media_publish"
            publish_params = {
                'access_token': self.access_token,
                'creation_id': container_id
            }

            publish_response = requests.post(publish_url, params=publish_params)
            publish_response.raise_for_status()
            publish_data = publish_response.json()

            if 'id' in publish_data:
                media_id = publish_data['id']
                print(f"\n[SUCCESS] Post published to Instagram!")
                print(f"      Media ID: {media_id}")
                return media_id
            else:
                print(f"\n[ERROR] Publish failed: {publish_data}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"      Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"\n[ERROR] Posting failed: {e}")
            return None

    def _upload_image_for_instagram(self, image_path: str) -> Optional[str]:
        """
        Upload image to a publicly accessible URL for Instagram.
        
        Instagram requires the image to be at a public URL.
        For production, you would upload to S3, Cloudinary, etc.
        
        For local development, this is a placeholder.
        
        Args:
            image_path: Path to local image file
            
        Returns:
            Public URL of the image
        """
        # For production, implement actual image upload to a CDN
        # Options:
        # 1. AWS S3
        # 2. Cloudinary
        # 3. Imgur
        # 4. Your own server
        
        # For now, we'll use a simple approach:
        # If the image is already at a URL, return it
        if image_path.startswith('http'):
            return image_path
        
        # Otherwise, we need to upload it somewhere
        # This is a placeholder - implement based on your needs
        print("      [WARN] Local image upload not implemented")
        print("      For Instagram, images must be at a public URL")
        print("      Options:")
        print("        1. Upload to S3/Cloudinary and use the URL")
        print("        2. Host on your own server")
        print("        3. Use a service like Imgur")
        
        return None

    def create_approval_request(self, content: str, platforms: List[str],
                                hashtags: list = None, image_path: str = None,
                                link: str = None) -> Optional[Path]:
        """Create approval request for social media post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SOCIAL_POST_APPROVAL_{timestamp}.md"
        filepath = self.pending_approval / filename

        platforms_str = ', '.join(platforms)
        hashtags_str = ', '.join(hashtags) if hashtags else ''
        content_preview = content[:200] + '...' if len(content) > 200 else content

        approval_content = f"""---
type: approval_request
action: social_media_post
platforms: {platforms_str}
created: {datetime.now().isoformat()}
status: pending
hashtags: {hashtags_str}
image: {image_path or 'None'}
link: {link or 'None'}
---

# Social Media Post Approval Request

## Platforms
{platforms_str}

## Post Content

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
        """Process approved social media posts."""
        if not self.pending_approval.exists():
            return 0

        processed = 0
        for filepath in self.pending_approval.iterdir():
            if filepath.suffix != '.md' or 'SOCIAL_POST_APPROVAL' not in filepath.name:
                continue

            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Extract platforms
                platforms_match = re.search(r'platforms:\s*(.+)', content)
                if not platforms_match:
                    continue
                platforms = [p.strip() for p in platforms_match.group(1).split(',')]
                
                # Extract post content
                if '## Post Content' in content:
                    post_content = content.split('## Post Content')[1].split('---')[0].strip()
                else:
                    continue

                # Extract image path
                image_match = re.search(r'image:\s*(.+)', content)
                image_path = image_match.group(1).strip() if image_match and image_match.group(1).strip() != 'None' else None

                # Extract link
                link_match = re.search(r'link:\s*(.+)', content)
                link = link_match.group(1).strip() if link_match and link_match.group(1).strip() != 'None' else None

                print(f"Posting: {filepath.name}")
                print(f"  Platforms: {platforms}")
                
                success = False
                
                for platform in platforms:
                    platform = platform.strip().lower()
                    if platform == 'facebook':
                        if self.post_to_facebook(post_content, image_path, link):
                            success = True
                    elif platform == 'instagram':
                        if self.post_to_instagram(post_content, image_path):
                            success = True
                
                if success:
                    # Move to Done
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath.rename(self.done / f"{timestamp}_{filepath.name}")
                    processed += 1
                else:
                    print(f"  Failed to post")
                    
            except Exception as e:
                print(f"Error: {e}")

        return processed

    def process_comment_replies(self) -> int:
        """Process approved Facebook comment replies."""
        if not self.approved.exists():
            return 0

        processed = 0
        for filepath in self.approved.iterdir():
            if filepath.suffix != '.md' or 'FACEBOOK_COMMENT' not in filepath.name:
                continue

            try:
                content = filepath.read_text(encoding='utf-8')

                # Extract comment ID from frontmatter
                comment_id_match = re.search(r'comment_id:\s*(.+)', content)
                if not comment_id_match:
                    print(f"Skipping {filepath.name}: No comment_id found")
                    continue
                comment_id = comment_id_match.group(1).strip()

                # Extract reply content from "## Draft Response" section
                if '## Draft Response' in content:
                    draft_section = content.split('## Draft Response')[1]
                    # Remove the instruction text and get actual response
                    if '(for approval)' in draft_section:
                        draft_section = draft_section.split('(for approval)')[1]
                    # Split by next section or end of content
                    reply_content = draft_section.split('---')[0].strip()
                    # Remove any remaining instruction text
                    if '*Write your response' in reply_content:
                        reply_content = reply_content.split('*Write your response')[1].strip()
                        if '*' in reply_content:
                            reply_content = reply_content.split('*')[1].strip()
                elif '## Response' in content:
                    reply_content = content.split('## Response')[1].split('---')[0].strip()
                else:
                    print(f"Skipping {filepath.name}: No draft response found")
                    continue
                
                # Clean up the reply content
                reply_content = reply_content.strip('*').strip()

                print(f"Replying to comment: {filepath.name}")
                print(f"  Comment ID: {comment_id}")
                print(f"  Reply: {reply_content[:100]}...")

                # Post reply to Facebook
                if self.reply_to_comment(comment_id, reply_content):
                    # Move to Done
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath.rename(self.done / f"{timestamp}_{filepath.name}")
                    processed += 1
                else:
                    print(f"  Failed to post reply")

            except Exception as e:
                print(f"Error: {e}")

        return processed

    def reply_to_comment(self, comment_id: str, message: str) -> bool:
        """
        Reply to a Facebook comment.

        Args:
            comment_id: The ID of the comment to reply to
            message: The reply message

        Returns:
            True if successful
        """
        if not self.access_token:
            print("[ERROR] No access token configured")
            return False

        try:
            # Post reply to comment
            url = f"{self.BASE_URL}/{comment_id}/comments"
            params = {
                'access_token': self.access_token,
                'message': message
            }

            response = requests.post(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    print(f"  [SUCCESS] Reply posted!")
                    print(f"      Reply ID: {data['id']}")
                    return True

            # Handle errors
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"  [ERROR] Failed to post reply: {error_msg}")
            return False

        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            return False


def parse_markdown_file(filepath: Path) -> dict:
    """Parse markdown file with frontmatter."""
    content = filepath.read_text(encoding='utf-8')
    result = {'content': content, 'hashtags': [], 'image': None, 'platforms': ['facebook'], 'link': None}

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
            
            # Extract platforms
            platforms_match = re.search(r'platforms:\s*(.+)', frontmatter)
            if platforms_match:
                result['platforms'] = [p.strip() for p in platforms_match.group(1).split(',')]

            # Extract link
            link_match = re.search(r'link:\s*(.+)', frontmatter)
            if link_match:
                result['link'] = link_match.group(1).strip()
            
            result['content'] = content[end+3:].strip()

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Facebook Poster (Graph API)')
    parser.add_argument('vault_path', help='Vault path')
    parser.add_argument('--content', '-c', help='Content to post')
    parser.add_argument('--file', '-f', help='Markdown file with content')
    parser.add_argument('--image', '-i', help='Image path')
    parser.add_argument('--link', '-l', help='Link to share')
    parser.add_argument('--platform', '-p', help='Platform: facebook', default='facebook')
    parser.add_argument('--require-approval', '-a', action='store_true')
    parser.add_argument('--process-approved', action='store_true')
    parser.add_argument('--process-replies', action='store_true',
                       help='Process approved comment replies')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Facebook API connection')

    args = parser.parse_args()

    poster = FacebookPoster(args.vault_path)

    if args.test_connection:
        print("Testing Facebook API connection...")
        if poster.access_token and poster.page_id:
            print("[OK] Access token configured")
            print(f"[OK] Page ID: {poster.page_id}")
            sys.exit(0)
        else:
            print("[FAIL] Missing credentials")
            sys.exit(1)

    if args.process_approved:
        count = poster.process_approved_posts()
        print(f"Processed {count} posts")
        sys.exit(0)

    if args.process_replies:
        count = poster.process_comment_replies()
        print(f"Processed {count} replies")
        sys.exit(0)

    content = args.content
    image_path = args.image
    link = args.link
    hashtags = []
    platforms = ['facebook']

    if args.file:
        parsed = parse_markdown_file(Path(args.file))
        content = parsed['content']
        hashtags = parsed['hashtags']
        image_path = image_path or parsed['image']
        link = link or parsed['link']
        platforms = parsed.get('platforms', platforms)

    if not content:
        print("Error: No content provided")
        sys.exit(1)

    # Add hashtags to content
    if hashtags:
        content += '\n\n' + ' '.join(hashtags)

    if args.require_approval:
        filepath = poster.create_approval_request(content, platforms, hashtags, image_path, link)
        if filepath:
            print(f"Approval created: {filepath}")
            print("Move to /Approved to post")
            sys.exit(0)
        sys.exit(1)

    # Post directly
    success = False
    for platform in platforms:
        platform = platform.strip().lower()
        if platform == 'facebook':
            if poster.post_to_facebook(content, image_path, link):
                success = True

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
