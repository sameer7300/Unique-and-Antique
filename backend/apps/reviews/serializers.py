"""
Serializers for the reviews app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Review, ReviewImage, ReviewHelpfulness, ReviewResponse,
    ReviewReport, ProductRating
)
from apps.products.serializers import ProductListSerializer

User = get_user_model()


class ReviewImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ReviewImage model.
    """
    
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption', 'position', 'created_at']
        read_only_fields = ['created_at']


class ReviewerSerializer(serializers.ModelSerializer):
    """
    Serializer for review author information.
    """
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']
    
    def to_representation(self, instance):
        """Customize reviewer representation."""
        data = super().to_representation(instance)
        # Only show first name and last initial for privacy
        if data.get('last_name'):
            data['last_name'] = data['last_name'][0] + '.'
        return data


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model in list views.
    """
    user = ReviewerSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    helpfulness_ratio = serializers.ReadOnlyField()
    is_helpful = serializers.ReadOnlyField()
    user_found_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'review_id', 'user', 'product', 'rating', 'title', 'content',
            'status', 'status_display', 'is_verified_purchase',
            'helpful_count', 'not_helpful_count', 'helpfulness_ratio',
            'is_helpful', 'user_found_helpful', 'images', 'created_at',
            'approved_at'
        ]
    
    def get_user_found_helpful(self, obj):
        """Check if current user found this review helpful."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = ReviewHelpfulness.objects.get(
                    review=obj,
                    user=request.user
                )
                return vote.is_helpful
            except ReviewHelpfulness.DoesNotExist:
                pass
        return None


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model in detail views.
    """
    user = ReviewerSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    response = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    helpfulness_ratio = serializers.ReadOnlyField()
    is_helpful = serializers.ReadOnlyField()
    user_found_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'review_id', 'user', 'product', 'rating', 'title',
            'content', 'status', 'status_display', 'is_verified_purchase',
            'helpful_count', 'not_helpful_count', 'helpfulness_ratio',
            'is_helpful', 'user_found_helpful', 'images', 'response',
            'created_at', 'updated_at', 'approved_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']
    
    def get_user_found_helpful(self, obj):
        """Check if current user found this review helpful."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = ReviewHelpfulness.objects.get(
                    review=obj,
                    user=request.user
                )
                return vote.is_helpful
            except ReviewHelpfulness.DoesNotExist:
                pass
        return None
    
    def get_response(self, obj):
        """Get store response to review."""
        try:
            response = obj.response
            if response.status == 'published':
                return {
                    'id': response.id,
                    'content': response.content,
                    'responder': response.responder.get_full_name(),
                    'created_at': response.created_at,
                    'published_at': response.published_at,
                }
        except ReviewResponse.DoesNotExist:
            pass
        return None


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reviews.
    """
    product_id = serializers.IntegerField(write_only=True)
    order_id = serializers.IntegerField(write_only=True, required=False)
    images = ReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'product_id', 'order_id', 'rating', 'title', 'content', 'images'
        ]
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate_product_id(self, value):
        """Validate product exists."""
        from apps.products.models import Product
        
        try:
            product = Product.objects.get(id=value, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        return value
    
    def validate_order_id(self, value):
        """Validate order exists and contains the product."""
        if value is None:
            return value
        
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        # Check if order belongs to current user
        request = self.context.get('request')
        if order.user != request.user:
            raise serializers.ValidationError("Order not found.")
        
        # Check if order is delivered
        if order.status != 'delivered':
            raise serializers.ValidationError(
                "Can only review products from delivered orders."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate review can be created."""
        from apps.products.models import Product
        from apps.orders.models import Order
        
        product = Product.objects.get(id=attrs['product_id'])
        user = self.context['request'].user
        order = None
        
        if attrs.get('order_id'):
            order = Order.objects.get(id=attrs['order_id'])
            
            # Check if order contains the product
            if not order.items.filter(product=product).exists():
                raise serializers.ValidationError(
                    "Product not found in the specified order."
                )
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(
            user=user,
            product=product,
            order=order
        ).first()
        
        if existing_review:
            raise serializers.ValidationError(
                "You have already reviewed this product."
            )
        
        attrs['product'] = product
        attrs['order'] = order
        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating reviews.
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, attrs):
        """Validate review can be updated."""
        review = self.instance
        
        # Only allow updates if review is pending or approved
        if review.status not in ['pending', 'approved']:
            raise serializers.ValidationError(
                "Cannot update review with current status."
            )
        
        return attrs


class ReviewModerationSerializer(serializers.ModelSerializer):
    """
    Serializer for moderating reviews (admin only).
    """
    
    class Meta:
        model = Review
        fields = ['status', 'moderation_notes']
    
    def validate_status(self, value):
        """Validate status transition."""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'pending': ['approved', 'rejected', 'flagged'],
                'approved': ['hidden', 'flagged'],
                'rejected': ['approved'],
                'flagged': ['approved', 'rejected', 'hidden'],
                'hidden': ['approved'],
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'."
                )
        
        return value


class ReviewResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for ReviewResponse model.
    """
    responder = ReviewerSerializer(read_only=True)
    review = ReviewListSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'review', 'responder', 'content', 'status',
            'status_display', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'published_at']


class ReviewResponseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating review responses.
    """
    
    class Meta:
        model = ReviewResponse
        fields = ['content', 'status']
    
    def validate(self, attrs):
        """Validate response can be created."""
        review = self.context['review']
        
        # Check if response already exists
        if hasattr(review, 'response'):
            raise serializers.ValidationError(
                "Response already exists for this review."
            )
        
        # Only allow responses to approved reviews
        if review.status != 'approved':
            raise serializers.ValidationError(
                "Can only respond to approved reviews."
            )
        
        return attrs


class ReviewReportSerializer(serializers.ModelSerializer):
    """
    Serializer for ReviewReport model.
    """
    reporter = ReviewerSerializer(read_only=True)
    review = ReviewListSerializer(read_only=True)
    reason_display = serializers.CharField(
        source='get_reason_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'report_id', 'review', 'reporter', 'reason',
            'reason_display', 'description', 'status', 'status_display',
            'assigned_to', 'resolution_notes', 'created_at', 'updated_at',
            'resolved_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'resolved_at']


class ReviewReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating review reports.
    """
    
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
    
    def validate(self, attrs):
        """Validate report can be created."""
        review = self.context['review']
        user = self.context['request'].user
        
        # Check if user already reported this review
        if ReviewReport.objects.filter(review=review, reporter=user).exists():
            raise serializers.ValidationError(
                "You have already reported this review."
            )
        
        # Cannot report own review
        if review.user == user:
            raise serializers.ValidationError(
                "Cannot report your own review."
            )
        
        return attrs


class ProductRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductRating model.
    """
    rating_distribution = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductRating
        fields = [
            'average_rating', 'total_reviews', 'rating_1_count',
            'rating_2_count', 'rating_3_count', 'rating_4_count',
            'rating_5_count', 'verified_reviews_count',
            'verified_average_rating', 'rating_distribution', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class ReviewHelpfulnessSerializer(serializers.Serializer):
    """
    Serializer for marking review as helpful/not helpful.
    """
    is_helpful = serializers.BooleanField()


class ReviewStatsSerializer(serializers.Serializer):
    """
    Serializer for review statistics.
    """
    total_reviews = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    approved_reviews = serializers.IntegerField()
    rejected_reviews = serializers.IntegerField()
    flagged_reviews = serializers.IntegerField()
    verified_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reports = serializers.IntegerField()
    pending_reports = serializers.IntegerField()


class BulkReviewModerationSerializer(serializers.Serializer):
    """
    Serializer for bulk review moderation.
    """
    review_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(
        choices=['approve', 'reject', 'flag', 'hide']
    )
    moderation_notes = serializers.CharField(required=False, allow_blank=True)


class ReviewFilterSerializer(serializers.Serializer):
    """
    Serializer for review filtering.
    """
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    verified_only = serializers.BooleanField(required=False, default=False)
    with_images = serializers.BooleanField(required=False, default=False)
    sort_by = serializers.ChoiceField(
        choices=['newest', 'oldest', 'highest_rating', 'lowest_rating', 'most_helpful'],
        required=False,
        default='newest'
    )


class ReviewSummarySerializer(serializers.Serializer):
    """
    Serializer for review summary information.
    """
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_distribution = serializers.DictField()
    verified_purchase_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    recent_reviews = ReviewListSerializer(many=True)
    top_positive_review = ReviewListSerializer(allow_null=True)
    top_negative_review = ReviewListSerializer(allow_null=True)
