# Project Structure - Unique and Antique E-commerce Platform

## 📁 Complete Project Structure

```
unique-antique/
├── 📄 README.md                    # Main project documentation
├── 📄 TODO.md                      # Task tracking and roadmap
├── 📄 ARCHITECTURE.md              # System architecture documentation
├── 📄 DEVELOPMENT_GUIDE.md         # Development setup and guidelines
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
├── 📄 .gitignore                   # Git ignore rules
├── 📄 docker-compose.yml           # Development environment
├── 📄 docker-compose.prod.yml      # Production environment
├── 📄 LICENSE                      # Project license
│
├── 📁 backend/                     # Django REST API Backend
│   ├── 📄 manage.py               # Django management script
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 .env.example           # Environment variables template
│   ├── 📄 Dockerfile             # Backend Docker configuration
│   ├── 📄 pytest.ini             # Test configuration
│   │
│   ├── 📁 config/                 # Django project configuration
│   │   ├── 📄 __init__.py
│   │   ├── 📄 asgi.py            # ASGI configuration
│   │   ├── 📄 wsgi.py            # WSGI configuration
│   │   ├── 📄 urls.py            # Main URL configuration
│   │   ├── 📄 celery.py          # Celery configuration
│   │   └── 📁 settings/           # Environment-specific settings
│   │       ├── 📄 __init__.py
│   │       ├── 📄 base.py        # Base settings
│   │       ├── 📄 development.py # Development settings
│   │       ├── 📄 production.py  # Production settings
│   │       └── 📄 testing.py     # Test settings
│   │
│   ├── 📁 apps/                   # Django applications
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📁 accounts/           # User management app
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 admin.py       # Django admin configuration
│   │   │   ├── 📄 apps.py        # App configuration
│   │   │   ├── 📄 models.py      # User, Profile models
│   │   │   ├── 📄 serializers.py # DRF serializers
│   │   │   ├── 📄 views.py       # API views
│   │   │   ├── 📄 urls.py        # URL patterns
│   │   │   ├── 📄 permissions.py # Custom permissions
│   │   │   ├── 📄 signals.py     # Django signals
│   │   │   ├── 📄 managers.py    # Custom model managers
│   │   │   ├── 📁 migrations/    # Database migrations
│   │   │   └── 📁 tests/         # Test files
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 test_models.py
│   │   │       ├── 📄 test_views.py
│   │   │       └── 📄 test_serializers.py
│   │   │
│   │   ├── 📁 products/           # Product catalog app
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 admin.py
│   │   │   ├── 📄 apps.py
│   │   │   ├── 📄 models.py      # Product, Category, ProductImage
│   │   │   ├── 📄 serializers.py # Product serializers
│   │   │   ├── 📄 views.py       # Product API views
│   │   │   ├── 📄 urls.py
│   │   │   ├── 📄 filters.py     # Product filtering
│   │   │   ├── 📄 search.py      # Search functionality
│   │   │   ├── 📄 tasks.py       # Celery tasks
│   │   │   ├── 📁 migrations/
│   │   │   └── 📁 tests/
│   │   │
│   │   ├── 📁 orders/             # Order management app
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 admin.py
│   │   │   ├── 📄 apps.py
│   │   │   ├── 📄 models.py      # Order, OrderItem, TrackingHistory
│   │   │   ├── 📄 serializers.py # Order serializers
│   │   │   ├── 📄 views.py       # Order API views
│   │   │   ├── 📄 urls.py
│   │   │   ├── 📄 tasks.py       # Background tasks
│   │   │   ├── 📄 services.py    # Business logic
│   │   │   ├── 📄 utils.py       # Order utilities
│   │   │   ├── 📁 migrations/
│   │   │   └── 📁 tests/
│   │   │
│   │   ├── 📁 payments/           # Payment processing app
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 admin.py
│   │   │   ├── 📄 apps.py
│   │   │   ├── 📄 models.py      # Payment model
│   │   │   ├── 📄 serializers.py
│   │   │   ├── 📄 views.py       # Stripe integration
│   │   │   ├── 📄 urls.py
│   │   │   ├── 📄 webhooks.py    # Stripe webhooks
│   │   │   ├── 📄 services.py    # Payment services
│   │   │   ├── 📄 exceptions.py  # Payment exceptions
│   │   │   ├── 📁 migrations/
│   │   │   └── 📁 tests/
│   │   │
│   │   ├── 📁 reviews/            # Reviews and ratings app
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 admin.py
│   │   │   ├── 📄 apps.py
│   │   │   ├── 📄 models.py      # Review model
│   │   │   ├── 📄 serializers.py # Review serializers
│   │   │   ├── 📄 views.py       # Review API views
│   │   │   ├── 📄 urls.py
│   │   │   ├── 📄 permissions.py # Review permissions
│   │   │   ├── 📄 tasks.py       # Review moderation tasks
│   │   │   ├── 📁 migrations/
│   │   │   └── 📁 tests/
│   │   │
│   │   └── 📁 cart/               # Shopping cart app
│   │       ├── 📄 __init__.py
│   │       ├── 📄 admin.py
│   │       ├── 📄 apps.py
│   │       ├── 📄 models.py      # CartItem model
│   │       ├── 📄 serializers.py
│   │       ├── 📄 views.py
│   │       ├── 📄 urls.py
│   │       ├── 📄 services.py    # Cart business logic
│   │       ├── 📁 migrations/
│   │       └── 📁 tests/
│   │
│   ├── 📁 utils/                  # Shared utilities
│   │   ├── 📄 __init__.py
│   │   ├── 📄 permissions.py     # Custom permissions
│   │   ├── 📄 pagination.py      # Custom pagination
│   │   ├── 📄 exceptions.py      # Custom exceptions
│   │   ├── 📄 validators.py      # Custom validators
│   │   ├── 📄 mixins.py          # Model/View mixins
│   │   ├── 📄 decorators.py      # Custom decorators
│   │   └── 📄 helpers.py         # Helper functions
│   │
│   ├── 📁 static/                 # Static files
│   │   ├── 📁 admin/             # Admin static files
│   │   ├── 📁 css/
│   │   ├── 📁 js/
│   │   └── 📁 images/
│   │
│   ├── 📁 media/                  # User uploaded files
│   │   ├── 📁 products/          # Product images
│   │   ├── 📁 categories/        # Category images
│   │   └── 📁 users/             # User avatars
│   │
│   ├── 📁 templates/              # Django templates
│   │   ├── 📁 admin/             # Admin templates
│   │   ├── 📁 emails/            # Email templates
│   │   └── 📁 errors/            # Error pages
│   │
│   ├── 📁 locale/                 # Internationalization
│   │   ├── 📁 en/
│   │   └── 📁 es/
│   │
│   └── 📁 tests/                  # Integration tests
│       ├── 📄 __init__.py
│       ├── 📄 test_api.py        # API integration tests
│       ├── 📄 test_auth.py       # Authentication tests
│       └── 📄 fixtures.py        # Test fixtures
│
├── 📁 frontend/                   # Next.js Frontend Application
│   ├── 📄 package.json           # Node.js dependencies
│   ├── 📄 package-lock.json      # Dependency lock file
│   ├── 📄 next.config.js         # Next.js configuration
│   ├── 📄 tailwind.config.js     # Tailwind CSS configuration
│   ├── 📄 tsconfig.json          # TypeScript configuration
│   ├── 📄 .env.example           # Environment variables template
│   ├── 📄 Dockerfile             # Frontend Docker configuration
│   ├── 📄 .eslintrc.json         # ESLint configuration
│   ├── 📄 .prettierrc            # Prettier configuration
│   ├── 📄 jest.config.js         # Jest test configuration
│   │
│   ├── 📁 public/                # Static assets
│   │   ├── 📄 favicon.ico
│   │   ├── 📄 logo.png
│   │   ├── 📁 images/            # Static images
│   │   └── 📁 icons/             # Icon files
│   │
│   ├── 📁 src/                   # Source code
│   │   ├── 📁 components/        # Reusable UI components
│   │   │   ├── 📁 ui/            # shadcn/ui components
│   │   │   │   ├── 📄 button.tsx
│   │   │   │   ├── 📄 input.tsx
│   │   │   │   ├── 📄 card.tsx
│   │   │   │   └── 📄 dialog.tsx
│   │   │   │
│   │   │   ├── 📁 layout/        # Layout components
│   │   │   │   ├── 📄 Header.tsx
│   │   │   │   ├── 📄 Footer.tsx
│   │   │   │   ├── 📄 Navigation.tsx
│   │   │   │   └── 📄 Layout.tsx
│   │   │   │
│   │   │   ├── 📁 product/       # Product-related components
│   │   │   │   ├── 📄 ProductCard.tsx
│   │   │   │   ├── 📄 ProductGrid.tsx
│   │   │   │   ├── 📄 ProductDetail.tsx
│   │   │   │   ├── 📄 ProductFilters.tsx
│   │   │   │   └── 📄 ProductSearch.tsx
│   │   │   │
│   │   │   ├── 📁 cart/          # Cart components
│   │   │   │   ├── 📄 CartItem.tsx
│   │   │   │   ├── 📄 CartSummary.tsx
│   │   │   │   └── 📄 CartDrawer.tsx
│   │   │   │
│   │   │   ├── 📁 auth/          # Authentication components
│   │   │   │   ├── 📄 LoginForm.tsx
│   │   │   │   ├── 📄 RegisterForm.tsx
│   │   │   │   └── 📄 ProtectedRoute.tsx
│   │   │   │
│   │   │   ├── 📁 order/         # Order components
│   │   │   │   ├── 📄 OrderSummary.tsx
│   │   │   │   ├── 📄 OrderTracking.tsx
│   │   │   │   └── 📄 OrderHistory.tsx
│   │   │   │
│   │   │   ├── 📁 admin/         # Admin components
│   │   │   │   ├── 📄 AdminLayout.tsx
│   │   │   │   ├── 📄 ProductManager.tsx
│   │   │   │   ├── 📄 OrderManager.tsx
│   │   │   │   └── 📄 Dashboard.tsx
│   │   │   │
│   │   │   └── 📁 common/        # Common components
│   │   │       ├── 📄 Loading.tsx
│   │   │       ├── 📄 ErrorBoundary.tsx
│   │   │       ├── 📄 Pagination.tsx
│   │   │       └── 📄 Modal.tsx
│   │   │
│   │   ├── 📁 pages/             # Next.js pages
│   │   │   ├── 📄 _app.tsx       # App component
│   │   │   ├── 📄 _document.tsx  # Document component
│   │   │   ├── 📄 index.tsx      # Homepage
│   │   │   ├── 📄 login.tsx      # Login page
│   │   │   ├── 📄 register.tsx   # Register page
│   │   │   ├── 📄 cart.tsx       # Shopping cart
│   │   │   ├── 📄 checkout.tsx   # Checkout page
│   │   │   │
│   │   │   ├── 📁 products/      # Product pages
│   │   │   │   ├── 📄 index.tsx  # Product listing
│   │   │   │   └── 📄 [slug].tsx # Product detail
│   │   │   │
│   │   │   ├── 📁 account/       # User account pages
│   │   │   │   ├── 📄 index.tsx  # Account dashboard
│   │   │   │   ├── 📄 profile.tsx # User profile
│   │   │   │   └── 📄 orders.tsx # Order history
│   │   │   │
│   │   │   ├── 📁 orders/        # Order pages
│   │   │   │   └── 📄 [id].tsx   # Order detail
│   │   │   │
│   │   │   ├── 📁 admin/         # Admin pages
│   │   │   │   ├── 📄 index.tsx  # Admin dashboard
│   │   │   │   ├── 📄 products.tsx # Product management
│   │   │   │   ├── 📄 orders.tsx # Order management
│   │   │   │   └── 📄 users.tsx  # User management
│   │   │   │
│   │   │   └── 📁 api/           # API routes (if needed)
│   │   │       └── 📄 hello.ts   # Example API route
│   │   │
│   │   ├── 📁 hooks/             # Custom React hooks
│   │   │   ├── 📄 useAuth.ts     # Authentication hook
│   │   │   ├── 📄 useCart.ts     # Cart management hook
│   │   │   ├── 📄 useApi.ts      # API interaction hook
│   │   │   ├── 📄 useLocalStorage.ts # Local storage hook
│   │   │   └── 📄 useDebounce.ts # Debounce hook
│   │   │
│   │   ├── 📁 utils/             # Utility functions
│   │   │   ├── 📄 api.ts         # API client configuration
│   │   │   ├── 📄 auth.ts        # Authentication utilities
│   │   │   ├── 📄 helpers.ts     # General helper functions
│   │   │   ├── 📄 constants.ts   # Application constants
│   │   │   ├── 📄 formatters.ts  # Data formatting functions
│   │   │   └── 📄 validators.ts  # Form validation functions
│   │   │
│   │   ├── 📁 types/             # TypeScript type definitions
│   │   │   ├── 📄 index.ts       # Common types
│   │   │   ├── 📄 user.ts        # User-related types
│   │   │   ├── 📄 product.ts     # Product-related types
│   │   │   ├── 📄 order.ts       # Order-related types
│   │   │   ├── 📄 cart.ts        # Cart-related types
│   │   │   └── 📄 api.ts         # API response types
│   │   │
│   │   ├── 📁 contexts/          # React contexts
│   │   │   ├── 📄 AuthContext.tsx # Authentication context
│   │   │   ├── 📄 CartContext.tsx # Cart context
│   │   │   └── 📄 ThemeContext.tsx # Theme context
│   │   │
│   │   ├── 📁 lib/               # Library configurations
│   │   │   ├── 📄 stripe.ts      # Stripe configuration
│   │   │   ├── 📄 axios.ts       # Axios configuration
│   │   │   └── 📄 utils.ts       # shadcn/ui utils
│   │   │
│   │   └── 📁 styles/            # Styles
│   │       ├── 📄 globals.css    # Global styles
│   │       └── 📄 components.css # Component styles
│   │
│   └── 📁 __tests__/             # Test files
│       ├── 📄 setup.ts           # Test setup
│       ├── 📁 components/        # Component tests
│       ├── 📁 pages/             # Page tests
│       ├── 📁 hooks/             # Hook tests
│       └── 📁 utils/             # Utility tests
│
├── 📁 docs/                      # Additional documentation
│   ├── 📄 API.md                # API documentation
│   ├── 📄 DEPLOYMENT.md         # Deployment guide
│   ├── 📄 TESTING.md            # Testing guide
│   ├── 📄 CONTRIBUTING.md       # Contribution guidelines
│   ├── 📄 CHANGELOG.md          # Version changelog
│   └── 📁 images/               # Documentation images
│
├── 📁 scripts/                   # Utility scripts
│   ├── 📄 setup.sh              # Project setup script
│   ├── 📄 deploy.sh             # Deployment script
│   ├── 📄 backup.sh             # Database backup script
│   └── 📄 seed_data.py          # Database seeding script
│
├── 📁 .github/                   # GitHub configuration
│   ├── 📁 workflows/            # GitHub Actions
│   │   ├── 📄 ci.yml            # Continuous Integration
│   │   ├── 📄 deploy.yml        # Deployment workflow
│   │   └── 📄 test.yml          # Testing workflow
│   ├── 📄 ISSUE_TEMPLATE.md     # Issue template
│   └── 📄 PULL_REQUEST_TEMPLATE.md # PR template
│
└── 📁 infrastructure/            # Infrastructure as Code
    ├── 📁 terraform/            # Terraform configurations
    ├── 📁 kubernetes/           # Kubernetes manifests
    └── 📁 docker/               # Docker configurations
```

## 📋 File Naming Conventions

### Backend (Python/Django)
- **Models**: `PascalCase` (e.g., `ProductCategory`)
- **Files**: `snake_case` (e.g., `product_views.py`)
- **Functions**: `snake_case` (e.g., `get_product_list`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_UPLOAD_SIZE`)

### Frontend (TypeScript/React)
- **Components**: `PascalCase` (e.g., `ProductCard.tsx`)
- **Files**: `camelCase` or `PascalCase` for components
- **Functions**: `camelCase` (e.g., `handleAddToCart`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

## 🎯 Key Directories Explained

### Backend Structure
- **`config/`**: Django project configuration and settings
- **`apps/`**: Feature-based Django applications
- **`utils/`**: Shared utilities and helper functions
- **`static/`**: Static files (CSS, JS, images)
- **`media/`**: User-uploaded files
- **`templates/`**: Django HTML templates

### Frontend Structure
- **`components/`**: Reusable UI components organized by feature
- **`pages/`**: Next.js pages with file-based routing
- **`hooks/`**: Custom React hooks for state management
- **`utils/`**: Utility functions and configurations
- **`types/`**: TypeScript type definitions
- **`contexts/`**: React context providers

## 🔧 Configuration Files

### Root Level
- **`docker-compose.yml`**: Development environment setup
- **`docker-compose.prod.yml`**: Production environment setup
- **`.gitignore`**: Git ignore patterns
- **`LICENSE`**: Project license

### Backend Configuration
- **`requirements.txt`**: Python dependencies
- **`pytest.ini`**: Test configuration
- **`.env.example`**: Environment variables template

### Frontend Configuration
- **`package.json`**: Node.js dependencies and scripts
- **`next.config.js`**: Next.js configuration
- **`tailwind.config.js`**: Tailwind CSS configuration
- **`tsconfig.json`**: TypeScript configuration
- **`jest.config.js`**: Jest testing configuration

## 📊 Development Workflow

### 1. Feature Development
```
1. Create feature branch from develop
2. Implement backend models/serializers/views
3. Create frontend components/pages
4. Write tests for both backend and frontend
5. Update documentation
6. Submit pull request
```

### 2. File Organization
- Group related files together
- Use consistent naming conventions
- Keep components small and focused
- Separate business logic from UI components

### 3. Import Organization
```typescript
// External libraries
import React from 'react';
import { NextPage } from 'next';

// Internal utilities
import { api } from '@/utils/api';
import { formatPrice } from '@/utils/formatters';

// Components
import { ProductCard } from '@/components/product/ProductCard';
import { Layout } from '@/components/layout/Layout';

// Types
import { Product } from '@/types/product';
```

## 🚀 Getting Started

1. **Clone the repository**
2. **Follow the structure** when adding new files
3. **Use the naming conventions** consistently
4. **Update documentation** when making structural changes
5. **Run tests** to ensure everything works

This structure provides a solid foundation for a scalable, maintainable e-commerce platform with clear separation of concerns and organized code architecture.

---

**Last Updated**: 2025-10-02
**Next Review**: When adding new major features
