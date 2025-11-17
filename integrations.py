"""
Third-Party Integration Services for Global Trade CRM/ERP
Payment processors, Shipping carriers, Email, Exchange rates, etc.
"""

import requests
from datetime import datetime, date
import os
from typing import Dict, List, Optional
import stripe
from forex_python.converter import CurrencyRates, RatesNotAvailableError


# ============================================================================
# PAYMENT INTEGRATIONS
# ============================================================================

class PaymentProcessor:
    """Base class for payment processors"""

    def process_payment(self, amount: float, currency: str, payment_method: str, metadata: dict) -> dict:
        raise NotImplementedError

    def refund_payment(self, transaction_id: str, amount: float = None) -> dict:
        raise NotImplementedError

    def get_payment_status(self, transaction_id: str) -> dict:
        raise NotImplementedError


class StripePaymentProcessor(PaymentProcessor):
    """Stripe payment integration"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('STRIPE_SECRET_KEY')
        if self.api_key:
            stripe.api_key = self.api_key

    def process_payment(self, amount: float, currency: str, payment_method: str, metadata: dict) -> dict:
        """
        Process payment through Stripe
        amount: in smallest currency unit (cents for USD)
        """
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method,
                confirm=True,
                metadata=metadata,
                automatic_payment_methods={'enabled': True, 'allow_redirects': 'never'}
            )

            return {
                'success': True,
                'transaction_id': intent.id,
                'status': intent.status,
                'amount': amount,
                'currency': currency,
                'created_at': datetime.fromtimestamp(intent.created).isoformat()
            }

        except stripe.error.CardError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'card_error'
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'stripe_error'
            }

    def refund_payment(self, transaction_id: str, amount: float = None) -> dict:
        """Refund a payment"""
        try:
            refund_params = {'payment_intent': transaction_id}
            if amount:
                refund_params['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)

            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_payment_status(self, transaction_id: str) -> dict:
        """Get payment status"""
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)

            return {
                'success': True,
                'transaction_id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,
                'currency': intent.currency.upper()
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_customer(self, email: str, name: str, metadata: dict = None) -> dict:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )

            return {
                'success': True,
                'customer_id': customer.id,
                'email': customer.email
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }


class PayPalPaymentProcessor(PaymentProcessor):
    """PayPal payment integration (placeholder for implementation)"""

    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('PAYPAL_CLIENT_SECRET')
        self.base_url = os.getenv('PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')

    def get_access_token(self) -> str:
        """Get PayPal OAuth access token"""
        auth = (self.client_id, self.client_secret)
        headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(
            f'{self.base_url}/v1/oauth2/token',
            auth=auth,
            headers=headers,
            data=data
        )

        if response.status_code == 200:
            return response.json().get('access_token')
        return None

    def process_payment(self, amount: float, currency: str, payment_method: str, metadata: dict) -> dict:
        # Implementation would go here
        return {'success': False, 'error': 'PayPal integration not fully implemented'}


# ============================================================================
# SHIPPING CARRIER INTEGRATIONS
# ============================================================================

class ShippingCarrier:
    """Base class for shipping carriers"""

    def create_shipment(self, shipment_data: dict) -> dict:
        raise NotImplementedError

    def track_shipment(self, tracking_number: str) -> dict:
        raise NotImplementedError

    def get_rates(self, origin: dict, destination: dict, packages: list) -> list:
        raise NotImplementedError

    def cancel_shipment(self, tracking_number: str) -> dict:
        raise NotImplementedError


class FedExCarrier(ShippingCarrier):
    """FedEx shipping integration"""

    def __init__(self, api_key: str = None, account_number: str = None):
        self.api_key = api_key or os.getenv('FEDEX_API_KEY')
        self.account_number = account_number or os.getenv('FEDEX_ACCOUNT_NUMBER')
        self.base_url = 'https://apis.fedex.com'

    def create_shipment(self, shipment_data: dict) -> dict:
        """Create FedEx shipment"""
        # This is a simplified example - actual FedEx API requires OAuth and more complex data structure
        return {
            'success': True,
            'tracking_number': f"FEDEX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'label_url': 'https://example.com/label.pdf',
            'carrier': 'FedEx'
        }

    def track_shipment(self, tracking_number: str) -> dict:
        """Track FedEx shipment"""
        # Placeholder implementation
        return {
            'success': True,
            'tracking_number': tracking_number,
            'status': 'IN_TRANSIT',
            'events': [
                {
                    'date': datetime.now().isoformat(),
                    'status': 'Picked up',
                    'location': 'Origin facility'
                }
            ]
        }

    def get_rates(self, origin: dict, destination: dict, packages: list) -> list:
        """Get shipping rates"""
        # Placeholder - actual implementation would call FedEx Rate API
        return [
            {
                'service_type': 'FEDEX_GROUND',
                'cost': 25.50,
                'currency': 'USD',
                'transit_days': 3
            },
            {
                'service_type': 'FEDEX_EXPRESS',
                'cost': 45.00,
                'currency': 'USD',
                'transit_days': 1
            }
        ]


class UPSCarrier(ShippingCarrier):
    """UPS shipping integration"""

    def __init__(self, api_key: str = None, account_number: str = None):
        self.api_key = api_key or os.getenv('UPS_API_KEY')
        self.account_number = account_number or os.getenv('UPS_ACCOUNT_NUMBER')
        self.base_url = 'https://onlinetools.ups.com/api'

    def create_shipment(self, shipment_data: dict) -> dict:
        return {
            'success': True,
            'tracking_number': f"UPS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'label_url': 'https://example.com/label.pdf',
            'carrier': 'UPS'
        }

    def track_shipment(self, tracking_number: str) -> dict:
        return {
            'success': True,
            'tracking_number': tracking_number,
            'status': 'IN_TRANSIT',
            'events': []
        }

    def get_rates(self, origin: dict, destination: dict, packages: list) -> list:
        return [
            {
                'service_type': 'UPS_GROUND',
                'cost': 23.00,
                'currency': 'USD',
                'transit_days': 3
            }
        ]


class DHLCarrier(ShippingCarrier):
    """DHL shipping integration"""

    def __init__(self, api_key: str = None, account_number: str = None):
        self.api_key = api_key or os.getenv('DHL_API_KEY')
        self.account_number = account_number or os.getenv('DHL_ACCOUNT_NUMBER')
        self.base_url = 'https://api.dhl.com'

    def create_shipment(self, shipment_data: dict) -> dict:
        return {
            'success': True,
            'tracking_number': f"DHL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'label_url': 'https://example.com/label.pdf',
            'carrier': 'DHL'
        }

    def track_shipment(self, tracking_number: str) -> dict:
        return {
            'success': True,
            'tracking_number': tracking_number,
            'status': 'IN_TRANSIT',
            'events': []
        }

    def get_rates(self, origin: dict, destination: dict, packages: list) -> list:
        return [
            {
                'service_type': 'DHL_EXPRESS',
                'cost': 55.00,
                'currency': 'USD',
                'transit_days': 2
            }
        ]


class ShippingService:
    """Unified shipping service that works with multiple carriers"""

    def __init__(self):
        self.carriers = {
            'fedex': FedExCarrier(),
            'ups': UPSCarrier(),
            'dhl': DHLCarrier()
        }

    def get_carrier(self, carrier_name: str) -> ShippingCarrier:
        """Get carrier instance"""
        return self.carriers.get(carrier_name.lower())

    def get_all_rates(self, origin: dict, destination: dict, packages: list) -> dict:
        """Get rates from all carriers"""
        all_rates = {}

        for carrier_name, carrier in self.carriers.items():
            try:
                rates = carrier.get_rates(origin, destination, packages)
                all_rates[carrier_name] = rates
            except Exception as e:
                all_rates[carrier_name] = {'error': str(e)}

        return all_rates

    def create_shipment(self, carrier_name: str, shipment_data: dict) -> dict:
        """Create shipment with specified carrier"""
        carrier = self.get_carrier(carrier_name)
        if carrier:
            return carrier.create_shipment(shipment_data)
        return {'success': False, 'error': 'Carrier not found'}

    def track_shipment(self, carrier_name: str, tracking_number: str) -> dict:
        """Track shipment"""
        carrier = self.get_carrier(carrier_name)
        if carrier:
            return carrier.track_shipment(tracking_number)
        return {'success': False, 'error': 'Carrier not found'}


# ============================================================================
# CURRENCY & EXCHANGE RATE SERVICE
# ============================================================================

class ExchangeRateService:
    """Currency conversion and exchange rate management"""

    def __init__(self):
        self.currency_rates = CurrencyRates()
        self.base_currency = 'USD'

    def get_rate(self, from_currency: str, to_currency: str, date_obj: date = None) -> Optional[float]:
        """Get exchange rate between two currencies"""
        try:
            if date_obj:
                rate = self.currency_rates.get_rate(from_currency, to_currency, date_obj)
            else:
                rate = self.currency_rates.get_rate(from_currency, to_currency)
            return rate
        except RatesNotAvailableError:
            return None

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert amount from one currency to another"""
        try:
            converted = self.currency_rates.convert(from_currency, to_currency, amount)
            return round(converted, 2)
        except RatesNotAvailableError:
            return None

    def get_all_rates(self, base_currency: str = None) -> dict:
        """Get all exchange rates for a base currency"""
        base = base_currency or self.base_currency
        try:
            rates = self.currency_rates.get_rates(base)
            return rates
        except RatesNotAvailableError:
            return {}

    def get_supported_currencies(self) -> list:
        """Get list of supported currencies"""
        return [
            'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'AUD', 'CAD', 'CHF', 'SGD',
            'HKD', 'NZD', 'SEK', 'KRW', 'NOK', 'MXN', 'BRL', 'ZAR', 'RUB', 'AED'
        ]


# ============================================================================
# EMAIL SERVICE
# ============================================================================

class EmailService:
    """Email sending and template management"""

    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.username)

    def send_email(self, to_email: str, subject: str, body: str,
                   html_body: str = None, attachments: list = None) -> dict:
        """Send email"""
        # This is a placeholder - actual implementation would use smtplib or flask-mail
        return {
            'success': True,
            'message_id': f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'to': to_email,
            'subject': subject
        }

    def send_order_confirmation(self, order_data: dict, customer_email: str) -> dict:
        """Send order confirmation email"""
        subject = f"Order Confirmation - {order_data.get('order_number')}"
        body = f"""
        Dear Customer,

        Thank you for your order!

        Order Number: {order_data.get('order_number')}
        Order Date: {order_data.get('order_date')}
        Total Amount: {order_data.get('total_amount')} {order_data.get('currency')}

        We will process your order and send you tracking information once shipped.

        Best regards,
        Your Trade Team
        """

        return self.send_email(customer_email, subject, body)

    def send_shipment_notification(self, shipment_data: dict, customer_email: str) -> dict:
        """Send shipment notification"""
        subject = f"Your order has shipped - Tracking: {shipment_data.get('tracking_number')}"
        body = f"""
        Dear Customer,

        Your order has been shipped!

        Tracking Number: {shipment_data.get('tracking_number')}
        Carrier: {shipment_data.get('carrier')}
        Expected Delivery: {shipment_data.get('estimated_delivery_date')}

        Track your shipment: [tracking link]

        Best regards,
        Your Trade Team
        """

        return self.send_email(customer_email, subject, body)


# ============================================================================
# CUSTOMS & TARIFF SERVICE
# ============================================================================

class CustomsService:
    """Customs and tariff calculation service"""

    def calculate_duty(self, hs_code: str, value: float, origin_country: str,
                      destination_country: str) -> dict:
        """Calculate customs duty"""
        # This is a placeholder - actual implementation would integrate with
        # customs databases or APIs like Avalara, Zonos, etc.

        # Example duty rates (simplified)
        duty_rates = {
            '8518': 0.025,  # 2.5% for audio equipment
            '6203': 0.162,  # 16.2% for men's clothing
            # ... more rates
        }

        hs_prefix = hs_code[:4] if len(hs_code) >= 4 else hs_code
        duty_rate = duty_rates.get(hs_prefix, 0.05)  # Default 5%

        duty_amount = value * duty_rate

        return {
            'hs_code': hs_code,
            'value': value,
            'duty_rate': duty_rate,
            'duty_amount': round(duty_amount, 2),
            'origin_country': origin_country,
            'destination_country': destination_country
        }

    def calculate_total_landed_cost(self, product_value: float, shipping_cost: float,
                                   insurance_cost: float, hs_code: str,
                                   origin_country: str, destination_country: str) -> dict:
        """Calculate total landed cost including duties and fees"""

        # Calculate duty
        duty_info = self.calculate_duty(hs_code, product_value, origin_country, destination_country)

        # Additional fees (placeholder)
        processing_fee = 25.00
        customs_clearance_fee = 50.00

        total_landed_cost = (
            product_value +
            shipping_cost +
            insurance_cost +
            duty_info['duty_amount'] +
            processing_fee +
            customs_clearance_fee
        )

        return {
            'product_value': product_value,
            'shipping_cost': shipping_cost,
            'insurance_cost': insurance_cost,
            'duty_amount': duty_info['duty_amount'],
            'processing_fee': processing_fee,
            'customs_clearance_fee': customs_clearance_fee,
            'total_landed_cost': round(total_landed_cost, 2),
            'breakdown': duty_info
        }


# ============================================================================
# INTEGRATION FACTORY
# ============================================================================

class IntegrationFactory:
    """Factory to get integration service instances"""

    _instances = {}

    @classmethod
    def get_payment_processor(cls, processor_type: str = 'stripe') -> PaymentProcessor:
        """Get payment processor instance"""
        if processor_type not in cls._instances:
            if processor_type == 'stripe':
                cls._instances[processor_type] = StripePaymentProcessor()
            elif processor_type == 'paypal':
                cls._instances[processor_type] = PayPalPaymentProcessor()
            else:
                raise ValueError(f"Unknown payment processor: {processor_type}")

        return cls._instances[processor_type]

    @classmethod
    def get_shipping_service(cls) -> ShippingService:
        """Get shipping service instance"""
        if 'shipping' not in cls._instances:
            cls._instances['shipping'] = ShippingService()
        return cls._instances['shipping']

    @classmethod
    def get_exchange_rate_service(cls) -> ExchangeRateService:
        """Get exchange rate service instance"""
        if 'exchange_rate' not in cls._instances:
            cls._instances['exchange_rate'] = ExchangeRateService()
        return cls._instances['exchange_rate']

    @classmethod
    def get_email_service(cls) -> EmailService:
        """Get email service instance"""
        if 'email' not in cls._instances:
            cls._instances['email'] = EmailService()
        return cls._instances['email']

    @classmethod
    def get_customs_service(cls) -> CustomsService:
        """Get customs service instance"""
        if 'customs' not in cls._instances:
            cls._instances['customs'] = CustomsService()
        return cls._instances['customs']
