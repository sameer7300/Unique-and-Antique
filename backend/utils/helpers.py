"""
Helper functions for the Unique and Antique E-commerce Platform.
"""

import uuid
import random
import string
from decimal import Decimal
from django.utils.text import slugify
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from typing import Optional, Dict, Any


def generate_unique_slug(model_class, title: str, slug_field: str = 'slug') -> str:
    """
    Generate a unique slug for a model instance.
    """
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def generate_order_number() -> str:
    """
    Generate a unique order number.
    Format: UA-YYYYMMDD-XXXX
    """
    date_str = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"UA-{date_str}-{random_str}"


def generate_sku(prefix: str = '', length: int = 8) -> str:
    """
    Generate a SKU with optional prefix.
    """
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{random_str}" if prefix else random_str


def calculate_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
    """
    Calculate tax amount.
    """
    return (amount * tax_rate / 100).quantize(Decimal('0.01'))


def calculate_shipping_cost(weight: Decimal, distance: Optional[float] = None) -> Decimal:
    """
    Calculate shipping cost based on weight and distance.
    This is a simple implementation - in production, you'd integrate with shipping APIs.
    """
    base_cost = Decimal('5.00')  # Base shipping cost
    weight_cost = weight * Decimal('0.50')  # $0.50 per kg
    
    if distance:
        distance_cost = Decimal(str(distance)) * Decimal('0.01')  # $0.01 per km
        return base_cost + weight_cost + distance_cost
    
    return base_cost + weight_cost


def format_currency(amount: Decimal, currency: str = 'USD') -> str:
    """
    Format currency amount for display.
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"


def send_notification_email(
    subject: str,
    message: str,
    recipient_list: list,
    html_message: Optional[str] = None
) -> bool:
    """
    Send notification email.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        # Log the error in production
        print(f"Email sending failed: {e}")
        return False


def generate_verification_token() -> str:
    """
    Generate a verification token.
    """
    return str(uuid.uuid4()).replace('-', '')


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    Example: john.doe@example.com -> j***@example.com
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 1:
        return email
    
    masked_local = local[0] + '*' * (len(local) - 1)
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.
    Example: +1234567890 -> +123***7890
    """
    if len(phone) < 4:
        return phone
    
    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]


def calculate_discount(original_price: Decimal, discount_percentage: Decimal) -> Decimal:
    """
    Calculate discount amount.
    """
    return (original_price * discount_percentage / 100).quantize(Decimal('0.01'))


def apply_discount(original_price: Decimal, discount_percentage: Decimal) -> Decimal:
    """
    Apply discount to price.
    """
    discount_amount = calculate_discount(original_price, discount_percentage)
    return original_price - discount_amount


def get_client_ip(request) -> str:
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}.{ext}" if ext else name


def generate_thumbnail_path(original_path: str, size: str) -> str:
    """
    Generate thumbnail path from original image path.
    """
    path_parts = original_path.rsplit('.', 1)
    if len(path_parts) == 2:
        return f"{path_parts[0]}_{size}.{path_parts[1]}"
    return f"{original_path}_{size}"


def parse_search_query(query: str) -> Dict[str, Any]:
    """
    Parse search query and extract filters.
    """
    # Simple implementation - can be extended for advanced search
    terms = query.strip().split()
    
    filters = {
        'terms': [],
        'price_min': None,
        'price_max': None,
        'category': None,
        'brand': None,
    }
    
    for term in terms:
        if term.startswith('price:'):
            # Handle price range: price:10-50
            price_range = term.split(':', 1)[1]
            if '-' in price_range:
                min_price, max_price = price_range.split('-', 1)
                try:
                    filters['price_min'] = Decimal(min_price)
                    filters['price_max'] = Decimal(max_price)
                except:
                    filters['terms'].append(term)
            else:
                filters['terms'].append(term)
        elif term.startswith('category:'):
            filters['category'] = term.split(':', 1)[1]
        elif term.startswith('brand:'):
            filters['brand'] = term.split(':', 1)[1]
        else:
            filters['terms'].append(term)
    
    return filters


def calculate_estimated_delivery(shipping_method: str, location: str = None) -> timezone.datetime:
    """
    Calculate estimated delivery date based on shipping method.
    """
    now = timezone.now()
    
    # Simple implementation - in production, integrate with shipping APIs
    delivery_days = {
        'standard': 5,
        'express': 2,
        'overnight': 1,
        'economy': 7,
    }
    
    days = delivery_days.get(shipping_method.lower(), 5)
    return now + timezone.timedelta(days=days)


def generate_barcode(product_id: int, variant_id: Optional[int] = None) -> str:
    """
    Generate barcode for product/variant.
    """
    # Simple implementation - in production, use proper barcode generation
    if variant_id:
        return f"2{product_id:06d}{variant_id:06d}"
    return f"1{product_id:012d}"


def validate_credit_card_number(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm.
    """
    # Remove spaces and non-digits
    card_number = ''.join(filter(str.isdigit, card_number))
    
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def get_card_type(card_number: str) -> str:
    """
    Determine credit card type from card number.
    """
    card_number = ''.join(filter(str.isdigit, card_number))
    
    if card_number.startswith('4'):
        return 'visa'
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return 'mastercard'
    elif card_number.startswith(('34', '37')):
        return 'amex'
    elif card_number.startswith('6011'):
        return 'discover'
    else:
        return 'unknown'
