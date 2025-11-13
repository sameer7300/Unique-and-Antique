"""
Admin configuration for the reviews app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count
from .models import (
    Review, ReviewImage, ReviewHelpfulness, ReviewResponse,
    ReviewReport, ProductRating
)


class ReviewImageInline(admin.TabularInline):
    """
    Inline admin for ReviewImage model.
    """
    model = ReviewImage
    extra = 0
    fields = ['image', 'caption', 'position']
    readonly_fields = ['created_at']


class ReviewHelpfulnessInline(admin.TabularInline):
    """
    Inline admin for ReviewHelpfulness model.
    """
    model = ReviewHelpfulness
    extra = 0
    fields = ['user', 'is_helpful', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review model.
    """
    list_display = [
        'title', 'product', 'user', 'rating', 'status',
        'is_verified_purchase', 'helpful_count', 'created_at'
    ]
    list_filter = [
        'rating', 'status', 'is_verified_purchase', 'created_at', 'approved_at'
    ]
    search_fields = [
        'title', 'content', 'product__title', 'user__email',
        'user__first_name', 'user__last_name'
    ]
    readonly_fields = [
        'review_id', 'created_at', 'updated_at', 'approved_at',
        'helpfulness_ratio', 'is_helpful'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('review_id', 'product', 'user', 'order')
        }),
        (_('Content'), {
            'fields': ('rating', 'title', 'content')
        }),
        (_('Status'), {
            'fields': ('status', 'is_verified_purchase')
        }),
        (_('Helpfulness'), {
            'fields': ('helpful_count', 'not_helpful_count', 'helpfulness_ratio', 'is_helpful'),
            'classes': ('collapse',)
        }),
        (_('Moderation'), {
            'fields': ('moderated_by', 'moderation_notes'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReviewImageInline, ReviewHelpfulnessInline]
    
    actions = ['approve_reviews', 'reject_reviews', 'flag_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_at=timezone.now(),
            moderated_by=request.user
        )
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = _('Approve selected reviews')
    
    def reject_reviews(self, request, queryset):
        """Reject selected reviews."""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            moderated_by=request.user
        )
        self.message_user(request, f'{updated} reviews rejected.')
    reject_reviews.short_description = _('Reject selected reviews')
    
    def flag_reviews(self, request, queryset):
        """Flag selected reviews for further review."""
        updated = queryset.update(
            status='flagged',
            moderated_by=request.user
        )
        self.message_user(request, f'{updated} reviews flagged.')
    flag_reviews.short_description = _('Flag selected reviews')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'user', 'order', 'moderated_by'
        )


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ReviewImage model.
    """
    list_display = ['review', 'image_preview', 'caption', 'position', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'caption']
    readonly_fields = ['created_at', 'image_preview']
    
    def image_preview(self, obj):
        """Display image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Preview')


@admin.register(ReviewHelpfulness)
class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    """
    Admin configuration for ReviewHelpfulness model.
    """
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review', 'user')


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    """
    Admin configuration for ReviewResponse model.
    """
    list_display = [
        'review', 'responder', 'status', 'created_at', 'published_at'
    ]
    list_filter = ['status', 'created_at', 'published_at']
    search_fields = ['review__title', 'content', 'responder__email']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        (_('Review'), {
            'fields': ('review',)
        }),
        (_('Response'), {
            'fields': ('responder', 'content', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_responses', 'hide_responses']
    
    def publish_responses(self, request, queryset):
        """Publish selected responses."""
        from django.utils import timezone
        updated = queryset.filter(status='draft').update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} responses published.')
    publish_responses.short_description = _('Publish selected responses')
    
    def hide_responses(self, request, queryset):
        """Hide selected responses."""
        updated = queryset.update(status='hidden')
        self.message_user(request, f'{updated} responses hidden.')
    hide_responses.short_description = _('Hide selected responses')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'review', 'responder'
        )


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for ReviewReport model.
    """
    list_display = [
        'report_id_short', 'review', 'reporter', 'reason',
        'status', 'assigned_to', 'created_at'
    ]
    list_filter = ['reason', 'status', 'created_at', 'resolved_at']
    search_fields = [
        'report_id', 'review__title', 'reporter__email', 'description'
    ]
    readonly_fields = [
        'report_id', 'created_at', 'updated_at', 'resolved_at'
    ]
    
    fieldsets = (
        (_('Report Information'), {
            'fields': ('report_id', 'review', 'reporter', 'reason')
        }),
        (_('Details'), {
            'fields': ('description', 'status')
        }),
        (_('Moderation'), {
            'fields': ('assigned_to', 'resolution_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def report_id_short(self, obj):
        """Display shortened report ID."""
        return str(obj.report_id)[:8] + '...'
    report_id_short.short_description = _('Report ID')
    
    actions = ['assign_to_me', 'mark_investigating', 'resolve_reports', 'dismiss_reports']
    
    def assign_to_me(self, request, queryset):
        """Assign selected reports to current user."""
        updated = queryset.filter(status='pending').update(
            assigned_to=request.user,
            status='investigating'
        )
        self.message_user(request, f'{updated} reports assigned to you.')
    assign_to_me.short_description = _('Assign selected reports to me')
    
    def mark_investigating(self, request, queryset):
        """Mark selected reports as under investigation."""
        updated = queryset.filter(status='pending').update(status='investigating')
        self.message_user(request, f'{updated} reports marked as investigating.')
    mark_investigating.short_description = _('Mark as investigating')
    
    def resolve_reports(self, request, queryset):
        """Resolve selected reports."""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=['pending', 'investigating']
        ).update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports resolved.')
    resolve_reports.short_description = _('Resolve selected reports')
    
    def dismiss_reports(self, request, queryset):
        """Dismiss selected reports."""
        updated = queryset.filter(
            status__in=['pending', 'investigating']
        ).update(status='dismissed')
        self.message_user(request, f'{updated} reports dismissed.')
    dismiss_reports.short_description = _('Dismiss selected reports')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'review', 'reporter', 'assigned_to'
        )


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductRating model.
    """
    list_display = [
        'product', 'average_rating', 'total_reviews',
        'verified_reviews_count', 'verified_average_rating', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = ['product__title']
    readonly_fields = [
        'average_rating', 'total_reviews', 'rating_1_count',
        'rating_2_count', 'rating_3_count', 'rating_4_count',
        'rating_5_count', 'verified_reviews_count',
        'verified_average_rating', 'updated_at', 'rating_distribution'
    ]
    
    fieldsets = (
        (_('Product'), {
            'fields': ('product',)
        }),
        (_('Overall Statistics'), {
            'fields': ('average_rating', 'total_reviews')
        }),
        (_('Rating Distribution'), {
            'fields': (
                'rating_1_count', 'rating_2_count', 'rating_3_count',
                'rating_4_count', 'rating_5_count', 'rating_distribution'
            ),
            'classes': ('collapse',)
        }),
        (_('Verified Purchase Statistics'), {
            'fields': ('verified_reviews_count', 'verified_average_rating'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_statistics']
    
    def update_statistics(self, request, queryset):
        """Update rating statistics for selected products."""
        updated = 0
        for rating in queryset:
            rating.update_statistics()
            updated += 1
        self.message_user(request, f'{updated} product ratings updated.')
    update_statistics.short_description = _('Update rating statistics')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
