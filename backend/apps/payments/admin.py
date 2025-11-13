"""
Admin configuration for the payments app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from .models import (
    Payment, PaymentRefund, PaymentMethod, PaymentWebhook, PaymentTransaction
)


class PaymentRefundInline(admin.TabularInline):
    """
    Inline admin for PaymentRefund model.
    """
    model = PaymentRefund
    extra = 0
    fields = ['amount', 'status', 'reason', 'created_at']
    readonly_fields = ['refund_id', 'created_at', 'processed_at']


class PaymentTransactionInline(admin.TabularInline):
    """
    Inline admin for PaymentTransaction model.
    """
    model = PaymentTransaction
    extra = 0
    fields = ['action', 'amount', 'status', 'created_at']
    readonly_fields = ['transaction_id', 'created_at', 'processed_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment model.
    """
    list_display = [
        'payment_id_short', 'order', 'provider', 'amount',
        'status', 'payment_type', 'is_successful', 'created_at'
    ]
    list_filter = [
        'provider', 'status', 'payment_type', 'created_at', 'processed_at'
    ]
    search_fields = [
        'payment_id', 'order__order_number', 'provider_payment_id',
        'provider_payment_intent_id'
    ]
    readonly_fields = [
        'payment_id', 'created_at', 'updated_at', 'processed_at',
        'is_successful', 'is_refundable', 'remaining_refundable_amount'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('payment_id', 'order', 'provider', 'status', 'payment_type')
        }),
        (_('Provider Details'), {
            'fields': ('provider_payment_id', 'provider_payment_intent_id')
        }),
        (_('Amount'), {
            'fields': ('amount', 'currency', 'processing_fee', 'refunded_amount')
        }),
        (_('Payment Method'), {
            'fields': ('payment_method_details',),
            'classes': ('collapse',)
        }),
        (_('Billing'), {
            'fields': ('billing_address',),
            'classes': ('collapse',)
        }),
        (_('Status Information'), {
            'fields': ('is_successful', 'is_refundable', 'remaining_refundable_amount'),
            'classes': ('collapse',)
        }),
        (_('Notes and Metadata'), {
            'fields': ('failure_reason', 'admin_notes', 'metadata'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentRefundInline, PaymentTransactionInline]
    
    actions = ['mark_succeeded', 'mark_failed', 'mark_cancelled']
    
    def payment_id_short(self, obj):
        """Display shortened payment ID."""
        return str(obj.payment_id)[:8] + '...'
    payment_id_short.short_description = _('Payment ID')
    
    def mark_succeeded(self, request, queryset):
        """Mark selected payments as succeeded."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='succeeded',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} payments marked as succeeded.')
    mark_succeeded.short_description = _('Mark selected payments as succeeded')
    
    def mark_failed(self, request, queryset):
        """Mark selected payments as failed."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='failed',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_failed.short_description = _('Mark selected payments as failed')
    
    def mark_cancelled(self, request, queryset):
        """Mark selected payments as cancelled."""
        updated = queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, f'{updated} payments marked as cancelled.')
    mark_cancelled.short_description = _('Mark selected payments as cancelled')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentRefund model.
    """
    list_display = [
        'refund_id_short', 'payment', 'amount', 'status',
        'reason', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = [
        'refund_id', 'payment__payment_id', 'provider_refund_id', 'reason'
    ]
    readonly_fields = [
        'refund_id', 'created_at', 'updated_at', 'processed_at'
    ]
    
    fieldsets = (
        (_('Refund Information'), {
            'fields': ('refund_id', 'payment', 'provider_refund_id', 'status')
        }),
        (_('Amount'), {
            'fields': ('amount', 'currency')
        }),
        (_('Details'), {
            'fields': ('reason', 'admin_notes')
        }),
        (_('Metadata'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def refund_id_short(self, obj):
        """Display shortened refund ID."""
        return str(obj.refund_id)[:8] + '...'
    refund_id_short.short_description = _('Refund ID')
    
    actions = ['process_refunds']
    
    def process_refunds(self, request, queryset):
        """Process selected refunds."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='processing',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} refunds marked as processing.')
    process_refunds.short_description = _('Process selected refunds')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentMethod model.
    """
    list_display = [
        'user', 'display_name', 'type', 'provider',
        'last_four', 'brand', 'is_default', 'is_active', 'created_at'
    ]
    list_filter = [
        'type', 'provider', 'brand', 'is_default',
        'is_active', 'created_at'
    ]
    search_fields = [
        'user__email', 'display_name', 'last_four',
        'provider_payment_method_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Payment Method'), {
            'fields': ('type', 'provider', 'provider_payment_method_id')
        }),
        (_('Display Information'), {
            'fields': ('display_name', 'last_four', 'brand')
        }),
        (_('Expiration'), {
            'fields': ('expires_month', 'expires_year'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_default', 'is_active')
        }),
        (_('Metadata'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentWebhook model.
    """
    list_display = [
        'webhook_id_short', 'provider', 'event_type',
        'status', 'related_payment', 'created_at'
    ]
    list_filter = ['provider', 'event_type', 'status', 'created_at']
    search_fields = [
        'webhook_id', 'provider_webhook_id', 'event_type'
    ]
    readonly_fields = ['webhook_id', 'created_at', 'processed_at']
    
    fieldsets = (
        (_('Webhook Information'), {
            'fields': ('webhook_id', 'provider', 'provider_webhook_id', 'event_type')
        }),
        (_('Processing'), {
            'fields': ('status', 'processing_notes', 'related_payment')
        }),
        (_('Event Data'), {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def webhook_id_short(self, obj):
        """Display shortened webhook ID."""
        return str(obj.webhook_id)[:8] + '...'
    webhook_id_short.short_description = _('Webhook ID')
    
    actions = ['mark_processed', 'mark_ignored']
    
    def mark_processed(self, request, queryset):
        """Mark selected webhooks as processed."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='processed',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} webhooks marked as processed.')
    mark_processed.short_description = _('Mark selected webhooks as processed')
    
    def mark_ignored(self, request, queryset):
        """Mark selected webhooks as ignored."""
        updated = queryset.filter(status='pending').update(status='ignored')
        self.message_user(request, f'{updated} webhooks marked as ignored.')
    mark_ignored.short_description = _('Mark selected webhooks as ignored')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentTransaction model.
    """
    list_display = [
        'transaction_id_short', 'payment', 'action',
        'amount', 'status', 'created_at'
    ]
    list_filter = ['action', 'status', 'created_at']
    search_fields = [
        'transaction_id', 'payment__payment_id',
        'provider_transaction_id'
    ]
    readonly_fields = [
        'transaction_id', 'created_at', 'processed_at'
    ]
    
    fieldsets = (
        (_('Transaction Information'), {
            'fields': ('transaction_id', 'payment', 'provider_transaction_id')
        }),
        (_('Action'), {
            'fields': ('action', 'status', 'amount', 'currency')
        }),
        (_('Response'), {
            'fields': ('response_data', 'error_message'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def transaction_id_short(self, obj):
        """Display shortened transaction ID."""
        return str(obj.transaction_id)[:8] + '...'
    transaction_id_short.short_description = _('Transaction ID')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')
