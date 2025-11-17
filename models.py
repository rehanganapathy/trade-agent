"""
Professional CRM/ERP Database Models for Global Trade Operations
SQLAlchemy ORM models for comprehensive trade management system
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Enum as SQLEnum

db = SQLAlchemy()

# ============================================================================
# ENUMS FOR TYPE SAFETY
# ============================================================================

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES = "sales"
    OPERATIONS = "operations"
    FINANCE = "finance"
    WAREHOUSE = "warehouse"
    VIEWER = "viewer"

class CompanyType(enum.Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    BOTH = "both"
    PARTNER = "partner"
    COMPETITOR = "competitor"

class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class OrderStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    READY_TO_SHIP = "ready_to_ship"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    WIRE_TRANSFER = "wire_transfer"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    LETTER_OF_CREDIT = "letter_of_credit"
    CASH = "cash"
    CHECK = "check"

class ShipmentStatus(enum.Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    CUSTOMS_CLEARANCE = "customs_clearance"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    RETURNED = "returned"

class DocumentType(enum.Enum):
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    CUSTOMS_DECLARATION = "customs_declaration"
    PROFORMA_INVOICE = "proforma_invoice"
    CONTRACT = "contract"
    PURCHASE_ORDER = "purchase_order"
    QUOTATION = "quotation"
    OTHER = "other"

class ActivityType(enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    DOCUMENT = "document"

# ============================================================================
# USER MANAGEMENT
# ============================================================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = db.relationship('Activity', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='assigned_to_user', lazy='dynamic', foreign_keys='Task.assigned_to')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'role': self.role.value,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# CRM - COMPANIES & CONTACTS
# ============================================================================

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    legal_name = db.Column(db.String(255))
    company_type = db.Column(SQLEnum(CompanyType), nullable=False)
    tax_id = db.Column(db.String(50))
    website = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))

    # Address fields
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    # Business details
    industry = db.Column(db.String(100))
    annual_revenue = db.Column(db.Float)
    employee_count = db.Column(db.Integer)
    payment_terms = db.Column(db.String(100))  # e.g., "Net 30", "Net 60"
    credit_limit = db.Column(db.Float)

    # Metadata
    notes = db.Column(db.Text)
    tags = db.Column(JSON)
    custom_fields = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts = db.relationship('Contact', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    leads = db.relationship('Lead', backref='company', lazy='dynamic')
    orders = db.relationship('Order', backref='company', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='company', lazy='dynamic')
    shipments = db.relationship('Shipment', backref='company', lazy='dynamic')
    activities = db.relationship('Activity', backref='company', lazy='dynamic')

    def to_dict(self, include_relationships=False):
        data = {
            'id': self.id,
            'name': self.name,
            'legal_name': self.legal_name,
            'company_type': self.company_type.value,
            'tax_id': self.tax_id,
            'website': self.website,
            'email': self.email,
            'phone': self.phone,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'industry': self.industry,
            'annual_revenue': self.annual_revenue,
            'employee_count': self.employee_count,
            'payment_terms': self.payment_terms,
            'credit_limit': self.credit_limit,
            'notes': self.notes,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_relationships:
            data['contacts'] = [c.to_dict() for c in self.contacts.all()]
            data['orders_count'] = self.orders.count()
            data['invoices_count'] = self.invoices.count()

        return data

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))  # Job title
    department = db.Column(db.String(100))
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = db.relationship('Activity', backref='contact', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'title': self.title,
            'department': self.department,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'is_primary': self.is_primary,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# CRM - LEADS & OPPORTUNITIES
# ============================================================================

class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, index=True)
    source = db.Column(db.String(100))  # e.g., "Website", "Referral", "Trade Show"
    estimated_value = db.Column(db.Float)
    probability = db.Column(db.Integer)  # 0-100
    expected_close_date = db.Column(db.Date)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    contact_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = db.relationship('User', backref='assigned_leads', foreign_keys=[assigned_to])

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'source': self.source,
            'estimated_value': self.estimated_value,
            'probability': self.probability,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'assigned_to': self.assigned_to,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# ============================================================================
# PRODUCT MANAGEMENT
# ============================================================================

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    hs_code = db.Column(db.String(20), index=True)
    category = db.Column(db.String(100))
    unit_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    unit_of_measure = db.Column(db.String(50))  # kg, pcs, boxes, etc.

    # Physical dimensions
    weight = db.Column(db.Float)
    weight_unit = db.Column(db.String(10))  # kg, lbs
    length = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    dimension_unit = db.Column(db.String(10))  # cm, in

    # Inventory
    reorder_level = db.Column(db.Integer)
    reorder_quantity = db.Column(db.Integer)

    # Trade specific
    origin_country = db.Column(db.String(100))
    manufacturer = db.Column(db.String(255))
    brand = db.Column(db.String(100))

    # Metadata
    image_url = db.Column(db.String(500))
    tags = db.Column(JSON)
    custom_fields = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

    def to_dict(self, include_inventory=False):
        data = {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'hs_code': self.hs_code,
            'category': self.category,
            'unit_price': self.unit_price,
            'currency': self.currency,
            'unit_of_measure': self.unit_of_measure,
            'dimensions': {
                'weight': self.weight,
                'weight_unit': self.weight_unit,
                'length': self.length,
                'width': self.width,
                'height': self.height,
                'dimension_unit': self.dimension_unit
            },
            'origin_country': self.origin_country,
            'manufacturer': self.manufacturer,
            'brand': self.brand,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

        if include_inventory:
            total_stock = sum(item.quantity_available for item in self.inventory_items.all())
            data['total_stock'] = total_stock

        return data

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

class Warehouse(db.Model):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    manager_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='warehouse', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'manager_name': self.manager_name,
            'phone': self.phone,
            'is_active': self.is_active
        }

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False, index=True)
    quantity_available = db.Column(db.Integer, default=0)
    quantity_reserved = db.Column(db.Integer, default=0)
    quantity_on_order = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))  # Bin/shelf location
    last_counted_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'warehouse_id', name='uix_product_warehouse'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'quantity_available': self.quantity_available,
            'quantity_reserved': self.quantity_reserved,
            'quantity_on_order': self.quantity_on_order,
            'location': self.location,
            'last_counted_at': self.last_counted_at.isoformat() if self.last_counted_at else None,
            'updated_at': self.updated_at.isoformat()
        }

# ============================================================================
# ORDER MANAGEMENT
# ============================================================================

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    status = db.Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT, index=True)
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Financial
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='USD')

    # Payment
    payment_status = db.Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(SQLEnum(PaymentMethod))
    payment_terms = db.Column(db.String(100))

    # Shipping
    incoterm = db.Column(db.String(10))  # FOB, CIF, etc.
    shipping_address_line1 = db.Column(db.String(255))
    shipping_address_line2 = db.Column(db.String(255))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    shipping_country = db.Column(db.String(100))

    # Metadata
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    sales_person = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contact = db.relationship('Contact', backref='orders')
    sales_user = db.relationship('User', backref='orders_created', foreign_keys=[sales_person])
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='order', lazy='dynamic')
    shipments = db.relationship('Shipment', backref='order', lazy='dynamic')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'company_id': self.company_id,
            'contact_id': self.contact_id,
            'status': self.status.value,
            'order_date': self.order_date.isoformat(),
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'shipping_cost': self.shipping_cost,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'payment_status': self.payment_status.value,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'payment_terms': self.payment_terms,
            'incoterm': self.incoterm,
            'shipping_address': {
                'line1': self.shipping_address_line1,
                'line2': self.shipping_address_line2,
                'city': self.shipping_city,
                'state': self.shipping_state,
                'postal_code': self.shipping_postal_code,
                'country': self.shipping_country
            },
            'notes': self.notes,
            'sales_person': self.sales_person,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items.all()]

        return data

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, default=0)
    tax_percent = db.Column(db.Float, default=0)
    line_total = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount_percent': self.discount_percent,
            'tax_percent': self.tax_percent,
            'line_total': self.line_total,
            'notes': self.notes
        }

# ============================================================================
# INVOICE & PAYMENT MANAGEMENT
# ============================================================================

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)

    # Financial
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='USD')

    # Status
    payment_status = db.Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'company_id': self.company_id,
            'order_id': self.order_id,
            'invoice_date': self.invoice_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'amount_paid': self.amount_paid,
            'balance': self.total_amount - self.amount_paid,
            'currency': self.currency,
            'payment_status': self.payment_status.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(SQLEnum(PaymentMethod), nullable=False)
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat(),
            'payment_method': self.payment_method.value,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# SHIPPING & LOGISTICS
# ============================================================================

class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), unique=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    status = db.Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING)

    # Carrier information
    carrier = db.Column(db.String(100))  # FedEx, UPS, DHL, etc.
    service_type = db.Column(db.String(100))  # Express, Standard, etc.

    # Dates
    ship_date = db.Column(db.Date)
    estimated_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)

    # Origin
    origin_address_line1 = db.Column(db.String(255))
    origin_city = db.Column(db.String(100))
    origin_state = db.Column(db.String(100))
    origin_country = db.Column(db.String(100))

    # Destination
    destination_address_line1 = db.Column(db.String(255))
    destination_address_line2 = db.Column(db.String(255))
    destination_city = db.Column(db.String(100))
    destination_state = db.Column(db.String(100))
    destination_postal_code = db.Column(db.String(20))
    destination_country = db.Column(db.String(100))

    # Package details
    total_weight = db.Column(db.Float)
    weight_unit = db.Column(db.String(10))
    number_of_packages = db.Column(db.Integer)

    # Costs
    shipping_cost = db.Column(db.Float)
    insurance_cost = db.Column(db.Float)
    customs_value = db.Column(db.Float)

    # Trade specific
    incoterm = db.Column(db.String(10))
    container_number = db.Column(db.String(50))
    seal_number = db.Column(db.String(50))
    vessel_name = db.Column(db.String(200))
    voyage_number = db.Column(db.String(50))

    # Metadata
    notes = db.Column(db.Text)
    tracking_events = db.Column(JSON)  # Store tracking history
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='shipment', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'order_id': self.order_id,
            'company_id': self.company_id,
            'status': self.status.value,
            'carrier': self.carrier,
            'service_type': self.service_type,
            'ship_date': self.ship_date.isoformat() if self.ship_date else None,
            'estimated_delivery_date': self.estimated_delivery_date.isoformat() if self.estimated_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'origin': {
                'address': self.origin_address_line1,
                'city': self.origin_city,
                'state': self.origin_state,
                'country': self.origin_country
            },
            'destination': {
                'line1': self.destination_address_line1,
                'line2': self.destination_address_line2,
                'city': self.destination_city,
                'state': self.destination_state,
                'postal_code': self.destination_postal_code,
                'country': self.destination_country
            },
            'total_weight': self.total_weight,
            'weight_unit': self.weight_unit,
            'number_of_packages': self.number_of_packages,
            'shipping_cost': self.shipping_cost,
            'incoterm': self.incoterm,
            'container_number': self.container_number,
            'tracking_events': self.tracking_events,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# DOCUMENT MANAGEMENT
# ============================================================================

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(SQLEnum(DocumentType), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(100))

    # Relations
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), index=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), index=True)

    # Versioning
    version = db.Column(db.Integer, default=1)
    parent_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))

    # Metadata
    description = db.Column(db.Text)
    tags = db.Column(JSON)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    uploaded_by_user = db.relationship('User', backref='uploaded_documents', foreign_keys=[uploaded_by])
    parent_document = db.relationship('Document', remote_side=[id], backref='versions')

    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type.value,
            'title': self.title,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'company_id': self.company_id,
            'order_id': self.order_id,
            'shipment_id': self.shipment_id,
            'invoice_id': self.invoice_id,
            'version': self.version,
            'description': self.description,
            'tags': self.tags,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# ACTIVITY TRACKING
# ============================================================================

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(SQLEnum(ActivityType), nullable=False, index=True)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)

    # Timing
    activity_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type.value,
            'subject': self.subject,
            'description': self.description,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'contact_id': self.contact_id,
            'activity_date': self.activity_date.isoformat(),
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# TASK MANAGEMENT
# ============================================================================

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent

    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relations
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)

    # Timing
    due_date = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = db.relationship('User', backref='tasks_created', foreign_keys=[created_by])
    related_company = db.relationship('Company', backref='tasks')
    related_order = db.relationship('Order', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'company_id': self.company_id,
            'order_id': self.order_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# ============================================================================
# NOTIFICATIONS
# ============================================================================

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # info, warning, error, success
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat()
        }

# ============================================================================
# EXCHANGE RATES (for multi-currency support)
# ============================================================================

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'

    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False, index=True)
    to_currency = db.Column(db.String(3), nullable=False, index=True)
    rate = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('from_currency', 'to_currency', 'date', name='uix_currencies_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': self.rate,
            'date': self.date.isoformat()
        }
