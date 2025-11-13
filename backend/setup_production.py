#!/usr/bin/env python
"""
Production setup script for Hostinger deployment
Run this after uploading files to the server
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from apps.settings.models import SiteSettings
from apps.products.models import Category, Brand

def setup_database():
    """Set up database with initial data"""
    print("🗄️  Setting up database...")
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Database migrations completed")

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("👤 Setting up admin user...")
    
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        print("Please enter superuser details:")
        execute_from_command_line(['manage.py', 'createsuperuser'])
    else:
        print("✅ Superuser already exists")

def setup_site_settings():
    """Set up initial site settings"""
    print("⚙️  Setting up site settings...")
    
    settings = SiteSettings.get_settings()
    settings.currency_code = 'PKR'
    settings.currency_symbol = 'PKR'
    settings.tax_rate = 18.00  # Pakistan GST rate
    settings.free_shipping_threshold = 5000.00
    settings.standard_shipping_cost = 200.00
    settings.express_shipping_cost = 500.00
    settings.minimum_order_amount = 500.00
    settings.save()
    
    print("✅ Site settings configured")

def create_sample_data():
    """Create sample categories and brands"""
    print("📦 Creating sample data...")
    
    # Sample categories
    categories = [
        {'name': 'Antique Furniture', 'slug': 'antique-furniture', 'description': 'Vintage and antique furniture pieces'},
        {'name': 'Collectibles', 'slug': 'collectibles', 'description': 'Rare and unique collectible items'},
        {'name': 'Art & Paintings', 'slug': 'art-paintings', 'description': 'Original artwork and vintage paintings'},
        {'name': 'Jewelry', 'slug': 'jewelry', 'description': 'Antique and vintage jewelry'},
        {'name': 'Home Decor', 'slug': 'home-decor', 'description': 'Vintage home decoration items'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Sample brands
    brands = [
        {'name': 'Victorian Era', 'slug': 'victorian-era', 'description': 'Items from the Victorian period'},
        {'name': 'Art Deco', 'slug': 'art-deco', 'description': 'Art Deco style items'},
        {'name': 'Mid-Century Modern', 'slug': 'mid-century-modern', 'description': 'Mid-century modern pieces'},
        {'name': 'Antique Collection', 'slug': 'antique-collection', 'description': 'General antique items'},
    ]
    
    for brand_data in brands:
        brand, created = Brand.objects.get_or_create(
            slug=brand_data['slug'],
            defaults=brand_data
        )
        if created:
            print(f"Created brand: {brand.name}")
    
    print("✅ Sample data created")

def collect_static():
    """Collect static files"""
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✅ Static files collected")

def main():
    """Main setup function"""
    print("=" * 60)
    print("UNIQUE & ANTIQUE - PRODUCTION SETUP")
    print("=" * 60)
    
    try:
        setup_database()
        create_superuser()
        setup_site_settings()
        create_sample_data()
        collect_static()
        
        print("\n" + "=" * 60)
        print("🎉 PRODUCTION SETUP COMPLETED!")
        print("=" * 60)
        print("Your Unique & Antique backend is ready!")
        print("You can now:")
        print("1. Access the admin panel")
        print("2. Add products and manage the store")
        print("3. Configure additional settings as needed")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
