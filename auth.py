"""
Authentication and Authorization Module
JWT-based authentication with role-based access control
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import jwt
import os
from models import User, UserRole, db

# Load configuration from environment variables
SECRET_KEY = os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))

# Token blacklist for logout functionality
# In production, use Redis or similar cache
token_blacklist = set()

def generate_token(user):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode and verify JWT token"""
    try:
        # Check if token is blacklisted
        if token in token_blacklist:
            return None

        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def blacklist_token(token):
    """Add token to blacklist (logout)"""
    token_blacklist.add(token)
    return True

def validate_password(password):
    """
    Validate password meets security requirements
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"

    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    return True, None

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def login_required(f):
    """Decorator to protect routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            return jsonify({'error': 'Authentication required', 'message': 'No token provided'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token', 'message': 'Token is invalid or expired'}), 401

        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Attach user to request context
        request.current_user = user

        return f(*args, **kwargs)

    return decorated_function

def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = request.current_user

            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires one of: {[r.value for r in allowed_roles]}'
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator

class PermissionChecker:
    """
    Permission system for granular access control
    Maps roles to permissions for different resources
    """

    # Define permissions for each role
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: {
            'users': ['create', 'read', 'update', 'delete'],
            'companies': ['create', 'read', 'update', 'delete'],
            'contacts': ['create', 'read', 'update', 'delete'],
            'products': ['create', 'read', 'update', 'delete'],
            'orders': ['create', 'read', 'update', 'delete', 'approve'],
            'invoices': ['create', 'read', 'update', 'delete'],
            'payments': ['create', 'read', 'update', 'delete'],
            'shipments': ['create', 'read', 'update', 'delete'],
            'inventory': ['create', 'read', 'update', 'delete', 'adjust'],
            'reports': ['read', 'export'],
            'settings': ['read', 'update'],
        },
        UserRole.MANAGER: {
            'users': ['read'],
            'companies': ['create', 'read', 'update'],
            'contacts': ['create', 'read', 'update'],
            'products': ['create', 'read', 'update'],
            'orders': ['create', 'read', 'update', 'approve'],
            'invoices': ['create', 'read', 'update'],
            'payments': ['create', 'read', 'update'],
            'shipments': ['create', 'read', 'update'],
            'inventory': ['read', 'update'],
            'reports': ['read', 'export'],
            'settings': ['read'],
        },
        UserRole.SALES: {
            'companies': ['create', 'read', 'update'],
            'contacts': ['create', 'read', 'update'],
            'products': ['read'],
            'orders': ['create', 'read', 'update'],
            'invoices': ['read'],
            'payments': ['read'],
            'shipments': ['read'],
            'inventory': ['read'],
            'reports': ['read'],
        },
        UserRole.OPERATIONS: {
            'companies': ['read'],
            'contacts': ['read'],
            'products': ['read', 'update'],
            'orders': ['read', 'update'],
            'invoices': ['read'],
            'payments': ['read'],
            'shipments': ['create', 'read', 'update'],
            'inventory': ['read', 'update', 'adjust'],
            'reports': ['read'],
        },
        UserRole.FINANCE: {
            'companies': ['read'],
            'contacts': ['read'],
            'products': ['read'],
            'orders': ['read'],
            'invoices': ['create', 'read', 'update'],
            'payments': ['create', 'read', 'update'],
            'shipments': ['read'],
            'inventory': ['read'],
            'reports': ['read', 'export'],
        },
        UserRole.WAREHOUSE: {
            'products': ['read'],
            'orders': ['read'],
            'shipments': ['read', 'update'],
            'inventory': ['read', 'update', 'adjust'],
        },
        UserRole.VIEWER: {
            'companies': ['read'],
            'contacts': ['read'],
            'products': ['read'],
            'orders': ['read'],
            'invoices': ['read'],
            'payments': ['read'],
            'shipments': ['read'],
            'inventory': ['read'],
            'reports': ['read'],
        },
    }

    @staticmethod
    def can_user(user, resource, action):
        """Check if user has permission for action on resource"""
        if not user or not user.is_active:
            return False

        role_perms = PermissionChecker.ROLE_PERMISSIONS.get(user.role, {})
        resource_perms = role_perms.get(resource, [])

        return action in resource_perms

    @staticmethod
    def check_permission(resource, action):
        """Decorator to check specific permission"""
        def decorator(f):
            @wraps(f)
            @login_required
            def decorated_function(*args, **kwargs):
                user = request.current_user

                if not PermissionChecker.can_user(user, resource, action):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'You do not have permission to {action} {resource}'
                    }), 403

                return f(*args, **kwargs)

            return decorated_function

        return decorator

# Convenience decorators for common permissions
def can_create(resource):
    return PermissionChecker.check_permission(resource, 'create')

def can_read(resource):
    return PermissionChecker.check_permission(resource, 'read')

def can_update(resource):
    return PermissionChecker.check_permission(resource, 'update')

def can_delete(resource):
    return PermissionChecker.check_permission(resource, 'delete')

def can_approve(resource):
    return PermissionChecker.check_permission(resource, 'approve')
