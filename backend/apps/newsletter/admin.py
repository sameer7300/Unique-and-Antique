from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import NewsletterSubscriber, Newsletter, NewsletterSendLog
from .services import NewsletterEmailService


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'status_badge', 'subscribed_at', 'subscriber_actions']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'ip_address']
    list_per_page = 50
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'is_active')
        }),
        ('Subscription Details', {
            'fields': ('subscribed_at', 'unsubscribed_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">● Inactive</span>'
            )
    status_badge.short_description = 'Status'
    
    def subscriber_actions(self, obj):
        if obj.is_active:
            return format_html(
                '<a class="button" href="{}">Unsubscribe</a>',
                reverse('admin:newsletter_unsubscribe', args=[obj.pk])
            )
        else:
            return format_html(
                '<a class="button" href="{}">Resubscribe</a>',
                reverse('admin:newsletter_resubscribe', args=[obj.pk])
            )
    subscriber_actions.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:subscriber_id>/unsubscribe/',
                self.admin_site.admin_view(self.unsubscribe_subscriber),
                name='newsletter_unsubscribe',
            ),
            path(
                '<int:subscriber_id>/resubscribe/',
                self.admin_site.admin_view(self.resubscribe_subscriber),
                name='newsletter_resubscribe',
            ),
        ]
        return custom_urls + urls
    
    def unsubscribe_subscriber(self, request, subscriber_id):
        subscriber = NewsletterSubscriber.objects.get(pk=subscriber_id)
        subscriber.unsubscribe()
        messages.success(request, f'{subscriber.email} has been unsubscribed.')
        return HttpResponseRedirect(reverse('admin:newsletter_newslettersubscriber_changelist'))
    
    def resubscribe_subscriber(self, request, subscriber_id):
        subscriber = NewsletterSubscriber.objects.get(pk=subscriber_id)
        subscriber.resubscribe()
        messages.success(request, f'{subscriber.email} has been resubscribed.')
        return HttpResponseRedirect(reverse('admin:newsletter_newslettersubscriber_changelist'))


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'status_badge', 'recipients_count', 'sent_count', 'created_at', 'newsletter_actions']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'subject']
    readonly_fields = ['created_by', 'created_at', 'sent_at', 'recipients_count', 'sent_count', 'failed_count']
    list_per_page = 20
    
    fieldsets = (
        ('Newsletter Content', {
            'fields': ('title', 'subject', 'content')
        }),
        ('Sending Options', {
            'fields': ('status', 'scheduled_at')
        }),
        ('Statistics', {
            'fields': ('recipients_count', 'sent_count', 'failed_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'scheduled': 'orange',
            'sent': 'green'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def newsletter_actions(self, obj):
        if obj.can_be_sent:
            return format_html(
                '<a class="button" href="{}" style="background-color: #417690; color: white;">Send Now</a>',
                reverse('admin:newsletter_send', args=[obj.pk])
            )
        elif obj.is_sent:
            return format_html(
                '<a class="button" href="{}">View Logs</a>',
                reverse('admin:newsletter_newslettersendlog_changelist') + f'?newsletter__id__exact={obj.pk}'
            )
        return '-'
    newsletter_actions.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new newsletter
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:newsletter_id>/send/',
                self.admin_site.admin_view(self.send_newsletter),
                name='newsletter_send',
            ),
        ]
        return custom_urls + urls
    
    def send_newsletter(self, request, newsletter_id):
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        
        if not newsletter.can_be_sent:
            messages.error(request, 'This newsletter cannot be sent.')
            return HttpResponseRedirect(reverse('admin:newsletter_newsletter_changelist'))
        
        # Send the newsletter
        try:
            result = NewsletterEmailService.send_newsletter(newsletter)
            if result['success']:
                messages.success(
                    request, 
                    f'Newsletter sent successfully! {result["sent_count"]} emails sent, {result["failed_count"]} failed.'
                )
            else:
                messages.error(request, f'Failed to send newsletter: {result["error"]}')
        except Exception as e:
            messages.error(request, f'Error sending newsletter: {str(e)}')
        
        return HttpResponseRedirect(reverse('admin:newsletter_newsletter_changelist'))


@admin.register(NewsletterSendLog)
class NewsletterSendLogAdmin(admin.ModelAdmin):
    list_display = ['newsletter', 'subscriber_email', 'status_badge', 'sent_at']
    list_filter = ['success', 'sent_at', 'newsletter']
    search_fields = ['newsletter__title', 'subscriber__email']
    readonly_fields = ['newsletter', 'subscriber', 'sent_at', 'success', 'error_message']
    list_per_page = 100
    
    def subscriber_email(self, obj):
        return obj.subscriber.email
    subscriber_email.short_description = 'Subscriber Email'
    
    def status_badge(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Success</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Failed</span>'
            )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation of send logs
