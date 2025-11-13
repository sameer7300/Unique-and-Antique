"""
Product models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """
    Product Category model with hierarchical structure.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent category')
    )
    image = models.ImageField(
        _('image'),
        upload_to='categories/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'products_category'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Get full category name including parent categories."""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name
    
    def get_descendants(self):
        """Get all descendant categories."""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants


class Brand(models.Model):
    """
    Product Brand model.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(
        _('logo'),
        upload_to='brands/',
        blank=True,
        null=True
    )
    website = models.URLField(_('website'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'products_brand'
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Main Product model.
    """
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('discontinued', _('Discontinued')),
    ]
    
    # Basic Information
    title = models.CharField(
        _('Product Title'), 
        max_length=200,
        help_text=_('Enter a clear, descriptive title that customers will search for. Example: "Victorian Oak Dining Table"')
    )
    slug = models.SlugField(
        _('URL Slug'), 
        max_length=220, 
        unique=True, 
        blank=True,
        help_text=_('This creates the web address for your product. Leave blank to auto-generate from title.')
    )
    description = models.TextField(
        _('Full Description'),
        help_text=_('Write a detailed description highlighting key features, history, and condition. This helps customers make informed decisions.')
    )
    short_description = models.TextField(
        _('Short Summary'),
        max_length=500,
        blank=True,
        help_text=_('A brief summary (1-2 sentences) that appears in product listings. Keep it engaging and informative.')
    )
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Product Category'),
        help_text=_('Choose the most appropriate category. This helps customers find your product when browsing.')
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Brand/Manufacturer'),
        help_text=_('Select the brand or manufacturer if known. Leave blank if unknown or generic.')
    )
    
    # Pricing
    price = models.DecimalField(
        _('Selling Price (PKR)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('The price customers will pay. Enter amount in Pakistani Rupees (e.g., 25000 for PKR 25,000)')
    )
    compare_price = models.DecimalField(
        _('Original Price (PKR)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('If this item is on sale, enter the original higher price here to show customers the discount')
    )
    cost_price = models.DecimalField(
        _('Your Cost Price (PKR)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('What you paid for this item (for your profit tracking). This is private and not shown to customers.')
    )
    
    # Inventory
    sku = models.CharField(
        _('Product Code (SKU)'),
        max_length=100,
        unique=True,
        help_text=_('A unique code for this product (e.g., "VIC-TABLE-001"). Use letters, numbers, and dashes only.')
    )
    stock = models.PositiveIntegerField(
        _('How Many Do You Have?'), 
        default=0,
        help_text=_('Enter the number of items you have in stock. Set to 0 if out of stock.')
    )
    low_stock_threshold = models.PositiveIntegerField(
        _('Low Stock Alert Level'),
        default=10,
        help_text=_('Get notified when stock drops to this number. Recommended: 5-10 items.')
    )
    track_inventory = models.BooleanField(
        _('Track Stock Levels'), 
        default=True,
        help_text=_('Check this to automatically track when items are sold and update stock levels.')
    )
    allow_backorders = models.BooleanField(
        _('Allow Orders When Out of Stock'), 
        default=False,
        help_text=_('Check this to let customers order even when you have 0 stock (useful for made-to-order items).')
    )
    
    # Physical Properties
    weight = models.DecimalField(
        _('weight (kg)'),
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    dimensions_length = models.DecimalField(
        _('length (cm)'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    dimensions_width = models.DecimalField(
        _('width (cm)'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    dimensions_height = models.DecimalField(
        _('height (cm)'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # SEO and Marketing
    meta_title = models.CharField(
        _('meta title'),
        max_length=60,
        blank=True,
        help_text=_('SEO title tag')
    )
    meta_description = models.CharField(
        _('meta description'),
        max_length=160,
        blank=True,
        help_text=_('SEO meta description')
    )
    tags = models.CharField(
        _('tags'),
        max_length=500,
        blank=True,
        help_text=_('Comma-separated tags')
    )
    
    # Status and Visibility
    status = models.CharField(
        _('Product Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('Draft = Not visible to customers | Active = Visible on website | Inactive = Hidden temporarily | Discontinued = No longer available')
    )
    is_featured = models.BooleanField(
        _('Feature This Product'), 
        default=False,
        help_text=_('Featured products are highlighted on the homepage and get more visibility to customers.')
    )
    is_digital = models.BooleanField(
        _('Digital Product (No Physical Item)'), 
        default=False,
        help_text=_('Check this for digital downloads, services, or virtual items that don\'t need shipping.')
    )
    requires_shipping = models.BooleanField(
        _('Needs to be Shipped'), 
        default=True,
        help_text=_('Uncheck this for pickup-only items or digital products that don\'t need shipping.')
    )
    
    # Additional Data
    attributes = models.JSONField(
        _('Product Features & Specifications'),
        default=dict,
        blank=True,
        help_text=_('Add product features like "Material: Wood, Color: Brown, Weight: 5kg" - one per line. System will automatically format this.')
    )
    care_instructions = models.JSONField(
        _('Care Instructions'),
        default=list,
        blank=True,
        help_text=_('Add care instructions like "Dust with soft cloth, Avoid direct sunlight, Keep away from moisture" - one per line. System will automatically format this.')
    )
    condition = models.CharField(
        _('condition'),
        max_length=100,
        blank=True,
        help_text=_('Product condition (e.g., Authentic Antique, Vintage, etc.)')
    )
    era = models.CharField(
        _('era'),
        max_length=100,
        blank=True,
        help_text=_('Historical era or period')
    )
    material = models.CharField(
        _('material'),
        max_length=200,
        blank=True,
        help_text=_('Primary materials used')
    )
    authenticity_verified = models.BooleanField(
        _('authenticity verified'),
        default=True,
        help_text=_('Whether the item has been verified as authentic')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    class Meta:
        db_table = 'products_product'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to active
        if self.status == 'active' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock > 0 or self.allow_backorders
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock."""
        if not self.track_inventory:
            return False
        return self.stock <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price is set."""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    @property
    def average_rating(self):
        """Get average rating from reviews."""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=self, status='approved')
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def review_count(self):
        """Get total number of approved reviews."""
        from apps.reviews.models import Review
        return Review.objects.filter(product=self, status='approved').count()


class ProductImage(models.Model):
    """
    Product Image model for multiple images per product.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('product')
    )
    image = models.ImageField(
        _('image'),
        upload_to='products/'
    )
    alt_text = models.CharField(
        _('alt text'),
        max_length=200,
        blank=True,
        help_text=_('Alternative text for accessibility')
    )
    position = models.PositiveIntegerField(_('position'), default=0)
    is_primary = models.BooleanField(_('is primary'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'products_productimage'
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['position', 'created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_primary=True),
                name='unique_primary_image_per_product'
            )
        ]
    
    def __str__(self):
        return f"{self.product.title} - Image {self.position}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # Set alt_text if not provided
        if not self.alt_text:
            self.alt_text = f"{self.product.title} image"
        
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product Variant model for products with variations (size, color, etc.).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('product')
    )
    name = models.CharField(_('variant name'), max_length=100)
    sku = models.CharField(_('variant SKU'), max_length=100, unique=True)
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(_('stock quantity'), default=0)
    attributes = models.JSONField(
        _('variant attributes'),
        default=dict,
        help_text=_('Variant-specific attributes (color, size, etc.)')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'products_productvariant'
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.product.title} - {self.name}"
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock > 0
