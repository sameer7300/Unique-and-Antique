#!/usr/bin/env python3
"""
WSGI configuration for CloudPanel deployment
"""
import sys
import os
from pathlib import Path

# Add the application directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    # Import Django WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # Log successful startup
    print("✅ Django WSGI application loaded successfully")
    
except Exception as e:
    # Log any errors during startup
    print(f"❌ Error loading Django WSGI application: {e}")
    
    # Create a simple error application
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Application Error</h1>
            <div class="error">
                <p><strong>Error:</strong> {str(e)}</p>
                <p>Please check the application logs and configuration.</p>
            </div>
        </body>
        </html>
        """
        return [error_html.encode('utf-8')]
