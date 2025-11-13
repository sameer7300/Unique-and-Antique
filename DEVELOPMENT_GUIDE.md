# Development Guide - Unique and Antique E-commerce Platform

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 18+** with npm/yarn
- **PostgreSQL 13+**
- **Redis 6+**
- **Git**
- **Docker & Docker Compose** (recommended)

### Initial Setup

1. **Clone and Setup Project**
   ```bash
   git clone <repository-url>
   cd unique-antique
   ```

2. **Environment Setup**
   ```bash
   # Copy environment templates
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   
   # Edit environment variables
   # Update database credentials, API keys, etc.
   ```

3. **Docker Development (Recommended)**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop services
   docker-compose down
   ```

4. **Manual Setup (Alternative)**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   
   # Frontend setup (new terminal)
   cd frontend
   npm install
   npm run dev
   ```

## 🏗️ Development Workflow

### Branch Strategy
```
main                    # Production-ready code
├── develop            # Integration branch
├── feature/user-auth  # Feature branches
├── feature/cart-system
├── hotfix/payment-bug # Hotfix branches
└── release/v1.0       # Release branches
```

### Commit Convention
```bash
# Format: type(scope): description
feat(auth): add JWT authentication
fix(cart): resolve quantity update bug
docs(readme): update installation guide
style(frontend): format code with prettier
refactor(api): optimize product queries
test(orders): add order creation tests
chore(deps): update dependencies
```

### Development Process
1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Changes**
   ```bash
   # Backend tests
   cd backend
   python manage.py test
   
   # Frontend tests
   cd frontend
   npm run test
   
   # Integration tests
   npm run test:e2e
   ```

4. **Submit Pull Request**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   git push origin feature/your-feature-name
   ```

## 🛠️ Backend Development

### Django Project Structure
```
backend/
├── config/                 # Project configuration
├── apps/                   # Django applications
│   ├── accounts/          # User management
│   ├── products/          # Product catalog
│   ├── orders/            # Order processing
│   ├── payments/          # Payment handling
│   └── reviews/           # Reviews system
├── utils/                 # Shared utilities
├── tests/                 # Test files
└── requirements/          # Dependencies
    ├── base.txt          # Base requirements
    ├── development.txt   # Dev requirements
    └── production.txt    # Prod requirements
```

### Creating New Django App
```bash
cd backend
python manage.py startapp app_name
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset migrations (development only)
python manage.py migrate app_name zero
rm apps/app_name/migrations/00*.py
python manage.py makemigrations app_name
python manage.py migrate
```

### API Development Guidelines

#### 1. Model Creation
```python
# apps/products/models.py
from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
```

#### 2. Serializer Creation
```python
# apps/products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
```

#### 3. ViewSet Creation
```python
# apps/products/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['title', 'description']
```

### Testing Guidelines
```python
# apps/products/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title="Test Product",
            description="Test Description",
            price=99.99,
            stock=10
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.title, "Test Product")
        self.assertEqual(self.product.slug, "test-product")

class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            title="Test Product",
            description="Test Description",
            price=99.99,
            stock=10
        )
    
    def test_get_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## 🎨 Frontend Development

### Next.js Project Structure
```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── layout/       # Layout components
│   │   └── features/     # Feature-specific components
│   ├── pages/            # Next.js pages
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript types
│   └── styles/           # Styles
├── public/               # Static assets
└── tests/                # Test files
```

### Component Development Guidelines

#### 1. Component Structure
```typescript
// src/components/ProductCard.tsx
import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';

interface ProductCardProps {
  product: Product;
  onAddToCart?: (productId: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  onAddToCart 
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <Link href={`/products/${product.slug}`}>
        <div className="relative h-48">
          <Image
            src={product.image}
            alt={product.title}
            fill
            className="object-cover"
          />
        </div>
      </Link>
      
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{product.title}</h3>
        <p className="text-gray-600 mb-2">${product.price}</p>
        
        {onAddToCart && (
          <button
            onClick={() => onAddToCart(product.id)}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Add to Cart
          </button>
        )}
      </div>
    </div>
  );
};
```

#### 2. Custom Hooks
```typescript
// src/hooks/useCart.ts
import { useState, useEffect } from 'react';
import { CartItem } from '@/types/cart';
import { api } from '@/utils/api';

export const useCart = () => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);

  const addToCart = async (productId: string, quantity: number = 1) => {
    setLoading(true);
    try {
      const response = await api.post('/cart/', {
        product_id: productId,
        quantity
      });
      setItems(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId: string) => {
    setLoading(true);
    try {
      await api.delete(`/cart/${itemId}/`);
      setItems(prev => prev.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Failed to remove from cart:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    items,
    loading,
    addToCart,
    removeFromCart
  };
};
```

#### 3. API Integration
```typescript
// src/utils/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
});

// Request interceptor for auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { api };
```

### Testing Guidelines
```typescript
// src/components/__tests__/ProductCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '../ProductCard';

const mockProduct = {
  id: '1',
  title: 'Test Product',
  price: 99.99,
  image: '/test-image.jpg',
  slug: 'test-product'
};

describe('ProductCard', () => {
  it('renders product information', () => {
    render(<ProductCard product={mockProduct} />);
    
    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('$99.99')).toBeInTheDocument();
  });

  it('calls onAddToCart when button is clicked', () => {
    const mockAddToCart = jest.fn();
    render(
      <ProductCard 
        product={mockProduct} 
        onAddToCart={mockAddToCart} 
      />
    );
    
    fireEvent.click(screen.getByText('Add to Cart'));
    expect(mockAddToCart).toHaveBeenCalledWith('1');
  });
});
```

## 🧪 Testing Strategy

### Backend Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.products

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing
```bash
# Unit tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

### Test Types
1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test API endpoints and database interactions
3. **E2E Tests**: Test complete user workflows
4. **Performance Tests**: Test load and response times

## 🚀 Deployment

### Environment Configuration
```bash
# Development
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0

# Production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/db
REDIS_URL=redis://prod-redis:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Docker Deployment
```bash
# Build images
docker-compose build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f backend
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend && python manage.py test
          cd frontend && npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
```

## 📝 Code Style Guidelines

### Python (Backend)
- Follow PEP 8
- Use Black for formatting
- Use isort for imports
- Maximum line length: 88 characters

### TypeScript (Frontend)
- Use Prettier for formatting
- Use ESLint for linting
- Prefer functional components
- Use TypeScript strict mode

### Git Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

---

**Happy Coding! 🚀**

For questions or issues, please check the [FAQ](FAQ.md) or create an issue in the repository.
