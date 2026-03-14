@echo off
REM =============================================================================
REM Final GitHub Push Preparation Script
REM =============================================================================
REM This script prepares your Gold Tier AI Employee project for GitHub push
REM by removing all sensitive files and verifying security.
REM =============================================================================

echo.
echo ============================================================
echo   GITHUB PUSH PREPARATION - GOLD TIER AI EMPLOYEE
echo ============================================================
echo.

echo Step 1: Removing sensitive files from git tracking...
echo ------------------------------------------------------------

REM Remove sensitive files from git tracking (but keep locally)
git rm --cached .env 2>nul && echo [OK] Removed .env from git
git rm --cached credentials.json 2>nul && echo [OK] Removed credentials.json from git
git rm --cached token.json 2>nul && echo [OK] Removed token.json from git
git rm --cached AI_Employee_Vault\token.json 2>nul && echo [OK] Removed AI_Employee_Vault\token.json from git

REM Remove session folders
git rm -r --cached AI_Employee_Vault\linkedin_session\ 2>nul && echo [OK] Removed linkedin_session from git
git rm -r --cached AI_Employee_Vault\Logs\ 2>nul && echo [OK] Removed Logs from git

REM Remove active processing folders
git rm -r --cached AI_Employee_Vault\Needs_Action\ 2>nul && echo [OK] Removed Needs_Action from git
git rm -r --cached AI_Employee_Vault\Pending_Approval\ 2>nul && echo [OK] Removed Pending_Approval from git
git rm -r --cached AI_Employee_Vault\Approved\ 2>nul && echo [OK] Removed Approved from git
git rm -r --cached AI_Employee_Vault\Rejected\ 2>nul && echo [OK] Removed Rejected from git
git rm -r --cached AI_Employee_Vault\In_Progress\ 2>nul && echo [OK] Removed In_Progress from git
git rm -r --cached AI_Employee_Vault\Inbox\ 2>nul && echo [OK] Removed Inbox from git

REM Remove Odoo/Postgres data
git rm -r --cached odoo\ 2>nul && echo [OK] Removed odoo/ from git
git rm -r --cached postgres\ 2>nul && echo [OK] Removed postgres/ from git
git rm -r --cached pgadmin\ 2>nul && echo [OK] Removed pgadmin/ from git

echo.
echo Step 2: Checking what will be committed...
echo ------------------------------------------------------------
git status --short

echo.
echo Step 3: Security verification...
echo ------------------------------------------------------------

REM Check if sensitive files are ignored
git check-ignore .env >nul 2>&1 && echo [OK] .env is ignored || echo [FAIL] .env NOT ignored
git check-ignore credentials.json >nul 2>&1 && echo [OK] credentials.json is ignored || echo [FAIL] credentials.json NOT ignored
git check-ignore token.json >nul 2>&1 && echo [OK] token.json is ignored || echo [FAIL] token.json NOT ignored
git check-ignore AI_Employee_Vault\Needs_Action >nul 2>&1 && echo [OK] Needs_Action is ignored || echo [FAIL] Needs_Action NOT ignored
git check-ignore AI_Employee_Vault\Pending_Approval >nul 2>&1 && echo [OK] Pending_Approval is ignored || echo [FAIL] Pending_Approval NOT ignored
git check-ignore AI_Employee_Vault\Approved >nul 2>&1 && echo [OK] Approved is ignored || echo [FAIL] Approved NOT ignored

echo.
echo Step 4: Files ready to commit...
echo ------------------------------------------------------------
echo.
echo SAFE TO COMMIT (Gold Tier Files):
echo   - GOLD_TIER.md
echo   - ODOO_SETUP.md
echo   - docker-compose.yml
echo   - requirements.txt
echo   - ralph_wiggum_loop.py
echo   - auto_generate_response.py
echo   - cleanup_security.bat/sh
echo   - All documentation files
echo   - All watcher scripts (facebook, twitter, odoo)
echo   - All MCP servers
echo.
echo SAFE TO COMMIT (Vault Structure):
echo   - AI_Employee_Vault/Dashboard.md
echo   - AI_Employee_Vault/Company_Handbook.md
echo   - AI_Employee_Vault/Business_Goals.md
echo   - AI_Employee_Vault/Templates/
echo   - AI_Employee_Vault/Done/ (completed items)
echo.
echo DO NOT COMMIT (Already in .gitignore):
echo   - .env (contains API keys)
echo   - credentials.json (Google OAuth)
echo   - token.json (OAuth tokens)
echo   - *_session/ folders (browser cookies)
echo   - Logs/ (activity logs)
echo   - Needs_Action/, Pending_Approval/, Approved/
echo   - odoo/, postgres/ (Docker data)
echo.

echo ============================================================
echo   READY TO PUSH CHECKLIST
echo ============================================================
echo.
echo Before pushing to GitHub, verify:
echo   [ ] No .env file will be committed
echo   [ ] No credentials.json will be committed
echo   [ ] No token.json files will be committed
echo   [ ] No session folders will be committed
echo   [ ] No Logs folder will be committed
echo   [ ] .gitignore is comprehensive
echo   [ ] README.md is up to date
echo   [ ] GOLD_TIER.md documents all features
echo.
echo If all boxes are checked, you can safely push!
echo.
echo ============================================================
echo.
echo Next steps:
echo   1. Review the files listed above
echo   2. Run: git add .
echo   3. Run: git commit -m "Complete Gold Tier AI Employee implementation"
echo   4. Run: git push origin main
echo.
echo ============================================================
echo.

pause
