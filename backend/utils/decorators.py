"""
Custom decorators for the Unique and Antique E-commerce Platform.
"""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.response import Response
import time
import logging

logger = logging.getLogger(__name__)


def cache_response(timeout=300, key_prefix=''):
    """
    Decorator to cache API responses.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{self.__class__.__name__}:{func.__name__}"
            if request.user.is_authenticated:
                cache_key += f":{request.user.id}"
            
            # Add query parameters to cache key
            if request.GET:
                cache_key += f":{hash(frozenset(request.GET.items()))}"
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response)
            
            # Get fresh response
            response = func(self, request, *args, **kwargs)
            
            # Cache successful responses
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator


def rate_limit(max_requests=100, window=3600, key_func=None):
    """
    Rate limiting decorator.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate rate limit key
            if key_func:
                rate_key = key_func(request)
            elif request.user.is_authenticated:
                rate_key = f"rate_limit:{request.user.id}:{func.__name__}"
            else:
                rate_key = f"rate_limit:{request.META.get('REMOTE_ADDR')}:{func.__name__}"
            
            # Get current request count
            current_requests = cache.get(rate_key, 0)
            
            if current_requests >= max_requests:
                return Response(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment request count
            cache.set(rate_key, current_requests + 1, window)
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def log_api_call(log_level=logging.INFO):
    """
    Decorator to log API calls.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            start_time = time.time()
            
            # Log request
            logger.log(log_level, f"API Call: {func.__name__} by {request.user}")
            
            try:
                response = func(self, request, *args, **kwargs)
                
                # Log successful response
                duration = time.time() - start_time
                logger.log(
                    log_level,
                    f"API Response: {func.__name__} - {response.status_code} - {duration:.2f}s"
                )
                
                return response
            
            except Exception as e:
                # Log error
                duration = time.time() - start_time
                logger.error(
                    f"API Error: {func.__name__} - {str(e)} - {duration:.2f}s"
                )
                raise
        
        return wrapper
    return decorator


def require_verified_user(func):
    """
    Decorator to require verified user.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.is_verified:
            return Response(
                {'error': 'Email verification required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return func(self, request, *args, **kwargs)
    return wrapper


def admin_required(func):
    """
    Decorator to require admin user.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return func(self, request, *args, **kwargs)
    return wrapper


def validate_json_content_type(func):
    """
    Decorator to validate JSON content type.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.content_type
            if not content_type.startswith('application/json'):
                return Response(
                    {'error': 'Content-Type must be application/json'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return func(self, request, *args, **kwargs)
    return wrapper


def handle_exceptions(default_response=None):
    """
    Decorator to handle exceptions gracefully.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                
                if default_response:
                    return default_response
                
                return Response(
                    {'error': 'An unexpected error occurred'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator


def measure_performance(func):
    """
    Decorator to measure function performance.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"Performance: {func.__name__} took {duration:.4f} seconds")
        
        return result
    return wrapper


def retry_on_failure(max_retries=3, delay=1):
    """
    Decorator to retry function on failure.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def validate_request_data(required_fields=None, optional_fields=None):
    """
    Decorator to validate request data.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            data = request.data
            
            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    return Response(
                        {
                            'error': 'Missing required fields',
                            'missing_fields': missing_fields
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check for unexpected fields
            if optional_fields is not None:
                allowed_fields = set(required_fields or []) | set(optional_fields)
                unexpected_fields = set(data.keys()) - allowed_fields
                
                if unexpected_fields:
                    return Response(
                        {
                            'error': 'Unexpected fields in request',
                            'unexpected_fields': list(unexpected_fields)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def conditional_cache(condition_func, timeout=300):
    """
    Decorator to conditionally cache responses.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not condition_func(request):
                return func(self, request, *args, **kwargs)
            
            # Use caching
            return cache_response(timeout)(func)(self, request, *args, **kwargs)
        return wrapper
    return decorator


# Class decorators

def add_cache_headers(timeout=300):
    """
    Class decorator to add cache headers to all methods.
    """
    def decorator(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, method_decorator(
                    cache_page(timeout), name='dispatch'
                )(attr))
        return cls
    return decorator


def add_cors_headers(cls):
    """
    Class decorator to add CORS headers.
    """
    def add_cors_to_response(self, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    original_dispatch = cls.dispatch
    
    def dispatch_with_cors(self, request, *args, **kwargs):
        response = original_dispatch(self, request, *args, **kwargs)
        return add_cors_to_response(self, response)
    
    cls.dispatch = dispatch_with_cors
    return cls
