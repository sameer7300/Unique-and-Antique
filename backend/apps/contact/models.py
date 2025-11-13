"""
Contact models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """
    Model to store contact form submissions.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    
    SUBJECT_CHOICES = [
        ('general', _('General Inquiry')),
        ('order', _('Order Related')),
        ('return', _('Return/Exchange')),
        ('product', _('Product Question')),
        ('technical', _('Technical Support')),
        ('complaint', _('Complaint')),
        ('partnership', _('Partnership')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    email = models.EmailField(_('email'))
    subject = models.CharField(
        _('subject'),
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='general'
    )
    message = models.TextField(_('message'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_read = models.BooleanField(_('is read'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    responded_at = models.DateTimeField(_('responded at'), null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(_('admin notes'), blank=True)
    
    class Meta:
        db_table = 'contact_messages'
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
