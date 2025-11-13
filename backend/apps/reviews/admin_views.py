"""
Admin views for the reviews app.
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

from .models import Review
from .serializers import ReviewDetailSerializer


class AdminReviewStatsView(APIView):
    """Get review statistics for admin dashboard."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Calculate stats
        total_reviews = Review.objects.count()
        pending_reviews = Review.objects.filter(status='pending').count()
        approved_reviews = Review.objects.filter(status='approved').count()
        
        # Calculate average rating
        avg_rating = Review.objects.filter(status='approved').aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        return Response({
            'total': total_reviews,
            'pending': pending_reviews,
            'approved': approved_reviews,
            'averageRating': float(avg_rating),
        })


class AdminReviewListView(ListAPIView):
    """List all reviews for admin with pagination and filtering."""
    permission_classes = [IsAdminUser]
    serializer_class = ReviewDetailSerializer
    
    def get_queryset(self):
        queryset = Review.objects.all().select_related('user', 'product')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(product__title__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Rating filtering
        rating = self.request.query_params.get('rating', None)
        if rating and rating != 'all':
            queryset = queryset.filter(rating=int(rating))
        
        return queryset.order_by('-created_at')


class AdminReviewDetailView(APIView):
    """Get, update, or delete a specific review."""
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            review = Review.objects.select_related('user', 'product').get(pk=pk)
            serializer = ReviewDetailSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            
            # Update allowed fields
            allowed_fields = ['status', 'admin_notes']
            for field in allowed_fields:
                if field in request.data:
                    setattr(review, field, request.data[field])
            
            review.save()
            serializer = ReviewDetailSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            review.delete()
            return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
