"""
Odoo Sync Watcher Module

Synchronizes data between AI Employee and Odoo ERP:
- Syncs customers from Odoo to vault
- Syncs invoices from Odoo to vault
- Creates action files for important Odoo events
- Generates financial reports for CEO briefings

Uses Odoo XML-RPC API for integration.

Usage:
    python watchers/odoo_sync_watcher.py /path/to/vault [--interval 600]
"""

import sys
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Odoo XML-RPC client
try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    print("Note: xmlrpc.client not available")


class OdooSyncWatcher(BaseWatcher):
    """
    Watches Odoo ERP for changes and syncs to vault.

    Attributes:
        odoo_url: Odoo server URL
        odoo_db: Database name
        odoo_username: Username
        odoo_password: Password
        odoo: Odoo XML-RPC client
        uid: User ID after authentication
    """

    def __init__(self, vault_path: str, check_interval: int = 600):
        """
        Initialize the Odoo sync watcher.

        Args:
            vault_path: Path to the Obsidian vault directory
            check_interval: How often to check for updates (seconds)
        """
        super().__init__(vault_path, check_interval)

        # Load Odoo credentials
        self._load_credentials()

        # Odoo directories
        self.accounting = self.vault_path / 'Accounting'
        self.invoices = self.vault_path / 'Invoices'
        self.customers = self.vault_path / 'Customers'
        
        for folder in [self.accounting, self.invoices, self.customers]:
            folder.mkdir(parents=True, exist_ok=True)

        # Processed items tracking
        self.processed_invoices_file = self.logs / 'odoo_processed_invoices.json'
        self.processed_invoices = self._load_processed_invoices()

        # Odoo client
        self.odoo = None
        self.uid = None
        self._connect()

    def _load_credentials(self):
        """Load Odoo credentials from environment."""
        from dotenv import load_dotenv
        load_dotenv()

        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo-db')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')

        self.logger.info(f"Odoo URL: {self.odoo_url}")
        self.logger.info(f"Odoo DB: {self.odoo_db}")

    def _load_processed_invoices(self) -> set:
        """Load previously processed invoice IDs."""
        if self.processed_invoices_file.exists():
            try:
                data = json.loads(self.processed_invoices_file.read_text())
                return set(data.get('ids', []))
            except:
                pass
        return set()

    def _save_processed_invoices(self):
        """Save processed invoice IDs."""
        ids_list = list(self.processed_invoices)[-500:]
        self.processed_invoices_file.write_text(
            json.dumps({'ids': ids_list, 'updated': self.get_timestamp()})
        )

    def _connect(self) -> bool:
        """Connect to Odoo."""
        if not ODOO_AVAILABLE:
            self.logger.error("xmlrpc.client not available")
            return False

        try:
            # Common endpoint
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            
            # Authenticate
            self.uid = common.authenticate(
                self.odoo_db, 
                self.odoo_username, 
                self.odoo_password, 
                {}
            )
            
            if self.uid:
                self.logger.info(f"Connected to Odoo (user ID: {self.uid})")
                
                # Object endpoint
                self.odoo = xmlrpc.client.ServerProxy(
                    f'{self.odoo_url}/xmlrpc/2/object'
                )
                return True
            else:
                self.logger.error("Odoo authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"Odoo connection error: {e}")
            return False

    def _execute(self, model: str, method: str, *args, **kwargs):
        """Execute a method on an Odoo model."""
        if not self.uid:
            raise Exception("Not connected to Odoo")

        return self.odoo.execute_kw(
            self.odoo_db, self.uid, self.odoo_password,
            model, method,
            args, kwargs
        )

    def _search_read(self, model: str, domain: List = None, 
                     fields: List[str] = None, limit: int = 100) -> List[Dict]:
        """Search and read records."""
        if domain is None:
            domain = []
        
        return self._execute(
            model, 'search_read',
            domain,
            fields=fields,
            limit=limit
        )

    def _check_new_invoices(self) -> List[Dict]:
        """Check for new invoices in Odoo."""
        invoices = []

        try:
            # Get invoices from last check
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', yesterday)
            ]
            
            invoices_data = self._search_read(
                'account.move',
                domain,
                ['id', 'name', 'partner_id', 'amount_total',
                 'amount_residual', 'state', 'invoice_date', 'invoice_date_due'],
                limit=50
            )
            
            for inv in invoices_data:
                if inv['id'] not in self.processed_invoices:
                    # Format partner_id (tuple [id, name])
                    if isinstance(inv.get('partner_id'), tuple):
                        inv['partner_id'] = inv['partner_id'][1]
                    
                    invoices.append(inv)
                    self.processed_invoices.add(inv['id'])

        except Exception as e:
            self.logger.error(f"Error checking invoices: {e}")

        return invoices

    def _check_overdue_invoices(self) -> List[Dict]:
        """Check for overdue invoices."""
        overdue = []

        try:
            # Get overdue invoices
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('invoice_date_due', '<', datetime.now().strftime('%Y-%m-%d'))
            ]
            
            invoices_data = self._search_read(
                'account.move',
                domain,
                ['id', 'name', 'partner_id', 'amount_residual',
                 'invoice_date_due', 'state'],
                limit=50
            )
            
            for inv in invoices_data:
                if isinstance(inv.get('partner_id'), tuple):
                    inv['partner_id'] = inv['partner_id'][1]
                overdue.append(inv)

        except Exception as e:
            self.logger.error(f"Error checking overdue invoices: {e}")

        return overdue

    def _get_dashboard_data(self) -> Dict:
        """Get dashboard data from Odoo."""
        try:
            # Get invoice statistics
            draft = self._search_read(
                'account.move',
                [('move_type', '=', 'out_invoice'), ('state', '=', 'draft')],
                ['id'],
                limit=1000
            )
            
            posted = self._search_read(
                'account.move',
                [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
                ['amount_total'],
                limit=1000
            )
            
            customers = self._search_read(
                'res.partner',
                [('customer_rank', '>', 0)],
                ['id'],
                limit=1000
            )
            
            return {
                'draft_invoices': len(draft),
                'posted_invoices': len(posted),
                'total_revenue': sum(inv['amount_total'] for inv in posted),
                'total_customers': len(customers)
            }

        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {}

    def check_for_updates(self) -> List[Dict]:
        """
        Check Odoo for updates.

        Returns:
            List of update dictionaries
        """
        if not self.odoo:
            if not self._connect():
                return []

        updates = []

        # Check new invoices
        new_invoices = self._check_new_invoices()
        for inv in new_invoices:
            updates.append({
                'type': 'new_invoice',
                'data': inv
            })

        # Check overdue invoices
        overdue = self._check_overdue_invoices()
        for inv in overdue:
            updates.append({
                'type': 'overdue_invoice',
                'data': inv
            })

        # Save processed invoices
        if new_invoices:
            self._save_processed_invoices()

        return updates

    def create_action_file(self, item: Dict) -> Optional[Path]:
        """
        Create a .md action file for an Odoo update.

        Args:
            item: Update dictionary

        Returns:
            Path to the created file
        """
        try:
            item_type = item['type']
            data = item['data']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if item_type == 'new_invoice':
                filename = f"ODOO_INVOICE_{timestamp}_{data['name']}.md"
                content = self._create_invoice_action_file(data)
            elif item_type == 'overdue_invoice':
                filename = f"ODOO_OVERDUE_{timestamp}_{data['name']}.md"
                content = self._create_overdue_action_file(data)
            else:
                return None

            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def _create_invoice_action_file(self, invoice: Dict) -> str:
        """Create action file for new invoice."""
        return f"""---
type: odoo_invoice
source: odoo_erp
invoice_id: {invoice['id']}
invoice_name: {invoice['name']}
customer: {invoice['partner_id']}
amount: {invoice['amount_total']}
due_date: {invoice.get('invoice_date_due', 'N/A')}
received: {self.get_timestamp()}
priority: normal
status: pending
---

# Odoo Invoice: {invoice['name']}

## Invoice Details
- **Invoice ID:** {invoice['id']}
- **Invoice Number:** {invoice['name']}
- **Customer:** {invoice['partner_id']}
- **Amount:** ${invoice['amount_total']}
- **Amount Due:** ${invoice.get('amount_residual', 0)}
- **Invoice Date:** {invoice.get('invoice_date', 'N/A')}
- **Due Date:** {invoice.get('invoice_date_due', 'N/A')}
- **Status:** {invoice['state']}

---

## Suggested Actions

- [ ] Review invoice details
- [ ] Send invoice to customer
- [ ] Schedule follow-up
- [ ] Record in accounting
- [ ] Move to /Done when complete

---

## Processing Notes

*Add notes here during processing*

---
*Created by OdooSyncWatcher*
"""

    def _create_overdue_action_file(self, invoice: Dict) -> str:
        """Create action file for overdue invoice."""
        return f"""---
type: odoo_overdue
source: odoo_erp
invoice_id: {invoice['id']}
invoice_name: {invoice['name']}
customer: {invoice['partner_id']}
amount_due: {invoice.get('amount_residual', 0)}
original_due_date: {invoice.get('invoice_date_due', 'N/A')}
received: {self.get_timestamp()}
priority: high
status: pending
---

# ⚠️ OVERDUE Invoice: {invoice['name']}

## Invoice Details
- **Invoice ID:** {invoice['id']}
- **Invoice Number:** {invoice['name']}
- **Customer:** {invoice['partner_id']}
- **Amount Due:** ${invoice.get('amount_residual', 0)}
- **Original Due Date:** {invoice.get('invoice_date_due', 'N/A')}
- **Status:** {invoice['state']}

---

## ⚠️ Action Required

This invoice is **OVERDUE** and requires immediate attention.

---

## Suggested Actions

- [ ] Contact customer for payment
- [ ] Send payment reminder
- [ ] Create approval for follow-up email
- [ ] Update payment status in Odoo
- [ ] Move to /Done when resolved

---

## Processing Notes

*Add notes here during processing*

---
*Created by OdooSyncWatcher*
"""

    def sync_customers_to_vault(self):
        """Sync all customers from Odoo to vault."""
        if not self.odoo:
            if not self._connect():
                return 0

        try:
            customers = self._search_read(
                'res.partner',
                [('customer_rank', '>', 0)],
                ['id', 'name', 'email', 'phone', 'company_name',
                 'street', 'city', 'country_id'],
                limit=1000
            )

            synced = 0
            for customer in customers:
                try:
                    # Create customer file
                    customer_file = self.customers / f"CUSTOMER_{customer['id']}_{self.sanitize_filename(customer['name'])}.md"
                    
                    # Format country
                    country = ''
                    if customer.get('country_id') and isinstance(customer['country_id'], tuple):
                        country = customer['country_id'][1]

                    content = f"""---
type: customer
source: odoo_erp
customer_id: {customer['id']}
name: {customer['name']}
email: {customer.get('email', '')}
phone: {customer.get('phone', '')}
company: {customer.get('company_name', '')}
city: {customer.get('city', '')}
country: {country}
synced: {self.get_timestamp()}
---

# Customer: {customer['name']}

## Contact Information
- **Customer ID:** {customer['id']}
- **Name:** {customer['name']}
- **Email:** {customer.get('email', 'N/A')}
- **Phone:** {customer.get('phone', 'N/A')}
- **Company:** {customer.get('company_name', 'N/A')}

## Address
- **Street:** {customer.get('street', 'N/A')}
- **City:** {customer.get('city', 'N/A')}
- **Country:** {country or 'N/A'}

---

*Synced from Odoo ERP*
"""

                    customer_file.write_text(content, encoding='utf-8')
                    synced += 1

                except Exception as e:
                    self.logger.error(f"Error syncing customer {customer['id']}: {e}")

            self.logger.info(f"Synced {synced} customers from Odoo")
            return synced

        except Exception as e:
            self.logger.error(f"Error syncing customers: {e}")
            return 0

    def sync_invoices_to_vault(self, limit: int = 100):
        """Sync invoices from Odoo to vault."""
        if not self.odoo:
            if not self._connect():
                return 0

        try:
            invoices = self._search_read(
                'account.move',
                [('move_type', '=', 'out_invoice')],
                ['id', 'name', 'partner_id', 'amount_total',
                 'amount_residual', 'state', 'invoice_date', 'invoice_date_due'],
                limit=limit
            )

            synced = 0
            for inv in invoices:
                try:
                    # Format partner_id
                    if isinstance(inv.get('partner_id'), tuple):
                        inv['partner_id'] = inv['partner_id'][1]

                    # Create invoice file (sanitize filename - remove slashes)
                    safe_name = inv['name'].replace('/', '_')
                    invoice_file = self.invoices / f"INVOICE_{inv['id']}_{safe_name}.md"

                    content = f"""---
type: invoice
source: odoo_erp
invoice_id: {inv['id']}
invoice_number: {inv['name']}
customer: {inv['partner_id']}
amount: {inv['amount_total']}
amount_due: {inv.get('amount_residual', 0)}
invoice_date: {inv.get('invoice_date', 'N/A')}
due_date: {inv.get('invoice_date_due', 'N/A')}
status: {inv['state']}
synced: {self.get_timestamp()}
---

# Invoice: {inv['name']}

## Invoice Details
- **Invoice ID:** {inv['id']}
- **Invoice Number:** {inv['name']}
- **Customer:** {inv['partner_id']}
- **Total Amount:** ${inv['amount_total']}
- **Amount Due:** ${inv.get('amount_residual', 0)}
- **Invoice Date:** {inv.get('invoice_date', 'N/A')}
- **Due Date:** {inv.get('invoice_date_due', 'N/A')}
- **Status:** {inv['state']}

---

*Synced from Odoo ERP*
"""

                    invoice_file.write_text(content, encoding='utf-8')
                    synced += 1

                except Exception as e:
                    self.logger.error(f"Error syncing invoice {inv['id']}: {e}")

            self.logger.info(f"Synced {synced} invoices from Odoo")
            return synced

        except Exception as e:
            self.logger.error(f"Error syncing invoices: {e}")
            return 0

    def generate_revenue_report(self, month: str = None) -> Optional[Path]:
        """Generate revenue report from Odoo data."""
        if not self.odoo:
            if not self._connect():
                return None

        try:
            if not month:
                month = datetime.now().strftime('%Y-%m')

            # Get invoices for the month
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', f'{month}-01')
            ]

            # Calculate next month
            year, month_num = month.split('-')
            next_month_num = int(month_num) + 1
            next_year = int(year)
            if next_month_num > 12:
                next_month_num = 1
                next_year += 1

            domain.append(('invoice_date', '<', f'{next_year}-{next_month_num:02d}-01'))

            invoices = self._search_read(
                'account.move',
                domain,
                ['id', 'name', 'partner_id', 'amount_total', 'invoice_date'],
                limit=1000
            )

            # Calculate totals
            total_revenue = sum(inv['amount_total'] for inv in invoices)
            invoice_count = len(invoices)
            average_invoice = total_revenue / invoice_count if invoice_count > 0 else 0

            # Create report file
            report_file = self.accounting / f"REVENUE_REPORT_{month}.md"

            content = f"""---
type: revenue_report
source: odoo_erp
period: {month}
generated: {self.get_timestamp()}
total_revenue: {total_revenue}
invoice_count: {invoice_count}
---

# Revenue Report: {month}

## Summary
- **Total Revenue:** ${total_revenue:,.2f}
- **Total Invoices:** {invoice_count}
- **Average Invoice:** ${average_invoice:,.2f}

---

## Invoice Details

| Invoice # | Customer | Amount | Date |
|-----------|----------|--------|------|
"""

            for inv in invoices[:50]:  # Limit table size
                customer = inv['partner_id']
                if isinstance(customer, tuple):
                    customer = customer[1]
                content += f"| {inv['name']} | {customer} | ${inv['amount_total']:,.2f} | {inv['invoice_date']} |\n"

            content += f"""
---

*Generated by OdooSyncWatcher from Odoo ERP*
"""

            report_file.write_text(content, encoding='utf-8')
            self.logger.info(f"Generated revenue report: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Error generating revenue report: {e}")
            return None

    def test_connection(self) -> bool:
        """Test Odoo connection."""
        if not self.odoo:
            if not self._connect():
                print("✗ Failed to connect to Odoo")
                return False

        try:
            # Get current user
            users = self._search_read(
                'res.users',
                [('id', '=', self.uid)],
                ['name', 'login'],
                limit=1
            )

            if users:
                print("✓ Connected to Odoo")
                print(f"  User: {users[0]['name']} ({users[0]['login']})")
                print(f"  URL: {self.odoo_url}")
                print(f"  Database: {self.odoo_db}")
                return True
            else:
                print("✗ Connected but couldn't get user info")
                return False

        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Odoo URL: {self.odoo_url}')

        if not self.odoo:
            if not self._connect():
                self.logger.error("Failed to connect to Odoo. Check credentials.")
                return

        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} Odoo update(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    self.logger.info(f'Created: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No Odoo updates')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self._connect()  # Try to reconnect

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Sync Watcher')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=600,
                       help='Check interval in seconds (default: 600)')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Odoo connection')
    parser.add_argument('--sync-customers', action='store_true',
                       help='Sync customers from Odoo')
    parser.add_argument('--sync-invoices', action='store_true',
                       help='Sync invoices from Odoo')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate revenue report')
    parser.add_argument('--month', '-m', help='Month for report (YYYY-MM)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')

    args = parser.parse_args()

    if not ODOO_AVAILABLE:
        print("Error: xmlrpc.client not available")
        sys.exit(1)

    watcher = OdooSyncWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval
    )

    if args.test_connection:
        success = watcher.test_connection()
        sys.exit(0 if success else 1)
    elif args.sync_customers:
        count = watcher.sync_customers_to_vault()
        print(f"Synced {count} customers")
        sys.exit(0)
    elif args.sync_invoices:
        count = watcher.sync_invoices_to_vault()
        print(f"Synced {count} invoices")
        sys.exit(0)
    elif args.generate_report:
        report = watcher.generate_revenue_report(args.month)
        if report:
            print(f"Report generated: {report}")
            sys.exit(0)
        sys.exit(1)
    elif args.once:
        count = watcher.run_once() if hasattr(watcher, 'run_once') else 0
        print(f"Processed {count} items")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
