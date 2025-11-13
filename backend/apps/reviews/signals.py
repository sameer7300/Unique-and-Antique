"""
Signals for the reviews app.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Review, ProductRating, ReviewHelpfulness
from .services import ReviewEmailService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Review)
def track_review_status_change(sender, instance, **kwargs):
    """
    Track review status changes to detect approval.
    """
    if instance.pk:
        try:
            old_review = Review.objects.get(pk=instance.pk)
            instance._old_status = old_review.status
        except Review.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Review)
def update_product_rating_on_review_save(sender, instance, **kwargs):
    """
    Update product rating statistics when review is saved and send approval emails.
    """
    if instance.status == 'approved':
        rating_stats, created = ProductRating.objects.get_or_create(
            product=instance.product
        )
        rating_stats.update_statistics()
        
        # Send approval email if status changed from non-approved to approved
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != 'approved' and not getattr(instance, '_skip_approval_email', False):
            try:
                ReviewEmailService.send_review_approval_email(instance)
                logger.info(f"Review approval email sent for review {instance.id}")
            except Exception as e:
                logger.error(f"Failed to send review approval email for review {instance.id}: {str(e)}")


@receiver(post_delete, sender=Review)
def update_product_rating_on_review_delete(sender, instance, **kwargs):
    """
    Update product rating statistics when review is deleted.
    """
    try:
        rating_stats = ProductRating.objects.get(product=instance.product)
        rating_stats.update_statistics()
    except ProductRating.DoesNotExist:
        pass


@receiver(post_save, sender=ReviewHelpfulness)
def update_review_helpfulness_counts(sender, instance, created, **kwargs):
    """
    Update review helpfulness counts when vote is saved.
    """
    if not created:
        # Vote was updated, recalculate counts
        review = instance.review
        helpful_count = review.helpfulness_votes.filter(is_helpful=True).count()
        not_helpful_count = review.helpfulness_votes.filter(is_helpful=False).count()
        
        review.helpful_count = helpful_count
        review.not_helpful_count = not_helpful_count
        review.save(update_fields=['helpful_count', 'not_helpful_count'])


@receiver(post_delete, sender=ReviewHelpfulness)
def update_review_helpfulness_on_delete(sender, instance, **kwargs):
    """
    Update review helpfulness counts when vote is deleted.
    """
    review = instance.review
    
    if instance.is_helpful:
        review.helpful_count = max(0, review.helpful_count - 1)
    else:
        review.not_helpful_count = max(0, review.not_helpful_count - 1)
    
    review.save(update_fields=['helpful_count', 'not_helpful_count'])
