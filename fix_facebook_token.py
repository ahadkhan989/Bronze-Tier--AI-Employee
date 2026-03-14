"""
Facebook Token Debugger & Fix Guide

This script helps you:
1. Check your current token type (User vs Page)
2. Verify permissions
3. Get step-by-step instructions for fixing issues

Usage:
    python fix_facebook_token.py
"""

import os
import requests
from dotenv import load_dotenv


def load_facebook_token():
    """Load Facebook token from .env file."""
    load_dotenv()
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    
    return token, page_id


def debug_token(token):
    """Debug Facebook access token."""
    if not token:
        print("\n❌ ERROR: No Facebook access token found in .env file")
        print("   Make sure FACEBOOK_ACCESS_TOKEN is set in your .env file")
        return None
    
    print("\n" + "=" * 70)
    print("  FACEBOOK TOKEN DEBUGGER")
    print("=" * 70)
    
    # Call Facebook Debug API
    debug_url = "https://graph.facebook.com/debug_token"
    params = {
        'input_token': token,
        'access_token': f"{os.getenv('FACEBOOK_APP_ID')}|{os.getenv('FACEBOOK_APP_SECRET')}"
    }
    
    try:
        response = requests.get(debug_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            token_info = data['data']
            
            print(f"\n📋 Token Information:")
            print(f"   • Type: {token_info.get('type', 'Unknown').upper()}")
            print(f"   • App ID: {token_info.get('app_id', 'N/A')}")
            print(f"   • User ID: {token_info.get('user_id', 'N/A')}")
            
            # Check if valid
            is_valid = token_info.get('is_valid', False)
            if is_valid:
                print(f"   • Status: ✅ VALID")
            else:
                print(f"   • Status: ❌ INVALID")
                print(f"      Error: {token_info.get('error', {}).get('message', 'Unknown error')}")
            
            # Check expiration
            expires_at = token_info.get('expires_at')
            if expires_at:
                from datetime import datetime
                expires_dt = datetime.fromtimestamp(expires_at)
                now = datetime.now()
                time_left = expires_dt - now
                
                if time_left.total_seconds() > 0:
                    print(f"   • Expires: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   • Time Left: {time_left.days} days, {time_left.seconds // 3600} hours")
                    
                    if time_left.days < 7:
                        print(f"   ⚠️  WARNING: Token expires in less than 7 days!")
                else:
                    print(f"   • Status: ❌ EXPIRED on {expires_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check permissions
            permissions = token_info.get('scopes', [])
            print(f"\n🔐 Permissions ({len(permissions)} found):")
            
            required_perms = ['pages_manage_posts', 'pages_read_engagement']
            optional_perms = ['instagram_basic', 'instagram_content_publish', 'publish_to_groups']
            
            print(f"   Required Permissions:")
            for perm in required_perms:
                status = "✅" if perm in permissions else "❌"
                print(f"      {status} {perm}")
            
            print(f"   Optional Permissions:")
            for perm in optional_perms:
                status = "✅" if perm in permissions else "⚪"
                print(f"      {status} {perm}")
            
            # Check for Page vs User token
            token_type = token_info.get('type', '').lower()
            if token_type == 'page':
                print(f"\n✅ Token Type: PAGE TOKEN (Correct!)")
            elif token_type == 'user':
                print(f"\n❌ Token Type: USER TOKEN (Incorrect!)")
                print(f"   You need a PAGE token to post to Facebook Pages.")
                print(f"   See instructions below.")
            else:
                print(f"\n⚠️  Token Type: {token_type.upper()} (Unknown)")
            
            return token_info
        else:
            print(f"\n❌ ERROR: Could not debug token")
            print(f"   Response: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Failed to debug token")
        print(f"   {e}")
        print(f"\n   This might happen if:")
        print(f"   1. App ID or App Secret is not set in .env")
        print(f"   2. Token is completely invalid")
        print(f"   3. Network error")
        return None


def print_fix_instructions(token_info):
    """Print step-by-step fix instructions."""
    
    print("\n" + "=" * 70)
    print("  FIX INSTRUCTIONS")
    print("=" * 70)
    
    if not token_info:
        print("\n📝 Step-by-Step: Get a New Page Access Token")
        print("\n1. Go to Graph API Explorer:")
        print("   https://developers.facebook.com/tools/explorer/")
        print("\n2. Select your app from dropdown:")
        print("   (AI Employee or your app name)")
        print("\n3. Click 'Get Token' → 'Get Page Access Token'")
        print("   ⚠️  IMPORTANT: Select 'Page Access Token' NOT 'User Token'")
        print("\n4. Select your Page:")
        print(f"   Page ID: {os.getenv('FACEBOOK_PAGE_ID', 'YOUR_PAGE_ID')}")
        print("\n5. Add these permissions:")
        print("   ✅ pages_manage_posts")
        print("   ✅ pages_read_engagement")
        print("\n6. Click 'Continue' → 'Allow'")
        print("\n7. Copy the generated token (starts with EAAn...)")
        print("\n8. Update your .env file:")
        print("   FACEBOOK_ACCESS_TOKEN=YOUR_NEW_TOKEN_HERE")
        return
    
    token_type = token_info.get('type', '').lower()
    is_valid = token_info.get('is_valid', False)
    permissions = token_info.get('scopes', [])
    
    # Check expiration
    if not is_valid:
        print("\n❌ ISSUE: Token is INVALID")
        print("\n📝 Solution:")
        print("   1. Your token has expired or been revoked")
        print("   2. Follow the steps above to get a new token")
        print("   3. Consider getting a long-lived token (60 days)")
    
    # Check token type
    elif token_type != 'page':
        print("\n❌ ISSUE: You have a USER token, need PAGE token")
        print("\n📝 Solution:")
        print("   1. Go to Graph API Explorer")
        print("   2. Click 'Get Token' → 'Get Page Access Token'")
        print("   3. Select your Page from the list")
        print("   4. This generates a PAGE token (not user token)")
        print("   5. Copy and update .env")
    
    # Check permissions
    else:
        missing_perms = []
        if 'pages_manage_posts' not in permissions:
            missing_perms.append('pages_manage_posts')
        if 'pages_read_engagement' not in permissions:
            missing_perms.append('pages_read_engagement')
        
        if missing_perms:
            print(f"\n❌ ISSUE: Missing permissions: {', '.join(missing_perms)}")
            print("\n📝 Solution:")
            print("   1. Go to Graph API Explorer")
            print("   2. Click 'Get Token' → 'Get Page Access Token'")
            print("   3. Select your Page")
            print("   4. Click 'Add Permissions'")
            print("   5. Add: pages_manage_posts, pages_read_engagement")
            print("   6. Click 'Continue' → 'Allow'")
            print("   7. Copy new token and update .env")
        else:
            print("\n✅ All required permissions are present!")
            print("\n📝 If still getting errors:")
            print("   1. Verify you're admin of the Facebook Page")
            print("   2. Go to your Page → Settings → Page Access")
            print("   3. Ensure your account has 'Full Control'")
            print("   4. Try generating token again")
    
    # Expiration warning
    expires_at = token_info.get('expires_at')
    if expires_at:
        from datetime import datetime
        expires_dt = datetime.fromtimestamp(expires_at)
        time_left = expires_dt - datetime.now()
        
        if time_left.total_seconds() > 0 and time_left.days < 7:
            print(f"\n⚠️  WARNING: Token expires in {time_left.days} days!")
            print("   Consider getting a long-lived token (60 days validity)")
            print("   Go to: https://developers.facebook.com/tools/debug/access_token/")
            print("   Click 'Extend Access Token'")


def test_page_token(token, page_id):
    """Test if page token works for posting."""
    if not page_id:
        print("\n⚠️  FACEBOOK_PAGE_ID not set in .env")
        return False
    
    print("\n" + "=" * 70)
    print("  TESTING PAGE TOKEN")
    print("=" * 70)
    
    # Try to get page info
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {'access_token': token}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            page_data = response.json()
            print(f"\n✅ SUCCESS! Token works for Page:")
            print(f"   Page Name: {page_data.get('name', 'N/A')}")
            print(f"   Page ID: {page_data.get('id', 'N/A')}")
            print(f"   You can now post to this page!")
            return True
        else:
            error = response.json()
            print(f"\n❌ FAILED: Token doesn't work for this page")
            print(f"   Error: {error.get('error', {}).get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("  FACEBOOK TOKEN DEBUGGER & FIX GUIDE")
    print("=" * 70)
    
    # Load token
    token, page_id = load_facebook_token()
    
    if not token:
        print("\n❌ No Facebook access token found!")
        print("\n📝 To fix:")
        print("   1. Open your .env file")
        print("   2. Add: FACEBOOK_ACCESS_TOKEN=your_token_here")
        print("   3. Get token from: https://developers.facebook.com/tools/explorer/")
        return
    
    # Debug token
    token_info = debug_token(token)
    
    # Print fix instructions
    print_fix_instructions(token_info)
    
    # Test token
    if token_info and token_info.get('is_valid'):
        test_page_token(token, page_id)
    
    print("\n" + "=" * 70)
    print("\n📚 Additional Resources:")
    print("   • Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print("   • Token Debugger: https://developers.facebook.com/tools/debug/access_token/")
    print("   • Page Access Docs: https://developers.facebook.com/docs/pages/access-token")
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
