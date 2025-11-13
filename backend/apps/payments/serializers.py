"""
Serializers for the payments app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    Payment, PaymentRefund, PaymentMethod, PaymentWebhook, PaymentTransaction
)

User = get_user_model()


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentMethod model.
    """
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'type', 'provider', 'display_name', 'last_four',
            'brand', 'is_default', 'is_active', 'expires_month',
            'expires_year', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payment methods.
    """
    provider_payment_method_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'type', 'provider', 'provider_payment_method_id', 'display_name',
            'last_four', 'brand', 'is_default', 'expires_month', 'expires_year'
        ]
    
    def validate_expires_month(self, value):
        """Validate expiration month."""
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value
    
    def validate_expires_year(self, value):
        """Validate expiration year."""
        if value is not None:
            from django.utils import timezone
            current_year = timezone.now().year
            if value < current_year or value > current_year + 20:
                raise serializers.ValidationError("Invalid expiration year.")
        return value


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentTransaction model.
    """
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'provider_transaction_id', 'action',
            'action_display', 'status', 'status_display', 'amount',
            'currency', 'response_data', 'error_message', 'created_at',
            'processed_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class PaymentRefundSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentRefund model.
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'provider_refund_id', 'amount', 'currency',
            'status', 'status_display', 'reason', 'admin_notes', 'metadata',
            'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'processed_at']


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model in list views.
    """
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(
        source='order.user.get_full_name',
        read_only=True
    )
    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_type_display = serializers.CharField(
        source='get_payment_type_display',
        read_only=True
    )
    is_successful = serializers.ReadOnlyField()
    is_refundable = serializers.ReadOnlyField()
    remaining_refundable_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'order_number', 'customer_name', 'provider',
            'provider_display', 'status', 'status_display', 'payment_type',
            'payment_type_display', 'amount', 'currency', 'processing_fee',
            'refunded_amount', 'is_successful', 'is_refundable',
            'remaining_refundable_amount', 'created_at', 'processed_at'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model in detail views.
    """
    order = serializers.SerializerMethodField()
    refunds = PaymentRefundSerializer(many=True, read_only=True)
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_type_display = serializers.CharField(
        source='get_payment_type_display',
        read_only=True
    )
    is_successful = serializers.ReadOnlyField()
    is_refundable = serializers.ReadOnlyField()
    remaining_refundable_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'order', 'provider', 'provider_display',
            'provider_payment_id', 'provider_payment_intent_id', 'status',
            'status_display', 'payment_type', 'payment_type_display',
            'amount', 'currency', 'processing_fee', 'payment_method_details',
            'billing_address', 'metadata', 'failure_reason', 'admin_notes',
            'refunded_amount', 'refunds', 'transactions', 'is_successful',
            'is_refundable', 'remaining_refundable_amount', 'created_at',
            'updated_at', 'processed_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'processed_at']
    
    def get_order(self, obj):
        """Get order information."""
        order = obj.order
        return {
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.user.get_full_name(),
            'customer_email': order.user.email,
            'total_amount': order.total_amount,
            'status': order.status,
        }


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments.
    """
    order_id = serializers.IntegerField(write_only=True)
    payment_method_id = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Payment
        fields = [
            'order_id', 'provider', 'payment_method_id', 'amount',
            'currency', 'billing_address', 'metadata'
        ]
    
    def validate_order_id(self, value):
        """Validate order exists and belongs to user."""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        # Check if order belongs to current user (if not admin)
        request = self.context.get('request')
        if request and not request.user.is_admin_user:
            if order.user != request.user:
                raise serializers.ValidationError("Order not found.")
        
        # Check if order can be paid
        if order.payment_status == 'paid':
            raise serializers.ValidationError("Order is already paid.")
        
        if order.status == 'cancelled':
            raise serializers.ValidationError("Cannot pay for cancelled order.")
        
        return value
    
    def validate_amount(self, value):
        """Validate payment amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value
    
    def validate(self, attrs):
        """Validate payment data."""
        from apps.orders.models import Order
        
        order = Order.objects.get(id=attrs['order_id'])
        
        # Validate amount matches order total
        if attrs['amount'] != order.total_amount:
            raise serializers.ValidationError(
                "Payment amount must match order total."
            )
        
        # Validate currency matches order currency
        currency = attrs.get('currency', 'USD')
        if currency != order.currency:
            raise serializers.ValidationError(
                "Payment currency must match order currency."
            )
        
        attrs['order'] = order
        return attrs


class PaymentRefundCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payment refunds.
    """
    
    class Meta:
        model = PaymentRefund
        fields = ['amount', 'reason', 'admin_notes']
    
    def validate_amount(self, value):
        """Validate refund amount."""
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be positive.")
        
        payment = self.context['payment']
        if value > payment.remaining_refundable_amount:
            raise serializers.ValidationError(
                f"Refund amount cannot exceed {payment.remaining_refundable_amount}."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate refund can be created."""
        payment = self.context['payment']
        
        if not payment.is_refundable:
            raise serializers.ValidationError("Payment is not refundable.")
        
        return attrs


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentWebhook model.
    """
    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'webhook_id', 'provider', 'provider_display',
            'provider_webhook_id', 'event_type', 'event_data', 'status',
            'status_display', 'processing_notes', 'related_payment',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class PaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for creating payment intents (Stripe).
    """
    order_id = serializers.IntegerField()
    payment_method_id = serializers.CharField(required=False)
    save_payment_method = serializers.BooleanField(default=False)
    
    def validate_order_id(self, value):
        """Validate order exists and can be paid."""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        if order.payment_status == 'paid':
            raise serializers.ValidationError("Order is already paid.")
        
        return value


class PaymentConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming payments.
    """
    payment_intent_id = serializers.CharField()
    payment_method_id = serializers.CharField(required=False)


class PaymentStatsSerializer(serializers.Serializer):
    """
    Serializer for payment statistics.
    """
    total_payments = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_refunds = serializers.IntegerField()
    total_refund_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class BulkPaymentUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk payment operations.
    """
    payment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(
        choices=['refund', 'cancel', 'capture']
    )
    refund_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    reason = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Validate bulk operation data."""
        action = attrs['action']
        
        if action == 'refund' and not attrs.get('refund_amount'):
            raise serializers.ValidationError(
                "Refund amount is required for refund action."
            )
        
        return attrs


class CODPaymentSerializer(serializers.Serializer):
    """
    Serializer for Cash on Delivery payments.
    """
    order_id = serializers.IntegerField()
    delivery_address = serializers.DictField()
    delivery_instructions = serializers.CharField(required=False, allow_blank=True)
    
    def validate_order_id(self, value):
        """Validate order exists and supports COD."""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        if order.payment_method != 'cod':
            raise serializers.ValidationError("Order does not support COD.")
        
        return value


class PaymentReportSerializer(serializers.Serializer):
    """
    Serializer for payment reports.
    """
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    provider = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Validate date range."""
        if attrs['date_from'] > attrs['date_to']:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )
        
        return attrs
