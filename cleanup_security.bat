@echo off
REM =============================================================================
REM Security Cleanup Script for AI Employee Repository (Windows)
REM =============================================================================
REM This script removes sensitive files from git tracking before pushing.
REM
REM Usage: cleanup_security.bat
REM =============================================================================

echo ==============================================
echo AI Employee Security Cleanup
echo ==============================================
echo.

echo Step 1: Removing sensitive files from git tracking...
echo ----------------------------------------------

REM Remove sensitive files from git tracking (but keep locally)
git rm --cached credentials.json 2>nul && echo [OK] Removed credentials.json from git
git rm --cached token.json 2>nul && echo [OK] Removed token.json from git
git rm --cached .env 2>nul && echo [OK] Removed .env from git
git rm --cached AI_Employee_Vault\token.json 2>nul && echo [OK] Removed AI_Employee_Vault\token.json from git

REM Remove session folders from git tracking
git rm -r --cached AI_Employee_Vault\linkedin_session\ 2>nul && echo [OK] Removed linkedin_session/ from git
git rm -r --cached AI_Employee_Vault\whatsapp_session\ 2>nul && echo [OK] Removed whatsapp_session/ from git
git rm -r --cached AI_Employee_Vault\facebook_session\ 2>nul && echo [OK] Removed facebook_session/ from git
git rm -r --cached AI_Employee_Vault\twitter_session\ 2>nul && echo [OK] Removed twitter_session/ from git

REM Remove logs from git tracking
git rm -r --cached AI_Employee_Vault\Logs\ 2>nul && echo [OK] Removed AI_Employee_Vault\Logs\ from git

REM Remove active processing folders
git rm -r --cached AI_Employee_Vault\Inbox\ 2>nul && echo [OK] Removed AI_Employee_Vault\Inbox\ from git
git rm -r --cached AI_Employee_Vault\Needs_Action\ 2>nul && echo [OK] Removed AI_Employee_Vault\Needs_Action\ from git
git rm -r --cached AI_Employee_Vault\Pending_Approval\ 2>nul && echo [OK] Removed AI_Employee_Vault\Pending_Approval\ from git
git rm -r --cached AI_Employee_Vault\Approved\ 2>nul && echo [OK] Removed AI_Employee_Vault\Approved\ from git
git rm -r --cached AI_Employee_Vault\Rejected\ 2>nul && echo [OK] Removed AI_Employee_Vault\Rejected\ from git

REM Remove Odoo/Postgres data
git rm -r --cached odoo\ 2>nul && echo [OK] Removed odoo/ from git
git rm -r --cached postgres\ 2>nul && echo [OK] Removed postgres/ from git
git rm -r --cached pgadmin\ 2>nul && echo [OK] Removed pgadmin/ from git

echo.
echo Step 2: Security Warning
echo ----------------------------------------------
echo The following files contain sensitive data - DO NOT commit them:
echo   - credentials.json (Google OAuth credentials)
echo   - token.json (OAuth tokens)
echo   - .env (Environment variables with API keys)
echo   - AI_Employee_Vault\*_session\ (Browser session data)
echo   - AI_Employee_Vault\Logs\ (May contain sensitive data)

echo.
echo Step 3: Verifying .gitignore...
echo ----------------------------------------------
if exist ".gitignore" (
    echo [OK] .gitignore file exists
) else (
    echo [ERROR] .gitignore file missing!
    if exist ".gitignore.example" (
        echo Creating .gitignore from .gitignore.example...
        copy .gitignore.example .gitignore
        echo [OK] Created .gitignore
    ) else (
        echo [ERROR] Cannot create .gitignore - file not found
    )
)

echo.
echo Step 4: Checking git status...
echo ----------------------------------------------
git status --short

echo.
echo Step 5: Security Checklist
echo ----------------------------------------------
echo Before pushing to GitHub, verify:
echo   [ ] No credentials.json in repository
echo   [ ] No token.json in repository
echo   [ ] No .env file in repository
echo   [ ] No session folders in repository
echo   [ ] No Logs folder in repository
echo   [ ] .gitignore is comprehensive
echo.

echo ==============================================
echo Security Cleanup Complete!
echo ==============================================
echo.
echo Next steps:
echo 1. Review git status above
echo 2. Commit the changes: git add . ^&^& git commit -m "Security cleanup"
echo 3. Push to GitHub: git push
echo.
echo WARNING: Never commit these files:
echo   - credentials.json
echo   - token.json
echo   - .env
echo   - *_session/ folders
echo   - Logs/ folders
echo.

pause
