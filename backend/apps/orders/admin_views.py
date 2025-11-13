"""
Admin views for the orders app.
"""

from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Order, OrderItem
from .serializers import OrderDetailSerializer


class AdminOrderStatsView(APIView):
    """Get order statistics for admin dashboard."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get date ranges
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate stats
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Calculate revenue
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_revenue = Order.objects.filter(
            created_at__gte=current_month_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        return Response({
            'total': total_orders,
            'pending': pending_orders,
            'revenue': float(total_revenue),
            'monthlyRevenue': float(monthly_revenue),
            'currency': 'PKR',
        })


class AdminOrderListView(ListAPIView):
    """List all orders for admin with pagination and filtering."""
    permission_classes = [IsAdminUser]
    serializer_class = OrderDetailSerializer
    
    def get_queryset(self):
        queryset = Order.objects.all().select_related('user').prefetch_related('items__product')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Payment status filtering
        payment_status = self.request.query_params.get('payment_status', None)
        if payment_status and payment_status != 'all':
            queryset = queryset.filter(payment_status=payment_status)
        
        return queryset.order_by('-created_at')


class AdminOrderDetailView(APIView):
    """Get, update, or delete a specific order."""
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            order = Order.objects.select_related('user').prefetch_related('items__product').get(pk=pk)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            
            # Update allowed fields
            allowed_fields = ['status', 'payment_status', 'tracking_number', 'notes']
            for field in allowed_fields:
                if field in request.data:
                    setattr(order, field, request.data[field])
            
            order.save()
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
