"""
Views for the reviews app.
"""

from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Avg, Count
import logging

logger = logging.getLogger(__name__)

from .models import (
    Review, ReviewImage, ReviewHelpfulness, ReviewResponse,
    ReviewReport, ProductRating
)
from .serializers import (
    ReviewListSerializer, ReviewDetailSerializer, ReviewCreateSerializer,
    ReviewUpdateSerializer, ReviewModerationSerializer, ReviewResponseSerializer,
    ReviewResponseCreateSerializer, ReviewReportSerializer, ReviewReportCreateSerializer,
    ProductRatingSerializer, ReviewHelpfulnessSerializer, ReviewStatsSerializer,
    BulkReviewModerationSerializer, ReviewFilterSerializer, ReviewSummarySerializer
)
from apps.products.models import Product
from utils.permissions import IsOwnerOrReadOnly, IsStaffOrAdmin, CanModerateReviews, IsVerifiedPurchaser
from utils.pagination import ReviewPagination
from utils.exceptions import ReviewError
from .services import ReviewEmailService


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product reviews.
    """
    pagination_class = ReviewPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'status', 'is_verified_purchase']
    search_fields = ['title', 'content', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'rating', 'helpful_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get reviews based on user permissions and filters."""
        queryset = Review.objects.select_related('user', 'product').prefetch_related('images')
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Only show approved reviews for non-staff users
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(status='approved')
        
        # Apply custom filters
        return self._apply_custom_filters(queryset)
    
    def _apply_custom_filters(self, queryset):
        """Apply custom filters from query parameters."""
        # Rating filter
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Verified purchase filter
        verified_only = self.request.query_params.get('verified_only')
        if verified_only and verified_only.lower() == 'true':
            queryset = queryset.filter(is_verified_purchase=True)
        
        # With images filter
        with_images = self.request.query_params.get('with_images')
        if with_images and with_images.lower() == 'true':
            queryset = queryset.filter(images__isnull=False).distinct()
        
        # Sort by filter
        sort_by = self.request.query_params.get('sort_by', 'newest')
        if sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'highest_rating':
            queryset = queryset.order_by('-rating', '-created_at')
        elif sort_by == 'lowest_rating':
            queryset = queryset.order_by('rating', '-created_at')
        elif sort_by == 'most_helpful':
            queryset = queryset.order_by('-helpful_count', '-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return ReviewListSerializer
        elif self.action == 'retrieve':
            return ReviewDetailSerializer
        elif self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'moderate':
            return ReviewModerationSerializer
        return ReviewDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]  # Could add IsVerifiedPurchaser
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action in ['moderate', 'bulk_moderate']:
            permission_classes = [CanModerateReviews]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create review for current user and send email notifications."""
        review = serializer.save(user=self.request.user)
        
        # Send email notifications (don't fail the request if email sending fails)
        try:
            ReviewEmailService.send_review_submission_emails(review)
        except Exception as e:
            logger.error(f"Failed to send review submission emails for review {review.id}: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful."""
        review = self.get_object()
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if review.user == request.user:
            return Response(
                {'error': 'Cannot vote on your own review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewHelpfulnessSerializer(data=request.data)
        if serializer.is_valid():
            is_helpful = serializer.validated_data['is_helpful']
            
            if is_helpful:
                review.mark_helpful(request.user)
                message = 'Review marked as helpful'
            else:
                review.mark_not_helpful(request.user)
                message = 'Review marked as not helpful'
            
            return Response({
                'message': message,
                'helpful_count': review.helpful_count,
                'not_helpful_count': review.not_helpful_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanModerateReviews])
    def moderate(self, request, pk=None):
        """Moderate review (admin only)."""
        review = self.get_object()
        serializer = ReviewModerationSerializer(review, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(moderated_by=request.user)
            
            response_serializer = ReviewDetailSerializer(
                review,
                context={'request': request}
            )
            return Response({
                'message': f'Review status updated to {review.get_status_display()}',
                'review': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[CanModerateReviews])
    def bulk_moderate(self, request):
        """Bulk moderate reviews."""
        serializer = BulkReviewModerationSerializer(data=request.data)
        if serializer.is_valid():
            review_ids = serializer.validated_data['review_ids']
            action = serializer.validated_data['action']
            moderation_notes = serializer.validated_data.get('moderation_notes', '')
            
            # Map actions to statuses
            status_map = {
                'approve': 'approved',
                'reject': 'rejected',
                'flag': 'flagged',
                'hide': 'hidden'
            }
            
            new_status = status_map.get(action)
            if not new_status:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update reviews
            updated_count = Review.objects.filter(
                id__in=review_ids
            ).update(
                status=new_status,
                moderated_by=request.user,
                moderation_notes=moderation_notes
            )
            
            return Response({
                'message': f'{updated_count} reviews {action}d successfully',
                'updated_count': updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOrAdmin])
    def stats(self, request):
        """Get review statistics."""
        stats = {
            'total_reviews': Review.objects.count(),
            'pending_reviews': Review.objects.filter(status='pending').count(),
            'approved_reviews': Review.objects.filter(status='approved').count(),
            'rejected_reviews': Review.objects.filter(status='rejected').count(),
            'flagged_reviews': Review.objects.filter(status='flagged').count(),
            'verified_reviews': Review.objects.filter(is_verified_purchase=True).count(),
            'average_rating': Review.objects.filter(
                status='approved'
            ).aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_reports': ReviewReport.objects.count(),
            'pending_reports': ReviewReport.objects.filter(status='pending').count(),
        }
        
        serializer = ReviewStatsSerializer(stats)
        return Response(serializer.data)


class ReviewResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing review responses.
    """
    serializer_class = ReviewResponseSerializer
    permission_classes = [CanModerateReviews]
    
    def get_queryset(self):
        """Get review responses."""
        return ReviewResponse.objects.select_related('review', 'responder')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ReviewResponseCreateSerializer
        return ReviewResponseSerializer
    
    def create(self, request, *args, **kwargs):
        """Create review response."""
        review_id = request.data.get('review_id')
        if not review_id:
            return Response(
                {'error': 'Review ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'review': review}
        )
        
        if serializer.is_valid():
            response = ReviewResponse.objects.create(
                review=review,
                responder=request.user,
                content=serializer.validated_data['content'],
                status=serializer.validated_data.get('status', 'draft')
            )
            
            response_serializer = ReviewResponseSerializer(
                response,
                context={'request': request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing review reports.
    """
    serializer_class = ReviewReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get review reports based on user permissions."""
        if self.request.user.is_staff:
            return ReviewReport.objects.select_related('review', 'reporter')
        else:
            return ReviewReport.objects.filter(reporter=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ReviewReportCreateSerializer
        return ReviewReportSerializer
    
    def create(self, request, *args, **kwargs):
        """Create review report."""
        review_id = request.data.get('review_id')
        if not review_id:
            return Response(
                {'error': 'Review ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'review': review, 'request': request}
        )
        
        if serializer.is_valid():
            report = ReviewReport.objects.create(
                review=review,
                reporter=request.user,
                reason=serializer.validated_data['reason'],
                description=serializer.validated_data.get('description', '')
            )
            
            response_serializer = ReviewReportSerializer(
                report,
                context={'request': request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanModerateReviews])
    def resolve(self, request, pk=None):
        """Resolve review report."""
        report = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        report.resolve(resolution_notes, request.user)
        
        serializer = ReviewReportSerializer(report, context={'request': request})
        return Response({
            'message': 'Report resolved successfully',
            'report': serializer.data
        })


class ProductReviewSummaryView(generics.RetrieveAPIView):
    """
    View for getting product review summary.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, product_id):
        """Get review summary for product."""
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get approved reviews
        reviews = Review.objects.filter(
            product=product,
            status='approved'
        ).select_related('user')
        
        # Calculate statistics
        total_reviews = reviews.count()
        if total_reviews == 0:
            return Response({
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'verified_purchase_percentage': 0,
                'recent_reviews': [],
                'top_positive_review': None,
                'top_negative_review': None
            })
        
        # Average rating
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Rating distribution
        rating_counts = reviews.values('rating').annotate(count=Count('rating'))
        rating_distribution = {i: 0 for i in range(1, 6)}
        for item in rating_counts:
            rating_distribution[item['rating']] = item['count']
        
        # Verified purchase percentage
        verified_count = reviews.filter(is_verified_purchase=True).count()
        verified_percentage = (verified_count / total_reviews) * 100
        
        # Recent reviews (last 5)
        recent_reviews = reviews.order_by('-created_at')[:5]
        
        # Top positive and negative reviews
        top_positive = reviews.filter(rating__gte=4).order_by('-helpful_count').first()
        top_negative = reviews.filter(rating__lte=2).order_by('-helpful_count').first()
        
        # Serialize data
        summary_data = {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2) if average_rating else 0,
            'rating_distribution': rating_distribution,
            'verified_purchase_percentage': round(verified_percentage, 1),
            'recent_reviews': ReviewListSerializer(
                recent_reviews,
                many=True,
                context={'request': request}
            ).data,
            'top_positive_review': ReviewListSerializer(
                top_positive,
                context={'request': request}
            ).data if top_positive else None,
            'top_negative_review': ReviewListSerializer(
                top_negative,
                context={'request': request}
            ).data if top_negative else None
        }
        
        serializer = ReviewSummarySerializer(summary_data)
        return Response(serializer.data)


class ProductRatingView(generics.RetrieveAPIView):
    """
    View for getting product rating statistics.
    """
    serializer_class = ProductRatingSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        """Get or create product rating statistics."""
        product_id = self.kwargs['product_id']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None
        
        rating_stats, created = ProductRating.objects.get_or_create(
            product=product
        )
        
        # Update statistics if needed
        if created or rating_stats.total_reviews == 0:
            rating_stats.update_statistics()
        
        return rating_stats
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve product rating statistics."""
        instance = self.get_object()
        if instance is None:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
