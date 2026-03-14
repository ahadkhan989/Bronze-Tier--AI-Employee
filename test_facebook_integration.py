"""
Facebook Integration Test Script

Tests all Facebook integration components:
1. Connection to Facebook Graph API
2. Reading messages/comments
3. Creating test post
4. Creating approval workflow

Usage:
    python test_facebook_integration.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num: int, text: str):
    """Print a step header."""
    print(f"\n[Step {step_num}] {text}\n")


def test_environment():
    """Test environment configuration."""
    print_header("TEST 1: Environment Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check credentials
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    instagram_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
    
    print("Checking environment variables...")
    print(f"  FACEBOOK_APP_ID: {'[SET]' if app_id else '[NOT SET]'}")
    print(f"  FACEBOOK_APP_SECRET: {'[SET]' if app_secret else '[NOT SET]'}")
    print(f"  FACEBOOK_ACCESS_TOKEN: {'[SET]' if access_token else '[NOT SET]'}")
    print(f"  FACEBOOK_PAGE_ID: {'[SET]' if page_id else '[NOT SET]'}")
    print(f"  INSTAGRAM_ACCOUNT_ID: {'[SET]' if instagram_id else '[NOT SET]'}")
    
    # Validate required
    required = [
        ('FACEBOOK_ACCESS_TOKEN', access_token),
        ('FACEBOOK_PAGE_ID', page_id),
    ]
    
    missing = [name for name, value in required if not value]
    
    if missing:
        print(f"\n[ERROR] Missing required variables: {', '.join(missing)}")
        print("  Please update your .env file")
        return False
    else:
        print("\n[OK] All required credentials are set")
        return True


def test_watcher_connection():
    """Test Facebook Watcher connection."""
    print_header("TEST 2: Facebook Watcher Connection")
    
    try:
        from watchers.facebook_watcher import FacebookWatcher
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        if not vault_path.exists():
            print(f"[WARN] Vault not found at {vault_path}")
            vault_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created vault directory")
        
        watcher = FacebookWatcher(str(vault_path))
        
        if watcher.access_token and watcher.page_id:
            print("[OK] Facebook Watcher initialized successfully")
            print(f"      Page ID: {watcher.page_id}")
            if watcher.instagram_account_id:
                print(f"      Instagram ID: {watcher.instagram_account_id}")
            else:
                print("      Instagram: Not configured")
            return True
        else:
            print("[FAIL] Facebook Watcher missing credentials")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error initializing watcher: {e}")
        return False


def test_read_messages():
    """Test reading Facebook messages."""
    print_header("TEST 3: Read Facebook Messages")
    
    try:
        from watchers.facebook_watcher import FacebookWatcher
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        watcher = FacebookWatcher(str(vault_path))
        
        if not watcher.access_token:
            print("[SKIP] No access token configured")
            return False
        
        print("Fetching recent messages...")
        messages = watcher._get_facebook_messages()
        
        if messages:
            print(f"[OK] Found {len(messages)} recent message(s)")
            for msg in messages[:3]:  # Show first 3
                print(f"      - From: {msg.get('from', 'Unknown')}")
                print(f"        Preview: {msg.get('message', '')[:50]}...")
        else:
            print("[INFO] No new messages found (this is normal)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error reading messages: {e}")
        return False


def test_read_comments():
    """Test reading Facebook comments."""
    print_header("TEST 4: Read Facebook Comments")
    
    try:
        from watchers.facebook_watcher import FacebookWatcher
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        watcher = FacebookWatcher(str(vault_path))
        
        if not watcher.access_token:
            print("[SKIP] No access token configured")
            return False
        
        print("Fetching recent comments...")
        comments = watcher._get_facebook_comments()
        
        if comments:
            print(f"[OK] Found {len(comments)} recent comment(s)")
            for comment in comments[:3]:  # Show first 3
                print(f"      - From: {comment.get('from', 'Unknown')}")
                print(f"        Preview: {comment.get('message', '')[:50]}...")
        else:
            print("[INFO] No new comments found (this is normal)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error reading comments: {e}")
        return False


def test_create_action_file():
    """Test creating action files."""
    print_header("TEST 5: Create Action File")
    
    try:
        from watchers.facebook_watcher import FacebookWatcher
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        watcher = FacebookWatcher(str(vault_path))
        
        # Create test message
        test_message = {
            'id': 'test_123',
            'platform': 'facebook',
            'type': 'message',
            'from': 'Test User',
            'message': 'This is a test message from the Facebook integration test.',
            'created_time': datetime.now().isoformat(),
            'priority': 'normal'
        }
        
        print("Creating test action file...")
        filepath = watcher.create_action_file(test_message)
        
        if filepath and filepath.exists():
            print(f"[OK] Action file created: {filepath.name}")
            print(f"      Location: {filepath}")
            
            # Show file content preview
            content = filepath.read_text()
            preview = content[:200].replace('\n', ' ')
            print(f"      Preview: {preview}...")
            
            # Clean up
            filepath.unlink()
            print(f"      [OK] Test file cleaned up")
            
            return True
        else:
            print("[FAIL] Failed to create action file")
            return False
        
    except Exception as e:
        print(f"[FAIL] Error creating action file: {e}")
        return False


def test_poster_connection():
    """Test Facebook Poster connection."""
    print_header("TEST 6: Facebook Poster Connection")
    
    try:
        from watchers.facebook_poster import FacebookPoster
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        poster = FacebookPoster(str(vault_path))
        
        if poster.access_token and poster.page_id:
            print("[OK] Facebook Poster initialized successfully")
            print(f"      Page ID: {poster.page_id}")
            if poster.instagram_account_id:
                print(f"      Instagram ID: {poster.instagram_account_id}")
            return True
        else:
            print("[FAIL] Facebook Poster missing credentials")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error initializing poster: {e}")
        return False


def test_create_approval_request():
    """Test creating approval request."""
    print_header("TEST 7: Create Approval Request")
    
    try:
        from watchers.facebook_poster import FacebookPoster
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        poster = FacebookPoster(str(vault_path))
        
        # Ensure Pending_Approval folder exists
        pending_approval = vault_path / 'Pending_Approval'
        pending_approval.mkdir(parents=True, exist_ok=True)
        
        print("Creating test approval request...")
        filepath = poster.create_approval_request(
            content="This is a test post from the Facebook integration test.",
            platforms=['facebook'],
            hashtags=['#Test', '#AI']
        )
        
        if filepath and filepath.exists():
            print(f"[OK] Approval request created: {filepath.name}")
            print(f"      Location: {filepath}")
            
            # Show file content preview
            content = filepath.read_text()
            preview = content[:200].replace('\n', ' ')
            print(f"      Preview: {preview}...")
            
            # Clean up
            filepath.unlink()
            print(f"      [OK] Test file cleaned up")
            
            return True
        else:
            print("[FAIL] Failed to create approval request")
            return False
        
    except Exception as e:
        print(f"[FAIL] Error creating approval request: {e}")
        return False


def test_post_to_facebook():
    """Test posting to Facebook (optional, requires confirmation)."""
    print_header("TEST 8: Post to Facebook (OPTIONAL)")
    
    print("This test will create an actual post on your Facebook Page.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("[SKIP] Skipped posting test")
        return True
    
    try:
        from watchers.facebook_poster import FacebookPoster
        
        vault_path = Path.cwd() / 'AI_Employee_Vault'
        poster = FacebookPoster(str(vault_path))
        
        content = f"🤖 AI Employee Test Post\n\nThis is a test post from the Facebook integration test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\n#AI #Automation #Test"
        
        print(f"\nPosting to Facebook...")
        print(f"Content: {content[:100]}...")
        
        post_id = poster.post_to_facebook(content)
        
        if post_id:
            print(f"\n[OK] Test post successful!")
            print(f"      Post ID: {post_id}")
            print(f"      URL: https://facebook.com/{post_id}")
            print("\n[INFO] Please delete this test post from your Facebook Page")
            return True
        else:
            print("\n[FAIL] Post failed")
            return False
        
    except Exception as e:
        print(f"[FAIL] Error posting: {e}")
        return False


def run_all_tests():
    """Run all Facebook integration tests."""
    print_header("FACEBOOK INTEGRATION TEST SUITE")
    
    print("This script tests all Facebook integration components.")
    print("Tests 1-7 are safe and won't create any posts.")
    print("Test 8 is optional and will create a test post.\n")
    
    results = []
    
    # Run tests
    results.append(("Environment", test_environment()))
    results.append(("Watcher Connection", test_watcher_connection()))
    results.append(("Read Messages", test_read_messages()))
    results.append(("Read Comments", test_read_comments()))
    results.append(("Create Action File", test_create_action_file()))
    results.append(("Poster Connection", test_poster_connection()))
    results.append(("Create Approval", test_create_approval_request()))
    results.append(("Post to Facebook", test_post_to_facebook()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("1. Start Facebook Watcher:")
        print("   python watchers/facebook_watcher.py AI_Employee_Vault --interval 300")
        print("\n2. Post to Facebook:")
        print("   python watchers/facebook_poster.py AI_Employee_Vault --content \"Hello!\" --platform facebook")
        return 0
    else:
        print(f"\n[WARN] {failed} test(s) failed. Please check the errors above.")
        return 1


def main():
    """Main entry point."""
    exit_code = run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
