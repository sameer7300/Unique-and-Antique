# Deployment Guide - Unique & Antique E-commerce Platform

## 🚀 Production Deployment Overview

This guide covers deploying the Unique & Antique e-commerce platform to production environments with proper security, scalability, and monitoring.

## 📋 Prerequisites

### System Requirements
- **Server**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 50GB+ SSD
- **CPU**: 2+ cores
- **Network**: Static IP with SSL certificate

### Required Services
- **PostgreSQL 13+**: Primary database
- **Redis 6+**: Caching and sessions
- **Nginx**: Reverse proxy and static files
- **Supervisor**: Process management
- **Certbot**: SSL certificates

## 🔧 Backend Deployment (Django)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip postgresql postgresql-contrib redis-server nginx supervisor git

# Create application user
sudo adduser --system --group --home /opt/unique-antique uniqueantique
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE unique_antique;
CREATE USER unique_antique_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE unique_antique TO unique_antique_user;
ALTER USER unique_antique_user CREATEDB;
\q
```

### 3. Application Deployment

```bash
# Switch to app user
sudo -u uniqueantique -i

# Clone repository
git clone <repository-url> /opt/unique-antique/app
cd /opt/unique-antique/app/backend

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create production environment file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=unique_antique
DB_USER=unique_antique_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
ADMIN_EMAIL=admin@yourdomain.com
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Gunicorn Configuration

```bash
# Create Gunicorn configuration
sudo tee /opt/unique-antique/gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "uniqueantique"
group = "uniqueantique"
tmp_upload_dir = None
errorlog = "/opt/unique-antique/logs/gunicorn_error.log"
accesslog = "/opt/unique-antique/logs/gunicorn_access.log"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
EOF

# Create logs directory
sudo mkdir -p /opt/unique-antique/logs
sudo chown uniqueantique:uniqueantique /opt/unique-antique/logs
```

### 5. Supervisor Configuration

```bash
# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/unique-antique.conf << EOF
[program:unique-antique]
command=/opt/unique-antique/app/backend/venv/bin/gunicorn config.wsgi:application -c /opt/unique-antique/gunicorn.conf.py
directory=/opt/unique-antique/app/backend
user=uniqueantique
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/unique-antique/logs/supervisor.log
environment=PATH="/opt/unique-antique/app/backend/venv/bin"

[program:unique-antique-celery]
command=/opt/unique-antique/app/backend/venv/bin/celery -A config worker -l info
directory=/opt/unique-antique/app/backend
user=uniqueantique
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/unique-antique/logs/celery.log
environment=PATH="/opt/unique-antique/app/backend/venv/bin"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start unique-antique
sudo supervisorctl start unique-antique-celery
```

## 🌐 Frontend Deployment (Next.js)

### 1. Build Application

```bash
# On development machine or CI/CD
cd frontend
npm install
npm run build

# Upload build to server
rsync -avz .next/ user@server:/opt/unique-antique/frontend/.next/
rsync -avz public/ user@server:/opt/unique-antique/frontend/public/
rsync -avz package.json user@server:/opt/unique-antique/frontend/
```

### 2. Server Setup

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Setup frontend
sudo mkdir -p /opt/unique-antique/frontend
sudo chown uniqueantique:uniqueantique /opt/unique-antique/frontend

# Switch to app user
sudo -u uniqueantique -i
cd /opt/unique-antique/frontend

# Install production dependencies
npm ci --only=production

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
EOF
```

### 3. PM2 Configuration

```bash
# Install PM2
sudo npm install -g pm2

# Create PM2 configuration
sudo -u uniqueantique tee /opt/unique-antique/frontend/ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'unique-antique-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/opt/unique-antique/frontend',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: '/opt/unique-antique/logs/frontend-error.log',
    out_file: '/opt/unique-antique/logs/frontend-out.log',
    log_file: '/opt/unique-antique/logs/frontend.log'
  }]
}
EOF

# Start application
sudo -u uniqueantique pm2 start /opt/unique-antique/frontend/ecosystem.config.js
sudo -u uniqueantique pm2 save
sudo pm2 startup
```

## 🔒 Nginx Configuration

### 1. SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 2. Nginx Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/unique-antique << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=auth:10m rate=5r/s;

# Upstream servers
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

# Main server block
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Auth routes (stricter rate limiting)
    location /api/auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Admin routes
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /opt/unique-antique/app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/unique-antique/app/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Frontend application
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/unique-antique /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring & Logging

### 1. Log Rotation

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/unique-antique << EOF
/opt/unique-antique/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 uniqueantique uniqueantique
    postrotate
        supervisorctl restart unique-antique
        pm2 reload unique-antique-frontend
    endscript
}
EOF
```

### 2. Health Checks

```bash
# Create health check script
sudo tee /opt/unique-antique/health-check.sh << EOF
#!/bin/bash

# Check backend
if ! curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo "Backend health check failed"
    supervisorctl restart unique-antique
fi

# Check frontend
if ! curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "Frontend health check failed"
    pm2 reload unique-antique-frontend
fi

# Check database
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Database health check failed"
fi

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis health check failed"
fi
EOF

sudo chmod +x /opt/unique-antique/health-check.sh

# Add to crontab
echo "*/5 * * * * /opt/unique-antique/health-check.sh" | sudo crontab -u uniqueantique -
```

## 🔄 Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo tee /opt/unique-antique/backup-db.sh << EOF
#!/bin/bash
BACKUP_DIR="/opt/unique-antique/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# Database backup
pg_dump -h localhost -U unique_antique_user unique_antique | gzip > \$BACKUP_DIR/db_\$DATE.sql.gz

# Media files backup
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz -C /opt/unique-antique/app/backend media/

# Keep only last 30 days
find \$BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

sudo chmod +x /opt/unique-antique/backup-db.sh

# Schedule daily backups
echo "0 2 * * * /opt/unique-antique/backup-db.sh" | sudo crontab -u uniqueantique -
```

## 🚀 Deployment Automation

### 1. Deployment Script

```bash
# Create deployment script
sudo tee /opt/unique-antique/deploy.sh << EOF
#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest code
cd /opt/unique-antique/app
git pull origin main

# Backend deployment
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Frontend deployment
cd ../frontend
npm ci --only=production
npm run build

# Restart services
supervisorctl restart unique-antique
supervisorctl restart unique-antique-celery
pm2 reload unique-antique-frontend

echo "Deployment completed successfully!"
EOF

sudo chmod +x /opt/unique-antique/deploy.sh
```

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Fail2Ban Configuration

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure Fail2Ban
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql unique_antique

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_products_category ON products_product(category_id);
CREATE INDEX CONCURRENTLY idx_products_brand ON products_product(brand_id);
CREATE INDEX CONCURRENTLY idx_orders_user ON orders_order(user_id);
CREATE INDEX CONCURRENTLY idx_orders_status ON orders_order(status);
CREATE INDEX CONCURRENTLY idx_reviews_product ON reviews_review(product_id);

-- Analyze tables
ANALYZE;
```

### 2. Redis Configuration

```bash
# Optimize Redis configuration
sudo tee -a /etc/redis/redis.conf << EOF
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF

sudo systemctl restart redis-server
```

## 🔍 Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Gunicorn is running: `supervisorctl status`
   - Check logs: `tail -f /opt/unique-antique/logs/gunicorn_error.log`

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env`

3. **Static Files Not Loading**
   - Run: `python manage.py collectstatic --noinput`
   - Check Nginx configuration

4. **SSL Certificate Issues**
   - Renew certificate: `sudo certbot renew`
   - Check certificate status: `sudo certbot certificates`

### Log Locations

- **Nginx**: `/var/log/nginx/`
- **Gunicorn**: `/opt/unique-antique/logs/gunicorn_*.log`
- **Supervisor**: `/opt/unique-antique/logs/supervisor.log`
- **Frontend**: `/opt/unique-antique/logs/frontend*.log`
- **Celery**: `/opt/unique-antique/logs/celery.log`

---

*Last Updated: October 2025*
