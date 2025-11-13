"""
Admin configuration for the cart app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from .models import Cart, CartItem, SavedItem, CartCoupon


class CartItemInline(admin.TabularInline):
    """
    Inline admin for CartItem model.
    """
    model = CartItem
    extra = 0
    fields = [
        'product', 'variant', 'quantity', 'price_at_add',
        'current_price', 'total_price', 'is_available'
    ]
    readonly_fields = [
        'price_at_add', 'current_price', 'total_price',
        'is_available', 'created_at', 'updated_at'
    ]


class CartCouponInline(admin.TabularInline):
    """
    Inline admin for CartCoupon model.
    """
    model = CartCoupon
    extra = 0
    fields = ['coupon_code', 'discount_amount', 'discount_type', 'applied_at']
    readonly_fields = ['applied_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for Cart model.
    """
    list_display = [
        'cart_id_short', 'user', 'status', 'total_items',
        'subtotal', 'total_weight', 'created_at', 'expires_at'
    ]
    list_filter = ['status', 'created_at', 'updated_at', 'expires_at']
    search_fields = [
        'cart_id', 'user__email', 'user__first_name',
        'user__last_name', 'session_key'
    ]
    readonly_fields = [
        'cart_id', 'total_items', 'subtotal', 'total_weight',
        'is_empty', 'created_at', 'updated_at'
    ]
    ordering = ['-updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Cart Information'), {
            'fields': ('cart_id', 'user', 'session_key', 'status')
        }),
        (_('Statistics'), {
            'fields': ('total_items', 'subtotal', 'total_weight', 'is_empty'),
            'classes': ('collapse',)
        }),
        (_('Conversion'), {
            'fields': ('converted_to_order',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CartItemInline, CartCouponInline]
    
    actions = ['mark_abandoned', 'mark_expired', 'clear_carts']
    
    def cart_id_short(self, obj):
        """Display shortened cart ID."""
        return str(obj.cart_id)[:8] + '...'
    cart_id_short.short_description = _('Cart ID')
    
    def mark_abandoned(self, request, queryset):
        """Mark selected carts as abandoned."""
        updated = queryset.filter(status='active').update(status='abandoned')
        self.message_user(request, f'{updated} carts marked as abandoned.')
    mark_abandoned.short_description = _('Mark selected carts as abandoned')
    
    def mark_expired(self, request, queryset):
        """Mark selected carts as expired."""
        updated = queryset.filter(status='active').update(status='expired')
        self.message_user(request, f'{updated} carts marked as expired.')
    mark_expired.short_description = _('Mark selected carts as expired')
    
    def clear_carts(self, request, queryset):
        """Clear all items from selected carts."""
        cleared = 0
        for cart in queryset:
            cart.clear()
            cleared += 1
        self.message_user(request, f'{cleared} carts cleared.')
    clear_carts.short_description = _('Clear selected carts')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').annotate(
            item_count=Count('items')
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for CartItem model.
    """
    list_display = [
        'cart', 'product', 'variant', 'quantity',
        'price_at_add', 'current_price', 'total_price',
        'price_changed', 'is_available', 'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = [
        'cart__cart_id', 'product__title', 'product__sku',
        'cart__user__email'
    ]
    readonly_fields = [
        'price_at_add', 'current_price', 'total_price',
        'price_changed', 'is_available', 'stock_available',
        'can_fulfill_quantity', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Cart'), {
            'fields': ('cart',)
        }),
        (_('Product Information'), {
            'fields': ('product', 'variant', 'quantity')
        }),
        (_('Pricing'), {
            'fields': ('price_at_add', 'current_price', 'total_price', 'price_changed')
        }),
        (_('Availability'), {
            'fields': ('is_available', 'stock_available', 'can_fulfill_quantity'),
            'classes': ('collapse',)
        }),
        (_('Options'), {
            'fields': ('options',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['remove_unavailable_items', 'update_prices']
    
    def remove_unavailable_items(self, request, queryset):
        """Remove unavailable items from carts."""
        removed = 0
        for item in queryset:
            if not item.is_available:
                item.delete()
                removed += 1
        self.message_user(request, f'{removed} unavailable items removed.')
    remove_unavailable_items.short_description = _('Remove unavailable items')
    
    def update_prices(self, request, queryset):
        """Update prices to current product prices."""
        updated = 0
        for item in queryset:
            if item.price_changed:
                item.price_at_add = item.current_price
                item.save()
                updated += 1
        self.message_user(request, f'{updated} item prices updated.')
    update_prices.short_description = _('Update prices to current')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cart', 'product', 'variant'
        )


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for SavedItem model.
    """
    list_display = [
        'user', 'product', 'variant', 'notes_preview', 'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = [
        'user__email', 'product__title', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Product'), {
            'fields': ('product', 'variant')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def notes_preview(self, obj):
        """Display preview of notes."""
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return _('No notes')
    notes_preview.short_description = _('Notes Preview')
    
    actions = ['move_to_cart']
    
    def move_to_cart(self, request, queryset):
        """Move selected saved items to cart."""
        moved = 0
        for saved_item in queryset:
            try:
                saved_item.move_to_cart()
                moved += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error moving {saved_item}: {str(e)}',
                    level='ERROR'
                )
        
        if moved > 0:
            self.message_user(request, f'{moved} items moved to cart.')
    move_to_cart.short_description = _('Move selected items to cart')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'product', 'variant'
        )


@admin.register(CartCoupon)
class CartCouponAdmin(admin.ModelAdmin):
    """
    Admin configuration for CartCoupon model.
    """
    list_display = [
        'cart', 'coupon_code', 'discount_amount',
        'discount_type', 'applied_at'
    ]
    list_filter = ['discount_type', 'applied_at']
    search_fields = [
        'cart__cart_id', 'coupon_code', 'cart__user__email'
    ]
    readonly_fields = ['applied_at']
    
    fieldsets = (
        (_('Cart'), {
            'fields': ('cart',)
        }),
        (_('Coupon'), {
            'fields': ('coupon_code', 'discount_amount', 'discount_type')
        }),
        (_('Applied'), {
            'fields': ('applied_at',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cart')


# Custom admin site configuration
admin.site.site_header = _('Unique and Antique E-commerce Admin')
admin.site.site_title = _('E-commerce Admin')
admin.site.index_title = _('Welcome to E-commerce Administration')

# Add custom CSS for better admin interface
class AdminConfig:
    """
    Custom admin configuration.
    """
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
