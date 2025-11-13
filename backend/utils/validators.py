"""
Custom validators for the Unique and Antique E-commerce Platform.
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """
    Validate phone number format.
    """
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            _('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
        )


def validate_postal_code(value):
    """
    Validate postal code format (supports various international formats).
    """
    # Basic validation - can be extended for specific country formats
    postal_regex = re.compile(r'^[A-Za-z0-9\s\-]{3,10}$')
    if not postal_regex.match(value):
        raise ValidationError(
            _('Enter a valid postal code.')
        )


def validate_sku(value):
    """
    Validate SKU format.
    """
    sku_regex = re.compile(r'^[A-Za-z0-9\-_]{3,50}$')
    if not sku_regex.match(value):
        raise ValidationError(
            _('SKU must contain only letters, numbers, hyphens, and underscores (3-50 characters).')
        )


def validate_rating(value):
    """
    Validate rating value (1-5).
    """
    if not isinstance(value, int) or value < 1 or value > 5:
        raise ValidationError(
            _('Rating must be an integer between 1 and 5.')
        )


def validate_discount_percentage(value):
    """
    Validate discount percentage (0-100).
    """
    if value < 0 or value > 100:
        raise ValidationError(
            _('Discount percentage must be between 0 and 100.')
        )


def validate_positive_decimal(value):
    """
    Validate that decimal value is positive.
    """
    if value < 0:
        raise ValidationError(
            _('This value must be positive.')
        )


def validate_image_size(image):
    """
    Validate image file size (max 5MB).
    """
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(
            _('Image file size must be less than 5MB.')
        )


def validate_image_dimensions(image):
    """
    Validate image dimensions (max 4000x4000).
    """
    from PIL import Image
    
    try:
        img = Image.open(image)
        width, height = img.size
        
        max_dimension = 4000
        if width > max_dimension or height > max_dimension:
            raise ValidationError(
                _('Image dimensions must be less than 4000x4000 pixels.')
            )
    except Exception:
        raise ValidationError(
            _('Invalid image file.')
        )


def validate_order_number(value):
    """
    Validate order number format.
    """
    order_regex = re.compile(r'^UA-\d{8}-\d{4}$')
    if not order_regex.match(value):
        raise ValidationError(
            _('Order number must be in format: UA-YYYYMMDD-XXXX')
        )


def validate_tracking_number(value):
    """
    Validate tracking number format.
    """
    # Basic validation - can be extended for specific carrier formats
    tracking_regex = re.compile(r'^[A-Za-z0-9]{6,30}$')
    if not tracking_regex.match(value):
        raise ValidationError(
            _('Tracking number must contain only letters and numbers (6-30 characters).')
        )


def validate_currency_code(value):
    """
    Validate currency code (ISO 4217).
    """
    # Common currency codes - can be extended
    valid_currencies = [
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD'
    ]
    
    if value.upper() not in valid_currencies:
        raise ValidationError(
            _('Invalid currency code. Supported currencies: %(currencies)s') % {
                'currencies': ', '.join(valid_currencies)
            }
        )


def validate_color_hex(value):
    """
    Validate hex color code.
    """
    hex_regex = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if not hex_regex.match(value):
        raise ValidationError(
            _('Enter a valid hex color code (e.g., #FF0000 or #F00).')
        )


def validate_slug(value):
    """
    Validate slug format.
    """
    slug_regex = re.compile(r'^[-a-zA-Z0-9_]+$')
    if not slug_regex.match(value):
        raise ValidationError(
            _('Slug can only contain letters, numbers, hyphens, and underscores.')
        )


def validate_json_schema(schema):
    """
    Decorator to validate JSON field against a schema.
    """
    def validator(value):
        import jsonschema
        try:
            jsonschema.validate(value, schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(
                _('Invalid JSON data: %(error)s') % {'error': str(e)}
            )
    return validator


# Common regex validators
alphanumeric_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]*$',
    message=_('Only alphanumeric characters are allowed.')
)

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.-]+$',
    message=_('Username can only contain letters, numbers, dots, hyphens, and underscores.')
)

# Product attribute validators
def validate_product_attributes(value):
    """
    Validate product attributes JSON structure.
    """
    if not isinstance(value, dict):
        raise ValidationError(_('Product attributes must be a JSON object.'))
    
    # Validate attribute keys and values
    for key, val in value.items():
        if not isinstance(key, str) or len(key) > 50:
            raise ValidationError(
                _('Attribute keys must be strings with maximum 50 characters.')
            )
        
        if isinstance(val, str) and len(val) > 200:
            raise ValidationError(
                _('Attribute values must be less than 200 characters.')
            )


def validate_dimensions(value):
    """
    Validate dimensions JSON structure.
    """
    required_fields = ['length', 'width', 'height']
    
    if not isinstance(value, dict):
        raise ValidationError(_('Dimensions must be a JSON object.'))
    
    for field in required_fields:
        if field not in value:
            raise ValidationError(
                _('Dimensions must include %(field)s.') % {'field': field}
            )
        
        try:
            dimension_value = float(value[field])
            if dimension_value <= 0:
                raise ValidationError(
                    _('%(field)s must be a positive number.') % {'field': field}
                )
        except (ValueError, TypeError):
            raise ValidationError(
                _('%(field)s must be a valid number.') % {'field': field}
            )
