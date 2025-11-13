#!/usr/bin/env python
"""
Setup script for Django Admin Theme Enhancement
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🎨 Setting up Django Admin Theme Enhancement for Unique & Antique")
    print("=" * 60)
    
    # Install required packages
    packages = [
        'django-jazzmin==2.6.0',
        'django-admin-interface==0.28.6', 
        'django-colorfield==0.11.0',
        'django-import-export==3.3.1',
        'django-admin-rangefilter==0.11.1',
        'django-nested-admin==4.0.2'
    ]
    
    print("📦 Installing admin enhancement packages...")
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    # Create static directories if they don't exist
    static_dirs = [
        BASE_DIR / 'static' / 'admin' / 'css',
        BASE_DIR / 'static' / 'admin' / 'js',
        BASE_DIR / 'static' / 'admin' / 'img'
    ]
    
    for static_dir in static_dirs:
        static_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {static_dir}")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Run migrations
    run_command("python manage.py makemigrations", "Creating migrations")
    run_command("python manage.py migrate", "Running migrations")
    
    # Create superuser if it doesn't exist
    print("\n👤 Checking for superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("No superuser found. Creating one...")
            print("Please enter superuser details:")
            
            email = input("Email: ")
            first_name = input("First Name: ")
            last_name = input("Last Name: ")
            
            user = User.objects.create_superuser(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                password='admin123'  # Default password
            )
            print(f"✅ Superuser created: {email}")
            print("🔑 Default password: admin123 (Please change this!)")
        else:
            print("✅ Superuser already exists")
            
    except Exception as e:
        print(f"⚠️  Could not create superuser: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Django Admin Theme Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Visit: http://localhost:8000/admin/")
    print("3. Login with your superuser credentials")
    print("4. Enjoy your beautiful new admin interface!")
    print("\n🎨 Features Added:")
    print("• Modern Jazzmin theme with custom styling")
    print("• Import/Export functionality for all models")
    print("• Advanced filtering with date and numeric ranges")
    print("• Enhanced forms with better UX")
    print("• Custom CSS and JavaScript enhancements")
    print("• Professional dashboard with statistics")
    print("\n💡 Tips:")
    print("• Use the UI Builder in the sidebar to customize colors")
    print("• Export data to Excel/CSV using the Export button")
    print("• Use date range filters for better data analysis")
    print("• Check the custom admin actions for bulk operations")

if __name__ == '__main__':
    main()
