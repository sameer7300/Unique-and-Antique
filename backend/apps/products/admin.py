"""
Admin configuration for the products app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter, NumericRangeFilter
from .models import Category, Brand, Product, ProductImage, ProductVariant
from .forms import ProductAdminForm


# Import/Export Resources
class ProductResource(resources.ModelResource):
    """Resource for importing/exporting products."""
    category_name = fields.Field(
        column_name='category',
        attribute='category__name',
        readonly=True
    )
    brand_name = fields.Field(
        column_name='brand',
        attribute='brand__name',
        readonly=True
    )
    
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'description', 'category_name', 'brand_name',
            'price', 'compare_price', 'sku', 'stock', 'status', 'is_featured',
            'created_at', 'updated_at'
        )
        export_order = fields


class CategoryResource(resources.ModelResource):
    """Resource for importing/exporting categories."""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent__name', 'is_active', 'sort_order')


class BrandResource(resources.ModelResource):
    """Resource for importing/exporting brands."""
    
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'description', 'website', 'is_active')


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for ProductImage model.
    """
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'position', 'is_primary']
    readonly_fields = ['created_at']


class ProductVariantInline(admin.TabularInline):
    """
    Inline admin for ProductVariant model.
    """
    model = ProductVariant
    extra = 0
    fields = ['name', 'sku', 'price', 'stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    """
    Admin configuration for Category model.
    """
    list_display = [
        'name', 'parent', 'product_count', 'is_active', 
        'sort_order', 'created_at'
    ]
    list_filter = ['is_active', 'parent', ('created_at', DateRangeFilter)]
    resource_class = CategoryResource
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'product_count']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        (_('Display'), {
            'fields': ('image', 'is_active', 'sort_order')
        }),
        (_('Statistics'), {
            'fields': ('product_count',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Get number of products in category."""
        return obj.products.filter(status='active').count()
    product_count.short_description = _('Active Products')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )


@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin):
    """
    Admin configuration for Brand model.
    """
    list_display = [
        'name', 'product_count', 'is_active', 'website', 'created_at'
    ]
    list_filter = ['is_active', ('created_at', DateRangeFilter)]
    resource_class = BrandResource
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'product_count']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Branding'), {
            'fields': ('logo', 'website')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
        (_('Statistics'), {
            'fields': ('product_count',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Get number of products for brand."""
        return obj.products.filter(status='active').count()
    product_count.short_description = _('Active Products')


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    """
    Enhanced admin configuration for Product model with user-friendly features.
    """
    resource_class = ProductResource
    form = ProductAdminForm
    list_display = [
        'title', 'category', 'brand', 'price', 'stock',
        'status', 'is_featured', 'average_rating', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'category', 'brand',
        'track_inventory', ('created_at', DateRangeFilter),
        ('price', NumericRangeFilter), ('stock', NumericRangeFilter)
    ]
    resource_class = ProductResource
    search_fields = ['title', 'description', 'sku', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'created_at', 'updated_at', 'published_at',
        'average_rating', 'review_count', 'is_in_stock', 'is_low_stock'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('📝 Product Details'), {
            'fields': ('title', 'slug', 'description', 'short_description'),
            'description': 'Enter the basic information about your product. The title should be clear and descriptive.'
        }),
        (_('🏷️ Category & Tags'), {
            'fields': ('category', 'brand', 'tags'),
            'description': 'Choose the right category and brand to help customers find your product easily.'
        }),
        (_('💰 Pricing'), {
            'fields': ('price', 'compare_price', 'cost_price'),
            'description': 'Set your product prices. Compare price is used to show discounts to customers.'
        }),
        (_('📦 Stock Management'), {
            'fields': (
                'sku', 'stock', 'low_stock_threshold',
                'track_inventory', 'allow_backorders'
            ),
            'description': 'Manage your product inventory. Set low stock alerts to avoid running out of products.'
        }),
        (_('✨ Product Features (Easy Text Format)'), {
            'fields': ('attributes_text',),
            'description': _('🎯 Add product features in simple text format. Just type "Feature: Value" on each line. Example: "Material: Oak Wood"')
        }),
        (_('🧼 Care Instructions (Easy Text Format)'), {
            'fields': ('care_instructions_text',),
            'description': _('💡 Add care instructions in simple text format. Just type one instruction per line. Example: "Dust with soft cloth"')
        }),
        (_('📐 Physical Properties'), {
            'fields': ('weight', 'dimensions_length', 'dimensions_width', 'dimensions_height', 'material', 'condition', 'era', 'authenticity_verified'),
            'description': 'Enter physical characteristics and authenticity details.'
        }),
        (_('🌐 SEO & Visibility'), {
            'fields': ('meta_title', 'meta_description', 'status', 'is_featured', 'is_digital', 'requires_shipping'),
            'description': 'Control how your product appears in search engines and on your website.'
        }),
        (_('🔧 Advanced (Auto-Generated)'), {
            'fields': ('attributes', 'care_instructions'),
            'classes': ('collapse',),
            'description': _('⚙️ These fields are automatically generated from your simple text above. No need to edit directly.')
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    actions = [
        'make_active', 'make_inactive', 'make_draft', 'make_featured', 
        'remove_featured', 'duplicate_products', 'export_low_stock'
    ]
    
    def make_active(self, request, queryset):
        """✅ Make products visible to customers"""
        updated = queryset.update(status='active')
        self.message_user(request, f'✅ {updated} products are now LIVE and visible to customers!')
    make_active.short_description = _('✅ Make products LIVE (visible to customers)')
    
    def make_inactive(self, request, queryset):
        """⏸️ Hide products temporarily"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'⏸️ {updated} products are now HIDDEN (customers can\'t see them)')
    make_inactive.short_description = _('⏸️ Hide products temporarily')
    
    def make_draft(self, request, queryset):
        """📝 Move products to draft"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'📝 {updated} products moved to DRAFT (not visible to customers)')
    make_draft.short_description = _('📝 Move to Draft (not visible)')
    
    def make_featured(self, request, queryset):
        """⭐ Feature products on homepage"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'⭐ {updated} products are now FEATURED on homepage!')
    make_featured.short_description = _('⭐ Feature on homepage (more visibility)')
    
    def remove_featured(self, request, queryset):
        """Remove featured status"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'📤 {updated} products removed from featured section')
    remove_featured.short_description = _('📤 Remove from featured section')
    
    def duplicate_products(self, request, queryset):
        """📋 Create copies of selected products"""
        count = 0
        for product in queryset:
            product.pk = None
            product.title = f"{product.title} (Copy)"
            product.slug = f"{product.slug}-copy"
            product.sku = f"{product.sku}-COPY"
            product.status = 'draft'
            product.save()
            count += 1
        self.message_user(request, f'📋 Created {count} product copies in Draft status')
    duplicate_products.short_description = _('📋 Create copies (useful for similar products)')
    
    def export_low_stock(self, request, queryset):
        """📊 Show low stock products"""
        low_stock = queryset.filter(stock__lte=10, track_inventory=True)
        count = low_stock.count()
        if count > 0:
            self.message_user(request, f'⚠️ Found {count} products with low stock! Check the filter above.')
        else:
            self.message_user(request, f'✅ All selected products have good stock levels!')
    export_low_stock.short_description = _('⚠️ Check stock levels')
    
    def save_model(self, request, obj, form, change):
        """🤖 Automatic smart features for non-IT admins"""
        
        # 1. Auto-generate slug from title
        if not obj.slug and obj.title:
            from django.utils.text import slugify
            obj.slug = slugify(obj.title)
            
        # 2. Auto-generate SKU if not provided
        if not obj.sku:
            # Create SKU from category and title
            category_code = obj.category.name[:3].upper() if obj.category else "PRD"
            title_code = "".join([word[:3].upper() for word in obj.title.split()[:2]])
            import random
            random_num = random.randint(100, 999)
            obj.sku = f"{category_code}-{title_code}-{random_num}"
            
        # 3. Auto-set published date when making active
        if obj.status == 'active' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
            
        # 4. Auto-generate meta description from description
        if not obj.meta_description and obj.description:
            # Take first 150 characters of description
            obj.meta_description = obj.description[:150] + "..." if len(obj.description) > 150 else obj.description
            
        # 5. Auto-set SEO title from product title
        if not obj.meta_title and obj.title:
            obj.meta_title = f"{obj.title} - Unique & Antique"
            
        super().save_model(request, obj, form, change)
        
        # 6. Show helpful message to admin
        if not change:  # New product
            self.message_user(request, f'🎉 Product "{obj.title}" created successfully! SKU: {obj.sku}')
        else:  # Updated product
            self.message_user(request, f'✅ Product "{obj.title}" updated successfully!')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductImage model.
    """
    list_display = ['product', 'image_preview', 'alt_text', 'position', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__title', 'alt_text']
    readonly_fields = ['created_at', 'image_preview']
    
    def image_preview(self, obj):
        """Display image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Preview')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductVariant model.
    """
    list_display = [
        'product', 'name', 'sku', 'price', 'stock',
        'is_active', 'is_in_stock', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__title', 'name', 'sku']
    readonly_fields = ['created_at', 'updated_at', 'is_in_stock']
    
    fieldsets = (
        (_('Product'), {
            'fields': ('product',)
        }),
        (_('Variant Information'), {
            'fields': ('name', 'sku', 'price', 'stock', 'attributes')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
        (_('Status'), {
            'fields': ('is_in_stock',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
