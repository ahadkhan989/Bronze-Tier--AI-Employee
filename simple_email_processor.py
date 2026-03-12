"""
Simple Email Processor

Automatically processes emails in Needs_Action folder without requiring Qwen Code CLI.
Creates simple responses and moves files to appropriate folders.

Usage:
    python simple_email_processor.py AI_Employee_Vault
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


def process_emails(vault_path: str):
    """Process emails in Needs_Action folder."""
    vault = Path(vault_path)
    needs_action = vault / 'Needs_Action'
    done = vault / 'Done'
    pending_approval = vault / 'Pending_Approval'
    plans = vault / 'Plans'
    
    # Ensure folders exist
    done.mkdir(exist_ok=True)
    pending_approval.mkdir(exist_ok=True)
    plans.mkdir(exist_ok=True)
    
    if not needs_action.exists():
        print("No Needs_Action folder found")
        return
    
    # Get all email files
    email_files = list(needs_action.glob('EMAIL_*.md'))
    
    if not email_files:
        print("No emails to process")
        return
    
    print(f"\n{'='*70}")
    print(f"SIMPLE EMAIL PROCESSOR")
    print(f"{'='*70}")
    print(f"Found {len(email_files)} email(s) to process\n")
    
    processed = 0
    for email_file in email_files:
        print(f"Processing: {email_file.name}")
        
        try:
            content = email_file.read_text(encoding='utf-8')
            
            # Extract email info
            subject = extract_field(content, 'subject')
            from_email = extract_field(content, 'from')
            email_type = extract_field(content, 'type')
            
            print(f"  From: {from_email}")
            print(f"  Subject: {subject}")
            
            # Determine action based on content
            content_lower = content.lower()
            
            if 'invoice' in content_lower:
                # Invoice request - create approval for sending invoice
                print(f"  [INFO] Invoice request detected")
                create_approval_request(
                    pending_approval,
                    action_type='send_invoice',
                    subject=subject,
                    from_email=from_email,
                    original_file=email_file.name
                )
                # Move to In_Progress (not Done yet)
                processed += 1
                
            elif 'unsubscribe' in content_lower or 'newsletter' in content_lower:
                # Newsletter/unsubscribe - just archive
                print(f"  [INFO] Newsletter/Unsubscribe - archiving")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest = done / f"{timestamp}_{email_file.name}"
                shutil.move(str(email_file), str(dest))
                print(f"  [INFO] Moved to Done/")
                processed += 1
                
            elif 'connect' in content_lower or 'linkedin' in content_lower:
                # Connection request - create simple response
                print(f"  [INFO] Connection request")
                create_approval_request(
                    pending_approval,
                    action_type='accept_connection',
                    subject=subject,
                    from_email=from_email,
                    original_file=email_file.name
                )
                processed += 1
                
            else:
                # General email - create response draft
                print(f"  [INFO] General email - creating response draft")
                create_approval_request(
                    pending_approval,
                    action_type='send_email',
                    subject=subject,
                    from_email=from_email,
                    original_file=email_file.name
                )
                processed += 1
            
        except Exception as e:
            print(f"  ERROR: {e}")
            # Move to Done anyway to avoid reprocessing
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest = done / f"{timestamp}_{email_file.name}"
            shutil.move(str(email_file), str(dest))
    
    print(f"\n{'='*70}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Processed: {processed} email(s)")
    print(f"\nNEXT STEPS:")
    print(f"1. Check Pending_Approval/ folder in Obsidian")
    print(f"2. Review and approve responses")
    print(f"3. Move approved files to Approved/ folder")
    print(f"4. Run: python orchestrator.py {vault_path} --process-approvals")
    print(f"{'='*70}\n")


def extract_field(content: str, field: str) -> str:
    """Extract a field from markdown frontmatter."""
    lines = content.split('\n')
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break
            continue
        
        if in_frontmatter and line.startswith(f'{field}:'):
            return line.split(':', 1)[1].strip()
    
    return 'Unknown'


def create_approval_request(folder: Path, action_type: str, subject: str, from_email: str, original_file: str):
    """Create an approval request file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"APPROVAL_{action_type.upper()}_{timestamp}.md"
    filepath = folder / filename
    
    # Generate appropriate response based on action type
    if action_type == 'send_invoice':
        response_body = f"""Dear Valued Client,

Thank you for your inquiry regarding the invoice.

We are preparing your invoice and will send it to you within 24 hours.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
Your Team"""
    elif action_type == 'accept_connection':
        response_body = f"""Hi,

Thank you for the connection request! I'd be happy to connect.

I specialize in AI automation and help businesses streamline their operations.

Looking forward to staying in touch!

Best regards,
Your Name"""
    else:
        response_body = f"""Dear Sender,

Thank you for your email regarding: {subject}

We have received your message and will get back to you shortly.

If this is urgent, please don't hesitate to contact us directly.

Best regards,
Your Team"""
    
    content = f"""---
type: approval_request
action: {action_type}
to: {from_email}
subject: Re: {subject}
created: {datetime.now().isoformat()}
status: pending
original_email: {original_file}
---

# Email Response Approval Request

## Email Details

- **To:** {from_email}
- **Subject:** Re: {subject}
- **Action:** {action_type}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Draft Response

{response_body}

---

## Instructions

### To Approve
1. Review the response above
2. Edit if needed
3. Move this file to `/Approved` folder

### To Reject
1. Move this file to `/Rejected` folder
2. Add rejection reason below

---

## Decision

- [ ] Approved → Moved to /Approved on ___________
- [ ] Rejected → Moved to /Rejected on ___________

**Rejection Reason (if applicable):**

---
*Created by Simple Email Processor*
"""
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] Created approval request: {filename}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_email_processor.py <vault_path>")
        print("Example: python simple_email_processor.py AI_Employee_Vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    process_emails(vault_path)


if __name__ == '__main__':
    main()
