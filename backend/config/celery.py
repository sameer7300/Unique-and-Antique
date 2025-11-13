"""
Celery configuration for Unique and Antique E-commerce Platform.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('unique_antique')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-carts': {
        'task': 'apps.cart.tasks.cleanup_expired_carts',
        'schedule': 3600.0,  # Run every hour
    },
    'send-order-reminders': {
        'task': 'apps.orders.tasks.send_order_reminders',
        'schedule': 86400.0,  # Run daily
    },
    'update-inventory-alerts': {
        'task': 'apps.products.tasks.check_low_stock',
        'schedule': 21600.0,  # Run every 6 hours
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
