"""
Views for the orders app.
"""

from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory, OrderShipment, OrderReturn, OrderReturnItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, OrderReturnSerializer, OrderReturnCreateSerializer,
    OrderStatsSerializer, BulkOrderUpdateSerializer
)
from .services import OrderEmailService
from apps.cart.models import Cart
from utils.permissions import IsOwnerOrReadOnly, IsStaffOrAdmin, CanManageOrders
from utils.pagination import OrderPagination
from utils.exceptions import OrderProcessingError
from utils.helpers import generate_order_number, calculate_estimated_delivery


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get orders based on user permissions."""
        if self.request.user.is_staff:
            return Order.objects.select_related('user').prefetch_related(
                'items__product', 'items__variant', 'status_history'
            )
        else:
            return Order.objects.filter(user=self.request.user).select_related(
                'user'
            ).prefetch_related('items__product', 'items__variant')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [CanManageOrders]
        elif self.action in ['list', 'retrieve', 'create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = self._create_order_from_data(serializer.validated_data, request.user)
                    
                    # Set flag to skip duplicate confirmation email from signals
                    order._skip_confirmation_email = True
                    
                    # Clear user's cart if order created from cart
                    cart_id = request.data.get('cart_id')
                    if cart_id:
                        try:
                            cart = Cart.objects.get(id=cart_id, user=request.user)
                            cart.status = 'converted'
                            cart.converted_to_order = order
                            cart.save()
                        except Cart.DoesNotExist:
                            pass
                    
                    # Send order confirmation emails
                    try:
                        email_result = OrderEmailService.send_order_confirmation_email(order)
                        if not email_result.get('customer_email_sent'):
                            # Log warning but don't fail the order
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Failed to send customer confirmation email for order {order.order_number}")
                    except Exception as e:
                        # Log error but don't fail the order
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending order confirmation emails for order {order.order_number}: {str(e)}")
                    
                    # Return created order
                    response_serializer = OrderDetailSerializer(
                        order,
                        context={'request': request}
                    )
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    
            except OrderProcessingError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _create_order_from_data(self, validated_data, user):
        """Create order from validated data."""
        from apps.products.models import Product, ProductVariant
        
        items_data = validated_data.pop('items')
        
        # Calculate order totals
        subtotal = Decimal('0.00')
        order_items = []
        
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            variant = None
            if item_data.get('variant_id'):
                variant = ProductVariant.objects.get(id=item_data['variant_id'])
            
            quantity = item_data['quantity']
            
            # Check stock availability before creating order
            if variant:
                if variant.stock < quantity:
                    raise OrderProcessingError(f"Insufficient stock for {product.title} - {variant.name}. Available: {variant.stock}, Requested: {quantity}")
            elif product.track_inventory:
                if product.stock < quantity:
                    raise OrderProcessingError(f"Insufficient stock for {product.title}. Available: {product.stock}, Requested: {quantity}")
            
            unit_price = variant.price if variant else product.price
            total_price = unit_price * quantity
            
            order_items.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
                'options': item_data.get('options', {})
            })
            
            subtotal += total_price
        
        # Calculate additional costs
        tax_rate = Decimal('8.25')  # Example tax rate
        tax_amount = (subtotal * tax_rate / 100).quantize(Decimal('0.01'))
        shipping_cost = Decimal('10.00')  # Example shipping cost
        discount_amount = Decimal('0.00')  # No discount for now
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            total_amount=total_amount,
            estimated_delivery_date=calculate_estimated_delivery(
                validated_data.get('shipping_method', 'standard')
            ),
            **validated_data
        )
        
        # Create order items and reduce stock
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                variant=item_data['variant'],
                product_name=item_data['product'].title,
                product_sku=item_data['variant'].sku if item_data['variant'] else item_data['product'].sku,
                variant_name=item_data['variant'].name if item_data['variant'] else '',
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                options=item_data['options']
            )
            
            # Reduce stock after creating order item
            if item_data['variant']:
                old_stock = item_data['variant'].stock
                item_data['variant'].stock -= item_data['quantity']
                item_data['variant'].save()
                print(f"Stock reduced for variant {item_data['variant'].name}: {old_stock} -> {item_data['variant'].stock}")
            elif item_data['product'].track_inventory:
                old_stock = item_data['product'].stock
                item_data['product'].stock -= item_data['quantity']
                item_data['product'].save()
                print(f"Stock reduced for product {item_data['product'].title}: {old_stock} -> {item_data['product'].stock}")
        
        return order
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if not request.user.is_staff and order.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic():
            old_status = order.status
            order.status = 'cancelled'
            # Set flag to skip duplicate status change email from signals (API handles it)
            order._skip_status_email = True
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes=f"Order cancelled by {request.user.get_full_name()}",
                changed_by=request.user
            )
            
            # Restore inventory
            for item in order.items.all():
                if item.variant:
                    old_stock = item.variant.stock
                    item.variant.stock += item.quantity
                    item.variant.save()
                    print(f"Stock restored for variant {item.variant.name}: {old_stock} -> {item.variant.stock}")
                elif item.product.track_inventory:
                    old_stock = item.product.stock
                    item.product.stock += item.quantity
                    item.product.save()
                    print(f"Stock restored for product {item.product.title}: {old_stock} -> {item.product.stock}")
            
            # Send cancellation emails
            try:
                email_result = OrderEmailService.send_order_status_change_email(
                    order, old_status, 'cancelled', request.user
                )
                if not email_result.get('customer_email_sent'):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to send cancellation email to customer for order {order.order_number}")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error sending cancellation emails for order {order.order_number}: {str(e)}")
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response({
            'message': 'Order cancelled successfully',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageOrders])
    def update_status(self, request, pk=None):
        """Update order status (admin only)."""
        order = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status transition
        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_status = order.status
            order.status = new_status
            
            # Update timestamps based on status
            if new_status == 'confirmed':
                order.confirmed_at = timezone.now()
            elif new_status == 'shipped':
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = timezone.now()
            
            # Set flag to skip duplicate status change email from signals (API handles it)
            order._skip_status_email = True
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes or f"Status changed from {old_status} to {new_status}",
                changed_by=request.user
            )
            
            # Send status change emails
            try:
                email_result = OrderEmailService.send_order_status_change_email(
                    order, old_status, new_status, request.user
                )
                if not email_result.get('customer_email_sent'):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to send status change email to customer for order {order.order_number}")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error sending status change emails for order {order.order_number}: {str(e)}")
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response({
            'message': f'Order status updated to {new_status}',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageOrders])
    def add_tracking(self, request, pk=None):
        """Add tracking information to order."""
        order = self.get_object()
        tracking_number = request.data.get('tracking_number')
        carrier = request.data.get('carrier')
        
        if not tracking_number:
            return Response(
                {'error': 'Tracking number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_status = order.status
            order.tracking_number = tracking_number
            order.carrier = carrier or ''
            
            # Update status to shipped if not already
            status_changed = False
            if order.status in ['confirmed', 'processing', 'packed']:
                order.status = 'shipped'
                order.shipped_at = timezone.now()
                status_changed = True
                # Set flag to skip duplicate status change email from signals (API handles it)
                order._skip_status_email = True
            
            order.save()
            
            # Create shipment record
            OrderShipment.objects.create(
                order=order,
                tracking_number=tracking_number,
                carrier=carrier or '',
                status='shipped',
                origin_address={},  # Would be filled with warehouse address
                destination_address=order.shipping_address,
                shipped_at=timezone.now()
            )
            
            # Create status history if status changed
            if status_changed:
                OrderStatusHistory.objects.create(
                    order=order,
                    status='shipped',
                    notes=f"Order shipped with tracking number {tracking_number}",
                    changed_by=request.user
                )
                
                # Send shipping notification emails
                try:
                    email_result = OrderEmailService.send_order_status_change_email(
                        order, old_status, 'shipped', request.user
                    )
                    if not email_result.get('customer_email_sent'):
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to send shipping email to customer for order {order.order_number}")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error sending shipping emails for order {order.order_number}: {str(e)}")
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response({
            'message': 'Tracking information added successfully',
            'order': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOrAdmin])
    def stats(self, request):
        """Get order statistics."""
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'shipped_orders': Order.objects.filter(status='shipped').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
            'returned_orders': Order.objects.filter(status='returned').count(),
            'total_revenue': Order.objects.filter(
                payment_status='paid'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00'),
            'average_order_value': Order.objects.aggregate(
                avg=Avg('total_amount')
            )['avg'] or Decimal('0.00'),
        }
        
        serializer = OrderStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[CanManageOrders])
    def bulk_update(self, request):
        """Bulk update orders."""
        serializer = BulkOrderUpdateSerializer(data=request.data)
        if serializer.is_valid():
            order_ids = serializer.validated_data['order_ids']
            action = serializer.validated_data['action']
            
            orders = Order.objects.filter(id__in=order_ids)
            updated_count = 0
            
            with transaction.atomic():
                if action == 'update_status':
                    new_status = serializer.validated_data['status']
                    for order in orders:
                        order.status = new_status
                        order.save()
                        
                        OrderStatusHistory.objects.create(
                            order=order,
                            status=new_status,
                            notes=f"Bulk status update to {new_status}",
                            changed_by=request.user
                        )
                        updated_count += 1
                
                elif action == 'cancel':
                    for order in orders:
                        if order.can_be_cancelled:
                            order.status = 'cancelled'
                            order.save()
                            
                            OrderStatusHistory.objects.create(
                                order=order,
                                status='cancelled',
                                notes="Bulk cancellation",
                                changed_by=request.user
                            )
                            updated_count += 1
                
                elif action == 'mark_shipped':
                    tracking_number = serializer.validated_data.get('tracking_number')
                    carrier = serializer.validated_data.get('carrier')
                    
                    for order in orders:
                        if order.status in ['confirmed', 'processing', 'packed']:
                            order.status = 'shipped'
                            order.shipped_at = timezone.now()
                            if tracking_number:
                                order.tracking_number = tracking_number
                            if carrier:
                                order.carrier = carrier
                            order.save()
                            
                            OrderStatusHistory.objects.create(
                                order=order,
                                status='shipped',
                                notes="Bulk shipping update",
                                changed_by=request.user
                            )
                            updated_count += 1
            
            return Response({
                'message': f'{updated_count} orders updated successfully',
                'updated_count': updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def track(self, request):
        """Track order by order number or tracking number."""
        identifier = request.query_params.get('identifier') or request.query_params.get('order_number')
        
        if not identifier:
            return Response(
                {'error': 'Order number or tracking number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to find order by order number first
        order = None
        try:
            order = Order.objects.select_related('user').prefetch_related(
                'items__product__images', 'items__variant', 'status_history', 'shipments'
            ).get(order_number=identifier)
        except Order.DoesNotExist:
            # Try to find by tracking number
            try:
                order = Order.objects.select_related('user').prefetch_related(
                    'items__product__images', 'items__variant', 'status_history', 'shipments'
                ).get(tracking_number=identifier)
            except Order.DoesNotExist:
                # Try to find by shipment tracking number
                try:
                    shipment = OrderShipment.objects.select_related('order__user').get(
                        tracking_number=identifier
                    )
                    order = shipment.order
                except OrderShipment.DoesNotExist:
                    pass
        
        if not order:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return order details for tracking
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(serializer.data)


class OrderReturnViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing order returns.
    """
    serializer_class = OrderReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'reason']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get returns based on user permissions."""
        if self.request.user.is_staff:
            return OrderReturn.objects.select_related('order__user').prefetch_related(
                'items__order_item__product'
            )
        else:
            return OrderReturn.objects.filter(
                order__user=self.request.user
            ).select_related('order').prefetch_related('items__order_item__product')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return OrderReturnCreateSerializer
        return OrderReturnSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a return request."""
        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {'error': 'Order ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                # Create return request
                return_request = OrderReturn.objects.create(
                    order=order,
                    reason=serializer.validated_data['reason'],
                    customer_notes=serializer.validated_data['customer_notes']
                )
                
                # Create return items
                for item_data in serializer.validated_data['items']:
                    order_item = order.items.get(id=item_data['order_item_id'])
                    OrderReturnItem.objects.create(
                        return_request=return_request,
                        order_item=order_item,
                        quantity=item_data['quantity'],
                        condition=item_data.get('condition', '')
                    )
                
                # Send return request emails
                try:
                    email_result = OrderEmailService.send_order_return_email(return_request)
                    if not email_result.get('customer_email_sent'):
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to send return confirmation email for return {return_request.return_number}")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error sending return emails for return {return_request.return_number}: {str(e)}")
                
                response_serializer = OrderReturnSerializer(
                    return_request,
                    context={'request': request}
                )
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageOrders])
    def approve(self, request, pk=None):
        """Approve return request."""
        return_request = self.get_object()
        
        if return_request.status != 'requested':
            return Response(
                {'error': 'Return request cannot be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            return_request.status = 'approved'
            return_request.approved_at = timezone.now()
            return_request.save()
            
            # Restore stock for returned items
            for return_item in return_request.items.all():
                order_item = return_item.order_item
                quantity_to_restore = return_item.quantity
                
                if order_item.variant:
                    old_stock = order_item.variant.stock
                    order_item.variant.stock += quantity_to_restore
                    order_item.variant.save()
                    print(f"Stock restored for returned variant {order_item.variant.name}: {old_stock} -> {order_item.variant.stock}")
                elif order_item.product.track_inventory:
                    old_stock = order_item.product.stock
                    order_item.product.stock += quantity_to_restore
                    order_item.product.save()
                    print(f"Stock restored for returned product {order_item.product.title}: {old_stock} -> {order_item.product.stock}")
        
        serializer = OrderReturnSerializer(return_request, context={'request': request})
        return Response({
            'message': 'Return request approved and stock restored',
            'return': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageOrders])
    def reject(self, request, pk=None):
        """Reject return request."""
        return_request = self.get_object()
        admin_notes = request.data.get('admin_notes', '')
        
        if return_request.status != 'requested':
            return Response(
                {'error': 'Return request cannot be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_request.status = 'rejected'
        return_request.admin_notes = admin_notes
        return_request.save()
        
        serializer = OrderReturnSerializer(return_request, context={'request': request})
        return Response({
            'message': 'Return request rejected',
            'return': serializer.data
        })
