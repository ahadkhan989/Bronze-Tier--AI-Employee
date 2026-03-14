"""
Odoo MCP Server

Model Context Protocol server for Odoo ERP integration.
Provides tools for:
- Creating/managing invoices
- Customer management
- Recording payments
- Generating reports
- Accounting operations

Usage:
    python mcp_servers/odoo_mcp_server.py
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Odoo XML-RPC client
try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    print("Note: xmlrpc.client not available (should be in Python stdlib)")

# MCP server imports
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Note: MCP server not installed.")
    print("Install with: pip install mcp")


class OdooClient:
    """
    Client for Odoo XML-RPC API.
    
    Attributes:
        url: Odoo server URL
        db: Database name
        username: Username
        password: Password
        uid: User ID after authentication
    """

    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo client.

        Args:
            url: Odoo server URL (e.g., http://localhost:8069)
            db: Database name
            username: Username
            password: Password
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self._connect()

    def _connect(self) -> bool:
        """Connect and authenticate to Odoo."""
        try:
            # Common endpoints
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Authenticate
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            
            if self.uid:
                print(f"Connected to Odoo as user ID: {self.uid}")
                return True
            else:
                print("Authentication failed")
                return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def execute(self, model: str, method: str, *args, **kwargs):
        """
        Execute a method on an Odoo model.

        Args:
            model: Model name (e.g., 'account.move')
            method: Method name (e.g., 'create')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Method result
        """
        if not self.uid:
            raise Exception("Not connected to Odoo")

        try:
            object_proxy = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object'
            )
            return object_proxy.execute_kw(
                self.db, self.uid, self.password,
                model, method,
                args, kwargs
            )
        except Exception as e:
            print(f"Error executing {method} on {model}: {e}")
            raise

    def search_read(self, model: str, domain: List = None, 
                    fields: List[str] = None, limit: int = 100) -> List[Dict]:
        """
        Search and read records from a model.

        Args:
            model: Model name
            domain: Search domain (filters)
            fields: Fields to return
            limit: Maximum records to return

        Returns:
            List of records
        """
        if domain is None:
            domain = []
        
        return self.execute(
            model, 'search_read',
            domain,
            fields=fields,
            limit=limit
        )

    def create(self, model: str, values: Dict) -> int:
        """
        Create a new record.

        Args:
            model: Model name
            values: Field values

        Returns:
            Record ID
        """
        return self.execute(model, 'create', [values])

    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """
        Update existing records.

        Args:
            model: Model name
            ids: Record IDs
            values: Field values to update

        Returns:
            True if successful
        """
        return self.execute(model, 'write', ids, values)

    def unlink(self, model: str, ids: List[int]) -> bool:
        """
        Delete records.

        Args:
            model: Model name
            ids: Record IDs

        Returns:
            True if successful
        """
        return self.execute(model, 'unlink', ids)


# Initialize MCP server
if MCP_AVAILABLE:
    mcp = FastMCP("Odoo ERP")
else:
    mcp = None

# Global Odoo client
odoo_client: Optional[OdooClient] = None


def initialize_odoo_client():
    """Initialize Odoo client from environment variables."""
    global odoo_client
    
    from dotenv import load_dotenv
    load_dotenv()

    url = os.getenv('ODOO_URL', 'http://localhost:8069')
    db = os.getenv('ODOO_DB', 'odoo-db')
    username = os.getenv('ODOO_USERNAME', 'admin')
    password = os.getenv('ODOO_PASSWORD', 'admin')

    odoo_client = OdooClient(url, db, username, password)
    return odoo_client is not None


# ============================================================================
# MCP Tools - Odoo Operations
# ============================================================================

@mcp.tool()
def odoo_test_connection() -> Dict:
    """
    Test connection to Odoo ERP.
    
    Returns:
        Connection status and server info
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {
                'success': False,
                'error': 'Failed to connect to Odoo'
            }
    
    try:
        # Get current user info
        user_data = odoo_client.search_read(
            'res.users',
            [('id', '=', odoo_client.uid)],
            ['name', 'login', 'company_id'],
            limit=1
        )
        
        return {
            'success': True,
            'connected': True,
            'user': user_data[0] if user_data else None,
            'url': odoo_client.url,
            'database': odoo_client.db
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_create_customer(name: str, email: str = None, phone: str = None,
                         company: str = None, street: str = None,
                         city: str = None, country: str = None) -> Dict:
    """
    Create a new customer in Odoo.
    
    Args:
        name: Customer name (required)
        email: Email address
        phone: Phone number
        company: Company name
        street: Street address
        city: City
        country: Country name
        
    Returns:
        Customer ID and details
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Prepare customer data
        customer_data = {
            'name': name,
            'company_type': 'person' if not company else 'company',
        }
        
        if email:
            customer_data['email'] = email
        if phone:
            customer_data['phone'] = phone
        if company:
            customer_data['company_name'] = company
        if street:
            customer_data['street'] = street
        if city:
            customer_data['city'] = city
        if country:
            # Find country ID
            countries = odoo_client.search_read(
                'res.country',
                [('name', '=', country)],
                ['id'],
                limit=1
            )
            if countries:
                customer_data['country_id'] = countries[0]['id']
        
        # Create customer
        customer_id = odoo_client.create('res.partner', customer_data)
        
        return {
            'success': True,
            'customer_id': customer_id,
            'name': name,
            'email': email,
            'message': f'Customer created successfully with ID: {customer_id}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_get_customer(customer_id: int = None, email: str = None, 
                      name: str = None) -> Dict:
    """
    Get customer details.
    
    Args:
        customer_id: Customer ID
        email: Customer email (alternative to ID)
        name: Customer name (alternative to ID)
        
    Returns:
        Customer details
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Build search domain
        domain = []
        if customer_id:
            domain.append(('id', '=', customer_id))
        elif email:
            domain.append(('email', '=', email))
        elif name:
            domain.append(('name', 'ilike', name))
        
        if not domain:
            return {'success': False, 'error': 'Must provide customer_id, email, or name'}
        
        # Search for customer
        customers = odoo_client.search_read(
            'res.partner',
            domain,
            ['id', 'name', 'email', 'phone', 'company_name', 
             'street', 'city', 'country_id'],
            limit=1
        )
        
        if customers:
            return {
                'success': True,
                'customer': customers[0]
            }
        else:
            return {
                'success': False,
                'error': 'Customer not found'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_create_invoice(customer_id: int = None, customer_email: str = None,
                        customer_name: str = None, amount: float = 0.0,
                        description: str = 'Invoice', invoice_date: str = None,
                        due_date: str = None) -> Dict:
    """
    Create a new customer invoice.
    
    Args:
        customer_id: Customer ID (or provide email/name)
        customer_email: Customer email
        customer_name: Customer name
        amount: Invoice amount (required)
        description: Invoice description
        invoice_date: Invoice date (YYYY-MM-DD)
        due_date: Due date (YYYY-MM-DD)
        
    Returns:
        Invoice ID and details
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Find customer
        customer = None
        if customer_id:
            customer_result = odoo_get_customer(customer_id=customer_id)
        elif customer_email:
            customer_result = odoo_get_customer(email=customer_email)
        elif customer_name:
            customer_result = odoo_get_customer(name=customer_name)
        else:
            return {'success': False, 'error': 'Must provide customer_id, email, or name'}
        
        if not customer_result.get('success') or not customer_result.get('customer'):
            return {'success': False, 'error': 'Customer not found'}
        
        customer = customer_result['customer']
        
        # Prepare invoice lines
        invoice_line_data = [{
            'product_id': False,
            'name': description,
            'quantity': 1,
            'price_unit': amount,
        }]
        
        # Prepare invoice data
        invoice_data = {
            'move_type': 'out_invoice',
            'partner_id': customer['id'],
            'invoice_line_ids': [(0, 0, line) for line in invoice_line_data],
        }
        
        if invoice_date:
            invoice_data['invoice_date'] = invoice_date
        if due_date:
            invoice_data['invoice_date_due'] = due_date
        
        # Create invoice
        invoice_id = odoo_client.create('account.move', invoice_data)
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'customer': customer['name'],
            'amount': amount,
            'description': description,
            'message': f'Invoice created successfully with ID: {invoice_id}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_list_invoices(limit: int = 10, status: str = None) -> Dict:
    """
    List invoices.
    
    Args:
        limit: Maximum number of invoices
        status: Filter by status (draft, posted, cancel)
        
    Returns:
        List of invoices
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Build search domain
        domain = []
        if status:
            domain.append(('state', '=', status))
        
        # Search invoices
        invoices = odoo_client.search_read(
            'account.move',
            domain,
            ['id', 'name', 'partner_id', 'amount_total', 
             'amount_due', 'state', 'invoice_date', 'invoice_date_due'],
            limit=limit
        )
        
        # Format partner_id (it's a tuple [id, name])
        for invoice in invoices:
            if isinstance(invoice.get('partner_id'), tuple):
                invoice['partner_id'] = invoice['partner_id'][1]
        
        return {
            'success': True,
            'invoices': invoices,
            'count': len(invoices)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_record_payment(invoice_id: int, amount: float = None,
                        payment_date: str = None, reference: str = None) -> Dict:
    """
    Record a payment for an invoice.
    
    Args:
        invoice_id: Invoice ID
        amount: Payment amount (defaults to full amount due)
        payment_date: Payment date (YYYY-MM-DD)
        reference: Payment reference
        
    Returns:
        Payment result
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Get invoice details
        invoices = odoo_client.search_read(
            'account.move',
            [('id', '=', invoice_id)],
            ['id', 'name', 'amount_total', 'amount_due', 'state'],
            limit=1
        )
        
        if not invoices:
            return {'success': False, 'error': 'Invoice not found'}
        
        invoice = invoices[0]
        
        # Use full amount if not specified
        if amount is None:
            amount = invoice['amount_due']
        
        # Register payment
        payment_data = {
            'journal_id': 1,  # Default bank journal
            'payment_method_id': 1,  # Default payment method
            'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d'),
            'amount': amount,
        }
        
        if reference:
            payment_data['payment_reference'] = reference
        
        # Create payment
        payment_wizard = odoo_client.execute(
            'account.register.payments',
            'create',
            [payment_data]
        )
        
        # Validate payment
        odoo_client.execute(
            'account.register.payments',
            'action_create_payments',
            [payment_wizard]
        )
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'amount': amount,
            'message': f'Payment of {amount} recorded for invoice {invoice["name"]}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_generate_revenue_report(month: str = None, 
                                  year: int = None) -> Dict:
    """
    Generate revenue report.
    
    Args:
        month: Month (YYYY-MM)
        year: Year (defaults to current year)
        
    Returns:
        Revenue report data
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        from datetime import datetime
        
        if not year:
            year = datetime.now().year
        
        # Build date domain
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
        
        if month:
            # Filter by month
            domain.append(('invoice_date', '>=', f'{month}-01'))
            next_month = f'{int(month[-2:]) + 1:02d}' if int(month[-2:]) < 12 else '01'
            next_year = str(int(year) + 1) if month.endswith('12') else month[:4]
            domain.append(('invoice_date', '<', f'{next_year}-{next_month}-01'))
        else:
            # Filter by year
            domain.append(('invoice_date', '>=', f'{year}-01-01'))
            domain.append(('invoice_date', '<=', f'{year}-12-31'))
        
        # Get invoices
        invoices = odoo_client.search_read(
            'account.move',
            domain,
            ['id', 'name', 'partner_id', 'amount_total', 'invoice_date'],
            limit=1000
        )
        
        # Calculate totals
        total_revenue = sum(inv['amount_total'] for inv in invoices)
        invoice_count = len(invoices)
        
        # Format invoices
        formatted_invoices = []
        for inv in invoices:
            if isinstance(inv.get('partner_id'), tuple):
                inv['partner_id'] = inv['partner_id'][1]
            formatted_invoices.append(inv)
        
        return {
            'success': True,
            'period': month or str(year),
            'total_revenue': total_revenue,
            'invoice_count': invoice_count,
            'invoices': formatted_invoices[:20]  # Limit for display
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def odoo_get_dashboard_summary() -> Dict:
    """
    Get Odoo dashboard summary for AI Employee briefing.
    
    Returns:
        Summary of key metrics
    """
    global odoo_client
    
    if not odoo_client:
        if not initialize_odoo_client():
            return {'success': False, 'error': 'Failed to connect to Odoo'}
    
    try:
        # Get invoice statistics
        draft_invoices = odoo_client.search_read(
            'account.move',
            [('move_type', '=', 'out_invoice'), ('state', '=', 'draft')],
            ['id'],
            limit=1000
        )
        
        posted_invoices = odoo_client.search_read(
            'account.move',
            [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
            ['amount_total'],
            limit=1000
        )
        
        # Get customer count
        customers = odoo_client.search_read(
            'res.partner',
            [('customer_rank', '>', 0)],
            ['id'],
            limit=1000
        )
        
        return {
            'success': True,
            'draft_invoices': len(draft_invoices),
            'posted_invoices': len(posted_invoices),
            'total_revenue': sum(inv['amount_total'] for inv in posted_invoices),
            'total_customers': len(customers),
            'message': f'Odoo Dashboard: {len(posted_invoices)} invoices, {len(customers)} customers'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main entry point for Odoo MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP server not installed")
        print("Install with: pip install mcp")
        sys.exit(1)
    
    if not ODOO_AVAILABLE:
        print("Error: xmlrpc.client not available")
        sys.exit(1)
    
    print("=" * 60)
    print("Odoo MCP Server")
    print("=" * 60)
    print("\nStarting Odoo MCP server...")
    
    # Initialize Odoo client
    if initialize_odoo_client():
        print("✓ Connected to Odoo")
    else:
        print("✗ Failed to connect to Odoo")
        print("  Make sure .env file is configured correctly")
    
    print("\nAvailable tools:")
    print("  - odoo_test_connection")
    print("  - odoo_create_customer")
    print("  - odoo_get_customer")
    print("  - odoo_create_invoice")
    print("  - odoo_list_invoices")
    print("  - odoo_record_payment")
    print("  - odoo_generate_revenue_report")
    print("  - odoo_get_dashboard_summary")
    print("\nServer running. Press Ctrl+C to stop.")
    
    # Run MCP server
    mcp.run()


if __name__ == '__main__':
    main()
