#!/usr/bin/env python
"""
Deployment script for Unique & Antique backend to Hostinger
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a deployment package excluding unnecessary files"""
    
    print("🚀 Creating deployment package...")
    
    # Current directory
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    # Create deployment directory
    deploy_dir = project_root / "deployment"
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
        'test_email.py',
        'deploy.py'
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
    
    # Create requirements.txt if it doesn't exist
    requirements_file = backend_deploy / "requirements.txt"
    if not requirements_file.exists():
        print("📝 Creating requirements.txt...")
        with open(requirements_file, 'w') as f:
            f.write("""Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3
Pillow==10.0.1
python-decouple==3.8
psycopg2-binary==2.9.7
redis==5.0.1
django-redis==5.4.0
celery==5.3.4
djangorestframework-simplejwt==5.3.0
stripe==7.8.0
django-colorfield==0.10.1
drf-spectacular==0.26.5
gunicorn==21.2.0
sentry-sdk==1.38.0
""")
    
    # Create deployment instructions
    instructions_file = deploy_dir / "DEPLOYMENT_INSTRUCTIONS.md"
    with open(instructions_file, 'w') as f:
        f.write("""# Deployment Instructions for Hostinger

## 1. Upload Files
Upload the entire `backend` folder to: `/domains/unique-antique.com/public_html/backend/`

## 2. SSH Commands
```bash
# Navigate to backend directory
cd domains/unique-antique.com/public_html/backend/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test the application
python manage.py runserver 0.0.0.0:8000
```

## 3. Environment Variables
Make sure to update the `.env` file with:
- Correct database credentials
- Production secret key
- Correct domain names
- Email settings

## 4. Database Setup
Create a PostgreSQL database in hPanel:
- Database name: u274375375_unique_antique
- Username: u274375375_unique_antique
- Password: [set a secure password]

## 5. Domain Configuration
Point your subdomain `backend.unique-antique.com` to the backend directory.

## 6. SSL Certificate
Enable SSL for both `unique-antique.com` and `backend.unique-antique.com` in hPanel.
""")
    
    print(f"✅ Deployment package created in: {deploy_dir}")
    print(f"📁 Backend files: {backend_deploy}")
    print(f"📋 Instructions: {instructions_file}")
    
    return deploy_dir

def main():
    """Main deployment function"""
    print("=" * 60)
    print("UNIQUE & ANTIQUE - HOSTINGER DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    try:
        deploy_dir = create_deployment_package()
        
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT PACKAGE READY!")
        print("=" * 60)
        print(f"📁 Package location: {deploy_dir}")
        print("\nNext steps:")
        print("1. Upload the 'backend' folder to Hostinger")
        print("2. Follow the instructions in DEPLOYMENT_INSTRUCTIONS.md")
        print("3. Configure your database and environment variables")
        print("4. Set up SSL certificates")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating deployment package: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
