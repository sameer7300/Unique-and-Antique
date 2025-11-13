# API Documentation - Unique & Antique E-commerce Platform

## 🔗 Base URL

- **Development**: `http://localhost:8000/api`
- **Production**: `https://backend.unique-antique.com/api`

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication with access and refresh tokens.

### Authentication Flow

1. **Register/Login** to get tokens
2. **Include access token** in Authorization header: `Bearer <access_token>`
3. **Refresh token** when access token expires
4. **Logout** to invalidate tokens

### Token Lifecycle
- **Access Token**: 60 minutes (configurable)
- **Refresh Token**: 7 days (configurable)
- **Auto-refresh**: Frontend automatically refreshes expired tokens

---

## 👤 Authentication Endpoints

### Register User
```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "customer",
    "is_verified": false
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "message": "Registration successful. Please check your email for verification."
}
```

### Login User
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "customer",
    "is_verified": true
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout User
```http
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

### Password Reset Request
```http
POST /api/auth/password/reset/
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

### Password Reset Confirm
```http
POST /api/auth/password/reset/confirm/
```

**Request Body:**
```json
{
  "token": "password-reset-token",
  "password": "newpassword123",
  "password_confirm": "newpassword123"
}
```

---

## 🛍️ Product Endpoints

### List Products
```http
GET /api/products/products/
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `search` (string): Search in title, description
- `category` (int): Filter by category ID
- `brand` (int): Filter by brand ID
- `min_price` (decimal): Minimum price filter
- `max_price` (decimal): Maximum price filter
- `is_featured` (boolean): Filter featured products
- `ordering` (string): Sort by field (price, -price, created_at, -created_at)

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/products/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Victorian Era Antique Vase",
      "slug": "victorian-era-antique-vase",
      "short_description": "Beautiful hand-crafted Victorian vase",
      "price": "299.99",
      "compare_price": "399.99",
      "discount_percentage": 25,
      "primary_image": {
        "id": 1,
        "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1.jpg",
        "alt_text": "Victorian Era Antique Vase"
      },
      "category": {
        "id": 1,
        "name": "Decorative Arts",
        "slug": "decorative-arts"
      },
      "brand": {
        "id": 1,
        "name": "Heritage Antiques",
        "slug": "heritage-antiques"
      },
      "average_rating": 4.5,
      "review_count": 12,
      "is_in_stock": true,
      "is_featured": true,
      "condition": "Authentic Antique",
      "era": "Victorian Era (1837-1901)",
      "material": "Fine Porcelain",
      "authenticity_verified": true
    }
  ]
}
```

### Get Product Detail
```http
GET /api/products/products/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Victorian Era Antique Vase",
  "slug": "victorian-era-antique-vase",
  "description": "This exquisite Victorian era vase represents the pinnacle of 19th-century craftsmanship...",
  "short_description": "Beautiful hand-crafted Victorian vase",
  "price": "299.99",
  "compare_price": "399.99",
  "sku": "VA-001",
  "stock": 1,
  "weight": "2.5",
  "dimensions_length": "15.0",
  "dimensions_width": "15.0",
  "dimensions_height": "25.0",
  "condition": "Authentic Antique",
  "era": "Victorian Era (1837-1901)",
  "material": "Fine Porcelain",
  "authenticity_verified": true,
  "care_instructions": [
    "Dust regularly with a soft, dry cloth",
    "Avoid direct sunlight to prevent fading",
    "Handle with care due to age and fragility",
    "Clean with mild soap and water if necessary"
  ],
  "category": {
    "id": 1,
    "name": "Decorative Arts",
    "slug": "decorative-arts",
    "full_name": "Home & Garden > Decorative Arts"
  },
  "brand": {
    "id": 1,
    "name": "Heritage Antiques",
    "slug": "heritage-antiques",
    "description": "Specializing in authentic Victorian era pieces"
  },
  "images": [
    {
      "id": 1,
      "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1.jpg",
      "alt_text": "Victorian Era Antique Vase - Front View",
      "position": 1,
      "is_primary": true
    },
    {
      "id": 2,
      "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1-detail.jpg",
      "alt_text": "Victorian Era Antique Vase - Detail View",
      "position": 2,
      "is_primary": false
    }
  ],
  "variants": [],
  "average_rating": 4.5,
  "review_count": 12,
  "is_in_stock": true,
  "is_featured": true,
  "related_products": [
    {
      "id": 2,
      "title": "Victorian Mirror Set",
      "slug": "victorian-mirror-set",
      "price": "450.00",
      "primary_image": {
        "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/mirror1.jpg"
      }
    }
  ]
}
```

### List Categories
```http
GET /api/products/categories/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Decorative Arts",
    "slug": "decorative-arts",
    "description": "Beautiful decorative pieces for your home",
    "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/categories/decorative-arts.jpg",
    "parent": null,
    "children": [
      {
        "id": 2,
        "name": "Vases & Pottery",
        "slug": "vases-pottery",
        "product_count": 25
      }
    ],
    "product_count": 45,
    "full_name": "Decorative Arts"
  }
]
```

### List Brands
```http
GET /api/products/brands/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Heritage Antiques",
    "slug": "heritage-antiques",
    "description": "Specializing in authentic Victorian era pieces",
    "logo": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/brands/heritage-logo.jpg",
    "website": "https://heritage-antiques.com",
    "product_count": 32
  }
]
```

---

## 🛒 Cart Endpoints

### Get User Cart
```http
GET /api/cart/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "Victorian Era Antique Vase",
        "slug": "victorian-era-antique-vase",
        "price": "299.99",
        "primary_image": {
          "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1.jpg"
        }
      },
      "quantity": 1,
      "price_at_add": "299.99",
      "total_price": "299.99",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_items": 1,
  "subtotal": "299.99",
  "total_weight": "2.5"
}
```

### Add Item to Cart
```http
POST /api/cart/add/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 1,
  "variant_id": null,
  "options": {}
}
```

**Response (201 Created):**
```json
{
  "message": "Item added to cart successfully",
  "cart_item": {
    "id": 1,
    "product": {
      "id": 1,
      "title": "Victorian Era Antique Vase"
    },
    "quantity": 1,
    "total_price": "299.99"
  }
}
```

### Update Cart Item
```http
PATCH /api/cart/update/{item_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "quantity": 2
}
```

**Response (200 OK):**
```json
{
  "message": "Cart item updated successfully",
  "cart_item": {
    "id": 1,
    "quantity": 2,
    "total_price": "599.98"
  }
}
```

### Remove Cart Item
```http
DELETE /api/cart/remove/{item_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Item removed from cart successfully"
}
```

### Clear Cart
```http
DELETE /api/cart/clear/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Cart cleared successfully"
}
```

---

## 📦 Order Endpoints

### List User Orders
```http
GET /api/orders/orders/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` (string): Filter by order status
- `ordering` (string): Sort by field (-created_at, total_amount)

**Response (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-2024-001",
      "order_id": "unique-order-id-123",
      "status": "delivered",
      "payment_status": "paid",
      "payment_method": "stripe",
      "total_amount": "299.99",
      "currency": "USD",
      "created_at": "2024-01-15T10:30:00Z",
      "estimated_delivery_date": "2024-01-20T00:00:00Z",
      "items": [
        {
          "id": 1,
          "product_title": "Victorian Era Antique Vase",
          "product_image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1.jpg",
          "quantity": 1,
          "price": "299.99",
          "total_price": "299.99"
        }
      ]
    }
  ]
}
```

### Create Order
```http
POST /api/orders/orders/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "payment_method": "stripe",
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1234567890"
  },
  "billing_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1234567890"
  },
  "notes": "Please handle with care"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_number": "ORD-2024-001",
  "order_id": "unique-order-id-123",
  "status": "pending",
  "payment_status": "pending",
  "total_amount": "299.99",
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_abc123"
}
```

### Get Order Detail
```http
GET /api/orders/orders/{id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_number": "ORD-2024-001",
  "order_id": "unique-order-id-123",
  "status": "delivered",
  "payment_status": "paid",
  "payment_method": "stripe",
  "subtotal": "299.99",
  "tax_amount": "24.00",
  "shipping_cost": "15.00",
  "discount_amount": "0.00",
  "total_amount": "338.99",
  "currency": "USD",
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1234567890"
  },
  "billing_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1234567890"
  },
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "Victorian Era Antique Vase",
        "slug": "victorian-era-antique-vase",
        "primary_image": {
          "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/products/vase1.jpg"
        }
      },
      "quantity": 1,
      "price": "299.99",
      "total_price": "299.99"
    }
  ],
  "status_history": [
    {
      "status": "pending",
      "timestamp": "2024-01-15T10:30:00Z",
      "notes": "Order placed"
    },
    {
      "status": "confirmed",
      "timestamp": "2024-01-15T11:00:00Z",
      "notes": "Payment confirmed"
    },
    {
      "status": "shipped",
      "timestamp": "2024-01-16T09:00:00Z",
      "notes": "Order shipped with tracking number: TRK123456789"
    },
    {
      "status": "delivered",
      "timestamp": "2024-01-18T14:30:00Z",
      "notes": "Order delivered successfully"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_delivery_date": "2024-01-20T00:00:00Z"
}
```

### Update Order Status (Admin Only)
```http
PATCH /api/orders/orders/{id}/status/
```

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "status": "shipped",
  "notes": "Order shipped with tracking number: TRK123456789",
  "tracking_number": "TRK123456789",
  "carrier": "FedEx"
}
```

**Response (200 OK):**
```json
{
  "message": "Order status updated successfully",
  "order": {
    "id": 1,
    "status": "shipped",
    "tracking_number": "TRK123456789"
  }
}
```

---

## ⭐ Review Endpoints

### List Product Reviews
```http
GET /api/reviews/reviews/?product={product_id}
```

**Query Parameters:**
- `product` (int): Product ID (required)
- `rating` (int): Filter by rating (1-5)
- `is_verified_purchase` (boolean): Filter verified purchases

**Response (200 OK):**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "John",
        "last_name": "D."
      },
      "rating": 5,
      "title": "Absolutely Beautiful!",
      "content": "This vase exceeded my expectations. The craftsmanship is incredible and it looks perfect in my living room.",
      "images": [
        {
          "id": 1,
          "image": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/reviews/review1.jpg",
          "caption": "Vase in my living room"
        }
      ],
      "is_verified_purchase": true,
      "is_approved": true,
      "helpfulness_score": 5,
      "created_at": "2024-01-20T15:30:00Z"
    }
  ]
}
```

### Create Review
```http
POST /api/reviews/reviews/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (multipart/form-data):**
```
product: 1
rating: 5
title: "Absolutely Beautiful!"
content: "This vase exceeded my expectations..."
images: [file1.jpg, file2.jpg]
```

**Response (201 Created):**
```json
{
  "id": 1,
  "message": "Review submitted successfully and is pending approval",
  "review": {
    "id": 1,
    "rating": 5,
    "title": "Absolutely Beautiful!",
    "is_approved": false
  }
}
```

---

## 👤 User Profile Endpoints

### Get User Profile
```http
GET /api/accounts/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "customer",
  "is_verified": true,
  "profile": {
    "avatar": "https://res.cloudinary.com/dvtxfejcs/image/upload/v1/unique-antique/avatars/user1.jpg",
    "bio": "Antique collector and enthusiast",
    "birth_date": "1985-06-15",
    "gender": "M",
    "website": "https://johndoe.com",
    "location": "New York, NY",
    "newsletter_subscription": true,
    "email_notifications": true,
    "sms_notifications": false
  },
  "addresses": [
    {
      "id": 1,
      "type": "both",
      "first_name": "John",
      "last_name": "Doe",
      "address_line_1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "US",
      "phone": "+1234567890",
      "is_default": true
    }
  ]
}
```

### Update User Profile
```http
PATCH /api/accounts/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "profile": {
    "bio": "Updated bio",
    "location": "Los Angeles, CA",
    "newsletter_subscription": false
  }
}
```

---

## 📧 Contact & Newsletter Endpoints

### Submit Contact Message
```http
POST /api/contact/messages/
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Product Inquiry",
  "message": "I'm interested in learning more about your Victorian era pieces.",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "message": "Your message has been sent successfully. We'll get back to you soon!",
  "reference_number": "MSG-2024-001"
}
```

### Newsletter Subscription
```http
POST /api/newsletter/subscribe/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "Successfully subscribed to newsletter",
  "subscription": {
    "email": "user@example.com",
    "status": "active"
  }
}
```

---

## 📊 Admin Dashboard Endpoints

### Dashboard Statistics
```http
GET /api/admin/dashboard/stats/
```

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
  "users": {
    "total": 1250,
    "new_this_month": 45,
    "verified": 1100
  },
  "products": {
    "total": 350,
    "active": 320,
    "draft": 20,
    "inactive": 10,
    "low_stock": 15
  },
  "orders": {
    "total": 890,
    "pending": 12,
    "processing": 8,
    "shipped": 25,
    "delivered": 820,
    "cancelled": 25,
    "total_revenue": "125450.75",
    "currency": "USD"
  },
  "reviews": {
    "total": 456,
    "pending": 8,
    "approved": 420,
    "rejected": 28,
    "average_rating": 4.3
  }
}
```

---

## 🚨 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": ["This field is required."],
      "password": ["Password must be at least 8 characters long."]
    }
  }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_REQUIRED`: User must be authenticated
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `PAYMENT_FAILED`: Payment processing error
- `INVENTORY_ERROR`: Insufficient stock
- `EMAIL_SEND_FAILED`: Email delivery failed

---

## 🔄 Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **General API endpoints**: 100 requests per minute
- **File upload endpoints**: 10 requests per minute
- **Admin endpoints**: 200 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## 📝 API Versioning

Current API version: **v1**

Version is specified in the URL path: `/api/v1/`

Future versions will maintain backward compatibility for at least 12 months.

---

## 🔍 Filtering & Searching

### Query Parameters

- **search**: Full-text search across relevant fields
- **ordering**: Sort results (prefix with `-` for descending)
- **page**: Page number for pagination
- **page_size**: Items per page (max 100)

### Example Requests

```http
# Search products
GET /api/products/products/?search=victorian&ordering=-created_at

# Filter by category and price range
GET /api/products/products/?category=1&min_price=100&max_price=500

# Get user orders sorted by date
GET /api/orders/orders/?ordering=-created_at&status=delivered
```

---

## 📱 Mobile API Considerations

### Optimizations for Mobile
- **Compressed responses**: Gzip compression enabled
- **Minimal data**: Only essential fields in list views
- **Image optimization**: Multiple image sizes available
- **Offline support**: Proper HTTP caching headers
- **Reduced payloads**: Pagination with smaller page sizes

### Mobile-Specific Endpoints
- **Featured products**: `/api/products/featured/` (optimized for mobile)
- **Quick search**: `/api/products/search/quick/` (fast autocomplete)
- **Cart summary**: `/api/cart/summary/` (minimal cart data)

---

*Last Updated: October 2025*
*API Version: 1.0*
