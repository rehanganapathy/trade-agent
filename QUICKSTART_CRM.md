# 🚀 Quick Start Guide - Professional CRM/ERP System

## ⚡ Fastest Way to Get Started (3 Steps)

### Step 1: Start the Application
```bash
cd /home/user/trade-agent
python crm_app.py
```

### Step 2: Open the Dashboard
Open your browser and navigate to:
```
http://localhost:5000/crm_dashboard.html
```

### Step 3: Login
Use these credentials:
- **Email**: `admin@tradepro.com`
- **Password**: `admin123`

That's it! You're now running a full-featured CRM/ERP system! 🎉

---

## 📋 What's Included

Your system is pre-loaded with sample data:

- **5 Users** (Admin, Manager, Sales, Operations, Finance)
- **5 Companies** (customers and suppliers across USA, China, Germany, Japan, UAE)
- **3 Contacts** (key contacts for companies)
- **5 Products** (electronics with HS codes)
- **3 Warehouses** (US, China, Germany)
- **15 Inventory Items** (stock across warehouses)
- **3 Orders** (in various statuses)
- **3 Invoices** (pending and paid)
- **1 Shipment** (in transit)
- **2 Leads** (sales opportunities)

---

## 🎯 What You Can Do

### 1. Dashboard
- View key metrics (revenue, orders, customers, shipments)
- See revenue trends (12-month chart)
- View order status distribution
- Browse recent orders

### 2. CRM Functions
- **Companies**: Create, view, edit customer and supplier records
- **Contacts**: Manage contact information
- **Leads**: Track sales opportunities through the pipeline

### 3. Operations
- **Products**: Manage product catalog with HS codes
- **Inventory**: Track stock across multiple warehouses
- **Orders**: Create and manage orders from draft to delivery
- **Shipments**: Track shipments with carrier integration

### 4. Finance
- **Invoices**: Generate and manage invoices
- **Payments**: Record and reconcile payments
- **Multi-currency**: Support for USD, EUR, JPY, CNY, etc.

---

## 🔑 User Accounts & Roles

| Email | Password | Role | Can Do |
|-------|----------|------|--------|
| admin@tradepro.com | admin123 | Admin | Everything |
| manager@tradepro.com | manager123 | Manager | Manage CRM, orders, reports |
| sales@tradepro.com | sales123 | Sales | Create orders, manage customers |
| ops@tradepro.com | ops123 | Operations | Shipments, inventory |
| finance@tradepro.com | finance123 | Finance | Invoices, payments |

---

## 🎨 Features to Explore

### Try These Actions:

1. **Create a New Company**
   - Click "CRM" → "Companies" → "+ New Company"
   - Fill in details and save
   - Notice it appears in the companies list

2. **Create a New Order**
   - Click "Orders" → "+ New Order"
   - Select a company
   - Add products
   - See order total calculated automatically

3. **View Dashboard Analytics**
   - Charts update in real-time
   - Revenue trends show last 12 months
   - Order status shows distribution

4. **Search & Filter**
   - Use the global search in top nav
   - Filter tables by status
   - Sort columns by clicking headers

---

## 🔧 Configuration

The system is configured via environment variables in `.env`:

```bash
# Key Settings
DATABASE_URL=sqlite:///trade_crm.db  # Database location
SECRET_KEY=...                        # Security key
GROQ_API_KEY=...                     # AI features (optional)
```

---

## 📊 Sample Data Details

### Companies Included:
1. **Global Electronics Inc** (USA) - Customer
2. **Pacific Traders Ltd** (China) - Supplier
3. **European Distribution GmbH** (Germany) - Both
4. **Tokyo Imports Corp** (Japan) - Customer
5. **Dubai Trading House** (UAE) - Customer

### Products Included:
1. Wireless Bluetooth Headphones - $149.99
2. Smartphone 5G - $899.99
3. Laptop Computer - $1,299.99
4. USB-C Cable - $19.99
5. Wireless Mouse - $39.99

---

## 🌐 API Access

The system also provides a full REST API:

```bash
# Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tradepro.com","password":"admin123"}'

# Use token to access API
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/companies
```

---

## 🎓 Next Steps

### For Development:
1. Add your own companies and products
2. Configure payment integrations (Stripe, PayPal)
3. Set up shipping carrier APIs (FedEx, UPS, DHL)
4. Enable email notifications

### For Production:
1. Change all passwords and secret keys
2. Switch to PostgreSQL database
3. Configure SSL/HTTPS
4. Set up proper email service
5. Add real payment gateway keys

---

## 📚 Documentation

- **Full Documentation**: See `CRM_README.md`
- **API Reference**: See `API_DOCUMENTATION.md` (coming soon)
- **Environment Config**: See `.env.example`
- **Database Schema**: See `models.py`

---

## 🐛 Troubleshooting

### Application won't start?
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Check if database exists
ls -la trade_crm.db

# Reinitialize if needed
python init_db.py
```

### Can't login?
- Make sure you're using the correct email/password
- Check the database was initialized (run `python init_db.py`)
- Clear browser cache and try again

### Dashboard not loading?
- Check the URL: `http://localhost:5000/crm_dashboard.html`
- Open browser console (F12) to see any errors
- Verify the application is running

---

## 💡 Tips

1. **Keyboard Shortcuts**: Use browser dev tools (F12) to see API calls
2. **Real-time Updates**: Refresh the page to see latest data
3. **Export Data**: Use the export buttons on tables
4. **Search**: Global search works across all modules
5. **Filters**: Click column headers to sort tables

---

## 🎉 You're Ready!

You now have a fully functional CRM/ERP system for global trade operations!

**What makes this special:**
- ✅ Professional UI/UX like Salesforce or SAP
- ✅ Complete CRM functionality
- ✅ Order and inventory management
- ✅ Shipping and logistics tracking
- ✅ Financial management
- ✅ Multi-currency support
- ✅ Ready for real integrations
- ✅ Scalable architecture
- ✅ Production-ready codebase

**Start using it immediately for:**
- Managing international trade operations
- Tracking global shipments
- Processing orders across countries
- Managing multi-warehouse inventory
- Handling multi-currency transactions
- Generating trade documents
- Monitoring business analytics

---

**Need Help?**
- 📖 Read the full documentation in `CRM_README.md`
- 🔧 Check configuration in `.env.example`
- 💻 Explore the code in `crm_app.py` and `models.py`
- 🌐 Test the API endpoints

**Happy Trading! 🚀**
