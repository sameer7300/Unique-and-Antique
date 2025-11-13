"""
Serializers for the cart app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, SavedItem, CartCoupon
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer

User = get_user_model()


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    """
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    current_price = serializers.ReadOnlyField()
    price_changed = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    stock_available = serializers.ReadOnlyField()
    can_fulfill_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity', 'price_at_add',
            'total_price', 'current_price', 'price_changed', 'is_available',
            'stock_available', 'can_fulfill_quantity', 'options',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'price_at_add']
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating cart items.
    """
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'variant_id', 'quantity', 'options']
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value
    
    def validate(self, attrs):
        """Validate product and variant availability."""
        from apps.products.models import Product, ProductVariant
        
        try:
            product = Product.objects.get(id=attrs['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        if product.status != 'active':
            raise serializers.ValidationError("Product is not available.")
        
        variant = None
        if attrs.get('variant_id'):
            try:
                variant = ProductVariant.objects.get(
                    id=attrs['variant_id'],
                    product=product
                )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found.")
            
            if not variant.is_active:
                raise serializers.ValidationError("Product variant is not available.")
        
        # Check stock availability
        quantity = attrs['quantity']
        if variant:
            if variant.stock < quantity:
                raise serializers.ValidationError(
                    f"Only {variant.stock} items available for this variant."
                )
        else:
            if product.track_inventory and product.stock < quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available."
                )
        
        attrs['product'] = product
        attrs['variant'] = variant
        return attrs


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating cart items.
    """
    
    class Meta:
        model = CartItem
        fields = ['quantity', 'options']
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value
    
    def validate(self, attrs):
        """Validate stock availability for updated quantity."""
        if 'quantity' in attrs:
            cart_item = self.instance
            quantity = attrs['quantity']
            
            if cart_item.variant:
                if cart_item.variant.stock < quantity:
                    raise serializers.ValidationError(
                        f"Only {cart_item.variant.stock} items available."
                    )
            else:
                product = cart_item.product
                if product.track_inventory and product.stock < quantity:
                    raise serializers.ValidationError(
                        f"Only {product.stock} items available."
                    )
        
        return attrs


class CartCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for CartCoupon model.
    """
    
    class Meta:
        model = CartCoupon
        fields = [
            'id', 'coupon_code', 'discount_amount', 'discount_type', 'applied_at'
        ]
        read_only_fields = ['applied_at']


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model.
    """
    items = CartItemSerializer(many=True, read_only=True)
    applied_coupons = CartCouponSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    total_weight = serializers.ReadOnlyField()
    is_empty = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'cart_id', 'status', 'items', 'applied_coupons',
            'total_items', 'subtotal', 'total_weight', 'is_empty',
            'created_at', 'updated_at', 'expires_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SavedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedItem model (Wishlist).
    """
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = SavedItem
        fields = [
            'id', 'product', 'variant', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SavedItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating saved items.
    """
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = SavedItem
        fields = ['product_id', 'variant_id', 'notes']
    
    def validate(self, attrs):
        """Validate product and variant existence."""
        from apps.products.models import Product, ProductVariant
        
        try:
            product = Product.objects.get(id=attrs['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        variant = None
        if attrs.get('variant_id'):
            try:
                variant = ProductVariant.objects.get(
                    id=attrs['variant_id'],
                    product=product
                )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found.")
        
        # Check if already saved
        user = self.context['request'].user
        if SavedItem.objects.filter(
            user=user,
            product=product,
            variant=variant
        ).exists():
            raise serializers.ValidationError("Item is already in your wishlist.")
        
        attrs['product'] = product
        attrs['variant'] = variant
        return attrs


class MoveToCartSerializer(serializers.Serializer):
    """
    Serializer for moving saved item to cart.
    """
    quantity = serializers.IntegerField(default=1, min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity against stock."""
        saved_item = self.context['saved_item']
        
        if saved_item.variant:
            if saved_item.variant.stock < value:
                raise serializers.ValidationError(
                    f"Only {saved_item.variant.stock} items available."
                )
        else:
            product = saved_item.product
            if product.track_inventory and product.stock < value:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available."
                )
        
        return value


class ApplyCouponSerializer(serializers.Serializer):
    """
    Serializer for applying coupon to cart.
    """
    coupon_code = serializers.CharField(max_length=50)
    
    def validate_coupon_code(self, value):
        """Validate coupon code."""
        # This is a placeholder - in a real implementation,
        # you would validate against a Coupon model
        valid_coupons = ['SAVE10', 'WELCOME20', 'FREESHIP']
        
        if value.upper() not in valid_coupons:
            raise serializers.ValidationError("Invalid coupon code.")
        
        return value.upper()


class CartSummarySerializer(serializers.Serializer):
    """
    Serializer for cart summary information.
    """
    total_items = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')


class BulkCartUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk cart operations.
    """
    action = serializers.ChoiceField(choices=['update', 'remove', 'clear'])
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    def validate(self, attrs):
        """Validate bulk operation data."""
        action = attrs['action']
        
        if action in ['update', 'remove'] and not attrs.get('items'):
            raise serializers.ValidationError(
                f"Items list is required for '{action}' action."
            )
        
        if action == 'update':
            for item in attrs.get('items', []):
                if 'id' not in item or 'quantity' not in item:
                    raise serializers.ValidationError(
                        "Each item must have 'id' and 'quantity' fields."
                    )
                
                if item['quantity'] <= 0:
                    raise serializers.ValidationError(
                        "Quantity must be positive."
                    )
        
        elif action == 'remove':
            for item in attrs.get('items', []):
                if 'id' not in item:
                    raise serializers.ValidationError(
                        "Each item must have 'id' field."
                    )
        
        return attrs


class CartStatsSerializer(serializers.Serializer):
    """
    Serializer for cart statistics.
    """
    total_carts = serializers.IntegerField()
    active_carts = serializers.IntegerField()
    abandoned_carts = serializers.IntegerField()
    converted_carts = serializers.IntegerField()
    average_cart_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_items_per_cart = serializers.DecimalField(max_digits=5, decimal_places=2)
