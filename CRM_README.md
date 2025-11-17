# Professional CRM/ERP System for Global Trade Operations

## 🌟 Overview

A comprehensive, professional-grade CRM/ERP system designed specifically for global trade operations. Features include customer relationship management, order processing, inventory tracking, shipping logistics, payment processing, and extensive third-party integrations.

## ✨ Key Features

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token management
- **Role-based access control (RBAC)** with 7 different user roles
- **Granular permissions** system for fine-grained access control
- **Password hashing** using Werkzeug security

### 👥 CRM Modules
- **Company Management**: Track customers, suppliers, and partners
- **Contact Management**: Maintain detailed contact information
- **Lead Management**: Sales pipeline with status tracking
- **Activity Tracking**: Log calls, meetings, emails, and notes

### 📦 Product & Inventory
- **Product Catalog**: Comprehensive product information with HS codes
- **Multi-warehouse Support**: Track inventory across multiple locations
- **Stock Management**: Real-time inventory levels and reservations
- **Automatic Reordering**: Low stock alerts and reorder points

### 🛒 Order Management
- **Complete Order Lifecycle**: Draft → Confirmed → Shipped → Delivered
- **Order Items**: Line-item tracking with pricing and discounts
- **Payment Tracking**: Multiple payment statuses and methods
- **Incoterms Support**: FOB, CIF, DDP, and all standard terms

### 💰 Financial Management
- **Invoice Generation**: Automated invoicing from orders
- **Payment Processing**: Stripe and PayPal integration ready
- **Multi-currency Support**: Real-time exchange rates
- **Payment Reconciliation**: Track payments against invoices

### 🚚 Shipping & Logistics
- **Carrier Integrations**: FedEx, UPS, DHL support
- **Tracking**: Real-time shipment tracking
- **Rate Shopping**: Compare rates across carriers
- **Documentation**: Automated trade document generation

### 📊 Analytics & Reporting
- **Dashboard KPIs**: Revenue, orders, customers, shipments
- **Visual Charts**: Revenue trends, order distribution
- **Custom Reports**: Exportable to PDF and Excel
- **Real-time Metrics**: Up-to-the-minute business intelligence

### 🔌 Integrations
- **Payment Processors**: Stripe, PayPal
- **Shipping Carriers**: FedEx, UPS, DHL
- **Email Services**: SMTP, SendGrid, Mailgun
- **Exchange Rates**: Real-time currency conversion
- **Customs**: Duty calculation and landed cost
- **Accounting**: QuickBooks, Xero (ready to integrate)

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework**: Flask 3.0+
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL/MySQL)
- **Authentication**: PyJWT
- **AI/ML**: Groq API with Llama 3.3 70B
- **Vector DB**: ChromaDB for intelligent autofill

**Frontend:**
- **Pure JavaScript** (no framework dependencies)
- **Modern CSS3** with Grid & Flexbox
- **Chart.js** for data visualization
- **Font Awesome** for icons

**Integrations:**
- **Payments**: Stripe SDK
- **Exchange Rates**: Forex-python
- **Email**: Flask-Mail
- **File Processing**: Pillow, ReportLab, OpenPyXL

### Database Schema

```
Users (Authentication)
├── Companies (CRM)
│   ├── Contacts
│   ├── Leads
│   ├── Activities
│   └── Orders
│       ├── Order Items
│       ├── Invoices
│       │   └── Payments
│       └── Shipments
│           └── Documents
├── Products (Catalog)
│   └── Inventory Items
│       └── Warehouses
├── Tasks (Workflow)
└── Notifications
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   cd trade-agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Start the application**
   ```bash
   python crm_app.py
   ```

7. **Access the dashboard**
   ```
   Open: http://localhost:5000/crm_dashboard.html
   ```

### Default Login Credentials

**Admin Account:**
- Email: `admin@tradepro.com`
- Password: `admin123`

**Other Accounts:**
- Manager: `manager@tradepro.com` / `manager123`
- Sales: `sales@tradepro.com` / `sales123`
- Operations: `ops@tradepro.com` / `ops123`
- Finance: `finance@tradepro.com` / `finance123`

## 📖 User Guide

### User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all features and settings |
| **Manager** | Manage CRM, orders, reports (no user management) |
| **Sales** | Create/edit companies, contacts, orders |
| **Operations** | Manage shipments, inventory, products |
| **Finance** | Manage invoices, payments, financial reports |
| **Warehouse** | Manage inventory and shipments |
| **Viewer** | Read-only access to all data |

### Key Workflows

#### 1. Creating a New Customer Order

1. **Navigate to Companies** → Create new company (if needed)
2. **Add Contacts** for the company
3. **Go to Orders** → Create New Order
4. **Select Company** and add order items
5. **Configure shipping** address and incoterms
6. **Submit Order** → Status: Draft
7. **Confirm Order** when ready to process

#### 2. Processing Shipments

1. **Navigate to Orders** → Select confirmed order
2. **Create Shipment** with carrier details
3. **System generates** tracking number
4. **Order status** updates to "Shipped"
5. **Customer receives** shipment notification email

#### 3. Managing Invoices & Payments

1. **System auto-generates** invoice when order confirmed
2. **Navigate to Invoices** → View invoice details
3. **Record Payment** when received
4. **Invoice status** updates automatically
5. **Payment reconciliation** tracked in real-time

#### 4. Inventory Management

1. **Navigate to Inventory** → View stock levels
2. **Adjust Stock** as needed (receiving, cycle counts)
3. **System alerts** for low stock items
4. **Multi-warehouse** tracking available

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=sqlite:///trade_crm.db  # or PostgreSQL for production

# AI Features
GROQ_API_KEY=your_api_key  # Required for AI form filling

# Payment Processing
STRIPE_SECRET_KEY=your_stripe_key
PAYPAL_CLIENT_ID=your_paypal_id

# Shipping
FEDEX_API_KEY=your_fedex_key
UPS_API_KEY=your_ups_key

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

### Database Migration

For production with PostgreSQL:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:pass@localhost/trade_crm

# Initialize database
python init_db.py
```

## 🎨 UI Customization

### Color Scheme

The UI uses CSS variables for easy theming:

```css
:root {
    --primary: #6366f1;      /* Indigo */
    --secondary: #8b5cf6;    /* Purple */
    --success: #10b981;      /* Green */
    --warning: #f59e0b;      /* Amber */
    --danger: #ef4444;       /* Red */
}
```

Edit in `/web/templates/crm_dashboard.html` to customize colors.

### Branding

Update company information in `.env`:

```bash
COMPANY_NAME=Your Company Name
COMPANY_LOGO_URL=https://yoursite.com/logo.png
```

## 📡 API Documentation

### Authentication

All API endpoints (except /api/auth/*) require JWT authentication.

**Login:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJ...",
  "user": { ... }
}
```

**Using Token:**
```bash
GET /api/companies
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...
```

### Key Endpoints

**Companies:**
```
GET    /api/companies              - List all companies
POST   /api/companies              - Create company
GET    /api/companies/<id>         - Get company details
PUT    /api/companies/<id>         - Update company
DELETE /api/companies/<id>         - Delete company
```

**Orders:**
```
GET    /api/orders                 - List all orders
POST   /api/orders                 - Create order
GET    /api/orders/<id>            - Get order details
PUT    /api/orders/<id>/status     - Update order status
```

**Products:**
```
GET    /api/products               - List all products
POST   /api/products               - Create product
GET    /api/products/<id>          - Get product details
```

**Inventory:**
```
GET    /api/inventory              - Get inventory levels
POST   /api/inventory/adjust       - Adjust inventory
```

**Shipments:**
```
GET    /api/shipments              - List all shipments
POST   /api/shipments              - Create shipment
GET    /api/shipments/<id>/track   - Track shipment
```

**Analytics:**
```
GET    /api/analytics/dashboard    - Get dashboard metrics
```

**Integrations:**
```
POST   /api/integrations/shipping/rates     - Get shipping rates
GET    /api/integrations/exchange-rates     - Get exchange rates
POST   /api/integrations/convert            - Convert currency
POST   /api/integrations/customs/duty       - Calculate duty
```

Full API documentation available at: `/api/docs` (coming soon)

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=False`
- [ ] Configure HTTPS/SSL
- [ ] Set up proper email service
- [ ] Configure real payment gateway keys
- [ ] Set up Redis for caching
- [ ] Configure backup strategy
- [ ] Set up monitoring (Sentry)
- [ ] Configure proper CORS origins
- [ ] Review and set all API keys

### Docker Deployment

```bash
# Build image
docker build -t trade-crm .

# Run container
docker run -p 5000:5000 --env-file .env trade-crm
```

### Heroku Deployment

```bash
# Create Heroku app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Initialize database
heroku run python init_db.py
```

## 🤝 Integration Guides

### Stripe Payment Integration

1. Get API keys from Stripe Dashboard
2. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLIC_KEY=pk_live_...
   ```
3. Payments automatically processed through `/api/payments`

### FedEx Shipping Integration

1. Register for FedEx Developer Account
2. Get API credentials
3. Add to `.env`:
   ```
   FEDEX_API_KEY=...
   FEDEX_ACCOUNT_NUMBER=...
   ```
4. Use `/api/shipments` to create shipments

### Email Notifications

1. Configure SMTP settings in `.env`
2. For Gmail, use App Password
3. System automatically sends:
   - Order confirmations
   - Shipment notifications
   - Invoice reminders

## 📊 Data Management

### Backup Database

```bash
# SQLite
cp trade_crm.db trade_crm.db.backup

# PostgreSQL
pg_dump trade_crm > backup.sql
```

### Import/Export Data

```bash
# Export companies to CSV
GET /api/companies?export=csv

# Export orders to Excel
GET /api/orders?export=xlsx
```

## 🐛 Troubleshooting

### Common Issues

**Database connection error:**
- Check `DATABASE_URL` in `.env`
- Ensure database server is running
- Verify credentials

**Authentication fails:**
- Check `SECRET_KEY` is set
- Verify JWT token is being sent
- Check token expiration (24 hours default)

**Integration errors:**
- Verify API keys in `.env`
- Check network connectivity
- Review API rate limits

### Logs

Application logs are in:
- Console output (development)
- `/var/log/trade-crm.log` (production)

## 📞 Support

For issues or questions:
- GitHub Issues: [github.com/yourorg/trade-crm/issues](https://github.com)
- Email: support@tradepro.com
- Documentation: [docs.tradepro.com](https://docs)

## 📄 License

Copyright © 2024 TradePro Global. All rights reserved.

## 🙏 Acknowledgments

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Chart.js** - Data visualization
- **Groq** - AI/LLM capabilities
- **Stripe** - Payment processing
- **All contributors** to the open-source libraries used

---

**Built with ❤️ for global trade professionals**
