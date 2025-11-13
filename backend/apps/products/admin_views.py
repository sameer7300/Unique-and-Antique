"""
Admin views for the products app.
"""

from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Product, Category, Brand
from .serializers import ProductDetailSerializer


class AdminProductStatsView(APIView):
    """Get product statistics for admin dashboard."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Calculate stats
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        draft_products = Product.objects.filter(status='draft').count()
        inactive_products = Product.objects.filter(status='inactive').count()
        low_stock_products = Product.objects.filter(stock__lte=5).count()
        featured_products = Product.objects.filter(is_featured=True).count()
        
        return Response({
            'total': total_products,
            'active': active_products,
            'draft': draft_products,
            'inactive': inactive_products,
            'lowStock': low_stock_products,
            'featured': featured_products,
        })


class AdminProductListView(ListAPIView):
    """List all products for admin with pagination and filtering."""
    permission_classes = [IsAdminUser]
    serializer_class = ProductDetailSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all().select_related('category', 'brand').prefetch_related('images', 'variants')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Category filtering
        category = self.request.query_params.get('category', None)
        if category and category != 'all':
            queryset = queryset.filter(category__name=category)
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class AdminProductDetailView(APIView):
    """Get, update, or delete a specific product."""
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            product = Product.objects.select_related('category', 'brand').prefetch_related('images', 'variants').get(pk=pk)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            
            # Update allowed fields
            allowed_fields = ['status', 'is_featured', 'stock', 'price', 'title', 'description']
            for field in allowed_fields:
                if field in request.data:
                    setattr(product, field, request.data[field])
            
            product.save()
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
