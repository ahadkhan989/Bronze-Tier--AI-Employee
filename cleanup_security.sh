#!/bin/bash
# =============================================================================
# Security Cleanup Script for AI Employee Repository
# =============================================================================
# This script removes sensitive files from git tracking and local storage
# before pushing to GitHub.
#
# Usage: 
#   Windows: cleanup_security.bat
#   Linux/Mac: ./cleanup_security.sh
# =============================================================================

echo "=============================================="
echo "AI Employee Security Cleanup"
echo "=============================================="
echo ""

# Colors for output (Linux/Mac only)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    if command -v tput >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo "✓ $1"
    fi
}

print_warning() {
    if command -v tput >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} $1"
    else
        echo "⚠ $1"
    fi
}

print_error() {
    if command -v tput >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} $1"
    else
        echo "✗ $1"
    fi
}

echo "Step 1: Removing sensitive files from git tracking..."
echo "----------------------------------------------"

# Remove sensitive files from git tracking (but keep locally)
git rm --cached credentials.json 2>/dev/null && print_success "Removed credentials.json from git"
git rm --cached token.json 2>/dev/null && print_success "Removed token.json from git"
git rm --cached .env 2>/dev/null && print_success "Removed .env from git"
git rm --cached AI_Employee_Vault/token.json 2>/dev/null && print_success "Removed AI_Employee_Vault/token.json from git"

# Remove session folders from git tracking
git rm -r --cached AI_Employee_Vault/linkedin_session/ 2>/dev/null && print_success "Removed linkedin_session/ from git"
git rm -r --cached AI_Employee_Vault/whatsapp_session/ 2>/dev/null && print_success "Removed whatsapp_session/ from git"
git rm -r --cached AI_Employee_Vault/facebook_session/ 2>/dev/null && print_success "Removed facebook_session/ from git"
git rm -r --cached AI_Employee_Vault/twitter_session/ 2>/dev/null && print_success "Removed twitter_session/ from git"

# Remove logs from git tracking
git rm -r --cached AI_Employee_Vault/Logs/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Logs/ from git"

# Remove active processing folders
git rm -r --cached AI_Employee_Vault/Inbox/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Inbox/ from git"
git rm -r --cached AI_Employee_Vault/Needs_Action/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Needs_Action/ from git"
git rm -r --cached AI_Employee_Vault/Pending_Approval/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Pending_Approval/ from git"
git rm -r --cached AI_Employee_Vault/Approved/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Approved/ from git"
git rm -r --cached AI_Employee_Vault/Rejected/ 2>/dev/null && print_success "Removed AI_Employee_Vault/Rejected/ from git"

# Remove Odoo/Postgres data
git rm -r --cached odoo/ 2>/dev/null && print_success "Removed odoo/ from git"
git rm -r --cached postgres/ 2>/dev/null && print_success "Removed postgres/ from git"
git rm -r --cached pgadmin/ 2>/dev/null && print_success "Removed pgadmin/ from git"

echo ""
echo "Step 2: Cleaning up local sensitive files..."
echo "----------------------------------------------"

# Note: We don't delete these files, just warn about them
print_warning "The following files contain sensitive data - DO NOT commit them:"
echo "  - credentials.json (Google OAuth credentials)"
echo "  - token.json (OAuth tokens)"
echo "  - .env (Environment variables with API keys)"
echo "  - AI_Employee_Vault/*_session/ (Browser session data)"
echo "  - AI_Employee_Vault/Logs/ (May contain sensitive data)"

echo ""
echo "Step 3: Verifying .gitignore..."
echo "----------------------------------------------"

# Check if .gitignore exists
if [ -f ".gitignore" ]; then
    print_success ".gitignore file exists"
else
    print_error ".gitignore file missing! Creating from .gitignore.example..."
    if [ -f ".gitignore.example" ]; then
        cp .gitignore.example .gitignore
        print_success "Created .gitignore from .gitignore.example"
    else
        print_error "Cannot create .gitignore - file not found"
    fi
fi

echo ""
echo "Step 4: Checking git status..."
echo "----------------------------------------------"
git status --short

echo ""
echo "Step 5: Security Checklist"
echo "----------------------------------------------"
echo "Before pushing to GitHub, verify:"
echo "  [ ] No credentials.json in repository"
echo "  [ ] No token.json in repository"
echo "  [ ] No .env file in repository"
echo "  [ ] No session folders in repository"
echo "  [ ] No Logs folder in repository"
echo "  [ ] .gitignore is comprehensive"
echo ""

echo "=============================================="
echo "Security Cleanup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Review git status above"
echo "2. Commit the changes: git add . && git commit -m 'Security cleanup'"
echo "3. Push to GitHub: git push"
echo ""
echo "⚠️  WARNING: Never commit these files:"
echo "   - credentials.json"
echo "   - token.json"
echo "   - .env"
echo "   - *_session/ folders"
echo "   - Logs/ folders"
echo ""
