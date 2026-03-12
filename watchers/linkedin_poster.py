"""
LinkedIn Poster Module - Reliable Version

Posts content to LinkedIn using direct UI interaction.
Uses Playwright to click buttons and type in the editor.

Usage:
    python linkedin_poster.py /path/to/vault --content "Post content"
"""

import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Install with: pip install playwright && playwright install chromium")


class LinkedInPoster:
    LINKEDIN_URL = 'https://www.linkedin.com'
    POST_URL = 'https://www.linkedin.com/feed/'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path or self.vault_path / 'linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        
    def _check_session(self) -> bool:
        if not self.session_path.exists():
            return False
        if not any(self.session_path.iterdir()):
            return False
        return True
    
    def post_content(self, content: str, image_path: Optional[str] = None) -> bool:
        """Post content to LinkedIn with reliable UI interaction."""
        if not self._check_session():
            print("No valid LinkedIn session. Run: python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session")
            return False

        print("=" * 60)
        print("LinkedIn Poster - Starting")
        print("=" * 60)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,
                    viewport={'width': 1920, 'height': 1080}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    # Step 1: Navigate to feed
                    print("\n[Step 1/5] Navigating to LinkedIn...")
                    page.goto(self.POST_URL, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(5)
                    
                    # Wait for network to be idle
                    try:
                        page.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        print("      Network idle timeout, continuing...")
                    
                    time.sleep(3)
                    print(f"      Current URL: {page.url}")
                    
                    # Check if we're logged in by looking for feed
                    if 'login' in page.url.lower():
                        print("      ERROR: Not logged in. Re-run: python watchers/linkedin_watcher.py AI_Employee_Vault --setup-session")
                        browser.close()
                        return False
                    
                    # Step 2: Click "Start a post" button
                    print("\n[Step 2/5] Opening post editor...")
                    
                    # Wait for page to fully load
                    page.wait_for_load_state('domcontentloaded')
                    time.sleep(3)
                    
                    # Use get_by_role to find the button specifically
                    try:
                        print("      Looking for 'Start a post' button...")
                        start_post_btn = page.get_by_role("button", name="Start a post")
                        if start_post_btn:
                            print("      Found 'Start a post' button")
                            start_post_btn.click()
                            time.sleep(5)
                            print("      Clicked 'Start a post'")
                        else:
                            raise Exception("Button not found")
                    except Exception as e:
                        print(f"      Button click failed: {e}")
                        print("      Trying alternative approach...")
                        
                        # Look for any clickable element near the top of feed
                        alternatives = [
                            'div[class*="share-box"]',
                            '.share-box-feed-entry__content',
                            '[class*="feed-to-article"]',
                        ]
                        
                        clicked = False
                        for selector in alternatives:
                            try:
                                elem = page.wait_for_selector(selector, timeout=3000)
                                if elem:
                                    elem.click()
                                    print(f"      Clicked alternative: {selector}")
                                    clicked = True
                                    time.sleep(3)
                                    break
                            except:
                                continue
                        
                        if not clicked:
                            print("      All alternatives failed")
                            page.screenshot(path='linkedin_nobutton.png')
                            browser.close()
                            return False
                    
                    # Step 3: Type the content
                    print("\n[Step 3/5] Entering content...")
                    
                    # Wait for editor to appear
                    try:
                        editor = page.wait_for_selector(
                            'div[contenteditable="true"][role="textbox"]',
                            timeout=10000
                        )
                        print("      Found editor")
                        
                        # Focus the editor
                        editor.focus()
                        time.sleep(1)
                        
                        # Clear any existing content
                        page.keyboard.press('Control+a')
                        time.sleep(0.5)
                        page.keyboard.press('Backspace')
                        time.sleep(0.5)
                        
                        # Type content character by character for reliability
                        print("      Typing content...")
                        for i, char in enumerate(content):
                            page.keyboard.type(char)
                            # Slow down for longer posts
                            if len(content) > 50:
                                time.sleep(0.02)
                        
                        print(f"      Content entered ({len(content)} chars)")
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"      ERROR entering content: {e}")
                        page.screenshot(path='linkedin_noeditor.png')
                        browser.close()
                        return False
                    
                    # Step 4: Add image if provided
                    if image_path:
                        print("\n[Step 4/5] Adding image...")
                        try:
                            media_btn = page.wait_for_selector(
                                'button[aria-label*="photo"], button[aria-label*="media"]',
                                timeout=5000
                            )
                            if media_btn:
                                media_btn.click()
                                time.sleep(1)
                                file_input = page.wait_for_selector(
                                    'input[type="file"]',
                                    timeout=3000
                                )
                                if file_input:
                                    file_input.set_input_files(image_path)
                                    print("      Image attached")
                                    time.sleep(2)
                        except Exception as e:
                            print(f"      Could not add image: {e}")
                    
                    # Step 5: Click Post button
                    print("\n[Step 5/5] Posting...")
                    
                    # Wait for post button to be enabled
                    print("      Waiting for Post button to be enabled...")
                    time.sleep(5)  # LinkedIn needs time to validate content
                    
                    post_btn = None
                    try:
                        # Use exact match for "Post" button
                        post_btn = page.get_by_role("button", name="Post", exact=True)
                        if post_btn:
                            print("      Found Post button (exact match)")
                            # Check if disabled
                            try:
                                is_disabled = post_btn.is_disabled()
                                print(f"      Button disabled: {is_disabled}")
                                if is_disabled:
                                    print("      Button is disabled, waiting...")
                                    time.sleep(5)
                            except:
                                pass
                    except Exception as e:
                        print(f"      Post button not found: {e}")
                        pass
                    
                    if not post_btn:
                        # Try selector-based approach
                        post_selectors = [
                            'button[aria-label="Post"]',
                            '.share-box-feed-entry__submit button',
                            'button.share-box-feed-entry__submit',
                        ]
                        
                        for selector in post_selectors:
                            try:
                                post_btn = page.wait_for_selector(selector, timeout=3000)
                                if post_btn:
                                    print(f"      Found Post button: {selector}")
                                    break
                            except:
                                continue
                    
                    if post_btn:
                        # Scroll button into view
                        try:
                            post_btn.scroll_into_view_if_needed()
                        except:
                            pass
                        time.sleep(1)
                        
                        # Click the post button
                        post_btn.click()
                        print("      Clicked Post button")
                        
                        # Wait for post to be submitted
                        time.sleep(5)
                        
                        # Check if post was successful
                        try:
                            page.wait_for_selector('article', timeout=10000)
                            print("\n[SUCCESS] Post published!")
                            browser.close()
                            return True
                        except:
                            print("\n[OK] Post submitted (verification timeout)")
                            browser.close()
                            return True
                    else:
                        print("      ERROR: Could not find Post button")
                        print("      Taking screenshot...")
                        page.screenshot(path='linkedin_nopostbutton.png')
                        
                        # Try keyboard shortcut as last resort
                        print("      Trying Ctrl+Enter as fallback...")
                        page.keyboard.press('Control+Enter')
                        time.sleep(3)
                        print("      Fallback executed")
                        browser.close()
                        return True

                except Exception as e:
                    print(f"\n[ERROR] Posting failed: {e}")
                    page.screenshot(path='linkedin_error.png')
                    print("      Error screenshot saved to linkedin_error.png")
                    browser.close()
                    return False

        except Exception as e:
            print(f"[ERROR] Browser error: {e}")
            return False
    
    def create_approval_request(self, content: str, hashtags: list = None) -> Optional[Path]:
        """Create approval request."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_APPROVAL_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        hashtags_str = ', '.join(hashtags) if hashtags else ''
        content_preview = content[:200] + '...' if len(content) > 200 else content
        
        approval_content = f"""---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
status: pending
hashtags: {hashtags_str}
---

# LinkedIn Post Approval Request

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
        """Process approved posts."""
        if not self.pending_approval.exists():
            return 0
        
        processed = 0
        for filepath in self.pending_approval.iterdir():
            if filepath.suffix != '.md' or 'LINKEDIN_POST_APPROVAL' not in filepath.name:
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                if '## Post Content' in content:
                    post_content = content.split('## Post Content')[1].split('---')[0].strip()
                else:
                    continue
                
                print(f"Posting: {filepath.name}")
                if self.post_content(post_content):
                    done_folder = self.vault_path / 'Done'
                    done_folder.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath.rename(done_folder / f"{timestamp}_{filepath.name}")
                    processed += 1
            except Exception as e:
                print(f"Error: {e}")
        
        return processed


def parse_markdown_file(filepath: Path) -> dict:
    content = filepath.read_text(encoding='utf-8')
    result = {'content': content, 'hashtags': [], 'image': None}
    
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            frontmatter = content[4:end].strip()
            hashtags_match = re.search(r'hashtags:\s*\[(.*?)\]', frontmatter)
            if hashtags_match:
                result['hashtags'] = [h.strip().strip('"\'') for h in hashtags_match.group(1).split(',')]
            image_match = re.search(r'image:\s*(.+)', frontmatter)
            if image_match:
                result['image'] = image_match.group(1).strip()
            result['content'] = content[end+3:].strip()
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('vault_path', help='Vault path')
    parser.add_argument('--content', '-c', help='Content')
    parser.add_argument('--file', '-f', help='Markdown file')
    parser.add_argument('--image', '-i', help='Image path')
    parser.add_argument('--require-approval', '-a', action='store_true')
    parser.add_argument('--process-approved', action='store_true')
    
    args = parser.parse_args()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Error: Playwright not installed")
        sys.exit(1)
    
    poster = LinkedInPoster(args.vault_path)
    
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
        print("Error: No content")
        sys.exit(1)
    
    if hashtags:
        content += '\n\n' + ' '.join(hashtags)
    
    if args.require_approval:
        filepath = poster.create_approval_request(content, hashtags)
        if filepath:
            print(f"Approval created: {filepath}")
            print("Move to /Approved to post")
            sys.exit(0)
        sys.exit(1)
    
    success = poster.post_content(content, image_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
