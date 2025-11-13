"""
Testing settings for Unique and Antique E-commerce Platform.
"""

from .base import *

# Test settings
DEBUG = True
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast hashing for tests
]

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Cache configuration for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery configuration for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Media files for testing
MEDIA_ROOT = '/tmp/test_media'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Test-specific settings
ALLOWED_HOSTS = ['testserver']
SECRET_KEY = 'test-secret-key'

# Disable CORS for testing
CORS_ALLOW_ALL_ORIGINS = True

# Stripe test keys
STRIPE_PUBLISHABLE_KEY = 'pk_test_test_key'
STRIPE_SECRET_KEY = 'sk_test_test_key'
STRIPE_WEBHOOK_SECRET = 'whsec_test_secret'
