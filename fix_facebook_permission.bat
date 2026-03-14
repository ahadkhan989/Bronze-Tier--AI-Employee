@echo off
REM =============================================================================
REM Quick Fix for Facebook Permission Error
REM =============================================================================
REM This will help you get the correct token with all required permissions
REM =============================================================================

echo.
echo ============================================================
echo   FACEBOOK PERMISSION FIX - QUICK GUIDE
echo ============================================================
echo.
echo The error "403 Forbidden" means your token is missing permissions.
echo.
echo FOLLOW THESE STEPS EXACTLY:
echo.
echo STEP 1: Go to Graph API Explorer
echo ------------------------------------------------
echo URL: https://developers.facebook.com/tools/explorer/
echo.
echo.
echo STEP 2: Select Your App
echo ------------------------------------------------
echo At the top, select your app: "AI Employee"
echo.
echo.
echo STEP 3: Get PAGE Access Token (IMPORTANT!)
echo ------------------------------------------------
echo 1. Click "Get Token" button (dropdown)
echo 2. Click "Get Page Access Token" (NOT "Get User Token")
echo 3. A popup will appear - login to Facebook if needed
echo 4. SELECT YOUR PAGE from the list (1023318870863610)
echo 5. Click "Next" or "Done"
echo.
echo.
echo STEP 4: Add ALL Required Permissions
echo ------------------------------------------------
echo Click "Add Permissions" and add these ONE BY ONE:
echo.
echo   1. Type: pages_manage_posts
echo      - Click it - Continue - Allow
echo.
echo   2. Type: pages_read_engagement
echo      - Click it - Continue - Allow
echo.
echo   3. Type: pages_read_user_content
echo      - Click it - Continue - Allow   (THIS IS THE KEY ONE!)
echo.
echo   4. Type: pages_show_list
echo      - Click it - Continue - Allow
echo.
echo.
echo STEP 5: Copy the Token
echo ------------------------------------------------
echo The token in the text field is your NEW PAGE TOKEN
echo It starts with: EAAn...
echo Click in the field, press Ctrl+A, then Ctrl+C to copy
echo.
echo.
echo STEP 6: Update Your .env File
echo ------------------------------------------------
echo 1. Open this file in Notepad:
echo    D:\code\Hackathon Project\Bronze-Tier--AI-Employee\.env
echo.
echo 2. Find this line:
echo    FACEBOOK_ACCESS_TOKEN=your_old_token
echo.
echo 3. Replace with your NEW token:
echo    FACEBOOK_ACCESS_TOKEN=EAAn...YOUR_NEW_LONG_TOKEN...
echo.
echo 4. Save the file
echo.
echo.
echo STEP 7: Test
echo ------------------------------------------------
echo Run this command:
echo   python watchers/facebook_watcher.py AI_Employee_Vault --interval 60
echo.
echo You should see:
echo   [OK] Found 0 new Facebook messages
echo   [OK] Found 0 new Facebook comments
echo.
echo Instead of the 403 error!
echo.
echo ============================================================
echo   NEED HELP?
echo ============================================================
echo.
echo If still getting error:
echo 1. Make sure you selected "Get PAGE Access Token" (not User Token)
echo 2. Make sure you added ALL 4 permissions listed above
echo 3. Make sure you updated the .env file and saved it
echo 4. Try generating the token again
echo.
echo Token Debugger: https://developers.facebook.com/tools/debug/access_token/
echo Graph API Explorer: https://developers.facebook.com/tools/explorer/
echo.
echo ============================================================
echo.

pause
