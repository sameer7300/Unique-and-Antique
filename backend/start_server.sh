#!/bin/bash
"""
Start script for Django application with Gunicorn
"""

# Set the application directory
APP_DIR="/home/cloudpanel/htdocs/backend.unique-antique.com"
cd $APP_DIR

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.production

# Start Gunicorn server
exec gunicorn \
    --config gunicorn_config.py \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info \
    --pid logs/gunicorn.pid \
    --user cloudpanel \
    --group cloudpanel \
    config.wsgi:application
