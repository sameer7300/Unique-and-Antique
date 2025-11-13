"""
Views for the cart app.
"""

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal

from .models import Cart, CartItem, SavedItem, CartCoupon
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    CartItemUpdateSerializer, SavedItemSerializer, SavedItemCreateSerializer,
    MoveToCartSerializer, ApplyCouponSerializer, CartSummarySerializer,
    BulkCartUpdateSerializer, CartStatsSerializer
)
from apps.products.models import Product, ProductVariant
from utils.permissions import IsOwnerOrReadOnly
from utils.exceptions import InsufficientStockError, CartError
from utils.helpers import calculate_tax, calculate_shipping_cost


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shopping carts.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get carts for current user."""
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create active cart for user."""
        cart, created = Cart.objects.get_or_create(
            user=self.request.user,
            status='active',
            defaults={'expires_at': None}
        )
        return cart
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active cart."""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart."""
        cart = self.get_object()
        cart.clear()
        
        serializer = self.get_serializer(cart)
        return Response({
            'message': 'Cart cleared successfully',
            'cart': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get cart summary with totals."""
        cart = self.get_object()
        
        # Calculate totals using dynamic settings
        from apps.settings.models import SiteSettings
        settings = SiteSettings.get_settings()
        
        subtotal = cart.subtotal
        
        # Calculate tax
        if settings.tax_enabled:
            tax_amount = (subtotal * settings.tax_rate) / 100
        else:
            tax_amount = Decimal('0.00')
        
        # Calculate shipping
        if settings.shipping_enabled and subtotal < settings.free_shipping_threshold:
            shipping_cost = settings.standard_shipping_cost
        else:
            shipping_cost = Decimal('0.00')
        
        discount_amount = sum(
            coupon.discount_amount for coupon in cart.applied_coupons.all()
        )
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount
        
        summary_data = {
            'total_items': cart.total_items,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'shipping_cost': shipping_cost,
            'discount_amount': discount_amount,
            'total_amount': total_amount,
            'currency': settings.currency_code,
            'tax_rate': settings.tax_rate,
            'free_shipping_threshold': settings.free_shipping_threshold
        }
        
        serializer = CartSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def apply_coupon(self, request):
        """Apply coupon to cart."""
        cart = self.get_object()
        serializer = ApplyCouponSerializer(data=request.data)
        
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            
            # Check if coupon already applied
            if cart.applied_coupons.filter(coupon_code=coupon_code).exists():
                return Response(
                    {'error': 'Coupon already applied'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Apply coupon (simplified logic)
            discount_amount = Decimal('10.00')  # Example fixed discount
            discount_type = 'fixed'
            
            CartCoupon.objects.create(
                cart=cart,
                coupon_code=coupon_code,
                discount_amount=discount_amount,
                discount_type=discount_type
            )
            
            return Response({
                'message': f'Coupon {coupon_code} applied successfully',
                'discount_amount': discount_amount
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update cart items."""
        cart = self.get_object()
        serializer = BulkCartUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            items = serializer.validated_data.get('items', [])
            
            with transaction.atomic():
                if action == 'update':
                    for item_data in items:
                        try:
                            cart_item = cart.items.get(id=item_data['id'])
                            cart_item.quantity = item_data['quantity']
                            cart_item.save()
                        except CartItem.DoesNotExist:
                            continue
                
                elif action == 'remove':
                    item_ids = [item['id'] for item in items]
                    cart.items.filter(id__in=item_ids).delete()
                
                elif action == 'clear':
                    cart.clear()
            
            # Return updated cart
            serializer = CartSerializer(cart, context={'request': request})
            return Response({
                'message': f'Cart {action} completed successfully',
                'cart': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cart items.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get cart items for current user's active cart."""
        try:
            cart = Cart.objects.get(user=self.request.user, status='active')
            return cart.items.all()
        except Cart.DoesNotExist:
            return CartItem.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return CartItemCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CartItemUpdateSerializer
        return CartItemSerializer
    
    def create(self, request, *args, **kwargs):
        """Add item to cart."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get or create active cart
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                status='active',
                defaults={'expires_at': None}
            )
            
            product = serializer.validated_data['product']
            variant = serializer.validated_data.get('variant')
            quantity = serializer.validated_data['quantity']
            options = serializer.validated_data.get('options', {})
            
            try:
                # Check if item already exists in cart
                existing_item = cart.items.filter(
                    product=product,
                    variant=variant
                ).first()
                
                if existing_item:
                    # Update quantity
                    new_quantity = existing_item.quantity + quantity
                    
                    # Check stock availability
                    if variant:
                        if variant.stock < new_quantity:
                            raise InsufficientStockError(
                                product, new_quantity, variant.stock
                            )
                    else:
                        if product.track_inventory and product.stock < new_quantity:
                            raise InsufficientStockError(
                                product, new_quantity, product.stock
                            )
                    
                    existing_item.quantity = new_quantity
                    existing_item.options.update(options)
                    existing_item.save()
                    
                    cart_item = existing_item
                else:
                    # Create new cart item
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        variant=variant,
                        quantity=quantity,
                        options=options
                    )
                
                serializer = CartItemSerializer(
                    cart_item,
                    context={'request': request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except InsufficientStockError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update cart item."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except InsufficientStockError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavedItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved items (wishlist).
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get saved items for current user."""
        return SavedItem.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return SavedItemCreateSerializer
        return SavedItemSerializer
    
    def perform_create(self, serializer):
        """Create saved item for current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def move_to_cart(self, request, pk=None):
        """Move saved item to cart."""
        saved_item = self.get_object()
        serializer = MoveToCartSerializer(
            data=request.data,
            context={'saved_item': saved_item}
        )
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            try:
                cart_item = saved_item.move_to_cart(quantity)
                
                # Return cart item data
                cart_serializer = CartItemSerializer(
                    cart_item,
                    context={'request': request}
                )
                
                return Response({
                    'message': 'Item moved to cart successfully',
                    'cart_item': cart_serializer.data
                })
                
            except InsufficientStockError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_move_to_cart(self, request):
        """Move multiple saved items to cart."""
        item_ids = request.data.get('item_ids', [])
        
        if not item_ids:
            return Response(
                {'error': 'No item IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        saved_items = self.get_queryset().filter(id__in=item_ids)
        moved_count = 0
        errors = []
        
        with transaction.atomic():
            for saved_item in saved_items:
                try:
                    saved_item.move_to_cart(1)  # Default quantity 1
                    moved_count += 1
                except InsufficientStockError as e:
                    errors.append({
                        'item_id': saved_item.id,
                        'error': str(e)
                    })
        
        return Response({
            'message': f'{moved_count} items moved to cart',
            'moved_count': moved_count,
            'errors': errors
        })


class GuestCartView(generics.GenericAPIView):
    """
    View for managing guest carts (session-based).
    """
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        """Get or create guest cart."""
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user=None,
            status='active'
        )
        return cart
    
    def get(self, request):
        """Get guest cart."""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Add item to guest cart."""
        cart = self.get_cart(request)
        serializer = CartItemCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data['product']
            variant = serializer.validated_data.get('variant')
            quantity = serializer.validated_data['quantity']
            options = serializer.validated_data.get('options', {})
            
            try:
                cart_item = cart.add_item(product, quantity, variant)
                if options:
                    cart_item.options = options
                    cart_item.save()
                
                item_serializer = CartItemSerializer(
                    cart_item,
                    context={'request': request}
                )
                return Response(item_serializer.data, status=status.HTTP_201_CREATED)
                
            except InsufficientStockError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Clear guest cart."""
        cart = self.get_cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared successfully'})


class CartStatsView(generics.GenericAPIView):
    """
    View for cart statistics (admin only).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get cart statistics."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.db.models import Avg, Count
        
        stats = {
            'total_carts': Cart.objects.count(),
            'active_carts': Cart.objects.filter(status='active').count(),
            'abandoned_carts': Cart.objects.filter(status='abandoned').count(),
            'converted_carts': Cart.objects.filter(status='converted').count(),
            'average_cart_value': Cart.objects.aggregate(
                avg_value=Avg('items__total_price')
            )['avg_value'] or 0,
            'average_items_per_cart': Cart.objects.annotate(
                item_count=Count('items')
            ).aggregate(
                avg_items=Avg('item_count')
            )['avg_items'] or 0,
        }
        
        serializer = CartStatsSerializer(stats)
        return Response(serializer.data)


class MergeCartsView(generics.GenericAPIView):
    """
    View for merging guest cart with user cart on login.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Merge guest cart with user cart."""
        session_key = request.data.get('session_key')
        
        if not session_key:
            return Response(
                {'error': 'Session key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get guest cart
            guest_cart = Cart.objects.get(
                session_key=session_key,
                user=None,
                status='active'
            )
        except Cart.DoesNotExist:
            return Response({'message': 'No guest cart found'})
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='active',
            defaults={'expires_at': None}
        )
        
        # Merge items
        merged_count = 0
        with transaction.atomic():
            for guest_item in guest_cart.items.all():
                # Check if item already exists in user cart
                existing_item = user_cart.items.filter(
                    product=guest_item.product,
                    variant=guest_item.variant
                ).first()
                
                if existing_item:
                    # Update quantity
                    existing_item.quantity += guest_item.quantity
                    existing_item.save()
                else:
                    # Move item to user cart
                    guest_item.cart = user_cart
                    guest_item.save()
                
                merged_count += 1
            
            # Delete guest cart
            guest_cart.delete()
        
        # Return merged cart
        serializer = CartSerializer(user_cart, context={'request': request})
        return Response({
            'message': f'{merged_count} items merged successfully',
            'cart': serializer.data
        })
