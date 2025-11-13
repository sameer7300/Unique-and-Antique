#!/usr/bin/env python
"""
CloudPanel deployment script for Unique & Antique backend
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_cloudpanel_deployment():
    """Create a CloudPanel-specific deployment package"""
    
    print("🚀 Creating CloudPanel deployment package...")
    
    # Current directory
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    # Create CloudPanel deployment directory
    deploy_dir = project_root / "cloudpanel_deployment"
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Backend deployment directory
    backend_deploy = deploy_dir / "backend"
    backend_deploy.mkdir()
    
    # Files and directories to exclude
    exclude_patterns = {
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git',
        '.gitignore',
        'node_modules',
        '.env',
        'db.sqlite3',
        'media',
        'staticfiles',
        'logs',
        '.pytest_cache',
        'test_*.py',
        'tests',
        'venv',
        'env',
        '.vscode',
        '.idea',
        'deployment',
        'cloudpanel_deployment',
        'test_email.py',
        'test_cloudinary.py',
        'test_contact_email.py',
        'test_review_email.py',
        'deploy.py',
        'deploy_cloudpanel.py'
    }
    
    def should_exclude(path):
        """Check if a path should be excluded"""
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern in path_str or path.name.startswith('.'):
                return True
        return False
    
    # Copy backend files
    print("📁 Copying backend files...")
    for item in backend_dir.iterdir():
        if not should_exclude(item):
            if item.is_dir():
                shutil.copytree(item, backend_deploy / item.name, 
                              ignore=shutil.ignore_patterns(*exclude_patterns))
            else:
                shutil.copy2(item, backend_deploy)
    
    # Copy production environment file
    prod_env = backend_dir / ".env.production"
    if prod_env.exists():
        shutil.copy2(prod_env, backend_deploy / ".env")
        print("✅ Production environment file copied as .env")
    
    # Ensure passenger_wsgi.py is included
    passenger_wsgi = backend_dir / "passenger_wsgi.py"
    if passenger_wsgi.exists():
        shutil.copy2(passenger_wsgi, backend_deploy / "passenger_wsgi.py")
        print("✅ CloudPanel WSGI file copied")
    
    # Create CloudPanel-specific requirements.txt
    requirements_file = backend_deploy / "requirements.txt"
    if not requirements_file.exists():
        print("📝 Creating CloudPanel requirements.txt...")
        with open(requirements_file, 'w') as f:
            f.write("""# Core Django
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3

# Database
psycopg2-binary==2.9.7
dj-database-url==2.1.0

# Authentication & Security
djangorestframework-simplejwt==5.3.0
cryptography==41.0.7

# File Storage & Images
Pillow==10.0.1
cloudinary==1.36.0
django-cloudinary-storage==0.3.0

# API Documentation
drf-spectacular==0.26.5

# Payment Processing
stripe==7.8.0

# Environment Management
python-decouple==3.8

# Production Server
gunicorn==21.2.0

# Monitoring
sentry-sdk==1.38.0

# Django Admin Enhancements
django-jazzmin==2.6.0
django-colorfield==0.11.0

# Caching (optional)
redis==5.0.1
django-redis==5.4.0

# Background Tasks (optional)
celery==5.3.4
""")
    
    # Create CloudPanel deployment script
    deploy_script = deploy_dir / "deploy_to_cloudpanel.sh"
    with open(deploy_script, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
# CloudPanel Deployment Script for Unique & Antique Backend

echo "🚀 Starting CloudPanel deployment..."

# Set variables
SITE_DIR="/home/cloudpanel/htdocs/backend.unique-antique.com"
BACKUP_DIR="/home/cloudpanel/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup of existing deployment
if [ -d "$SITE_DIR" ]; then
    echo "📦 Creating backup..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$SITE_DIR" "$BACKUP_DIR/"
fi

# Create site directory if it doesn't exist
mkdir -p "$SITE_DIR"

# Copy files
echo "📁 Copying application files..."
cp -r backend/* "$SITE_DIR/"

# Set permissions
echo "🔐 Setting permissions..."
chown -R cloudpanel:cloudpanel "$SITE_DIR"
chmod -R 755 "$SITE_DIR"
chmod +x "$SITE_DIR/start_server.sh"

# Create virtual environment
echo "🐍 Setting up Python environment..."
cd "$SITE_DIR"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run Django setup
echo "🔧 Setting up Django..."
python manage.py collectstatic --noinput
python manage.py migrate

# Create logs directory
mkdir -p "$SITE_DIR/logs"
chown -R cloudpanel:cloudpanel "$SITE_DIR/logs"

# Setup systemd service
echo "⚙️ Setting up Gunicorn service..."
cp "$SITE_DIR/systemd_service.conf" /etc/systemd/system/unique-antique-backend.service
systemctl daemon-reload
systemctl enable unique-antique-backend

# Start the service
echo "🔄 Starting application service..."
systemctl start unique-antique-backend

# Check service status
echo "📊 Checking service status..."
systemctl status unique-antique-backend --no-pager

echo "✅ CloudPanel deployment completed!"
echo "🌐 Your application should now be available at: https://backend.unique-antique.com"
echo "📊 Check service status: systemctl status unique-antique-backend"
echo "📋 View logs: journalctl -u unique-antique-backend -f"
""")
    
    # Make script executable
    os.chmod(deploy_script, 0o755)
    
    # Create CloudPanel configuration guide
    config_guide = deploy_dir / "CLOUDPANEL_CONFIG.md"
    with open(config_guide, 'w', encoding='utf-8') as f:
        f.write("""# CloudPanel Configuration Guide

## Quick Deployment Steps

### 1. Upload Files
Upload the `backend` folder to your VPS:
```bash
scp -r backend/* root@your-vps-ip:/home/cloudpanel/htdocs/backend.unique-antique.com/
```

### 2. Run Deployment Script
```bash
ssh root@your-vps-ip
cd /path/to/uploaded/files
chmod +x deploy_to_cloudpanel.sh
./deploy_to_cloudpanel.sh
```

### 3. Configure Environment
Edit the `.env` file with your actual values:
```bash
nano /home/cloudpanel/htdocs/backend.unique-antique.com/.env
```

### 4. Create Superuser
```bash
cd /home/cloudpanel/htdocs/backend.unique-antique.com/
source venv/bin/activate
python manage.py createsuperuser
```

### 5. Test Deployment
Visit: https://backend.unique-antique.com/admin/

## CloudPanel Site Settings

### Application Settings
- **Application Type:** `Reverse Proxy`
- **Proxy URL:** `http://127.0.0.1:8000`
- **Port:** `8000`
- **Document Root:** `/home/cloudpanel/htdocs/backend.unique-antique.com`

### Service Management
```bash
# Start service
sudo systemctl start unique-antique-backend

# Stop service
sudo systemctl stop unique-antique-backend

# Restart service
sudo systemctl restart unique-antique-backend

# Check status
sudo systemctl status unique-antique-backend

# View logs
journalctl -u unique-antique-backend -f
```

## Database Setup
1. Create PostgreSQL database in CloudPanel
2. Update database credentials in `.env` file
3. Run migrations: `python manage.py migrate`

## SSL Certificate
1. Go to CloudPanel → Sites → SSL/TLS
2. Select "Let's Encrypt"
3. Add domain: `backend.unique-antique.com`
4. Create certificate

## Monitoring
- Check logs: `/home/cloudpanel/logs/backend.unique-antique.com/`
- Monitor application: CloudPanel → Sites → Monitoring
""")
    
    # Create environment template
    env_template = deploy_dir / "env_template.txt"
    with open(env_template, 'w', encoding='utf-8') as f:
        f.write("""# Copy this to .env and update with your actual values

# Django Settings
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.production

# Allowed Hosts (update with your actual domain)
ALLOWED_HOSTS=backend.unique-antique.com,unique-antique.com,your-vps-ip

# Database Settings (update with CloudPanel database credentials)
USE_POSTGRES=True
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Email Settings
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@unique-antique.com
EMAIL_HOST_PASSWORD=your-email-password
ADMIN_EMAIL=admin@unique-antique.com

# Frontend URL
FRONTEND_URL=https://unique-antique.com

# CORS Settings
CORS_ALLOWED_ORIGINS=https://unique-antique.com,https://www.unique-antique.com
CSRF_TRUSTED_ORIGINS=https://unique-antique.com,https://www.unique-antique.com,https://backend.unique-antique.com

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=dvtxfejcs
CLOUDINARY_API_KEY=717773432419483
CLOUDINARY_API_SECRET=VbPz1C7n2UqFzohKH5ZruKv33vY

# Stripe Settings (use live keys for production)
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Security Settings
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
""")
    
    print(f"✅ CloudPanel deployment package created in: {deploy_dir}")
    print(f"📁 Backend files: {backend_deploy}")
    print(f"🚀 Deployment script: {deploy_script}")
    print(f"📋 Configuration guide: {config_guide}")
    
    return deploy_dir

def main():
    """Main deployment function"""
    print("=" * 60)
    print("UNIQUE & ANTIQUE - CLOUDPANEL DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    try:
        deploy_dir = create_cloudpanel_deployment()
        
        print("\n" + "=" * 60)
        print("🎉 CLOUDPANEL DEPLOYMENT PACKAGE READY!")
        print("=" * 60)
        print(f"📁 Package location: {deploy_dir}")
        print("\nNext steps:")
        print("1. Upload the 'backend' folder to your VPS")
        print("2. Run the deployment script on your VPS")
        print("3. Configure environment variables")
        print("4. Set up database and SSL certificate")
        print("5. Test your deployment")
        print("\nSee CLOUDPANEL_CONFIG.md for detailed instructions")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating CloudPanel deployment package: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
