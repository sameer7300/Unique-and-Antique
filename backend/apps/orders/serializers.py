"""
Serializers for the orders app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderShipment,
    OrderReturn, OrderReturnItem
)
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'product_sku',
            'variant_name', 'quantity', 'unit_price', 'total_price',
            'options', 'created_at'
        ]
        read_only_fields = ['created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for OrderStatusHistory model.
    """
    changed_by_name = serializers.CharField(
        source='changed_by.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'status', 'status_display', 'notes', 'changed_by',
            'changed_by_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class OrderShipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderShipment model.
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = OrderShipment
        fields = [
            'id', 'tracking_number', 'carrier', 'service_type', 'status',
            'status_display', 'origin_address', 'destination_address',
            'weight', 'dimensions', 'created_at', 'shipped_at',
            'estimated_delivery', 'delivered_at'
        ]
        read_only_fields = ['created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model in list views.
    """
    customer_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    total_items = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_returned = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_id', 'customer_name', 'status',
            'status_display', 'payment_status', 'payment_status_display',
            'payment_method', 'payment_method_display', 'total_amount',
            'currency', 'total_items', 'can_be_cancelled', 'can_be_returned',
            'is_paid', 'is_completed', 'created_at', 'estimated_delivery_date'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model in detail views.
    """
    customer = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shipments = OrderShipmentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    total_items = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_returned = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_id', 'customer', 'status',
            'status_display', 'payment_status', 'payment_status_display',
            'payment_method', 'payment_method_display', 'subtotal',
            'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'currency', 'shipping_address', 'billing_address', 'shipping_method',
            'tracking_number', 'carrier', 'customer_notes', 'admin_notes',
            'items', 'status_history', 'shipments', 'total_items',
            'can_be_cancelled', 'can_be_returned', 'is_paid', 'is_completed',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at',
            'delivered_at', 'estimated_delivery_date'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]
    
    def get_customer(self, obj):
        """Get customer information."""
        user = obj.user
        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'phone': user.phone,
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating orders.
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'payment_method', 'shipping_address', 'billing_address',
            'shipping_method', 'customer_notes', 'items'
        ]
    
    def validate_items(self, value):
        """Validate order items."""
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        
        from apps.products.models import Product, ProductVariant
        
        for item in value:
            # Validate required fields
            required_fields = ['product_id', 'quantity']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(
                        f"Item missing required field: {field}"
                    )
            
            # Validate product exists
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {item['product_id']} not found."
                )
            
            if product.status != 'active':
                raise serializers.ValidationError(
                    f"Product '{product.title}' is not available."
                )
            
            # Validate variant if provided
            variant = None
            if item.get('variant_id'):
                try:
                    variant = ProductVariant.objects.get(
                        id=item['variant_id'],
                        product=product
                    )
                except ProductVariant.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Product variant with id {item['variant_id']} not found."
                    )
                
                if not variant.is_active:
                    raise serializers.ValidationError(
                        f"Product variant is not available."
                    )
            
            # Validate quantity
            quantity = item['quantity']
            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be positive.")
            
            # Check stock availability
            if variant:
                if variant.stock < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.title} - {variant.name}. "
                        f"Available: {variant.stock}, Requested: {quantity}"
                    )
            else:
                if product.track_inventory and product.stock < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.title}. "
                        f"Available: {product.stock}, Requested: {quantity}"
                    )
        
        return value
    
    def validate_shipping_address(self, value):
        """Validate shipping address format."""
        required_fields = [
            'first_name', 'last_name', 'address_line_1',
            'city', 'state', 'postal_code', 'country'
        ]
        
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(
                    f"Shipping address missing required field: {field}"
                )
        
        return value
    
    def validate_billing_address(self, value):
        """Validate billing address format."""
        required_fields = [
            'first_name', 'last_name', 'address_line_1',
            'city', 'state', 'postal_code', 'country'
        ]
        
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(
                    f"Billing address missing required field: {field}"
                )
        
        return value


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating orders (admin only).
    """
    
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'shipping_method', 'tracking_number',
            'carrier', 'admin_notes', 'estimated_delivery_date'
        ]
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['processing', 'cancelled'],
                'processing': ['packed', 'cancelled'],
                'packed': ['shipped', 'cancelled'],
                'shipped': ['out_for_delivery', 'delivered'],
                'out_for_delivery': ['delivered', 'failed_delivery'],
                'delivered': ['returned'],
                'cancelled': [],  # Cannot transition from cancelled
                'returned': [],   # Cannot transition from returned
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'."
                )
        
        return value


class OrderReturnItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderReturnItem model.
    """
    order_item = OrderItemSerializer(read_only=True)
    
    class Meta:
        model = OrderReturnItem
        fields = ['id', 'order_item', 'quantity', 'condition']


class OrderReturnSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderReturn model.
    """
    items = OrderReturnItemSerializer(many=True, read_only=True)
    order = OrderListSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    reason_display = serializers.CharField(
        source='get_reason_display',
        read_only=True
    )
    
    class Meta:
        model = OrderReturn
        fields = [
            'id', 'return_number', 'order', 'status', 'status_display',
            'reason', 'reason_display', 'customer_notes', 'admin_notes',
            'refund_amount', 'items', 'created_at', 'updated_at',
            'approved_at', 'processed_at'
        ]
        read_only_fields = [
            'return_number', 'created_at', 'updated_at', 'approved_at', 'processed_at'
        ]


class OrderReturnCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating order returns.
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = OrderReturn
        fields = ['reason', 'customer_notes', 'items']
    
    def validate_items(self, value):
        """Validate return items."""
        if not value:
            raise serializers.ValidationError("Return must have at least one item.")
        
        order = self.context['order']
        
        for item in value:
            # Validate required fields
            if 'order_item_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'order_item_id' and 'quantity'."
                )
            
            # Validate order item exists
            try:
                order_item = order.items.get(id=item['order_item_id'])
            except OrderItem.DoesNotExist:
                raise serializers.ValidationError(
                    f"Order item with id {item['order_item_id']} not found."
                )
            
            # Validate quantity
            quantity = item['quantity']
            if quantity <= 0 or quantity > order_item.quantity:
                raise serializers.ValidationError(
                    f"Invalid return quantity for {order_item.product_name}. "
                    f"Must be between 1 and {order_item.quantity}."
                )
        
        return value
    
    def validate(self, attrs):
        """Validate order can be returned."""
        order = self.context['order']
        
        if not order.can_be_returned:
            raise serializers.ValidationError("This order cannot be returned.")
        
        return attrs


class OrderStatsSerializer(serializers.Serializer):
    """
    Serializer for order statistics.
    """
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    confirmed_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    returned_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)


class BulkOrderUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk order updates.
    """
    order_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(
        choices=['update_status', 'cancel', 'mark_shipped']
    )
    status = serializers.CharField(required=False)
    tracking_number = serializers.CharField(required=False)
    carrier = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Validate bulk operation data."""
        action = attrs['action']
        
        if action == 'update_status' and not attrs.get('status'):
            raise serializers.ValidationError(
                "Status is required for update_status action."
            )
        
        if action == 'mark_shipped':
            if not attrs.get('tracking_number'):
                raise serializers.ValidationError(
                    "Tracking number is required for mark_shipped action."
                )
        
        return attrs
