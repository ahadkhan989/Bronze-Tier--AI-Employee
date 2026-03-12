"""
Gmail Watcher Module

Monitors Gmail for new important emails and creates action files in the Obsidian vault.
Uses Gmail API to fetch unread, important messages.

Usage:
    python gmail_watcher.py /path/to/vault [--interval 120] [--authenticate]
"""

import sys
import time
import json
import pickle
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Note: Google API packages not installed.")
    print("Install with: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important emails and creates action files.
    
    Attributes:
        credentials_path: Path to OAuth credentials JSON
        token_path: Path to saved OAuth token
        processed_ids: Set of processed message IDs
        priority_keywords: Keywords that indicate high priority
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self, vault_path: str, credentials_path: Optional[str] = None,
                 check_interval: int = 120, priority_only: bool = False):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            credentials_path: Path to OAuth credentials JSON (default: credentials.json)
            check_interval: How often to check for updates (in seconds)
            priority_only: Only process emails with priority keywords
        """
        super().__init__(vault_path, check_interval)
        
        # Set up paths
        self.credentials_path = Path(credentials_path or 'credentials.json')
        self.token_path = self.vault_path / 'token.json'
        self.processed_ids_file = self.logs / 'gmail_processed_ids.json'
        
        # Load processed IDs
        self.processed_ids = self._load_processed_ids()
        
        # Priority keywords
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'important',
            'help', 'deadline', 'action required', 'immediate'
        ]
        
        # Ignore certain senders
        self.ignore_senders = ['noreply@', 'notifications@', 'donotreply@']
        
        self.priority_only = priority_only
        self.service = None
        
    def _load_processed_ids(self) -> set:
        """Load previously processed message IDs from file."""
        if self.processed_ids_file.exists():
            try:
                data = json.loads(self.processed_ids_file.read_text())
                return set(data.get('ids', []))
            except:
                pass
        return set()
    
    def _save_processed_ids(self):
        """Save processed message IDs to file."""
        # Keep only last 1000 IDs to prevent unbounded growth
        ids_list = list(self.processed_ids)[-1000:]
        self.processed_ids_file.write_text(
            json.dumps({'ids': ids_list, 'updated': self.get_timestamp()})
        )
    
    def _authenticate(self):
        """Perform OAuth authentication flow."""
        print("Starting Gmail authentication...")
        print("Opening browser for Google login...")
        print("")

        if not self.credentials_path.exists():
            print(f"Error: Credentials file not found: {self.credentials_path}")
            print("Please download credentials.json from Google Cloud Console")
            return False

        try:
            app_flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.SCOPES
            )
            creds = app_flow.run_local_server(host='localhost', port=8080)

            # Save credentials
            self.token_path.write_text(creds.to_json())
            print(f"\n[OK] Authentication successful! Token saved to: {self.token_path}")
            return True

        except Exception as e:
            print(f"\n[ERROR] Authentication failed: {e}")
            return False
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid credentials, refreshing if needed."""
        creds = None
        
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            except Exception as e:
                self.logger.warning(f"Error loading token: {e}")
                self.token_path.unlink()
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.token_path.write_text(creds.to_json())
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    return None
        
        return creds
    
    def _connect(self) -> bool:
        """Connect to Gmail API."""
        try:
            creds = self._get_credentials()
            if not creds:
                self.logger.error("No valid credentials available")
                return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Connected to Gmail API")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail API: {e}")
            return False
    
    def _decode_message(self, message: Dict) -> Dict:
        """Decode a Gmail message into readable format."""
        try:
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Get body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
                            break
            elif 'body' in message['payload']:
                if message['payload']['body'].get('data'):
                    body = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'snippet': message.get('snippet', ''),
                'body': body[:2000],  # Limit body length
                'headers': headers
            }
            
        except Exception as e:
            self.logger.error(f"Error decoding message: {e}")
            return None
    
    def _is_priority(self, message: Dict) -> bool:
        """Check if message contains priority keywords."""
        text = f"{message.get('subject', '')} {message.get('snippet', '')}".lower()
        return any(kw in text for kw in self.priority_keywords)
    
    def _should_ignore(self, from_email: str) -> bool:
        """Check if sender should be ignored."""
        from_lower = from_email.lower()
        return any(ignore in from_lower for ignore in self.ignore_senders)
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for new emails in Gmail.
        
        Returns:
            List of new message dictionaries
        """
        if not self.service:
            if not self._connect():
                return []
        
        new_messages = []
        
        try:
            # Query for unread, important messages
            query = 'is:unread'
            if self.priority_only:
                query += ' AND (important OR priority:high)'
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                if msg['id'] in self.processed_ids:
                    continue
                
                # Get full message details
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                decoded = self._decode_message(full_msg)
                
                if decoded and not self._should_ignore(decoded['from']):
                    # Check priority
                    if self._is_priority(decoded):
                        decoded['priority'] = 'high'
                    else:
                        decoded['priority'] = 'normal'
                    
                    new_messages.append(decoded)
                    self.processed_ids.add(msg['id'])
            
            # Save processed IDs
            if new_messages:
                self._save_processed_ids()
            
        except HttpError as e:
            if e.resp.status == 429:
                self.logger.warning("Gmail API rate limit exceeded")
            else:
                self.logger.error(f"Gmail API error: {e}")
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            self.service = None  # Force reconnect on next check
        
        return new_messages
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create a .md action file for an email.
        
        Args:
            message: Decoded email message dictionary
            
        Returns:
            Path to the created file
        """
        try:
            # Sanitize subject for filename
            subject = self.sanitize_filename(message['subject'])[:50]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"EMAIL_{timestamp}_{subject}.md"
            filepath = self.needs_action / filename
            
            # Extract sender name
            from_email = message['from']
            if '<' in from_email:
                from_name = from_email.split('<')[0].strip()
            else:
                from_name = from_email
            
            content = f"""---
type: email
from: {from_email}
subject: {message['subject']}
received: {self.get_timestamp()}
priority: {message['priority']}
status: pending
message_id: {message['id']}
---

# Email: {message['subject']}

## Header Information
- **From:** {from_name} <{from_email}>
- **Received:** {self.get_timestamp()}
- **Priority:** {message['priority'].title()}

---

## Email Content

{message['snippet']}

{message['body'][:1000] if message['body'] else '*Full content not available*'}

---

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create follow-up task
- [ ] Archive after processing

---

## Processing Notes

*Add notes here during processing*

---

## Resolution

- [ ] Moved to /Done
- [ ] Date Completed: ___________

---
*Created by GmailWatcher*
"""
            
            filepath.write_text(content, encoding='utf-8')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def run(self):
        """Main run loop with Gmail-specific error handling."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Priority only: {self.priority_only}')
        
        # Initial connection
        if not self._connect():
            self.logger.error("Failed to connect to Gmail API. Run with --authenticate first.")
            return
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new email(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    priority_str = f" [{item['priority'].upper()}]"
                                    self.logger.info(f'Created action file: {filepath.name}{priority_str}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new emails')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self.service = None  # Force reconnect
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point for the Gmail watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault directory')
    parser.add_argument('--credentials', '-c', help='Path to OAuth credentials JSON')
    parser.add_argument('--interval', '-i', type=int, default=120, 
                       help='Check interval in seconds (default: 120)')
    parser.add_argument('--priority-only', '-p', action='store_true',
                       help='Only process priority emails')
    parser.add_argument('--authenticate', '-a', action='store_true',
                       help='Run authentication flow')
    
    args = parser.parse_args()
    
    if not GMAIL_AVAILABLE:
        print("Error: Google API packages not installed")
        print("Install with: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)
    
    if args.authenticate:
        watcher = GmailWatcher(args.vault_path, args.credentials)
        success = watcher._authenticate()
        sys.exit(0 if success else 1)
    
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials,
        check_interval=args.interval,
        priority_only=args.priority_only
    )
    
    watcher.run()


if __name__ == '__main__':
    main()
