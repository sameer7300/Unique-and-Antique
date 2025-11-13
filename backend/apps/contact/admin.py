"""
Contact admin configuration for the Unique and Antique E-commerce Platform.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for contact messages.
    """
    
    list_display = [
        'name',
        'email',
        'subject_display',
        'status_badge',
        'is_read',
        'created_at',
        'responded_at'
    ]
    
    list_filter = [
        'status',
        'subject',
        'is_read',
        'created_at',
        'responded_at'
    ]
    
    search_fields = [
        'name',
        'email',
        'message'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('status', 'is_read', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_display(self, obj):
        """Display subject with icon."""
        return obj.get_subject_display()
    subject_display.short_description = 'Subject'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#fbbf24',
            'in_progress': '#3b82f6',
            'resolved': '#10b981',
            'closed': '#6b7280'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related()
