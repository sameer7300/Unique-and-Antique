"""
Model and view mixins for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action


class TimestampMixin(models.Model):
    """
    Abstract model mixin that provides created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Abstract model mixin that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the object.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the object.
        """
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """
        Restore a soft-deleted object.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class ActiveManager(models.Manager):
    """
    Manager that excludes soft-deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    Manager that includes all objects (including soft-deleted).
    """
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(SoftDeleteMixin, TimestampMixin):
    """
    Abstract model that combines soft delete and timestamp functionality.
    """
    objects = ActiveManager()
    all_objects = AllObjectsManager()
    
    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """
    Abstract model mixin that provides slug functionality.
    """
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.slug and hasattr(self, 'title'):
            from django.utils.text import slugify
            from .helpers import generate_unique_slug
            self.slug = generate_unique_slug(self.__class__, self.title)
        elif not self.slug and hasattr(self, 'name'):
            from django.utils.text import slugify
            from .helpers import generate_unique_slug
            self.slug = generate_unique_slug(self.__class__, self.name)
        super().save(*args, **kwargs)


class SEOMixin(models.Model):
    """
    Abstract model mixin that provides SEO fields.
    """
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO title tag (max 60 characters)"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description (max 160 characters)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO keywords (comma-separated)"
    )
    
    class Meta:
        abstract = True


class ViewCountMixin(models.Model):
    """
    Abstract model mixin that provides view count functionality.
    """
    view_count = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def increment_view_count(self):
        """
        Increment the view count and update last viewed timestamp.
        """
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])


class StatusMixin(models.Model):
    """
    Abstract model mixin that provides status functionality.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    class Meta:
        abstract = True
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_inactive(self):
        return self.status == 'inactive'
    
    @property
    def is_draft(self):
        return self.status == 'draft'


class PositionMixin(models.Model):
    """
    Abstract model mixin that provides position/ordering functionality.
    """
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
        ordering = ['position']


# View Mixins

class CacheResponseMixin:
    """
    Mixin to add caching to API responses.
    """
    cache_timeout = 300  # 5 minutes default
    
    def get_cache_key(self, request, *args, **kwargs):
        """
        Generate cache key for the request.
        """
        from django.core.cache.utils import make_template_fragment_key
        key_parts = [
            self.__class__.__name__,
            request.path,
            str(request.user.id) if request.user.is_authenticated else 'anonymous',
        ]
        return ':'.join(key_parts)
    
    def get_cached_response(self, request, *args, **kwargs):
        """
        Get cached response if available.
        """
        from django.core.cache import cache
        cache_key = self.get_cache_key(request, *args, **kwargs)
        return cache.get(cache_key)
    
    def cache_response(self, request, response, *args, **kwargs):
        """
        Cache the response.
        """
        from django.core.cache import cache
        cache_key = self.get_cache_key(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout)


class BulkActionMixin:
    """
    Mixin to add bulk actions to viewsets.
    """
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Bulk delete objects.
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'No IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        queryset.delete()
        
        return Response({
            'message': f'{count} items deleted successfully',
            'deleted_count': count
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update objects.
        """
        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        
        if not ids or not update_data:
            return Response(
                {'error': 'IDs and update data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.update(**update_data)
        
        return Response({
            'message': f'{count} items updated successfully',
            'updated_count': count
        })


class ExportMixin:
    """
    Mixin to add export functionality to viewsets.
    """
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export data as CSV.
        """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename()}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        fields = self.get_export_fields()
        writer.writerow(fields)
        
        # Write data
        queryset = self.filter_queryset(self.get_queryset())
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field, '')
                row.append(str(value))
            writer.writerow(row)
        
        return response
    
    def get_export_filename(self):
        """
        Get filename for export.
        """
        return f"{self.__class__.__name__.lower()}_export"
    
    def get_export_fields(self):
        """
        Get fields to include in export.
        """
        if hasattr(self, 'export_fields'):
            return self.export_fields
        
        # Default to serializer fields
        serializer = self.get_serializer()
        return list(serializer.fields.keys())


class FilterMixin:
    """
    Mixin to add common filtering functionality.
    """
    
    def filter_by_date_range(self, queryset, field_name, start_date, end_date):
        """
        Filter queryset by date range.
        """
        if start_date:
            queryset = queryset.filter(**{f"{field_name}__gte": start_date})
        if end_date:
            queryset = queryset.filter(**{f"{field_name}__lte": end_date})
        return queryset
    
    def filter_by_user(self, queryset, user):
        """
        Filter queryset by user.
        """
        if user and user.is_authenticated:
            return queryset.filter(user=user)
        return queryset.none()
    
    def filter_by_status(self, queryset, status_list):
        """
        Filter queryset by status list.
        """
        if status_list:
            return queryset.filter(status__in=status_list)
        return queryset


class SearchMixin:
    """
    Mixin to add search functionality.
    """
    search_fields = []
    
    def get_search_queryset(self, queryset, search_term):
        """
        Filter queryset by search term.
        """
        if not search_term or not self.search_fields:
            return queryset
        
        from django.db.models import Q
        
        search_query = Q()
        for field in self.search_fields:
            search_query |= Q(**{f"{field}__icontains": search_term})
        
        return queryset.filter(search_query)


class AuditMixin(models.Model):
    """
    Abstract model mixin that provides audit trail functionality.
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
