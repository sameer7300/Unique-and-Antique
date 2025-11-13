"""
Development settings for Unique and Antique E-commerce Platform.
"""

from .base import *

# Debug settings
DEBUG = True

# Additional apps for development
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Additional middleware for development
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

def show_toolbar(request):
    """
    Custom function to determine when to show debug toolbar.
    Exclude API endpoints to prevent CSP nonce errors.
    """
    if not DEBUG:
        return False
    if request.path.startswith('/api/'):
        return False
    return True

# Debug toolbar configuration to exclude API endpoints
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

# Database for development (SQLite for quick setup, PostgreSQL recommended)
# Uncomment below to use SQLite for development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email backend for development - Use SMTP for actual email sending
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Console only for testing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Actual SMTP sending

# Static files for development
STATICFILES_DIRS += [
    BASE_DIR / 'static',
]

# Media files for development
MEDIA_ROOT = BASE_DIR / 'media'

# Disable HTTPS redirect in development
SECURE_SSL_REDIRECT = False

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True  # Allow credentials (cookies) to be sent

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # Set to False for development (HTTP)
CSRF_COOKIE_HTTPONLY = False  # Allow JS access to CSRF token

# Cache settings for development (use database cache for sessions)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Session settings for development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-site requests
SESSION_COOKIE_HTTPONLY = True  # Security: prevent JS access to session cookie
SESSION_COOKIE_SECURE = False  # Set to False for development (HTTP)

# Logging for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Django Extensions
SHELL_PLUS_PRINT_SQL = True

# Development-specific settings
ALLOWED_HOSTS = ['*']  # Allow all hosts in development

# Disable password validators in development for easier testing
AUTH_PASSWORD_VALIDATORS = []

# Development database settings (if using PostgreSQL)
if config('USE_POSTGRES', default=True, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='unique_antique_dev'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='password'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
