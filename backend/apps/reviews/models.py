"""
Review and Rating models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Review(models.Model):
    """
    Product review model.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('flagged', _('Flagged')),
        ('hidden', _('Hidden')),
    ]
    
    # Review identification
    review_id = models.UUIDField(
        _('review ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Related objects
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('product')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('reviewer')
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name=_('order'),
        help_text=_('Order this review is based on (for verified purchases)')
    )
    
    # Review content
    rating = models.PositiveIntegerField(
        _('rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5 stars')
    )
    title = models.CharField(
        _('review title'),
        max_length=200,
        help_text=_('Short title for the review')
    )
    content = models.TextField(
        _('review content'),
        help_text=_('Detailed review content')
    )
    
    # Review metadata
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_verified_purchase = models.BooleanField(
        _('verified purchase'),
        default=False,
        help_text=_('Review from verified purchaser')
    )
    
    # Helpfulness tracking
    helpful_count = models.PositiveIntegerField(
        _('helpful count'),
        default=0,
        help_text=_('Number of users who found this review helpful')
    )
    not_helpful_count = models.PositiveIntegerField(
        _('not helpful count'),
        default=0,
        help_text=_('Number of users who found this review not helpful')
    )
    
    # Moderation
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews',
        verbose_name=_('moderated by')
    )
    moderation_notes = models.TextField(
        _('moderation notes'),
        blank=True,
        help_text=_('Internal notes for moderation')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    
    class Meta:
        db_table = 'reviews_review'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['product', 'user', 'order']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['rating', 'status']),
            models.Index(fields=['is_verified_purchase', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.rating}★ by {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Set verified purchase status
        if self.order and not self.is_verified_purchase:
            # Check if user actually purchased this product
            order_items = self.order.items.filter(product=self.product)
            if order_items.exists() and self.order.status == 'delivered':
                self.is_verified_purchase = True
        
        # Set approved_at timestamp
        if self.status == 'approved' and not self.approved_at:
            from django.utils import timezone
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio."""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return (self.helpful_count / total_votes) * 100
    
    @property
    def is_helpful(self):
        """Check if review is considered helpful."""
        return self.helpfulness_ratio >= 60  # 60% threshold
    
    def mark_helpful(self, user):
        """Mark review as helpful by a user."""
        vote, created = ReviewHelpfulness.objects.get_or_create(
            review=self,
            user=user,
            defaults={'is_helpful': True}
        )
        
        if not created and not vote.is_helpful:
            vote.is_helpful = True
            vote.save()
            self.not_helpful_count = max(0, self.not_helpful_count - 1)
        
        if created or not vote.is_helpful:
            self.helpful_count += 1
            self.save(update_fields=['helpful_count'])
    
    def mark_not_helpful(self, user):
        """Mark review as not helpful by a user."""
        vote, created = ReviewHelpfulness.objects.get_or_create(
            review=self,
            user=user,
            defaults={'is_helpful': False}
        )
        
        if not created and vote.is_helpful:
            vote.is_helpful = False
            vote.save()
            self.helpful_count = max(0, self.helpful_count - 1)
        
        if created or vote.is_helpful:
            self.not_helpful_count += 1
            self.save(update_fields=['not_helpful_count'])


class ReviewImage(models.Model):
    """
    Images attached to reviews.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('review')
    )
    image = models.ImageField(
        _('image'),
        upload_to='reviews/',
        help_text=_('Review image')
    )
    caption = models.CharField(
        _('caption'),
        max_length=200,
        blank=True,
        help_text=_('Image caption')
    )
    position = models.PositiveIntegerField(
        _('position'),
        default=0,
        help_text=_('Display order of images')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'reviews_reviewimage'
        verbose_name = _('Review Image')
        verbose_name_plural = _('Review Images')
        ordering = ['position', 'created_at']
        indexes = [
            models.Index(fields=['review', 'position']),
        ]
    
    def __str__(self):
        return f"Image for {self.review.title}"


class ReviewHelpfulness(models.Model):
    """
    Track user votes on review helpfulness.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpfulness_votes',
        verbose_name=_('review')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_votes',
        verbose_name=_('user')
    )
    is_helpful = models.BooleanField(
        _('is helpful'),
        help_text=_('True if user found review helpful, False otherwise')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'reviews_reviewhelpfulness'
        verbose_name = _('Review Helpfulness Vote')
        verbose_name_plural = _('Review Helpfulness Votes')
        unique_together = ['review', 'user']
        indexes = [
            models.Index(fields=['review', 'is_helpful']),
        ]
    
    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.get_full_name()} found review {helpful_text}"


class ReviewResponse(models.Model):
    """
    Responses to reviews (from store owners/admins).
    """
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('hidden', _('Hidden')),
    ]
    
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response',
        verbose_name=_('review')
    )
    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_responses',
        verbose_name=_('responder'),
        help_text=_('Admin/staff member who responded')
    )
    
    # Response content
    content = models.TextField(
        _('response content'),
        help_text=_('Response to the review')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    class Meta:
        db_table = 'reviews_reviewresponse'
        verbose_name = _('Review Response')
        verbose_name_plural = _('Review Responses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review', 'status']),
        ]
    
    def __str__(self):
        return f"Response to: {self.review.title}"
    
    def save(self, *args, **kwargs):
        # Set published_at timestamp
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)


class ReviewReport(models.Model):
    """
    Reports for inappropriate reviews.
    """
    
    REASON_CHOICES = [
        ('spam', _('Spam')),
        ('inappropriate', _('Inappropriate Content')),
        ('fake', _('Fake Review')),
        ('offensive', _('Offensive Language')),
        ('irrelevant', _('Irrelevant to Product')),
        ('personal_info', _('Contains Personal Information')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('investigating', _('Under Investigation')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
    ]
    
    # Report identification
    report_id = models.UUIDField(
        _('report ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Related objects
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('review')
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_reports',
        verbose_name=_('reporter')
    )
    
    # Report details
    reason = models.CharField(
        _('reason'),
        max_length=20,
        choices=REASON_CHOICES
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Additional details about the report')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Moderation
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_review_reports',
        verbose_name=_('assigned to')
    )
    resolution_notes = models.TextField(
        _('resolution notes'),
        blank=True,
        help_text=_('Notes about how the report was resolved')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    
    class Meta:
        db_table = 'reviews_reviewreport'
        verbose_name = _('Review Report')
        verbose_name_plural = _('Review Reports')
        ordering = ['-created_at']
        unique_together = ['review', 'reporter']
        indexes = [
            models.Index(fields=['review', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"Report {self.report_id} - {self.get_reason_display()}"
    
    def resolve(self, resolution_notes='', resolved_by=None):
        """Mark report as resolved."""
        self.status = 'resolved'
        self.resolution_notes = resolution_notes
        if resolved_by:
            self.assigned_to = resolved_by
        
        from django.utils import timezone
        self.resolved_at = timezone.now()
        self.save()


class ProductRating(models.Model):
    """
    Aggregated rating statistics for products.
    """
    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='rating_stats',
        verbose_name=_('product')
    )
    
    # Rating statistics
    average_rating = models.DecimalField(
        _('average rating'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text=_('Average rating from all approved reviews')
    )
    total_reviews = models.PositiveIntegerField(
        _('total reviews'),
        default=0,
        help_text=_('Total number of approved reviews')
    )
    
    # Rating distribution
    rating_1_count = models.PositiveIntegerField(_('1 star count'), default=0)
    rating_2_count = models.PositiveIntegerField(_('2 star count'), default=0)
    rating_3_count = models.PositiveIntegerField(_('3 star count'), default=0)
    rating_4_count = models.PositiveIntegerField(_('4 star count'), default=0)
    rating_5_count = models.PositiveIntegerField(_('5 star count'), default=0)
    
    # Verified purchase statistics
    verified_reviews_count = models.PositiveIntegerField(
        _('verified reviews count'),
        default=0,
        help_text=_('Number of reviews from verified purchases')
    )
    verified_average_rating = models.DecimalField(
        _('verified average rating'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text=_('Average rating from verified purchases only')
    )
    
    # Timestamps
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'reviews_productrating'
        verbose_name = _('Product Rating Statistics')
        verbose_name_plural = _('Product Rating Statistics')
        indexes = [
            models.Index(fields=['average_rating']),
            models.Index(fields=['total_reviews']),
        ]
    
    def __str__(self):
        return f"{self.product.title} - {self.average_rating}★ ({self.total_reviews} reviews)"
    
    def update_statistics(self):
        """Update rating statistics from approved reviews."""
        from django.db.models import Avg, Count
        
        approved_reviews = self.product.reviews.filter(status='approved')
        
        # Calculate basic statistics
        stats = approved_reviews.aggregate(
            avg_rating=Avg('rating'),
            total_count=Count('id')
        )
        
        self.average_rating = stats['avg_rating'] or 0.00
        self.total_reviews = stats['total_count'] or 0
        
        # Calculate rating distribution
        rating_counts = approved_reviews.values('rating').annotate(
            count=Count('rating')
        )
        
        # Reset counts
        self.rating_1_count = 0
        self.rating_2_count = 0
        self.rating_3_count = 0
        self.rating_4_count = 0
        self.rating_5_count = 0
        
        # Update counts
        for item in rating_counts:
            rating = item['rating']
            count = item['count']
            setattr(self, f'rating_{rating}_count', count)
        
        # Calculate verified purchase statistics
        verified_reviews = approved_reviews.filter(is_verified_purchase=True)
        verified_stats = verified_reviews.aggregate(
            avg_rating=Avg('rating'),
            total_count=Count('id')
        )
        
        self.verified_average_rating = verified_stats['avg_rating'] or 0.00
        self.verified_reviews_count = verified_stats['total_count'] or 0
        
        self.save()
    
    @property
    def rating_distribution(self):
        """Get rating distribution as percentages."""
        if self.total_reviews == 0:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        return {
            1: round((self.rating_1_count / self.total_reviews) * 100, 1),
            2: round((self.rating_2_count / self.total_reviews) * 100, 1),
            3: round((self.rating_3_count / self.total_reviews) * 100, 1),
            4: round((self.rating_4_count / self.total_reviews) * 100, 1),
            5: round((self.rating_5_count / self.total_reviews) * 100, 1),
        }
