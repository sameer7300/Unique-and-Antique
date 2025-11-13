# Development Setup Guide - Unique & Antique E-commerce Platform

## 🚀 Quick Start for Developers

This guide will help you set up the Unique & Antique e-commerce platform for local development. The platform consists of a Django REST API backend and a Next.js frontend with a luxury antique theme.

## 📋 Prerequisites

### Required Software
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+** (or SQLite for quick setup)
- **Redis 6+**
- **Git**

### Optional Tools
- **Docker & Docker Compose** (for containerized development)
- **VS Code** with recommended extensions
- **Postman** or **Insomnia** for API testing

## 🛠️ Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd unique-antique
```

### 2. Backend Setup (Django)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `backend/.env` with your settings:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-development-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# For PostgreSQL (optional):
# DB_NAME=unique_antique_dev
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=localhost
# DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Development)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@localhost

# Cloudinary (Image Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Stripe (Test Keys)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend URL
FRONTEND_URL=http://localhost:3000

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json

# Start development server
python manage.py runserver
```

### 5. Frontend Setup (Next.js)

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

```bash
# Start development server
npm run dev
```

## 🐳 Docker Development Setup

### 1. Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: unique_antique
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=True
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api

volumes:
  postgres_data:
```

## 🔧 Development Tools Configuration

### VS Code Extensions

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml"
  ]
}
```

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## 📊 Database Management

### PostgreSQL Setup (Optional)

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE unique_antique_dev;
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE unique_antique_dev TO dev_user;
\q
```

### Database Commands

```bash
# Reset database
python manage.py flush

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# SQL for migration
python manage.py sqlmigrate app_name migration_number
```

## 🧪 Testing Setup

### Backend Testing

```bash
# Install test dependencies
pip install pytest pytest-django factory-boy coverage

# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing

```bash
# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## 🔍 Debugging Setup

### Django Debug Toolbar

Add to `backend/requirements-dev.txt`:

```txt
django-debug-toolbar==4.2.0
```

Configure in `settings/development.py`:

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }
```

### Frontend Debugging

Install React Developer Tools browser extension and configure Next.js debugging in VS Code:

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/frontend/node_modules/.bin/next",
      "args": ["dev"],
      "cwd": "${workspaceFolder}/frontend",
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Next.js: debug client-side",
      "type": "pwa-chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

## 📧 Email Development

### Using Django Console Backend

For development, configure email backend in `settings/development.py`:

```python
# Console email backend (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Or use file backend
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

### Using MailHog (Recommended)

```bash
# Install MailHog
go install github.com/mailhog/MailHog@latest

# Or use Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Configure Django settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
```

Access MailHog web interface at http://localhost:8025

## 🚀 Development Workflow

### 1. Daily Development

```bash
# Start backend
cd backend
source venv/bin/activate
python manage.py runserver

# Start frontend (new terminal)
cd frontend
npm run dev

# Start Redis (if not using Docker)
redis-server

# Start Celery worker (new terminal)
cd backend
source venv/bin/activate
celery -A config worker -l info
```

### 2. Code Quality

```bash
# Backend code formatting
black .
isort .
flake8 .

# Frontend code formatting
npm run lint
npm run format
```

### 3. Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

## 🔧 Common Development Tasks

### Adding New Django App

```bash
# Create new app
python manage.py startapp new_app

# Add to INSTALLED_APPS in settings
# Create models, views, serializers
# Create and run migrations
python manage.py makemigrations new_app
python manage.py migrate
```

### Adding New Frontend Page

```bash
# Create page component
mkdir -p src/app/new-page
touch src/app/new-page/page.tsx

# Add to navigation if needed
# Update TypeScript types if needed
```

### Database Seeding

```bash
# Create fixture
python manage.py dumpdata app_name.ModelName --indent 2 > fixtures/model_data.json

# Load fixture
python manage.py loaddata fixtures/model_data.json
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql
   ```

3. **Redis Connection Issues**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Start Redis
   redis-server
   ```

4. **Python Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Node Modules Issues**
   ```bash
   # Clear npm cache and reinstall
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

### Log Locations

- **Django**: Console output or `logs/django.log`
- **Next.js**: Console output
- **PostgreSQL**: `/var/log/postgresql/`
- **Redis**: Console output or `/var/log/redis/`

## 📚 Useful Commands

### Django Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clear_cache

# Shell with Django context
python manage.py shell

# Database shell
python manage.py dbshell
```

### Frontend Commands

```bash
# Install new package
npm install package-name

# Update packages
npm update

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check
```

## 🎯 Development Best Practices

### Code Organization

1. **Backend**: Follow Django app structure
2. **Frontend**: Use feature-based folder structure
3. **Shared**: Keep types and utilities organized
4. **Tests**: Mirror source code structure

### Git Practices

1. **Commit Messages**: Use conventional commits
2. **Branch Naming**: `feature/`, `bugfix/`, `hotfix/`
3. **Pull Requests**: Include description and testing notes
4. **Code Review**: Required before merging

### Performance

1. **Database**: Use select_related and prefetch_related
2. **API**: Implement pagination and filtering
3. **Frontend**: Use React.memo and useMemo appropriately
4. **Images**: Optimize images and use Next.js Image component

---

*Last Updated: October 2025*
*Development Environment: Local Development*
