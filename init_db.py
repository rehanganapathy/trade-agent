"""
Database Initialization and Seeding Script
Creates tables and populates with sample data for CRM/ERP system
"""

from datetime import datetime, date, timedelta
from crm_app import app, db
from models import (
    User, UserRole, Company, CompanyType, Contact, Lead, LeadStatus,
    Product, Warehouse, InventoryItem, Order, OrderStatus, OrderItem,
    Invoice, Payment, PaymentStatus, PaymentMethod, Shipment, ShipmentStatus,
    Document, DocumentType, Activity, ActivityType, Task, Notification,
    ExchangeRate
)


def create_users():
    """Create sample users with different roles"""
    print("Creating users...")

    users_data = [
        {
            'email': 'admin@example.com',
            'username': 'admin',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': UserRole.ADMIN,
            'phone': '+1-555-0100'
        },
        {
            'email': 'admin@tradepro.com',
            'username': 'admin_tradepro',
            'password': 'Admin123!',
            'first_name': 'Trade',
            'last_name': 'Administrator',
            'role': UserRole.ADMIN,
            'phone': '+1-555-0100'
        },
        {
            'email': 'manager@tradepro.com',
            'username': 'manager',
            'password': 'Manager123!',
            'first_name': 'Sarah',
            'last_name': 'Manager',
            'role': UserRole.MANAGER,
            'phone': '+1-555-0101'
        },
        {
            'email': 'sales@tradepro.com',
            'username': 'sales',
            'password': 'Sales123!',
            'first_name': 'John',
            'last_name': 'Sales',
            'role': UserRole.SALES,
            'phone': '+1-555-0102'
        },
        {
            'email': 'ops@tradepro.com',
            'username': 'operations',
            'password': 'Ops123!',
            'first_name': 'Mike',
            'last_name': 'Operations',
            'role': UserRole.OPERATIONS,
            'phone': '+1-555-0103'
        },
        {
            'email': 'finance@tradepro.com',
            'username': 'finance',
            'password': 'Finance123!',
            'first_name': 'Emma',
            'last_name': 'Finance',
            'role': UserRole.FINANCE,
            'phone': '+1-555-0104'
        }
    ]

    users = []
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            phone=user_data['phone']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        users.append(user)

    db.session.commit()
    print(f"✅ Created {len(users)} users")
    return users


def create_companies():
    """Create sample companies"""
    print("Creating companies...")

    companies_data = [
        {
            'name': 'Global Electronics Inc',
            'legal_name': 'Global Electronics Incorporated',
            'company_type': CompanyType.CUSTOMER,
            'tax_id': '12-3456789',
            'email': 'info@globalelectronics.com',
            'phone': '+1-555-1000',
            'address_line1': '123 Tech Drive',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94105',
            'country': 'USA',
            'industry': 'Electronics',
            'payment_terms': 'Net 30',
            'credit_limit': 500000.00
        },
        {
            'name': 'Pacific Traders Ltd',
            'legal_name': 'Pacific Traders Limited',
            'company_type': CompanyType.SUPPLIER,
            'tax_id': '98-7654321',
            'email': 'contact@pacifictraders.com',
            'phone': '+86-21-5555-0001',
            'address_line1': '456 Harbor Road',
            'city': 'Shanghai',
            'state': 'Shanghai',
            'postal_code': '200000',
            'country': 'China',
            'industry': 'Manufacturing',
            'payment_terms': 'Net 60'
        },
        {
            'name': 'European Distribution GmbH',
            'legal_name': 'European Distribution GmbH',
            'company_type': CompanyType.BOTH,
            'tax_id': 'DE123456789',
            'email': 'info@eudist.de',
            'phone': '+49-30-5555-0002',
            'address_line1': '789 Commerce Strasse',
            'city': 'Berlin',
            'state': 'Berlin',
            'postal_code': '10115',
            'country': 'Germany',
            'industry': 'Distribution',
            'payment_terms': 'Net 45',
            'credit_limit': 750000.00
        },
        {
            'name': 'Tokyo Imports Corp',
            'legal_name': 'Tokyo Imports Corporation',
            'company_type': CompanyType.CUSTOMER,
            'tax_id': 'JP-1234567890',
            'email': 'sales@tokyoimports.jp',
            'phone': '+81-3-5555-0003',
            'address_line1': '321 Business District',
            'city': 'Tokyo',
            'state': 'Tokyo',
            'postal_code': '100-0001',
            'country': 'Japan',
            'industry': 'Import/Export',
            'payment_terms': 'Net 30',
            'credit_limit': 350000.00
        },
        {
            'name': 'Dubai Trading House',
            'legal_name': 'Dubai Trading House LLC',
            'company_type': CompanyType.CUSTOMER,
            'tax_id': 'AE-987654321',
            'email': 'info@dubaitrading.ae',
            'phone': '+971-4-5555-0004',
            'address_line1': '555 Trade Center',
            'city': 'Dubai',
            'state': 'Dubai',
            'postal_code': '12345',
            'country': 'UAE',
            'industry': 'Trading',
            'payment_terms': 'Net 15',
            'credit_limit': 600000.00
        }
    ]

    companies = []
    for company_data in companies_data:
        company = Company(**company_data)
        db.session.add(company)
        companies.append(company)

    db.session.commit()
    print(f"✅ Created {len(companies)} companies")
    return companies


def create_contacts(companies):
    """Create sample contacts"""
    print("Creating contacts...")

    contacts = []

    # Global Electronics contacts
    contacts.append(Contact(
        company_id=companies[0].id,
        first_name='Robert',
        last_name='Chen',
        title='Purchasing Manager',
        department='Procurement',
        email='r.chen@globalelectronics.com',
        phone='+1-555-1001',
        is_primary=True
    ))

    # Pacific Traders contacts
    contacts.append(Contact(
        company_id=companies[1].id,
        first_name='Li',
        last_name='Wang',
        title='Sales Director',
        department='Sales',
        email='l.wang@pacifictraders.com',
        phone='+86-21-5555-0011',
        is_primary=True
    ))

    # European Distribution contacts
    contacts.append(Contact(
        company_id=companies[2].id,
        first_name='Anna',
        last_name='Schmidt',
        title='Supply Chain Manager',
        department='Operations',
        email='a.schmidt@eudist.de',
        phone='+49-30-5555-0012',
        is_primary=True
    ))

    for contact in contacts:
        db.session.add(contact)

    db.session.commit()
    print(f"✅ Created {len(contacts)} contacts")
    return contacts


def create_products():
    """Create sample products"""
    print("Creating products...")

    products_data = [
        {
            'sku': 'ELEC-001',
            'name': 'Wireless Bluetooth Headphones',
            'description': 'Premium noise-canceling wireless headphones',
            'hs_code': '8518300000',
            'category': 'Electronics',
            'unit_price': 149.99,
            'currency': 'USD',
            'unit_of_measure': 'pcs',
            'weight': 0.25,
            'weight_unit': 'kg',
            'origin_country': 'China',
            'manufacturer': 'TechSound',
            'brand': 'TechSound Pro'
        },
        {
            'sku': 'ELEC-002',
            'name': 'Smartphone 5G',
            'description': 'Latest generation 5G smartphone',
            'hs_code': '8517120000',
            'category': 'Electronics',
            'unit_price': 899.99,
            'currency': 'USD',
            'unit_of_measure': 'pcs',
            'weight': 0.19,
            'weight_unit': 'kg',
            'origin_country': 'Korea',
            'manufacturer': 'MobileTech',
            'brand': 'MobileTech X'
        },
        {
            'sku': 'ELEC-003',
            'name': 'Laptop Computer',
            'description': 'Business laptop with 16GB RAM',
            'hs_code': '8471300000',
            'category': 'Electronics',
            'unit_price': 1299.99,
            'currency': 'USD',
            'unit_of_measure': 'pcs',
            'weight': 1.8,
            'weight_unit': 'kg',
            'origin_country': 'Taiwan',
            'manufacturer': 'ComputerPro',
            'brand': 'ComputerPro Elite'
        },
        {
            'sku': 'ACC-001',
            'name': 'USB-C Cable',
            'description': 'High-speed USB-C charging cable',
            'hs_code': '8544421000',
            'category': 'Accessories',
            'unit_price': 19.99,
            'currency': 'USD',
            'unit_of_measure': 'pcs',
            'weight': 0.05,
            'weight_unit': 'kg',
            'origin_country': 'China',
            'manufacturer': 'CableWorks'
        },
        {
            'sku': 'ACC-002',
            'name': 'Wireless Mouse',
            'description': 'Ergonomic wireless mouse',
            'hs_code': '8471607100',
            'category': 'Accessories',
            'unit_price': 39.99,
            'currency': 'USD',
            'unit_of_measure': 'pcs',
            'weight': 0.12,
            'weight_unit': 'kg',
            'origin_country': 'China',
            'manufacturer': 'InputDevices'
        }
    ]

    products = []
    for product_data in products_data:
        product = Product(**product_data)
        db.session.add(product)
        products.append(product)

    db.session.commit()
    print(f"✅ Created {len(products)} products")
    return products


def create_warehouses():
    """Create sample warehouses"""
    print("Creating warehouses...")

    warehouses_data = [
        {
            'name': 'US West Coast Warehouse',
            'code': 'WH-US-001',
            'address_line1': '1000 Logistics Way',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90001',
            'country': 'USA',
            'manager_name': 'David Johnson',
            'phone': '+1-555-2000'
        },
        {
            'name': 'Shanghai Distribution Center',
            'code': 'WH-CN-001',
            'address_line1': '200 Warehouse Road',
            'city': 'Shanghai',
            'state': 'Shanghai',
            'postal_code': '201100',
            'country': 'China',
            'manager_name': 'Zhang Wei',
            'phone': '+86-21-5555-2001'
        },
        {
            'name': 'European Hub',
            'code': 'WH-DE-001',
            'address_line1': '50 Lagerstrasse',
            'city': 'Hamburg',
            'state': 'Hamburg',
            'postal_code': '20095',
            'country': 'Germany',
            'manager_name': 'Klaus Mueller',
            'phone': '+49-40-5555-2002'
        }
    ]

    warehouses = []
    for warehouse_data in warehouses_data:
        warehouse = Warehouse(**warehouse_data)
        db.session.add(warehouse)
        warehouses.append(warehouse)

    db.session.commit()
    print(f"✅ Created {len(warehouses)} warehouses")
    return warehouses


def create_inventory(products, warehouses):
    """Create sample inventory"""
    print("Creating inventory...")

    inventory_items = []

    # Add inventory for each product in each warehouse
    for warehouse in warehouses:
        for product in products:
            item = InventoryItem(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_available=100 + (product.id * 10),
                quantity_reserved=5,
                quantity_on_order=20,
                location=f'A{product.id}-B{warehouse.id}',
                last_counted_at=datetime.utcnow()
            )
            db.session.add(item)
            inventory_items.append(item)

    db.session.commit()
    print(f"✅ Created {len(inventory_items)} inventory items")
    return inventory_items


def create_orders(companies, products, users):
    """Create sample orders"""
    print("Creating orders...")

    orders = []

    # Order 1 - Confirmed
    order1 = Order(
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-001",
        company_id=companies[0].id,
        status=OrderStatus.CONFIRMED,
        order_date=date.today() - timedelta(days=5),
        currency='USD',
        payment_status=PaymentStatus.PENDING,
        payment_terms='Net 30',
        incoterm='FOB',
        shipping_address_line1='123 Tech Drive',
        shipping_city='San Francisco',
        shipping_state='CA',
        shipping_postal_code='94105',
        shipping_country='USA',
        notes='Urgent order - expedited shipping required',
        sales_person=users[2].id
    )

    # Add items to order 1
    item1 = OrderItem(
        product_id=products[0].id,
        quantity=50,
        unit_price=149.99,
        line_total=50 * 149.99
    )
    item2 = OrderItem(
        product_id=products[3].id,
        quantity=100,
        unit_price=19.99,
        line_total=100 * 19.99
    )
    order1.items.extend([item1, item2])

    order1.subtotal = sum([item.line_total for item in order1.items])
    order1.tax_amount = order1.subtotal * 0.08
    order1.shipping_cost = 150.00
    order1.total_amount = order1.subtotal + order1.tax_amount + order1.shipping_cost

    orders.append(order1)
    db.session.add(order1)

    # Order 2 - In Production
    order2 = Order(
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-002",
        company_id=companies[2].id,
        status=OrderStatus.IN_PRODUCTION,
        order_date=date.today() - timedelta(days=3),
        currency='EUR',
        payment_status=PaymentStatus.PARTIAL,
        payment_terms='Net 45',
        incoterm='CIF',
        shipping_address_line1='789 Commerce Strasse',
        shipping_city='Berlin',
        shipping_state='Berlin',
        shipping_postal_code='10115',
        shipping_country='Germany',
        sales_person=users[2].id
    )

    item3 = OrderItem(
        product_id=products[1].id,
        quantity=30,
        unit_price=899.99,
        line_total=30 * 899.99
    )
    order2.items.append(item3)

    order2.subtotal = sum([item.line_total for item in order2.items])
    order2.tax_amount = order2.subtotal * 0.19
    order2.shipping_cost = 250.00
    order2.total_amount = order2.subtotal + order2.tax_amount + order2.shipping_cost

    orders.append(order2)
    db.session.add(order2)

    # Order 3 - Shipped
    order3 = Order(
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-003",
        company_id=companies[3].id,
        status=OrderStatus.SHIPPED,
        order_date=date.today() - timedelta(days=10),
        currency='JPY',
        payment_status=PaymentStatus.PAID,
        payment_terms='Net 30',
        incoterm='DDP',
        shipping_address_line1='321 Business District',
        shipping_city='Tokyo',
        shipping_state='Tokyo',
        shipping_postal_code='100-0001',
        shipping_country='Japan',
        sales_person=users[2].id
    )

    item4 = OrderItem(
        product_id=products[2].id,
        quantity=25,
        unit_price=1299.99,
        line_total=25 * 1299.99
    )
    order3.items.append(item4)

    order3.subtotal = sum([item.line_total for item in order3.items])
    order3.tax_amount = order3.subtotal * 0.10
    order3.shipping_cost = 300.00
    order3.total_amount = order3.subtotal + order3.tax_amount + order3.shipping_cost

    orders.append(order3)
    db.session.add(order3)

    db.session.commit()
    print(f"✅ Created {len(orders)} orders")
    return orders


def create_invoices(orders):
    """Create sample invoices"""
    print("Creating invoices...")

    invoices = []

    for order in orders:
        invoice = Invoice(
            invoice_number=f"INV-{order.order_number.replace('ORD', '')}",
            company_id=order.company_id,
            order_id=order.id,
            invoice_date=order.order_date + timedelta(days=1),
            due_date=order.order_date + timedelta(days=30),
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total_amount=order.total_amount,
            currency=order.currency,
            payment_status=order.payment_status
        )

        # Add payments for paid invoices
        if order.payment_status == PaymentStatus.PAID:
            payment = Payment(
                amount=invoice.total_amount,
                payment_date=invoice.due_date - timedelta(days=5),
                payment_method=PaymentMethod.WIRE_TRANSFER,
                reference_number=f"WIRE-{invoice.invoice_number}",
                notes='Payment received via bank transfer'
            )
            invoice.payments.append(payment)
            invoice.amount_paid = invoice.total_amount

        elif order.payment_status == PaymentStatus.PARTIAL:
            payment = Payment(
                amount=invoice.total_amount / 2,
                payment_date=invoice.invoice_date + timedelta(days=15),
                payment_method=PaymentMethod.WIRE_TRANSFER,
                reference_number=f"WIRE-PARTIAL-{invoice.invoice_number}"
            )
            invoice.payments.append(payment)
            invoice.amount_paid = invoice.total_amount / 2

        invoices.append(invoice)
        db.session.add(invoice)

    db.session.commit()
    print(f"✅ Created {len(invoices)} invoices")
    return invoices


def create_shipments(orders):
    """Create sample shipments"""
    print("Creating shipments...")

    shipments = []

    # Only create shipments for shipped orders
    shipped_orders = [o for o in orders if o.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]]

    for order in shipped_orders:
        shipment = Shipment(
            tracking_number=f"FEDEX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{order.id}",
            order_id=order.id,
            company_id=order.company_id,
            status=ShipmentStatus.IN_TRANSIT,
            carrier='FedEx',
            service_type='International Priority',
            ship_date=order.order_date + timedelta(days=3),
            estimated_delivery_date=order.order_date + timedelta(days=10),
            origin_address_line1='1000 Logistics Way',
            origin_city='Los Angeles',
            origin_state='CA',
            origin_country='USA',
            destination_address_line1=order.shipping_address_line1,
            destination_city=order.shipping_city,
            destination_state=order.shipping_state,
            destination_postal_code=order.shipping_postal_code,
            destination_country=order.shipping_country,
            total_weight=50.5,
            weight_unit='kg',
            number_of_packages=3,
            shipping_cost=order.shipping_cost,
            incoterm=order.incoterm,
            tracking_events=[
                {'date': '2024-01-15T10:00:00', 'status': 'Picked up', 'location': 'Los Angeles, CA'},
                {'date': '2024-01-16T14:30:00', 'status': 'In transit', 'location': 'Memphis, TN'},
                {'date': '2024-01-17T08:15:00', 'status': 'Customs clearance', 'location': 'Tokyo, Japan'}
            ]
        )
        shipments.append(shipment)
        db.session.add(shipment)

    db.session.commit()
    print(f"✅ Created {len(shipments)} shipments")
    return shipments


def create_leads(companies, users):
    """Create sample leads"""
    print("Creating leads...")

    leads_data = [
        {
            'company_id': companies[0].id,
            'title': 'Q2 Electronics Purchase',
            'description': 'Large order expected for Q2',
            'status': LeadStatus.QUALIFIED,
            'source': 'Trade Show',
            'estimated_value': 250000.00,
            'probability': 75,
            'expected_close_date': date.today() + timedelta(days=45),
            'assigned_to': users[2].id,
            'contact_name': 'Robert Chen',
            'contact_email': 'r.chen@globalelectronics.com'
        },
        {
            'title': 'New Customer - Tech Startup',
            'description': 'Tech startup looking for bulk electronics',
            'status': LeadStatus.NEW,
            'source': 'Website',
            'estimated_value': 75000.00,
            'probability': 25,
            'expected_close_date': date.today() + timedelta(days=60),
            'assigned_to': users[2].id,
            'contact_name': 'Jane Smith',
            'contact_email': 'jane@techstartup.com'
        }
    ]

    leads = []
    for lead_data in leads_data:
        lead = Lead(**lead_data)
        db.session.add(lead)
        leads.append(lead)

    db.session.commit()
    print(f"✅ Created {len(leads)} leads")
    return leads


def init_database():
    """Initialize the entire database with sample data"""
    print("\n" + "="*80)
    print("INITIALIZING CRM/ERP DATABASE")
    print("="*80 + "\n")

    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        print("✅ Database schema created\n")

        # Create sample data
        users = create_users()
        companies = create_companies()
        contacts = create_contacts(companies)
        products = create_products()
        warehouses = create_warehouses()
        inventory = create_inventory(products, warehouses)
        orders = create_orders(companies, products, users)
        invoices = create_invoices(orders)
        shipments = create_shipments(orders)
        leads = create_leads(companies, users)

        print("\n" + "="*80)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*80)
        print("\n📊 Summary:")
        print(f"   Users: {len(users)}")
        print(f"   Companies: {len(companies)}")
        print(f"   Contacts: {len(contacts)}")
        print(f"   Products: {len(products)}")
        print(f"   Warehouses: {len(warehouses)}")
        print(f"   Inventory Items: {len(inventory)}")
        print(f"   Orders: {len(orders)}")
        print(f"   Invoices: {len(invoices)}")
        print(f"   Shipments: {len(shipments)}")
        print(f"   Leads: {len(leads)}")
        print("\n🔑 Login Credentials:")
        print("   Admin:")
        print("     Email: admin@tradepro.com")
        print("     Password: admin123")
        print("\n   Manager:")
        print("     Email: manager@tradepro.com")
        print("     Password: manager123")
        print("\n   Sales:")
        print("     Email: sales@tradepro.com")
        print("     Password: sales123")
        print("\n🚀 Start the application:")
        print("   python crm_app.py")
        print("\n🌐 Access the dashboard:")
        print("   http://localhost:5000/crm_dashboard.html")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    init_database()
