## Instructions For Facebook Posting

### For Simple Post Immediately
- python watchers/facebook_poster.py AI_Employee_Vault \ --content "Hello From AI Employee" --platform facebook

### For Post With Approval Workflow
- python watchers/facebook_poster.py AI_Employee_Vault \ --content "Hello From AI Employee" --require approval



#### Start Facebook Watcher 
Open a terminal and run:

2. Start Watcher (Check every 1 minute)
- python watchers/facebook_watcher.py AI_Employee_Vault --interval 60


1. Start Watcher (Check every 5 minutes)
- python watchers/facebook_watcher.py AI_Employee_Vault --interval 300

What it does :
       - Polls Facebook Graph API (Every 5 Minutes).
       - Detects New Messages on your Facebook page.
       - Detects New Comments on your Posts.
       - Creates actions files in Need_Action/ folder.


2. Process Messages with Qwen Code:
When the watchers creates action files, process them.
- cd AI_Employee_Vault
- qwen "Review all facebook messages in Need_Action folder, Draft polite responses for each."

Qwen code will:
  - Read each message/comment
  - Draft appropriate responses
  - Create approval requests in Pending_Approval/


3. Review and Approve Responses:
Open Obsidian and go to :
  - AI_Employee_Vault/Pending_Approval

Review each file, then:
  - Approve: Move file to Approved/
  - Reject : Move file to Rejected/


4. Send Approved Responses:
Run this command:
- python watchers/facebook_poster.py AI_Employee_Vault --process-approved

What happens:
  - Read all approved files.
  - Post responses to Facebook via Graph API.
  - Move files to Done/





## Instructions For ODOO
### Add data to Odoo
First You Need To Add Some Customers And Invoices To Odoo...


1. Open Odoo: http://localhost:8069
2. Login: admin / admin
3. Install CRM App (If not already installed)
4. Add Customers: 
       - Go to CRM -> Customers -> New 
       - Add a few test customers

5. Install Invoicing App
6. Create Invoices:
       - Go to Invoicing -> Customers -> New Invoice
       - Create a few test invoices


#### After that Run these commands to Test and Check

### For Test Connection
- python watchers/odoo_sync_watcher.py AI_Employee_Vault --test-connection

### For Sync Customers
- python watchers/odoo_sync_watcher.py AI_Employee_Vault --sync-customers

### For Sync Invoices
- python watchers/odoo_sync_watcher.py AI_Employee_Vault --sync-invoices

### For Generate Revenue Report
- python watchers/odoo_sync_watcher.py AI_Employee_Vault --generate-report


### Start Watcher (Monitors For New Invoices Every 10 Minutes)
- python watchers/odoo_sync_watcher.py AI_Employee_Vault --interval 600