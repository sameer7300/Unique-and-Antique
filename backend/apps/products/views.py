"""
Views for the products app.
"""

from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404

from .models import Category, Brand, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer, CategoryTreeSerializer, BrandSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductSearchSerializer, ProductStatsSerializer, BulkProductUpdateSerializer,
    ProductImageSerializer, ProductVariantSerializer
)
from utils.permissions import IsAdminOrReadOnly, IsStaffOrAdmin
from utils.pagination import ProductPagination, StandardResultsSetPagination
from utils.decorators import cache_response
from utils.mixins import CacheResponseMixin, BulkActionMixin, ExportMixin


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve', 'tree']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsStaffOrAdmin]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure."""
        root_categories = Category.objects.filter(
            parent=None,
            is_active=True
        ).order_by('sort_order', 'name')
        
        serializer = CategoryTreeSerializer(
            root_categories,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in this category."""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            status='active'
        ).select_related('category', 'brand').prefetch_related('images')
        
        # Apply pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product brands.
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve', 'products']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsStaffOrAdmin]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products for this brand."""
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            status='active'
        ).select_related('category', 'brand').prefetch_related('images')
        
        # Apply pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ProductFilter:
    """
    Custom filter class for products.
    """
    
    @staticmethod
    def filter_products(queryset, request):
        """Apply filters to product queryset."""
        # Category filter
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Brand filter
        brand_id = request.query_params.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        
        # Price range filter
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Rating filter
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=min_rating)
        
        # Availability filter
        in_stock = request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(track_inventory=False) |
                Q(track_inventory=True, stock__gt=0) |
                Q(track_inventory=True, allow_backorders=True)
            )
        
        # Featured filter
        featured = request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search) |
                Q(category__name__icontains=search) |
                Q(brand__name__icontains=search)
            )
        
        return queryset


class ProductViewSet(CacheResponseMixin, BulkActionMixin, ExportMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    """
    queryset = Product.objects.select_related('category', 'brand').prefetch_related(
        'images', 'variants', 'reviews'
    )
    lookup_field = 'slug'
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'brand', 'status', 'is_featured']
    search_fields = ['title', 'description', 'tags', 'sku']
    ordering_fields = ['title', 'price', 'created_at', 'stock']
    ordering = ['-created_at']
    cache_timeout = 300  # 5 minutes
    
    def get_queryset(self):
        """Get filtered queryset."""
        queryset = super().get_queryset()
        
        # Only show active products for non-admin users
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(status='active')
        
        # Apply custom filters
        queryset = ProductFilter.filter_products(queryset, self.request)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to handle custom sorting."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Handle custom sorting
        sort_param = request.query_params.get('sort')
        print(f"ProductViewSet.list - sort_param: {sort_param}")
        
        if sort_param == 'random':
            # Disable caching for random sorting
            self.cache_timeout = 0
            queryset = queryset.order_by('?')
            print(f"Applied random sorting, queryset count: {queryset.count()}")
            if queryset.exists():
                print(f"First product after random sort: {queryset.first().title}")
        elif sort_param == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_param == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_param == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        elif sort_param == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_param == 'popularity':
            queryset = queryset.annotate(
                review_count=Count('reviews')
            ).order_by('-review_count')
        elif sort_param == 'name':
            queryset = queryset.order_by('title')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        elif self.action == 'search':
            return ProductSearchSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve', 'search', 'featured', 'categories', 'brands']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsStaffOrAdmin]
        
        return [permission() for permission in permission_classes]
    
    @cache_response(timeout=600)  # 10 minutes cache
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        products = self.get_queryset().filter(
            is_featured=True,
            status='active'
        )[:12]  # Limit to 12 featured products
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced product search."""
        queryset = self.get_queryset()
        
        # Apply search filters
        queryset = ProductFilter.filter_products(queryset, request)
        
        # Apply sorting
        sort_by = request.query_params.get('sort', 'relevance')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'popularity':
            queryset = queryset.annotate(
                review_count=Count('reviews')
            ).order_by('-review_count')
        elif sort_by == 'random':
            queryset = queryset.order_by('?')
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSearchSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSearchSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view_count(self, request, pk=None):
        """Increment product view count."""
        product = self.get_object()
        product.increment_view_count()
        return Response({'message': 'View count incremented'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOrAdmin])
    def stats(self, request):
        """Get product statistics."""
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'low_stock_products': Product.objects.filter(
                track_inventory=True,
                stock__lte=models.F('low_stock_threshold')
            ).count(),
            'out_of_stock_products': Product.objects.filter(
                track_inventory=True,
                stock=0
            ).count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_brands': Brand.objects.filter(is_active=True).count(),
        }
        
        serializer = ProductStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def bulk_update(self, request):
        """Bulk update products."""
        serializer = BulkProductUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product_ids = serializer.validated_data['product_ids']
            updates = serializer.validated_data['updates']
            
            # Update products
            updated_count = Product.objects.filter(
                id__in=product_ids
            ).update(**updates)
            
            return Response({
                'message': f'{updated_count} products updated successfully',
                'updated_count': updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related products."""
        product = self.get_object()
        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id)[:8]
        
        serializer = ProductListSerializer(
            related_products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product images.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOrAdmin]
    
    def get_queryset(self):
        """Get images for specific product."""
        product_id = self.kwargs.get('product_pk')
        return ProductImage.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        """Create image for specific product."""
        product_id = self.kwargs.get('product_pk')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product variants.
    """
    serializer_class = ProductVariantSerializer
    permission_classes = [IsStaffOrAdmin]
    
    def get_queryset(self):
        """Get variants for specific product."""
        product_id = self.kwargs.get('product_pk')
        return ProductVariant.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        """Create variant for specific product."""
        product_id = self.kwargs.get('product_pk')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)


# Function-based views for specific endpoints

@api_view(['GET'])
@cache_response(timeout=3600)  # 1 hour cache
def get_categories_tree(request):
    """Get category tree structure."""
    root_categories = Category.objects.filter(
        parent=None,
        is_active=True
    ).order_by('sort_order', 'name')
    
    serializer = CategoryTreeSerializer(
        root_categories,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@cache_response(timeout=1800)  # 30 minutes cache
def get_featured_products(request):
    """Get featured products."""
    products = Product.objects.filter(
        is_featured=True,
        status='active'
    ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    serializer = ProductListSerializer(
        products,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
def get_shuffled_products(request):
    """Get shuffled products for new arrivals."""
    limit = int(request.query_params.get('limit', 8))
    
    # Get all active products and shuffle them
    products = Product.objects.filter(
        status='active'
    ).select_related('category', 'brand').prefetch_related('images').order_by('?')[:limit]
    
    # Debug logging
    print(f"Shuffled products request - limit: {limit}, found: {products.count()}")
    if products.exists():
        print(f"First product: {products.first().title}")
    
    serializer = ProductListSerializer(
        products,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


class ProductRecommendationView(generics.ListAPIView):
    """
    View for product recommendations.
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get recommended products."""
        # Simple recommendation based on category and rating
        # In production, this would use more sophisticated algorithms
        
        product_id = self.kwargs.get('pk')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Product.objects.none()
        
        # Get products from same category with high ratings
        recommended = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating', '-created_at')[:10]
        
        return recommended


class ProductComparisonView(generics.GenericAPIView):
    """
    View for comparing products.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Compare multiple products."""
        product_ids = request.data.get('product_ids', [])
        
        if not product_ids or len(product_ids) < 2:
            return Response(
                {'error': 'At least 2 product IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(product_ids) > 5:
            return Response(
                {'error': 'Maximum 5 products can be compared'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = Product.objects.filter(
            id__in=product_ids,
            status='active'
        ).select_related('category', 'brand').prefetch_related('images')
        
        if products.count() != len(product_ids):
            return Response(
                {'error': 'Some products not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductDetailSerializer(
            products,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'products': serializer.data,
            'comparison_attributes': [
                'price', 'brand', 'rating', 'features', 'specifications'
            ]
        })
