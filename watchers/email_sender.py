"""
Email Sender Module

Sends emails via Gmail API. Used by the orchestrator to process approved emails.

Usage:
    python email_sender.py send --to recipient@example.com --subject "Subject" --body "Body"
    python email_sender.py draft --to recipient@example.com --subject "Subject" --body "Body"
"""

import sys
import base64
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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


class EmailSender:
    """Send emails via Gmail API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self, credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json'):
        """
        Initialize email sender.
        
        Args:
            credentials_path: Path to OAuth credentials
            token_path: Path to saved token
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        
    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid credentials."""
        creds = None
        
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            except Exception as e:
                print(f"Error loading token: {e}")
                self.token_path.unlink()
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.token_path.write_text(creds.to_json())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    return None
        
        return creds
    
    def connect(self) -> bool:
        """Connect to Gmail API."""
        try:
            creds = self._get_credentials()
            if not creds:
                print("No valid credentials available")
                return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def _create_message(self, to: str, subject: str, body: str,
                        html: bool = False, attachments: List[str] = None,
                        cc: List[str] = None, bcc: List[str] = None) -> dict:
        """Create email message."""
        message = MIMEMultipart() if attachments else MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = ', '.join(cc)
        
        # Add body
        if html:
            message.attach(MIMEText(body, 'html'))
        else:
            message.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{Path(filepath).name}"'
                        )
                        message.attach(part)
                except Exception as e:
                    print(f"Error attaching {filepath}: {e}")
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def send_email(self, to: str, subject: str, body: str,
                   html: bool = False, attachments: List[str] = None,
                   cc: List[str] = None, bcc: List[str] = None) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            html: Whether body is HTML
            attachments: List of attachment file paths
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            
        Returns:
            True if sent successfully
        """
        if not self.service:
            if not self.connect():
                return False
        
        try:
            message = self._create_message(
                to, subject, body, html, attachments, cc, bcc
            )
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f"Email sent successfully! Message ID: {sent_message['id']}")
            return True
            
        except HttpError as e:
            print(f"Gmail API error: {e}")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def create_draft(self, to: str, subject: str, body: str,
                     html: bool = False, attachments: List[str] = None) -> Optional[str]:
        """
        Create a draft email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            html: Whether body is HTML
            attachments: List of attachment file paths
            
        Returns:
            Draft ID if successful
        """
        if not self.service:
            if not self.connect():
                return None
        
        try:
            message = self._create_message(to, subject, body, html, attachments)
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            print(f"Draft created successfully! Draft ID: {draft['id']}")
            return draft['id']
            
        except Exception as e:
            print(f"Error creating draft: {e}")
            return None


def authenticate():
    """Run authentication flow."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    credentials_path = Path('credentials.json')
    token_path = Path('token.json')
    
    if not credentials_path.exists():
        print("Error: credentials.json not found")
        print("Download from Google Cloud Console")
        return False
    
    try:
        app_flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, EmailSender.SCOPES
        )
        creds = app_flow.run_local_server(host='localhost', port=8081)
        
        token_path.write_text(creds.to_json())
        print(f"[OK] Authentication successful! Token saved to: {token_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email Sender for AI Employee')
    parser.add_argument('action', choices=['send', 'draft', 'authenticate'],
                       help='Action to perform')
    parser.add_argument('--to', '-t', help='Recipient email address')
    parser.add_argument('--subject', '-s', help='Email subject')
    parser.add_argument('--body', '-b', help='Email body text')
    parser.add_argument('--html', action='store_true', help='Body is HTML')
    parser.add_argument('--attachments', '-a', nargs='+', help='Attachment file paths')
    parser.add_argument('--cc', nargs='+', help='CC email addresses')
    parser.add_argument('--credentials', '-c', default='credentials.json',
                       help='Path to credentials.json')
    parser.add_argument('--token', default='token.json', help='Path to token.json')
    
    args = parser.parse_args()
    
    if not GMAIL_AVAILABLE:
        print("Error: Google API packages not installed")
        print("Install with: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)
    
    if args.action == 'authenticate':
        success = authenticate()
        sys.exit(0 if success else 1)
    
    if not args.to or not args.subject or not args.body:
        print("Error: --to, --subject, and --body are required for send/draft")
        sys.exit(1)
    
    sender = EmailSender(args.credentials, args.token)
    
    if args.action == 'send':
        success = sender.send_email(
            to=args.to,
            subject=args.subject,
            body=args.body,
            html=args.html,
            attachments=args.attachments,
            cc=args.cc
        )
        sys.exit(0 if success else 1)
    
    elif args.action == 'draft':
        draft_id = sender.create_draft(
            to=args.to,
            subject=args.subject,
            body=args.body,
            html=args.html,
            attachments=args.attachments
        )
        sys.exit(0 if draft_id else 1)


if __name__ == '__main__':
    main()
