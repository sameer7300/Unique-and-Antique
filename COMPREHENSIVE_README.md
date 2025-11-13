# Unique & Antique - E-commerce Platform

## 🏛️ Project Overview

**Unique & Antique** is a sophisticated, full-stack e-commerce platform specializing in antiques, vintage items, and unique collectibles. Built with modern web technologies, it provides a luxury shopping experience with comprehensive features for both customers and administrators.

### 🎯 Key Features

- **🛍️ Complete E-commerce Solution**: Product catalog, shopping cart, checkout, order management
- **👤 Advanced User Management**: Custom authentication, profiles, addresses, preferences
- **💳 Payment Processing**: Stripe integration with multiple payment methods
- **📦 Order Lifecycle**: Complete order tracking from placement to delivery
- **⭐ Review System**: Customer reviews with ratings, images, and moderation
- **📧 Email Notifications**: Automated emails for orders, status changes, newsletters
- **📱 Responsive Design**: Mobile-first luxury antique theme
- **🔐 Security**: JWT authentication, CSRF protection, input validation
- **📊 Admin Dashboard**: Comprehensive admin interface with analytics

## 🏗️ Architecture Overview

### Technology Stack

#### Backend (Django REST API)
- **Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: PostgreSQL with Redis caching
- **Authentication**: JWT with refresh tokens
- **File Storage**: Cloudinary for images
- **Email**: SMTP with professional templates
- **Background Tasks**: Celery with Redis broker
- **Payment**: Stripe integration
- **Admin**: Enhanced Django Admin with Jazzmin theme

#### Frontend (Next.js)
- **Framework**: Next.js 15.5.4 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS 4 + shadcn/ui components
- **Animations**: Framer Motion + GSAP
- **State Management**: React Context + custom hooks
- **HTTP Client**: Axios with interceptors
- **Theme**: Luxury antique design system

### Project Structure

```
unique-antique/
├── 📁 backend/                     # Django REST API
│   ├── 📁 apps/                    # Django applications
│   │   ├── 📁 accounts/           # User management & authentication
│   │   ├── 📁 products/           # Product catalog & management
│   │   ├── 📁 orders/             # Order processing & tracking
│   │   ├── 📁 payments/           # Payment processing (Stripe)
│   │   ├── 📁 reviews/            # Review & rating system
│   │   ├── 📁 cart/               # Shopping cart management
│   │   ├── 📁 contact/            # Contact form & messaging
│   │   ├── 📁 newsletter/         # Newsletter subscriptions
│   │   └── 📁 settings/           # Site configuration
│   ├── 📁 config/                 # Django configuration
│   ├── 📁 templates/              # Email & admin templates
│   ├── 📁 static/                 # Static files
│   └── 📁 media/                  # User uploads
├── 📁 frontend/                   # Next.js application
│   ├── 📁 src/
│   │   ├── 📁 app/               # Next.js App Router pages
│   │   ├── 📁 components/        # Reusable UI components
│   │   ├── 📁 contexts/          # React Context providers
│   │   └── 📁 lib/               # Utilities & API client
│   └── 📁 public/                # Static assets
└── 📁 docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+**
- **Redis 6+**
- **Git**

### 1. Clone Repository

```bash
git clone <repository-url>
cd unique-antique
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Environment setup
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs

## 📊 Database Schema

### Core Models

#### User Management
- **User**: Custom user model with roles, 2FA, verification
- **Profile**: Extended user information (bio, avatar, preferences)
- **Address**: Multiple addresses per user (shipping/billing)

#### Product Catalog
- **Category**: Hierarchical product categories
- **Brand**: Product brands with logos and descriptions
- **Product**: Main product model with variants and images
- **ProductImage**: Multiple images per product
- **ProductVariant**: Product variations (size, color, etc.)

#### Order Management
- **Order**: Complete order information and status tracking
- **OrderItem**: Individual items within orders
- **OrderStatusHistory**: Status change tracking with timestamps

#### Reviews & Ratings
- **Review**: Customer reviews with ratings and images
- **ReviewImage**: Multiple images per review
- **ReviewHelpfulness**: Review voting system

#### Shopping Cart
- **Cart**: User shopping carts
- **CartItem**: Items in shopping carts
- **SavedItem**: Wishlist functionality

#### Communication
- **ContactMessage**: Customer inquiries and support
- **NewsletterSubscriber**: Email newsletter subscriptions
- **Newsletter**: Newsletter campaigns and tracking

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=unique_antique
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@unique-antique.com
EMAIL_HOST_PASSWORD=your-email-password
ADMIN_EMAIL=info@unique-antique.com

# Cloudinary (Image Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Stripe Payment
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 🎨 Design System

### Color Palette
- **Primary**: Emerald Green (#10b981)
- **Secondary**: Antique Gold (#d4af37)
- **Accent**: Copper (#b87333)
- **Neutral**: Gray scale for backgrounds and text

### Typography
- **Headings**: Playfair Display (serif) for luxury feel
- **Body**: Inter (sans-serif) for readability
- **Code**: JetBrains Mono for technical content

### Components
- **shadcn/ui**: Base component library
- **Custom Components**: Luxury-themed extensions
- **Animations**: Framer Motion for smooth interactions
- **Icons**: Lucide React for consistent iconography

## 📱 Features Deep Dive

### User Authentication
- **JWT-based**: Secure token authentication with refresh
- **Email Verification**: Required for account activation
- **Two-Factor Authentication**: TOTP support with backup codes
- **Password Reset**: Secure password recovery flow
- **Role-based Access**: Customer, Staff, Admin roles

### Product Management
- **Rich Product Data**: Detailed specifications, care instructions
- **Image Management**: Multiple images with Cloudinary storage
- **Inventory Tracking**: Stock levels and low stock alerts
- **Categories & Brands**: Hierarchical organization
- **Search & Filtering**: Advanced product discovery

### Order Processing
- **Complete Lifecycle**: From cart to delivery tracking
- **Payment Integration**: Stripe for secure payments
- **Email Notifications**: Automated customer and admin alerts
- **Status Tracking**: Real-time order status updates
- **Invoice Generation**: Professional PDF invoices

### Review System
- **Verified Purchases**: Reviews linked to actual purchases
- **Image Support**: Customers can upload review images
- **Moderation**: Admin approval workflow
- **Helpfulness Voting**: Community-driven review quality

### Admin Dashboard
- **Enhanced Interface**: Jazzmin theme with custom styling
- **Analytics**: Sales, orders, and customer insights
- **Bulk Operations**: Efficient product and order management
- **Email Templates**: Professional branded communications

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **CSRF Protection**: Cross-site request forgery prevention
- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Comprehensive data validation
- **Rate Limiting**: API endpoint protection

### Data Protection
- **Password Hashing**: Secure password storage
- **Sensitive Data**: Encrypted storage for payment info
- **File Upload Security**: Validated and sanitized uploads
- **SQL Injection Prevention**: ORM-based queries
- **XSS Protection**: Output sanitization

## 📧 Email System

### Automated Notifications
- **Order Confirmation**: Immediate order placement confirmation
- **Status Updates**: Real-time order status changes
- **Shipping Notifications**: Tracking information delivery
- **Newsletter Campaigns**: Marketing email management
- **Admin Alerts**: Important system notifications

### Template System
- **Professional Design**: Branded email templates
- **Responsive Layout**: Mobile-optimized emails
- **Dynamic Content**: Personalized email content
- **Multi-format**: HTML and plain text versions

## 🚀 Deployment

### Production Environment
- **Backend**: Django with Gunicorn + Nginx
- **Frontend**: Next.js with static optimization
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session and data caching
- **File Storage**: Cloudinary CDN for images
- **SSL/TLS**: HTTPS encryption throughout

### Monitoring & Logging
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Response time tracking
- **Security Logging**: Authentication and access logs
- **Email Delivery**: SMTP delivery monitoring

## 🧪 Testing

### Backend Testing
- **Unit Tests**: Model and view testing
- **Integration Tests**: API endpoint testing
- **Authentication Tests**: Security flow validation
- **Database Tests**: Data integrity verification

### Frontend Testing
- **Component Tests**: UI component validation
- **Integration Tests**: User flow testing
- **API Tests**: Backend integration testing
- **E2E Tests**: Complete user journey validation

## 📈 Performance Optimization

### Backend Optimization
- **Database Indexing**: Optimized query performance
- **Caching Strategy**: Redis-based caching
- **Query Optimization**: Efficient database queries
- **Background Tasks**: Celery for heavy operations

### Frontend Optimization
- **Code Splitting**: Optimized bundle sizes
- **Image Optimization**: Next.js image optimization
- **Caching**: Browser and CDN caching
- **Lazy Loading**: On-demand component loading

## 🤝 Contributing

### Development Workflow
1. **Fork Repository**: Create personal fork
2. **Feature Branch**: Create feature-specific branch
3. **Development**: Implement changes with tests
4. **Code Review**: Submit pull request for review
5. **Deployment**: Merge to main branch

### Code Standards
- **Python**: PEP 8 compliance with Black formatting
- **TypeScript**: ESLint configuration with Prettier
- **Git**: Conventional commit messages
- **Documentation**: Comprehensive code documentation

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Token refresh
- `POST /api/auth/password/reset/` - Password reset

### Product Endpoints
- `GET /api/products/products/` - Product listing
- `GET /api/products/products/{id}/` - Product detail
- `GET /api/products/categories/` - Category listing
- `GET /api/products/brands/` - Brand listing
- `GET /api/products/featured/` - Featured products

### Order Endpoints
- `GET /api/orders/orders/` - User orders
- `POST /api/orders/orders/` - Create order
- `GET /api/orders/orders/{id}/` - Order detail
- `PATCH /api/orders/orders/{id}/status/` - Update status

### Cart Endpoints
- `GET /api/cart/` - Get user cart
- `POST /api/cart/add/` - Add item to cart
- `PATCH /api/cart/update/{id}/` - Update cart item
- `DELETE /api/cart/remove/{id}/` - Remove cart item

## 🏆 Production Features

### Scalability
- **Horizontal Scaling**: Load balancer ready
- **Database Scaling**: Read replicas support
- **CDN Integration**: Global content delivery
- **Microservices Ready**: Modular architecture

### Reliability
- **Error Handling**: Graceful error recovery
- **Backup Strategy**: Automated database backups
- **Health Checks**: System monitoring endpoints
- **Failover**: Redundant system components

## 📞 Support & Maintenance

### Monitoring
- **System Health**: Real-time system monitoring
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Automated error reporting
- **User Analytics**: Usage pattern analysis

### Maintenance
- **Regular Updates**: Security and feature updates
- **Database Maintenance**: Optimization and cleanup
- **Backup Verification**: Regular backup testing
- **Security Audits**: Periodic security reviews

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Community**: For the excellent web framework
- **Next.js Team**: For the powerful React framework
- **shadcn/ui**: For the beautiful component library
- **Tailwind CSS**: For the utility-first CSS framework
- **Stripe**: For secure payment processing

---

**Built with ❤️ for the antique and vintage community**

*Last Updated: October 2025*
