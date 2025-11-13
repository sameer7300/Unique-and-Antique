# CloudPanel Deployment Guide - Unique & Antique Backend

## Overview
This guide will help you deploy the Unique & Antique Django backend to Hostinger VPS using CloudPanel dashboard.

**Target Domain:** `backend.unique-antique.com`

## Prerequisites

### 1. Hostinger VPS Setup
- ✅ Hostinger VPS with CloudPanel installed
- ✅ Domain `unique-antique.com` pointed to your VPS IP
- ✅ SSH access to your VPS
- ✅ CloudPanel dashboard access

### 2. Required Information
- **VPS IP Address:** Your Hostinger VPS IP
- **Domain:** `backend.unique-antique.com`
- **Database:** PostgreSQL
- **Python Version:** 3.9+

## Step 1: CloudPanel Initial Setup

### 1.1 Access CloudPanel Dashboard
```
https://your-vps-ip:8443
```

### 1.2 Create Site in CloudPanel
1. **Login to CloudPanel**
2. **Go to Sites → Add Site**
3. **Site Configuration:**
   - **Site Name:** `backend.unique-antique.com`
   - **Site Type:** `Python`
   - **Python Version:** `3.9` or higher
   - **Document Root:** `/home/cloudpanel/htdocs/backend.unique-antique.com`

### 1.3 SSL Certificate Setup
1. **Go to Sites → SSL/TLS**
2. **Select:** `Let's Encrypt`
3. **Domain:** `backend.unique-antique.com`
4. **Click:** `Create Certificate`

## Step 2: Database Setup

### 2.1 Create PostgreSQL Database
1. **Go to Databases → Add Database**
2. **Database Configuration:**
   - **Database Name:** `unique_antique`
   - **Database User:** `unique_antique_user`
   - **Password:** `[Generate Strong Password]`
   - **Database Type:** `PostgreSQL`

### 2.2 Note Database Credentials
```
DB_NAME=unique_antique
DB_USER=unique_antique_user
DB_PASSWORD=[your-generated-password]
DB_HOST=localhost
DB_PORT=5432
```

## Step 3: File Upload and Setup

### 3.1 Upload Backend Files
**Option A: Using CloudPanel File Manager**
1. Go to **Files → File Manager**
2. Navigate to `/home/cloudpanel/htdocs/backend.unique-antique.com/`
3. Upload the entire `deployment/backend/` folder contents

**Option B: Using SSH/SCP**
```bash
# From your local machine
scp -r deployment/backend/* root@your-vps-ip:/home/cloudpanel/htdocs/backend.unique-antique.com/
```

### 3.2 Set Correct Permissions
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Set permissions
chown -R cloudpanel:cloudpanel /home/cloudpanel/htdocs/backend.unique-antique.com/
chmod -R 755 /home/cloudpanel/htdocs/backend.unique-antique.com/
```

## Step 4: Python Environment Setup

### 4.1 SSH into VPS and Setup Virtual Environment
```bash
# SSH into VPS
ssh root@your-vps-ip

# Navigate to site directory
cd /home/cloudpanel/htdocs/backend.unique-antique.com/

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4.2 Install Additional System Dependencies
```bash
# Install system packages
apt update
apt install -y python3-dev postgresql-server-dev-all build-essential

# Install Python packages that might need compilation
pip install psycopg2-binary pillow
```

## Step 5: Environment Configuration

### 5.1 Update Environment Variables
```bash
# Edit the .env file
nano .env
```

**Update with your actual values:**
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.production

# Allowed Hosts
ALLOWED_HOSTS=backend.unique-antique.com,unique-antique.com,your-vps-ip,localhost,127.0.0.1

# Database Settings
USE_POSTGRES=True
DB_NAME=unique_antique
DB_USER=unique_antique_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings (if available)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/2

# Email Settings (Hostinger SMTP)
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@unique-antique.com
EMAIL_HOST_PASSWORD=your-email-password
ADMIN_EMAIL=admin@unique-antique.com

# Frontend URL
FRONTEND_URL=https://unique-antique.com

# CORS Settings
CORS_ALLOWED_ORIGINS=https://unique-antique.com,https://www.unique-antique.com,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://unique-antique.com,https://www.unique-antique.com,https://backend.unique-antique.com

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=dvtxfejcs
CLOUDINARY_API_KEY=717773432419483
CLOUDINARY_API_SECRET=VbPz1C7n2UqFzohKH5ZruKv33vY

# Stripe Settings
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

## Step 6: Django Setup

### 6.1 Run Django Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test the setup
python manage.py check --deploy
```

### 6.2 Run Production Setup Script
```bash
# Run the production setup script
python setup_production.py
```

## Step 7: CloudPanel Application Configuration

### 7.1 Configure Python Application in CloudPanel
1. **Go to Sites → Add Site**
2. **Site Configuration:**
   - **Site Name:** `backend.unique-antique.com`
   - **Site Type:** `Python`
   - **Python Version:** `3.9` or higher
   - **Document Root:** `/home/cloudpanel/htdocs/backend.unique-antique.com`

### 7.2 Setup Gunicorn Service
```bash
# Make start script executable
chmod +x /home/cloudpanel/htdocs/backend.unique-antique.com/start_server.sh

# Create systemd service
sudo cp /home/cloudpanel/htdocs/backend.unique-antique.com/systemd_service.conf /etc/systemd/system/unique-antique-backend.service

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable unique-antique-backend
sudo systemctl start unique-antique-backend

# Check service status
sudo systemctl status unique-antique-backend
```

### 7.3 Configure CloudPanel Site Settings
1. **Go to Sites → backend.unique-antique.com → Settings**
2. **Application Settings:**
   - **Application Type:** `Reverse Proxy`
   - **Proxy URL:** `http://127.0.0.1:8000`
   - **Port:** `8000`

### 7.4 Update Nginx Configuration
The vhost configuration you provided is perfect for this setup. It will:
- Proxy requests to Gunicorn on port 8000
- Handle static files directly
- Provide SSL termination
- Set proper headers for Django

## Step 8: Nginx Configuration (Optional)

### 8.1 Custom Nginx Configuration
If you need custom Nginx settings, create:
```bash
nano /home/cloudpanel/htdocs/backend.unique-antique.com/.htaccess
```

**Add:**
```apache
# Django static files
RewriteEngine On
RewriteRule ^static/(.*)$ /static/$1 [L]
RewriteRule ^media/(.*)$ /media/$1 [L]

# API routes
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ passenger_wsgi.py [L]
```

## Step 9: Testing and Verification

### 9.1 Test Application
```bash
# Test Django application
cd /home/cloudpanel/htdocs/backend.unique-antique.com/
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 9.2 Test API Endpoints
```bash
# Test API health
curl https://backend.unique-antique.com/api/health/

# Test admin access
curl https://backend.unique-antique.com/admin/

# Test API documentation
curl https://backend.unique-antique.com/api/docs/
```

### 9.3 Check Logs
```bash
# Check CloudPanel logs
tail -f /home/cloudpanel/logs/backend.unique-antique.com/error.log
tail -f /home/cloudpanel/logs/backend.unique-antique.com/access.log

# Check Django logs (if configured)
tail -f /home/cloudpanel/htdocs/backend.unique-antique.com/logs/django.log
```

## Step 10: Post-Deployment Configuration

### 10.1 Setup Monitoring
1. **CloudPanel Monitoring**
   - Enable site monitoring in CloudPanel
   - Set up email alerts for downtime

2. **Application Monitoring**
   - Configure Sentry for error tracking
   - Set up log rotation

### 10.2 Backup Configuration
1. **Database Backups**
   - Configure automated PostgreSQL backups
   - Set up CloudPanel backup schedules

2. **File Backups**
   - Configure application file backups
   - Set up media file backups (Cloudinary handles this)

### 10.3 Security Hardening
```bash
# Update system packages
apt update && apt upgrade -y

# Configure firewall (if not done)
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 8443
ufw enable

# Set up fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

## Step 11: Domain and DNS Configuration

### 11.1 DNS Settings
Configure these DNS records in your domain provider:
```
Type    Name        Value               TTL
A       backend     your-vps-ip         300
CNAME   www         unique-antique.com  300
```

### 11.2 SSL Certificate Verification
```bash
# Check SSL certificate
openssl s_client -connect backend.unique-antique.com:443 -servername backend.unique-antique.com
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Not Starting
```bash
# Check Python path
which python3
/home/cloudpanel/htdocs/backend.unique-antique.com/venv/bin/python --version

# Check WSGI file
python3 /home/cloudpanel/htdocs/backend.unique-antique.com/passenger_wsgi.py
```

#### 2. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U unique_antique_user -d unique_antique

# Check PostgreSQL status
systemctl status postgresql
```

#### 3. Static Files Not Loading
```bash
# Recollect static files
cd /home/cloudpanel/htdocs/backend.unique-antique.com/
source venv/bin/activate
python manage.py collectstatic --clear --noinput
```

#### 4. Permission Issues
```bash
# Fix permissions
chown -R cloudpanel:cloudpanel /home/cloudpanel/htdocs/backend.unique-antique.com/
chmod -R 755 /home/cloudpanel/htdocs/backend.unique-antique.com/
chmod +x /home/cloudpanel/htdocs/backend.unique-antique.com/passenger_wsgi.py
```

## Maintenance Commands

### Regular Maintenance
```bash
# Update dependencies
cd /home/cloudpanel/htdocs/backend.unique-antique.com/
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Database maintenance
python manage.py migrate
python manage.py collectstatic --noinput

# Clear cache (if using Redis)
redis-cli flushall

# Restart application
touch /home/cloudpanel/htdocs/backend.unique-antique.com/tmp/restart.txt
```

### Log Monitoring
```bash
# Monitor application logs
tail -f /home/cloudpanel/logs/backend.unique-antique.com/error.log

# Monitor system logs
journalctl -f -u nginx
journalctl -f -u postgresql
```

## Success Verification

After successful deployment, you should be able to access:

- ✅ **API Documentation:** `https://backend.unique-antique.com/api/docs/`
- ✅ **Admin Panel:** `https://backend.unique-antique.com/admin/`
- ✅ **API Health Check:** `https://backend.unique-antique.com/api/health/`
- ✅ **Static Files:** `https://backend.unique-antique.com/static/`

## Next Steps

1. **Frontend Deployment:** Deploy the Next.js frontend
2. **Domain Configuration:** Point `unique-antique.com` to frontend
3. **Email Testing:** Test contact and review email functionality
4. **Payment Testing:** Test Stripe integration
5. **Performance Optimization:** Configure caching and CDN

Your Unique & Antique backend is now successfully deployed on Hostinger VPS using CloudPanel! 🎉
