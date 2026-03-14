"""
Auto-Response Generator for Facebook Comments

Automatically generates draft responses for Facebook comments using Qwen Code.

Usage:
    python auto_generate_response.py AI_Employee_Vault
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def find_pending_comments(vault_path: Path):
    """Find Facebook comment files that need responses."""
    needs_action = vault_path / 'Needs_Action'
    
    if not needs_action.exists():
        return []
    
    pending = []
    for file in needs_action.glob('FACEBOOK_COMMENT_*.md'):
        content = file.read_text(encoding='utf-8')
        
        # Check if already has a response
        if '## Draft Response' in content:
            draft_section = content.split('## Draft Response')[1]
            # Check if it's just the placeholder text
            if '*Write your response' in draft_section or draft_section.strip() == '':
                pending.append(file)
        else:
            pending.append(file)
    
    return pending


def extract_comment_info(content: str) -> dict:
    """Extract comment information from the file."""
    info = {
        'from': 'Unknown',
        'content': '',
        'platform': 'facebook'
    }
    
    # Extract from frontmatter
    if 'from:' in content:
        try:
            from_line = content.split('from:')[1].split('\n')[0].strip()
            info['from'] = from_line
        except:
            pass
    
    # Extract comment content
    if '## Content' in content:
        try:
            content_section = content.split('## Content')[1]
            if '---' in content_section:
                content_section = content_section.split('---')[0]
            info['content'] = content_section.strip()
        except:
            pass
    
    return info


def generate_response_with_qwen(vault_path: Path, comment_file: Path):
    """Generate response using Qwen Code."""
    
    # Extract comment info
    content = comment_file.read_text(encoding='utf-8')
    comment_info = extract_comment_info(content)
    
    print(f"\n{'='*60}")
    print(f"Generating response for: {comment_file.name}")
    print(f"{'='*60}")
    print(f"From: {comment_info['from']}")
    print(f"Comment: {comment_info['content']}")
    print()
    
    # Create prompt for Qwen Code
    prompt = f"""You are a social media manager for a business. Generate a friendly, professional response to this Facebook comment.

**Comment Details:**
- From: {comment_info['from']}
- Platform: Facebook
- Comment: {comment_info['content']}

**Response Guidelines:**
- Be friendly and professional
- Keep it concise (1-3 sentences)
- Add an emoji if appropriate
- If they're asking about pricing/services, invite them to DM
- If it's positive feedback, thank them warmly
- If it's a question, provide helpful information

**Task:**
Write ONLY the response text (no explanations, no markdown).

**Response:**"""

    # Try to use Claude Code if available
    try:
        print("Calling Qwen Code for response generation...")
        
        # Change to vault directory
        original_dir = Path.cwd()
        import os
        os.chdir(str(vault_path))
        
        # Run Qwen Code
        result = subprocess.run(
            ['claude', prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"✓ Generated response: {response}")
            return response
        else:
            print(f"✗ Qwen Code error: {result.stderr}")
            
    except FileNotFoundError:
        print("⚠ Qwen Code not found. Using template response.")
        response = generate_template_response(comment_info)
        print(f"✓ Generated template response: {response}")
        return response
    except subprocess.TimeoutExpired:
        print("⚠ Qwen Code timeout. Using template response.")
        response = generate_template_response(comment_info)
        print(f"✓ Generated template response: {response}")
        return response
    except Exception as e:
        print(f"⚠ Error: {e}. Using template response.")
        response = generate_template_response(comment_info)
        print(f"✓ Generated template response: {response}")
        return response


def generate_template_response(comment_info: dict) -> str:
    """Generate a template response based on comment content."""
    
    comment_text = comment_info['content'].lower()
    
    # Positive comment
    if any(word in comment_text for word in ['great', 'awesome', 'good', 'nice', 'love', 'amazing', 'thanks']):
        return f"Thank you so much! We're glad you liked it! 😊"
    
    # Question about price
    if any(word in comment_text for word in ['price', 'cost', 'how much', 'pricing']):
        return f"Thanks for your interest! Please DM us for pricing details. We'd love to help! 💼"
    
    # Question
    if '?' in comment_info['content']:
        return f"Great question! Please send us a DM and we'll get back to you with more information. 📩"
    
    # Negative comment
    if any(word in comment_text for word in ['bad', 'worst', 'hate', 'terrible', 'awful']):
        return f"We're sorry to hear about your experience. Please DM us so we can make this right. 🙏"
    
    # Default response
    return f"Thanks for your comment! We appreciate your engagement. 😊"


def update_file_with_response(vault_path: Path, comment_file: Path, response: str):
    """Update the comment file with the generated response."""
    
    content = comment_file.read_text(encoding='utf-8')
    
    # Find the Draft Response section
    if '## Draft Response (for approval)' in content:
        # Replace the placeholder with actual response
        parts = content.split('## Draft Response (for approval)')
        before = parts[0]
        after = parts[1]
        
        # Find and replace the placeholder text
        if '*Write your response here' in after:
            after = after.replace('*Write your response here, then move file to Pending_Approval/*', response)
        elif '(for approval)' in after:
            after = after.replace('(for approval)', response)
        else:
            # Just add response after the header
            after = '\n\n' + response + after
        
        new_content = before + '## Draft Response (for approval)\n\n' + response + after
        
    elif '## Draft Response' in content:
        # Replace existing draft
        parts = content.split('## Draft Response')
        before = parts[0]
        after = parts[1]
        
        # Remove old response
        if '---' in after:
            after = after.split('---', 1)[1]
        
        new_content = before + '## Draft Response\n\n' + response + '---' + after
    else:
        # Add new Draft Response section before Processing Notes
        if '## Processing Notes' in content:
            parts = content.split('## Processing Notes')
            before = parts[0]
            after = parts[1]
            new_content = before + '\n## Draft Response\n\n' + response + '\n\n---\n\n## Processing Notes' + after
        else:
            # Add at the end
            new_content = content + '\n\n## Draft Response\n\n' + response
    
    # Write updated content
    comment_file.write_text(new_content, encoding='utf-8')
    print(f"✓ File updated: {comment_file.name}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python auto_generate_response.py <vault_path>")
        print("Example: python auto_generate_response.py AI_Employee_Vault")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f"Error: Vault path not found: {vault_path}")
        sys.exit(1)
    
    print("="*60)
    print("  AUTO-RESPONSE GENERATOR FOR FACEBOOK COMMENTS")
    print("="*60)
    
    # Find pending comments
    pending = find_pending_comments(vault_path)
    
    if not pending:
        print("\n✓ No pending comments need responses")
        print("  All files already have draft responses")
        sys.exit(0)
    
    print(f"\nFound {len(pending)} comment(s) needing responses\n")
    
    # Process each comment
    generated = 0
    for comment_file in pending:
        try:
            # Generate response
            response = generate_response_with_qwen(vault_path, comment_file)
            
            if response:
                # Update file
                update_file_with_response(vault_path, comment_file, response)
                generated += 1
                print()
        except Exception as e:
            print(f"✗ Error processing {comment_file.name}: {e}")
    
    print("="*60)
    print(f"  SUMMARY")
    print("="*60)
    print(f"  Processed: {len(pending)} comments")
    print(f"  Generated: {generated} responses")
    print(f"  Location: {vault_path / 'Needs_Action'}")
    print("="*60)
    print()
    print("Next Steps:")
    print("1. Review generated responses in Needs_Action/")
    print("2. Move files to Pending_Approval/ for review")
    print("3. Move to Approved/ when ready")
    print("4. Run: python watchers/facebook_poster.py AI_Employee_Vault --process-replies")
    print()


if __name__ == '__main__':
    main()
