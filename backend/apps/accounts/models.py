"""
User and Profile models for the Unique and Antique E-commerce Platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    
    ROLE_CHOICES = [
        ('customer', _('Customer')),
        ('admin', _('Admin')),
        ('staff', _('Staff')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(
        _('phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )
    is_verified = models.BooleanField(_('email verified'), default=False)
    
    # Two-Factor Authentication
    two_factor_enabled = models.BooleanField(_('2FA enabled'), default=False)
    two_factor_secret = models.CharField(_('2FA secret'), max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(_('backup codes'), default=list, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_staff_user(self):
        return self.role == 'staff' or self.is_staff


class Profile(models.Model):
    """
    User Profile model for additional user information.
    """
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    website = models.URLField(_('website'), blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(
        _('newsletter subscription'),
        default=True
    )
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True
    )
    sms_notifications = models.BooleanField(
        _('SMS notifications'),
        default=False
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'accounts_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class Address(models.Model):
    """
    User Address model for shipping and billing addresses.
    """
    
    ADDRESS_TYPES = [
        ('shipping', _('Shipping')),
        ('billing', _('Billing')),
        ('both', _('Both')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    type = models.CharField(
        _('address type'),
        max_length=20,
        choices=ADDRESS_TYPES,
        default='shipping'
    )
    first_name = models.CharField(_('first name'), max_length=50)
    last_name = models.CharField(_('last name'), max_length=50)
    company = models.CharField(_('company'), max_length=100, blank=True)
    address_line_1 = models.CharField(_('address line 1'), max_length=255)
    address_line_2 = models.CharField(_('address line 2'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state/province'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='United States')
    phone = models.CharField(
        _('phone number'),
        max_length=17,
        blank=True,
        validators=[User.phone_regex]
    )
    is_default = models.BooleanField(_('default address'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'accounts_address'
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', '-created_at']
        unique_together = ['user', 'type', 'is_default']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.state}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return ", ".join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per type per user
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                type=self.type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
