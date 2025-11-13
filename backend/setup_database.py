#!/usr/bin/env python
"""
Database setup script for the e-commerce platform.
This script handles the initial database setup and migrations.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def setup_database():
    """Set up the database with proper migration order."""
    
    print("🚀 Setting up database for Unique and Antique E-commerce Platform...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    django.setup()
    
    try:
        # Step 1: Create migrations for accounts first (custom user model)
        print("\n📝 Creating migrations for accounts app...")
        execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
        
        # Step 2: Create migrations for other apps
        apps = ['products', 'cart', 'orders', 'payments', 'reviews']
        for app in apps:
            print(f"\n📝 Creating migrations for {app} app...")
            execute_from_command_line(['manage.py', 'makemigrations', app])
        
        # Step 3: Run migrations
        print("\n🔧 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Step 4: Create superuser (optional)
        print("\n👤 Database setup complete!")
        print("\nTo create a superuser, run:")
        print("python manage.py createsuperuser")
        
        print("\n✅ Database setup completed successfully!")
        print("🌟 Your e-commerce platform is ready to go!")
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you have the correct database settings in .env")
        print("2. Ensure the database server is running (if using PostgreSQL)")
        print("3. Check that all required packages are installed")
        return False
    
    return True

if __name__ == '__main__':
    setup_database()
