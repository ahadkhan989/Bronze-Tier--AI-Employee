# Odoo ERP Setup Guide

Complete guide for setting up Odoo Community Edition with Docker Compose for the AI Employee Gold Tier.

---

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **8GB+ RAM** available for Odoo
- **10GB+ disk space** for Odoo data

---

## 🚀 Quick Start

### Step 1: Start Odoo with Docker Compose

```bash
# Navigate to project directory
cd "D:\code\Hackathon Project\Bronze-Tier--AI-Employee"

# Start Odoo and PostgreSQL
docker-compose up -d odoo postgres

# Check status
docker-compose ps

# View logs
docker-compose logs -f odoo
```

### Step 2: Access Odoo

Open your browser and navigate to:
- **URL:** http://localhost:8069
- **Database:** `odoo-db`
- **Email:** `admin`
- **Password:** `admin`

### Step 3: Configure Odoo

1. **Create your company database** (if not auto-created)
2. **Install required apps:**
   - Invoicing
   - Accounting
   - CRM
   - Sales
   - Contacts

### Step 4: Test Connection

```bash
# Test Odoo connection from AI Employee
python watchers/odoo_sync_watcher.py AI_Employee_Vault --test-connection
```

---

## 📁 Directory Structure

```
Bronze-Tier--AI-Employee/
├── docker-compose.yml           # Docker Compose configuration
├── .env                         # Environment variables (create this)
├── odoo/
│   ├── addons/                  # Custom Odoo modules
│   ├── data/                    # Odoo data directory
│   └── logs/                    # Odoo logs
└── postgres/
    └── data/                    # PostgreSQL data
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo-db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# PostgreSQL Configuration
POSTGRES_DB=odoo-db
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo_password

# Security
ODOO_ADMIN_PASSWORD=admin_password
```

### Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| `odoo` | 8069 | Odoo ERP web interface |
| `postgres` | (internal) | PostgreSQL database |
| `pgadmin` | 8080 | Database management (optional) |

---

## 🔧 Common Commands

### Start/Stop Odoo

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart Odoo
docker-compose restart odoo

# Stop and remove everything (WARNING: deletes data)
docker-compose down -v
```

### View Logs

```bash
# View all logs
docker-compose logs

# View Odoo logs only
docker-compose logs odoo

# Follow logs in real-time
docker-compose logs -f odoo

# Last 100 lines
docker-compose logs --tail=100 odoo
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U odoo -d odoo-db

# Backup database
docker-compose exec postgres pg_dump -U odoo odoo-db > backup.sql

# Restore database
docker-compose exec postgres psql -U odoo odoo-db < backup.sql

# List databases
docker-compose exec postgres psql -U odoo -c "\l"
```

### Odoo Shell

```bash
# Access Odoo shell (for debugging)
docker-compose exec odoo odoo shell -d odoo-db
```

---

## 🏗️ Odoo MCP Integration

### Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  Claude Code    │────▶│  Odoo MCP    │────▶│  Odoo ERP    │
│  (AI Employee)  │     │   Server     │     │  (Docker)    │
└─────────────────┘     └──────────────┘     └──────────────┘
```

### Available Odoo Operations

| Operation | Description |
|-----------|-------------|
| **Create Invoice** | Generate new customer invoices |
| **Create Customer** | Add new customer records |
| **Record Payment** | Log invoice payments |
| **List Invoices** | Get invoice list with filters |
| **Get Customer** | Retrieve customer details |
| **Generate Report** | Create financial reports |

### Usage Examples

```bash
# Test connection
python watchers/odoo_sync_watcher.py AI_Employee_Vault --test-connection

# Create customer
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --create-customer \
  --name "John Doe" \
  --email "john@example.com" \
  --phone "+1-555-0123"

# Create invoice
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --create-invoice \
  --customer "John Doe" \
  --amount 1500 \
  --description "Consulting services"

# List invoices
python watchers/odoo_sync_watcher.py AI_Employee_Vault --list-invoices

# Generate revenue report
python watchers/odoo_sync_watcher.py AI_Employee_Vault \
  --generate-report \
  --type monthly_revenue \
  --month 2026-03
```

---

## 🔒 Security Best Practices

### Change Default Passwords

```bash
# After first login, change admin password in Odoo
# Settings → Users & Companies → Users → Administrator → Change Password
```

### Environment Variables

Never commit `.env` file:

```bash
echo ".env" >> .gitignore
```

### Network Security

```yaml
# In docker-compose.yml, restrict network access
networks:
  default:
    name: ai-employee-network
    driver: bridge
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U odoo odoo-db > backups/odoo_backup_$DATE.sql

# Keep last 7 days
find backups/ -name "odoo_backup_*.sql" -mtime +7 -delete
```

---

## 🐛 Troubleshooting

### Odoo Won't Start

```bash
# Check logs
docker-compose logs odoo

# Check if port is in use
netstat -ano | findstr :8069

# Restart with fresh database
docker-compose down -v
docker-compose up -d odoo postgres
```

### Database Connection Error

```bash
# Check PostgreSQL status
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U odoo -d odoo-db -c "SELECT 1"
```

### Odoo is Slow

```bash
# Increase Odoo memory limit
# Edit docker-compose.yml:
# services:
#   odoo:
#     deploy:
#       resources:
#         limits:
#           memory: 4G
```

### Can't Access Odoo

```bash
# Check if Odoo is running
docker-compose ps

# Check firewall settings
# Windows: Allow Docker through Windows Firewall
# Mac: Check System Preferences → Security & Privacy

# Try localhost vs 127.0.0.1
# http://localhost:8069
# http://127.0.0.1:8069
```

---

## 📊 Odoo Apps for AI Employee

Recommended apps to install:

### Core Apps
1. **Invoicing** - Create and manage invoices
2. **Accounting** - Full accounting features
3. **CRM** - Customer relationship management
4. **Sales** - Sales orders and quotations
5. **Contacts** - Customer/contact management

### Optional Apps
6. **Inventory** - Stock management
7. **Purchase** - Purchase orders
8. **Projects** - Project management
9. **Timesheets** - Time tracking
10. **Helpdesk** - Customer support tickets

---

## 🔗 Resources

- **Odoo Documentation:** https://www.odoo.com/documentation
- **Odoo External API:** https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

*Odoo setup complete! Your AI Employee can now integrate with a full-featured ERP system.*
