from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber model"""
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Subscriber's email address"
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Subscriber's name (optional)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the subscription is active"
    )
    subscribed_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the user subscribed"
    )
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user unsubscribed"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when subscribed"
    )
    
    class Meta:
        db_table = 'newsletter_subscribers'
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def unsubscribe(self):
        """Unsubscribe the user"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def resubscribe(self):
        """Resubscribe the user"""
        self.is_active = True
        self.unsubscribed_at = None
        self.save()


class Newsletter(models.Model):
    """Newsletter campaign model"""
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    SENT = 'sent'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SCHEDULED, 'Scheduled'),
        (SENT, 'Sent'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Newsletter title"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Email subject line"
    )
    content = models.TextField(
        help_text="Newsletter content (HTML supported)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        help_text="Newsletter status"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='newsletters',
        help_text="User who created the newsletter"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the newsletter was created"
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to send the newsletter"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the newsletter was sent"
    )
    recipients_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of recipients"
    )
    sent_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of emails sent successfully"
    )
    failed_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of emails that failed to send"
    )
    
    class Meta:
        db_table = 'newsletters'
        ordering = ['-created_at']
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_sent(self):
        return self.status == self.SENT
    
    @property
    def can_be_sent(self):
        return self.status in [self.DRAFT, self.SCHEDULED]


class NewsletterSendLog(models.Model):
    """Log of newsletter sends to individual subscribers"""
    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.CASCADE,
        related_name='send_logs'
    )
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.CASCADE,
        related_name='send_logs'
    )
    sent_at = models.DateTimeField(
        default=timezone.now
    )
    success = models.BooleanField(
        default=True,
        help_text="Whether the email was sent successfully"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if sending failed"
    )
    
    class Meta:
        db_table = 'newsletter_send_logs'
        ordering = ['-sent_at']
        unique_together = ['newsletter', 'subscriber']
        verbose_name = 'Newsletter Send Log'
        verbose_name_plural = 'Newsletter Send Logs'
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.newsletter.title} → {self.subscriber.email}"
