"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, Address


class AddressInline(admin.TabularInline):
    """
    Inline admin for Address model.
    """
    model = Address
    extra = 0
    fields = [
        'type', 'first_name', 'last_name', 'city',
        'state', 'country', 'is_default'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model.
    """
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'role', 'is_verified', 'is_active', 'created_at'
    ]
    list_filter = [
        'role', 'is_verified', 'is_active', 'is_staff',
        'is_superuser', 'created_at'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        (_('Permissions'), {
            'fields': (
                'role', 'is_verified', 'is_active', 'is_staff',
                'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'phone', 'role', 'password1', 'password2'
            ),
        }),
    )
    
    inlines = [AddressInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model.
    """
    list_display = [
        'user', 'gender', 'location', 'newsletter_subscription',
        'email_notifications', 'created_at'
    ]
    list_filter = [
        'gender', 'newsletter_subscription', 'email_notifications',
        'sms_notifications', 'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Personal Information'), {
            'fields': ('avatar', 'bio', 'birth_date', 'gender', 'website', 'location')
        }),
        (_('Preferences'), {
            'fields': (
                'newsletter_subscription', 'email_notifications', 'sms_notifications'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin configuration for Address model.
    """
    list_display = [
        'user', 'type', 'first_name', 'last_name',
        'city', 'state', 'country', 'is_default', 'created_at'
    ]
    list_filter = ['type', 'country', 'state', 'is_default', 'created_at']
    search_fields = [
        'user__email', 'first_name', 'last_name',
        'city', 'state', 'postal_code'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user', 'type', 'is_default')}),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'company', 'phone')
        }),
        (_('Address'), {
            'fields': (
                'address_line_1', 'address_line_2', 'city',
                'state', 'postal_code', 'country'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
