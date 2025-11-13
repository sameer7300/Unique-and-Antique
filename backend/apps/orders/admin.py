"""
Admin configuration for the orders app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Sum, Count
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderShipment,
    OrderReturn, OrderReturnItem
)


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem model.
    """
    model = OrderItem
    extra = 0
    fields = [
        'product', 'variant', 'product_name', 'quantity',
        'unit_price', 'total_price'
    ]
    readonly_fields = ['product_name', 'total_price', 'created_at']


class OrderStatusHistoryInline(admin.TabularInline):
    """
    Inline admin for OrderStatusHistory model.
    """
    model = OrderStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['created_at']


class OrderShipmentInline(admin.TabularInline):
    """
    Inline admin for OrderShipment model.
    """
    model = OrderShipment
    extra = 0
    fields = [
        'tracking_number', 'carrier', 'status',
        'shipped_at', 'estimated_delivery'
    ]
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model.
    """
    list_display = [
        'order_number', 'user', 'status', 'payment_status',
        'payment_method', 'total_amount', 'total_items', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method',
        'created_at', 'confirmed_at', 'shipped_at', 'delivered_at'
    ]
    search_fields = [
        'order_number', 'user__email', 'user__first_name',
        'user__last_name', 'tracking_number'
    ]
    readonly_fields = [
        'order_id', 'order_number', 'created_at', 'updated_at',
        'confirmed_at', 'shipped_at', 'delivered_at',
        'total_items', 'can_be_cancelled', 'can_be_returned', 'is_paid'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'order_id', 'user', 'status', 'payment_status')
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount', 'currency')
        }),
        (_('Addresses'), {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        (_('Shipping'), {
            'fields': ('shipping_method', 'tracking_number', 'carrier', 'estimated_delivery_date')
        }),
        (_('Notes'), {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        (_('Status Information'), {
            'fields': ('can_be_cancelled', 'can_be_returned', 'is_paid'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline, OrderShipmentInline]
    
    actions = [
        'mark_confirmed', 'mark_processing', 'mark_shipped',
        'mark_delivered', 'mark_cancelled'
    ]
    
    def mark_confirmed(self, request, queryset):
        """Mark selected orders as confirmed."""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_confirmed.short_description = _('Mark selected orders as confirmed')
    
    def mark_processing(self, request, queryset):
        """Mark selected orders as processing."""
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_processing.short_description = _('Mark selected orders as processing')
    
    def mark_shipped(self, request, queryset):
        """Mark selected orders as shipped."""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=['confirmed', 'processing', 'packed']
        ).update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_shipped.short_description = _('Mark selected orders as shipped')
    
    def mark_delivered(self, request, queryset):
        """Mark selected orders as delivered."""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=['shipped', 'out_for_delivery']
        ).update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = _('Mark selected orders as delivered')
    
    def mark_cancelled(self, request, queryset):
        """Mark selected orders as cancelled."""
        updated = queryset.filter(
            status__in=['pending', 'confirmed', 'processing']
        ).update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as cancelled.')
    mark_cancelled.short_description = _('Mark selected orders as cancelled')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').annotate(
            item_count=Count('items')
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderItem model.
    """
    list_display = [
        'order', 'product_name', 'variant_name', 'quantity',
        'unit_price', 'total_price', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'order__order_number', 'product__title',
        'product_name', 'product_sku'
    ]
    readonly_fields = ['total_price', 'created_at']
    
    fieldsets = (
        (_('Order'), {
            'fields': ('order',)
        }),
        (_('Product Information'), {
            'fields': ('product', 'variant', 'product_name', 'product_sku', 'variant_name')
        }),
        (_('Pricing'), {
            'fields': ('quantity', 'unit_price', 'total_price')
        }),
        (_('Options'), {
            'fields': ('options',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'product', 'variant'
        )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderStatusHistory model.
    """
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'changed_by'
        )


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderShipment model.
    """
    list_display = [
        'order', 'tracking_number', 'carrier', 'status',
        'shipped_at', 'estimated_delivery', 'delivered_at'
    ]
    list_filter = ['status', 'carrier', 'shipped_at', 'delivered_at']
    search_fields = ['order__order_number', 'tracking_number', 'carrier']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (_('Order'), {
            'fields': ('order',)
        }),
        (_('Shipment Details'), {
            'fields': ('tracking_number', 'carrier', 'service_type', 'status')
        }),
        (_('Addresses'), {
            'fields': ('origin_address', 'destination_address'),
            'classes': ('collapse',)
        }),
        (_('Package Information'), {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'shipped_at', 'estimated_delivery', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


class OrderReturnItemInline(admin.TabularInline):
    """
    Inline admin for OrderReturnItem model.
    """
    model = OrderReturnItem
    extra = 0
    fields = ['order_item', 'quantity', 'condition']


@admin.register(OrderReturn)
class OrderReturnAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderReturn model.
    """
    list_display = [
        'return_number', 'order', 'status', 'reason',
        'refund_amount', 'created_at'
    ]
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['return_number', 'order__order_number', 'customer_notes']
    readonly_fields = [
        'return_number', 'created_at', 'updated_at',
        'approved_at', 'processed_at'
    ]
    
    fieldsets = (
        (_('Return Information'), {
            'fields': ('return_number', 'order', 'status', 'reason')
        }),
        (_('Details'), {
            'fields': ('customer_notes', 'admin_notes')
        }),
        (_('Refund'), {
            'fields': ('refund_amount',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'approved_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderReturnItemInline]
    
    actions = ['approve_returns', 'process_returns']
    
    def approve_returns(self, request, queryset):
        """Approve selected returns."""
        from django.utils import timezone
        updated = queryset.filter(status='requested').update(
            status='approved', 
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} returns approved.')
    approve_returns.short_description = _('Approve selected returns')
    
    def process_returns(self, request, queryset):
        """Process selected returns."""
        from django.utils import timezone
        updated = queryset.filter(status='approved').update(
            status='processed',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} returns processed.')
    process_returns.short_description = _('Process selected returns')


@admin.register(OrderReturnItem)
class OrderReturnItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderReturnItem model.
    """
    list_display = ['return_request', 'order_item', 'quantity', 'condition']
    search_fields = [
        'return_request__return_number',
        'order_item__product_name'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'return_request', 'order_item'
        )
