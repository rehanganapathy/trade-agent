"""
Professional CRM/ERP Flask Application for Global Trade Operations
Complete RESTful API with authentication, CRM, inventory, orders, and integrations
"""

from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List
import json
import os

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename

# Import existing functionality
from agent import fill_form
from vector_db import VectorDB, get_autofill_data

# Import new CRM/ERP modules
from models import db, User, UserRole, Company, CompanyType, Contact, Lead, LeadStatus
from models import Product, Order, OrderStatus, OrderItem, Invoice, Payment, PaymentStatus, PaymentMethod
from models import Shipment, ShipmentStatus, Document, DocumentType, Activity, ActivityType
from models import Task, Notification, Warehouse, InventoryItem, ExchangeRate
from auth import generate_token, login_required, role_required, can_create, can_read, can_update, can_delete, validate_password, blacklist_token
from integrations import IntegrationFactory

# Import HS classifier
try:
    from llm_hs_classifier import get_classifier
    hs_classifier = get_classifier()
    hs_classifier_available = True
except Exception as e:
    print(f"⚠️  LLM HS Classifier not available: {e}")
    hs_classifier = None
    hs_classifier_available = False

# Base directories
BASE_DIR = Path(__file__).parent
TEMPLATE_ROOT = BASE_DIR / "templates"
WEB_ROOT = BASE_DIR / "web"
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=str(WEB_ROOT / "templates"),
    static_folder=str(WEB_ROOT / "static"),
    static_url_path="/static",
)

# Configuration
# Use JWT_SECRET_KEY if available, fallback to SECRET_KEY for consistency with auth.py
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trade_crm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)

# Initialize vector DB for form autofill
try:
    vector_db = VectorDB()
except Exception as e:
    print(f"Warning: Vector DB not available: {e}")
    vector_db = None

# Initialize integration services
payment_service = None
shipping_service = None
email_service = None
exchange_service = None
customs_service = None

try:
    payment_service = IntegrationFactory.get_payment_processor('stripe')
    shipping_service = IntegrationFactory.get_shipping_service()
    email_service = IntegrationFactory.get_email_service()
    exchange_service = IntegrationFactory.get_exchange_rate_service()
    customs_service = IntegrationFactory.get_customs_service()
    print("✅ Integration services initialized")
except Exception as e:
    print(f"⚠️  Some integration services not available: {e}")


def _list_form_templates() -> List[str]:
    """List available form templates"""
    if not TEMPLATE_ROOT.exists():
        return []
    return [p.name for p in TEMPLATE_ROOT.glob("*.json")]


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route("/")
def index():
    """Redirect to CRM dashboard"""
    from flask import redirect
    return redirect('/crm')


@app.route("/crm")
def crm_dashboard():
    """CRM Dashboard - Main Application Interface"""
    return render_template("crm_dashboard.html")


@app.route("/legacy")
def legacy_index():
    """Legacy trade form interface"""
    template_files = _list_form_templates()
    db_available = vector_db is not None
    return render_template("index.html", templates=template_files, db_available=db_available)


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': True,
            'vector_db': vector_db is not None,
            'hs_classifier': hs_classifier_available,
            'payment': payment_service is not None,
            'shipping': shipping_service is not None,
            'email': email_service is not None
        }
    })


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register new user"""
    data = request.get_json()

    # Validate required fields
    required = ['email', 'username', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate password strength
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409

    # Create user
    user = User(
        email=data['email'],
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=UserRole[data.get('role', 'VIEWER').upper()],
        phone=data.get('phone')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = generate_token(user)

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'token': token
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    """User login"""
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate token
    token = generate_token(user)

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    })


@app.route("/api/auth/me", methods=["GET"])
@login_required
def get_current_user():
    """Get current user info"""
    return jsonify(request.current_user.to_dict())


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    """Logout user by blacklisting their token"""
    from auth import get_token_from_header

    token = get_token_from_header()
    if token:
        blacklist_token(token)

    return jsonify({
        'message': 'Logged out successfully'
    }), 200


# ============================================================================
# COMPANY ROUTES
# ============================================================================

@app.route("/api/companies", methods=["GET"])
@can_read('companies')
def get_companies():
    """Get all companies with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    company_type = request.args.get('type')
    search = request.args.get('search')

    query = Company.query

    if company_type:
        query = query.filter_by(company_type=CompanyType[company_type.upper()])

    if search:
        query = query.filter(or_(
            Company.name.ilike(f'%{search}%'),
            Company.email.ilike(f'%{search}%')
        ))

    pagination = query.order_by(Company.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'companies': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route("/api/companies/<int:company_id>", methods=["GET"])
@can_read('companies')
def get_company(company_id):
    """Get company by ID"""
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict(include_relationships=True))


@app.route("/api/companies", methods=["POST"])
@can_create('companies')
def create_company():
    """Create new company"""
    data = request.get_json()

    company = Company(
        name=data['name'],
        legal_name=data.get('legal_name'),
        company_type=CompanyType[data['company_type'].upper()],
        tax_id=data.get('tax_id'),
        website=data.get('website'),
        email=data.get('email'),
        phone=data.get('phone'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
        industry=data.get('industry'),
        payment_terms=data.get('payment_terms'),
        notes=data.get('notes'),
        tags=data.get('tags', [])
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({
        'message': 'Company created successfully',
        'company': company.to_dict()
    }), 201


@app.route("/api/companies/<int:company_id>", methods=["PUT"])
@can_update('companies')
def update_company(company_id):
    """Update company"""
    company = Company.query.get_or_404(company_id)
    data = request.get_json()

    # Update fields
    for field in ['name', 'legal_name', 'tax_id', 'website', 'email', 'phone',
                  'address_line1', 'address_line2', 'city', 'state', 'postal_code',
                  'country', 'industry', 'payment_terms', 'notes', 'tags']:
        if field in data:
            setattr(company, field, data[field])

    if 'company_type' in data:
        company.company_type = CompanyType[data['company_type'].upper()]

    db.session.commit()

    return jsonify({
        'message': 'Company updated successfully',
        'company': company.to_dict()
    })


@app.route("/api/companies/<int:company_id>", methods=["DELETE"])
@can_delete('companies')
def delete_company(company_id):
    """Delete company"""
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()

    return jsonify({'message': 'Company deleted successfully'})


# ============================================================================
# CONTACT ROUTES
# ============================================================================

@app.route("/api/contacts", methods=["GET"])
@can_read('contacts')
def get_contacts():
    """Get all contacts"""
    company_id = request.args.get('company_id', type=int)
    search = request.args.get('search')

    query = Contact.query

    if company_id:
        query = query.filter_by(company_id=company_id)

    if search:
        query = query.filter(or_(
            Contact.first_name.ilike(f'%{search}%'),
            Contact.last_name.ilike(f'%{search}%'),
            Contact.email.ilike(f'%{search}%')
        ))

    contacts = query.all()
    return jsonify([c.to_dict() for c in contacts])


@app.route("/api/contacts", methods=["POST"])
@can_create('contacts')
def create_contact():
    """Create new contact"""
    data = request.get_json()

    contact = Contact(
        company_id=data['company_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        title=data.get('title'),
        department=data.get('department'),
        email=data.get('email'),
        phone=data.get('phone'),
        mobile=data.get('mobile'),
        is_primary=data.get('is_primary', False),
        notes=data.get('notes')
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({
        'message': 'Contact created successfully',
        'contact': contact.to_dict()
    }), 201


# ============================================================================
# LEAD ROUTES
# ============================================================================

@app.route("/api/leads", methods=["GET"])
@can_read('companies')
def get_leads():
    """Get all leads"""
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to', type=int)

    query = Lead.query

    if status:
        query = query.filter_by(status=LeadStatus[status.upper()])
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)

    leads = query.order_by(Lead.created_at.desc()).all()
    return jsonify([l.to_dict() for l in leads])


@app.route("/api/leads", methods=["POST"])
@can_create('companies')
def create_lead():
    """Create new lead"""
    data = request.get_json()

    lead = Lead(
        company_id=data.get('company_id'),
        title=data['title'],
        description=data.get('description'),
        status=LeadStatus[data.get('status', 'NEW').upper()],
        source=data.get('source'),
        estimated_value=data.get('estimated_value'),
        probability=data.get('probability'),
        expected_close_date=datetime.fromisoformat(data['expected_close_date']).date() if data.get('expected_close_date') else None,
        assigned_to=data.get('assigned_to'),
        contact_name=data.get('contact_name'),
        contact_email=data.get('contact_email'),
        contact_phone=data.get('contact_phone'),
        notes=data.get('notes')
    )

    db.session.add(lead)
    db.session.commit()

    return jsonify({
        'message': 'Lead created successfully',
        'lead': lead.to_dict()
    }), 201


# ============================================================================
# PRODUCT ROUTES
# ============================================================================

@app.route("/api/products", methods=["GET"])
@can_read('products')
def get_products():
    """Get all products"""
    category = request.args.get('category')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Product.query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(or_(
            Product.name.ilike(f'%{search}%'),
            Product.sku.ilike(f'%{search}%'),
            Product.description.ilike(f'%{search}%')
        ))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [p.to_dict(include_inventory=True) for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route("/api/products/<int:product_id>", methods=["GET"])
@can_read('products')
def get_product(product_id):
    """Get product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict(include_inventory=True))


@app.route("/api/products", methods=["POST"])
@can_create('products')
def create_product():
    """Create new product"""
    data = request.get_json()

    product = Product(
        sku=data['sku'],
        name=data['name'],
        description=data.get('description'),
        hs_code=data.get('hs_code'),
        category=data.get('category'),
        unit_price=data['unit_price'],
        currency=data.get('currency', 'USD'),
        unit_of_measure=data.get('unit_of_measure'),
        weight=data.get('weight'),
        weight_unit=data.get('weight_unit'),
        length=data.get('length'),
        width=data.get('width'),
        height=data.get('height'),
        dimension_unit=data.get('dimension_unit'),
        origin_country=data.get('origin_country'),
        manufacturer=data.get('manufacturer'),
        brand=data.get('brand'),
        tags=data.get('tags', [])
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201


# ============================================================================
# ORDER ROUTES
# ============================================================================

@app.route("/api/orders", methods=["GET"])
@can_read('orders')
def get_orders():
    """Get all orders"""
    status = request.args.get('status')
    company_id = request.args.get('company_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Order.query

    if status:
        query = query.filter_by(status=OrderStatus[status.upper()])
    if company_id:
        query = query.filter_by(company_id=company_id)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'orders': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route("/api/orders/<int:order_id>", methods=["GET"])
@can_read('orders')
def get_order(order_id):
    """Get order by ID"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict(include_items=True))


@app.route("/api/orders", methods=["POST"])
@can_create('orders')
def create_order():
    """Create new order"""
    data = request.get_json()

    # Generate order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    order = Order(
        order_number=order_number,
        company_id=data['company_id'],
        contact_id=data.get('contact_id'),
        status=OrderStatus.DRAFT,
        order_date=date.today(),
        currency=data.get('currency', 'USD'),
        payment_terms=data.get('payment_terms'),
        incoterm=data.get('incoterm'),
        shipping_address_line1=data.get('shipping_address_line1'),
        shipping_address_line2=data.get('shipping_address_line2'),
        shipping_city=data.get('shipping_city'),
        shipping_state=data.get('shipping_state'),
        shipping_postal_code=data.get('shipping_postal_code'),
        shipping_country=data.get('shipping_country'),
        notes=data.get('notes'),
        sales_person=request.current_user.id
    )

    # Add order items
    subtotal = 0
    for item_data in data.get('items', []):
        product = Product.query.get(item_data['product_id'])
        if not product:
            return jsonify({'error': f"Product {item_data['product_id']} not found"}), 404

        line_total = item_data['quantity'] * item_data['unit_price']
        line_total = line_total * (1 - item_data.get('discount_percent', 0) / 100)

        item = OrderItem(
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            discount_percent=item_data.get('discount_percent', 0),
            tax_percent=item_data.get('tax_percent', 0),
            line_total=line_total
        )
        order.items.append(item)
        subtotal += line_total

    # Calculate totals
    order.subtotal = subtotal
    order.tax_amount = subtotal * (data.get('tax_percent', 0) / 100)
    order.shipping_cost = data.get('shipping_cost', 0)
    order.discount_amount = data.get('discount_amount', 0)
    order.total_amount = order.subtotal + order.tax_amount + order.shipping_cost - order.discount_amount

    db.session.add(order)
    db.session.commit()

    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict(include_items=True)
    }), 201


@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
@can_update('orders')
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    new_status = OrderStatus[data['status'].upper()]
    order.status = new_status

    db.session.commit()

    # Send notification email if shipped
    if new_status == OrderStatus.SHIPPED and email_service:
        # Would send email here
        pass

    return jsonify({
        'message': 'Order status updated',
        'order': order.to_dict()
    })


# ============================================================================
# INVOICE ROUTES
# ============================================================================

@app.route("/api/invoices", methods=["GET"])
@can_read('invoices')
def get_invoices():
    """Get all invoices"""
    status = request.args.get('status')
    company_id = request.args.get('company_id', type=int)

    query = Invoice.query

    if status:
        query = query.filter_by(payment_status=PaymentStatus[status.upper()])
    if company_id:
        query = query.filter_by(company_id=company_id)

    invoices = query.order_by(Invoice.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invoices])


@app.route("/api/invoices", methods=["POST"])
@can_create('invoices')
def create_invoice():
    """Create new invoice"""
    data = request.get_json()

    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Get order if specified
    order = None
    if data.get('order_id'):
        order = Order.query.get(data['order_id'])

    invoice = Invoice(
        invoice_number=invoice_number,
        company_id=data['company_id'],
        order_id=data.get('order_id'),
        invoice_date=date.today(),
        due_date=datetime.fromisoformat(data['due_date']).date(),
        subtotal=data.get('subtotal', order.subtotal if order else 0),
        tax_amount=data.get('tax_amount', order.tax_amount if order else 0),
        total_amount=data.get('total_amount', order.total_amount if order else 0),
        currency=data.get('currency', 'USD'),
        notes=data.get('notes')
    )

    db.session.add(invoice)
    db.session.commit()

    return jsonify({
        'message': 'Invoice created successfully',
        'invoice': invoice.to_dict()
    }), 201


# ============================================================================
# PAYMENT ROUTES
# ============================================================================

@app.route("/api/payments", methods=["POST"])
@can_create('payments')
def record_payment():
    """Record a payment"""
    data = request.get_json()

    invoice = Invoice.query.get_or_404(data['invoice_id'])

    payment = Payment(
        invoice_id=data['invoice_id'],
        amount=data['amount'],
        payment_date=datetime.fromisoformat(data['payment_date']).date() if data.get('payment_date') else date.today(),
        payment_method=data['payment_method'],
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )

    db.session.add(payment)

    # Update invoice paid amount
    invoice.amount_paid += data['amount']

    # Update payment status
    if invoice.amount_paid >= invoice.total_amount:
        invoice.payment_status = PaymentStatus.PAID
    elif invoice.amount_paid > 0:
        invoice.payment_status = PaymentStatus.PARTIAL
    elif date.today() > invoice.due_date:
        invoice.payment_status = PaymentStatus.OVERDUE

    db.session.commit()

    return jsonify({
        'message': 'Payment recorded successfully',
        'payment': payment.to_dict(),
        'invoice': invoice.to_dict()
    }), 201


# ============================================================================
# SHIPMENT ROUTES
# ============================================================================

@app.route("/api/shipments", methods=["GET"])
@can_read('shipments')
def get_shipments():
    """Get all shipments"""
    status = request.args.get('status')
    order_id = request.args.get('order_id', type=int)

    query = Shipment.query

    if status:
        query = query.filter_by(status=ShipmentStatus[status.upper()])
    if order_id:
        query = query.filter_by(order_id=order_id)

    shipments = query.order_by(Shipment.created_at.desc()).all()
    return jsonify([s.to_dict() for s in shipments])


@app.route("/api/shipments", methods=["POST"])
@can_create('shipments')
def create_shipment():
    """Create new shipment"""
    data = request.get_json()

    order = Order.query.get_or_404(data['order_id'])

    shipment = Shipment(
        order_id=data['order_id'],
        company_id=order.company_id,
        carrier=data['carrier'],
        service_type=data.get('service_type'),
        ship_date=datetime.fromisoformat(data['ship_date']).date() if data.get('ship_date') else date.today(),
        destination_address_line1=order.shipping_address_line1,
        destination_address_line2=order.shipping_address_line2,
        destination_city=order.shipping_city,
        destination_state=order.shipping_state,
        destination_postal_code=order.shipping_postal_code,
        destination_country=order.shipping_country,
        total_weight=data.get('total_weight'),
        weight_unit=data.get('weight_unit'),
        number_of_packages=data.get('number_of_packages', 1),
        shipping_cost=data.get('shipping_cost'),
        incoterm=order.incoterm,
        notes=data.get('notes')
    )

    # Create shipment with carrier if integration available
    if shipping_service:
        result = shipping_service.create_shipment(data['carrier'], data)
        if result.get('success'):
            shipment.tracking_number = result.get('tracking_number')

    db.session.add(shipment)

    # Update order status
    order.status = OrderStatus.SHIPPED

    db.session.commit()

    return jsonify({
        'message': 'Shipment created successfully',
        'shipment': shipment.to_dict()
    }), 201


@app.route("/api/shipments/<int:shipment_id>/track", methods=["GET"])
@can_read('shipments')
def track_shipment(shipment_id):
    """Track shipment status"""
    shipment = Shipment.query.get_or_404(shipment_id)

    # Try to get live tracking if integration available
    if shipping_service and shipment.tracking_number:
        tracking_data = shipping_service.track_shipment(shipment.carrier, shipment.tracking_number)
        return jsonify(tracking_data)

    return jsonify(shipment.to_dict())


# ============================================================================
# INVENTORY ROUTES
# ============================================================================

@app.route("/api/inventory", methods=["GET"])
@can_read('inventory')
def get_inventory():
    """Get inventory levels"""
    warehouse_id = request.args.get('warehouse_id', type=int)
    product_id = request.args.get('product_id', type=int)
    low_stock = request.args.get('low_stock', type=bool)

    query = InventoryItem.query

    if warehouse_id:
        query = query.filter_by(warehouse_id=warehouse_id)
    if product_id:
        query = query.filter_by(product_id=product_id)

    items = query.all()

    # Filter low stock items
    if low_stock:
        items = [item for item in items if item.product.reorder_level and item.quantity_available <= item.product.reorder_level]

    return jsonify([item.to_dict() for item in items])


@app.route("/api/inventory/adjust", methods=["POST"])
@can_update('inventory')
def adjust_inventory():
    """Adjust inventory levels"""
    data = request.get_json()

    item = InventoryItem.query.filter_by(
        product_id=data['product_id'],
        warehouse_id=data['warehouse_id']
    ).first()

    if not item:
        # Create new inventory item
        item = InventoryItem(
            product_id=data['product_id'],
            warehouse_id=data['warehouse_id'],
            quantity_available=0
        )
        db.session.add(item)

    # Adjust quantity
    adjustment = data.get('adjustment', 0)
    item.quantity_available += adjustment
    item.last_counted_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Inventory adjusted successfully',
        'inventory': item.to_dict()
    })


# ============================================================================
# WAREHOUSE ROUTES
# ============================================================================

@app.route("/api/warehouses", methods=["GET"])
@can_read('inventory')
def get_warehouses():
    """Get all warehouses"""
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    return jsonify([w.to_dict() for w in warehouses])


@app.route("/api/warehouses", methods=["POST"])
@can_create('inventory')
def create_warehouse():
    """Create new warehouse"""
    data = request.get_json()

    warehouse = Warehouse(
        name=data['name'],
        code=data['code'],
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
        manager_name=data.get('manager_name'),
        phone=data.get('phone')
    )

    db.session.add(warehouse)
    db.session.commit()

    return jsonify({
        'message': 'Warehouse created successfully',
        'warehouse': warehouse.to_dict()
    }), 201


# ============================================================================
# DOCUMENT ROUTES
# ============================================================================

@app.route("/api/documents", methods=["GET"])
@can_read('companies')
def get_documents():
    """Get documents"""
    company_id = request.args.get('company_id', type=int)
    order_id = request.args.get('order_id', type=int)
    document_type = request.args.get('type')

    query = Document.query

    if company_id:
        query = query.filter_by(company_id=company_id)
    if order_id:
        query = query.filter_by(order_id=order_id)
    if document_type:
        query = query.filter_by(document_type=DocumentType[document_type.upper()])

    documents = query.order_by(Document.created_at.desc()).all()
    return jsonify([d.to_dict() for d in documents])


@app.route("/api/documents/upload", methods=["POST"])
@can_create('companies')
def upload_document():
    """Upload a document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Secure filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Create document record
    document = Document(
        document_type=DocumentType[request.form.get('document_type', 'OTHER').upper()],
        title=request.form.get('title', filename),
        file_name=filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type,
        company_id=request.form.get('company_id', type=int),
        order_id=request.form.get('order_id', type=int),
        shipment_id=request.form.get('shipment_id', type=int),
        invoice_id=request.form.get('invoice_id', type=int),
        description=request.form.get('description'),
        uploaded_by=request.current_user.id
    )

    db.session.add(document)
    db.session.commit()

    return jsonify({
        'message': 'Document uploaded successfully',
        'document': document.to_dict()
    }), 201


# ============================================================================
# INTEGRATION ROUTES
# ============================================================================

@app.route("/api/integrations/shipping/rates", methods=["POST"])
@can_read('shipments')
def get_shipping_rates():
    """Get shipping rates from all carriers"""
    data = request.get_json()

    if not shipping_service:
        return jsonify({'error': 'Shipping service not available'}), 503

    rates = shipping_service.get_all_rates(
        origin=data['origin'],
        destination=data['destination'],
        packages=data['packages']
    )

    return jsonify(rates)


@app.route("/api/integrations/exchange-rates", methods=["GET"])
def get_exchange_rates():
    """Get current exchange rates"""
    base_currency = request.args.get('base', 'USD')

    if not exchange_service:
        return jsonify({'error': 'Exchange rate service not available'}), 503

    rates = exchange_service.get_all_rates(base_currency)

    return jsonify({
        'base_currency': base_currency,
        'rates': rates,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route("/api/integrations/convert", methods=["POST"])
def convert_currency():
    """Convert between currencies"""
    data = request.get_json()

    if not exchange_service:
        return jsonify({'error': 'Exchange rate service not available'}), 503

    converted = exchange_service.convert(
        amount=data['amount'],
        from_currency=data['from_currency'],
        to_currency=data['to_currency']
    )

    return jsonify({
        'amount': data['amount'],
        'from_currency': data['from_currency'],
        'to_currency': data['to_currency'],
        'converted_amount': converted
    })


@app.route("/api/integrations/customs/duty", methods=["POST"])
def calculate_duty():
    """Calculate customs duty"""
    data = request.get_json()

    if not customs_service:
        return jsonify({'error': 'Customs service not available'}), 503

    duty = customs_service.calculate_duty(
        hs_code=data['hs_code'],
        value=data['value'],
        origin_country=data['origin_country'],
        destination_country=data['destination_country']
    )

    return jsonify(duty)


# ============================================================================
# EXISTING FORM FILL ROUTES (Keep original functionality)
# ============================================================================

@app.route("/api/fill", methods=["POST"])
@login_required
def api_fill():
    """Fill form using AI (original functionality)"""
    data = request.get_json(force=True)
    template_name = data.get("template")
    prompt = data.get("prompt", "")
    use_db = bool(data.get("use_db", True))
    save_to_db = bool(data.get("save_to_db", False))
    auto_classify_hs = bool(data.get("auto_classify_hs", True))

    if not template_name:
        return jsonify({"error": "template is required"}), 400

    template_path = TEMPLATE_ROOT / template_name
    if not template_path.exists():
        return jsonify({"error": f"template {template_name} not found"}), 404

    with template_path.open() as f:
        template = json.load(f)

    # Get autofill data if enabled
    autofill_data = {}
    if use_db and vector_db:
        autofill_data = get_autofill_data(vector_db, prompt, template_name)

    # Fill form using AI
    filled = fill_form(template, prompt, autofill_data, auto_classify_hs)

    # Save to vector DB if requested
    if save_to_db and vector_db:
        vector_db.add_submission(template_name, filled)

    return jsonify(filled)


@app.route("/api/classify-hs", methods=["POST"])
@login_required
def api_classify_hs():
    """Classify product to HS code"""
    data = request.get_json()
    product_description = data.get("product_description", "")
    top_n = data.get("top_n", 5)

    if not hs_classifier_available:
        return jsonify({"error": "HS classifier not available"}), 503

    results = hs_classifier.classify(product_description, top_n=top_n)

    return jsonify(results)


@app.route("/api/templates", methods=["GET"])
@login_required
def api_list_templates():
    """List all form templates"""
    templates = _list_form_templates()
    return jsonify(templates)


@app.route("/api/templates/<template_name>", methods=["GET"])
@login_required
def api_get_template(template_name):
    """Get template structure"""
    template_path = TEMPLATE_ROOT / template_name
    if not template_path.exists():
        return jsonify({"error": "template not found"}), 404

    with template_path.open() as f:
        template = json.load(f)

    return jsonify(template)


@app.route("/api/history", methods=["GET"])
@login_required
def api_history():
    """Get submission history"""
    if not vector_db:
        return jsonify([])

    query_text = request.args.get("query", "")
    template = request.args.get("template", "")
    limit = int(request.args.get("limit", 10))

    history = vector_db.search_submissions(query_text, template, limit)

    return jsonify(history)


# ============================================================================
# ANALYTICS & REPORTING ROUTES
# ============================================================================

@app.route("/api/analytics/dashboard", methods=["GET"])
@login_required
def get_dashboard_analytics():
    """Get dashboard analytics"""
    # Calculate key metrics
    total_companies = Company.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == PaymentStatus.PAID
    ).scalar() or 0

    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    open_invoices = Invoice.query.filter(
        Invoice.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
    ).count()

    # Recent activity
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_shipments = Shipment.query.order_by(Shipment.created_at.desc()).limit(5).all()

    return jsonify({
        'metrics': {
            'total_companies': total_companies,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'pending_orders': pending_orders,
            'open_invoices': open_invoices
        },
        'recent_orders': [o.to_dict() for o in recent_orders],
        'recent_shipments': [s.to_dict() for s in recent_shipments]
    })


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("✅ Database initialized!")


@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    # Create admin user
    admin = User(
        email='admin@example.com',
        username='admin',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # Create sample warehouse
    warehouse = Warehouse(
        name='Main Warehouse',
        code='WH001',
        city='New York',
        country='USA'
    )
    db.session.add(warehouse)

    db.session.commit()
    print("✅ Database seeded with sample data!")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
