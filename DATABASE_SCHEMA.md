# Database Schema Documentation - Unique & Antique E-commerce Platform

## 📊 Overview

The Unique & Antique platform uses PostgreSQL as the primary database with a well-structured schema designed for scalability, performance, and data integrity. The schema supports a complete e-commerce workflow from user management to order fulfillment.

## 🏗️ Schema Architecture

### Database Design Principles
- **Normalized Structure**: Reduces data redundancy and ensures consistency
- **Foreign Key Constraints**: Maintains referential integrity
- **Indexed Fields**: Optimized for common query patterns
- **Audit Fields**: Tracks creation and modification timestamps
- **Soft Deletes**: Preserves data integrity for business records

## 👤 User Management Schema

### accounts_user
**Purpose**: Custom user model extending Django's AbstractUser

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Unique user identifier |
| email | EmailField | UNIQUE, NOT NULL | User's email address (login) |
| username | CharField(150) | UNIQUE, NOT NULL | Unique username |
| first_name | CharField(150) | | User's first name |
| last_name | CharField(150) | | User's last name |
| phone | CharField(17) | NULLABLE | Phone number with regex validation |
| role | CharField(20) | DEFAULT 'customer' | User role (customer/admin/staff) |
| is_verified | BooleanField | DEFAULT False | Email verification status |
| two_factor_enabled | BooleanField | DEFAULT False | 2FA activation status |
| two_factor_secret | CharField(32) | NULLABLE | TOTP secret key |
| backup_codes | JSONField | DEFAULT [] | 2FA backup codes |
| is_active | BooleanField | DEFAULT True | Account active status |
| is_staff | BooleanField | DEFAULT False | Staff access permission |
| is_superuser | BooleanField | DEFAULT False | Superuser privileges |
| date_joined | DateTimeField | AUTO_NOW_ADD | Account creation timestamp |
| last_login | DateTimeField | NULLABLE | Last login timestamp |
| created_at | DateTimeField | AUTO_NOW_ADD | Record creation time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

**Indexes:**
- `idx_user_email` (email)
- `idx_user_username` (username)
- `idx_user_role` (role)

### accounts_profile
**Purpose**: Extended user profile information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Profile identifier |
| user_id | BigIntegerField | FK(accounts_user), UNIQUE | Associated user |
| avatar | ImageField | NULLABLE | Profile picture |
| bio | TextField(500) | | User biography |
| birth_date | DateField | NULLABLE | Date of birth |
| gender | CharField(1) | CHOICES | Gender (M/F/O/N) |
| website | URLField | | Personal website |
| location | CharField(100) | | User location |
| newsletter_subscription | BooleanField | DEFAULT True | Newsletter opt-in |
| email_notifications | BooleanField | DEFAULT True | Email notification preference |
| sms_notifications | BooleanField | DEFAULT False | SMS notification preference |
| created_at | DateTimeField | AUTO_NOW_ADD | Profile creation time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### accounts_address
**Purpose**: User shipping and billing addresses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Address identifier |
| user_id | BigIntegerField | FK(accounts_user) | Address owner |
| type | CharField(20) | CHOICES | Address type (shipping/billing/both) |
| first_name | CharField(50) | NOT NULL | Recipient first name |
| last_name | CharField(50) | NOT NULL | Recipient last name |
| company | CharField(100) | NULLABLE | Company name |
| address_line_1 | CharField(255) | NOT NULL | Primary address line |
| address_line_2 | CharField(255) | NULLABLE | Secondary address line |
| city | CharField(100) | NOT NULL | City name |
| state | CharField(100) | NOT NULL | State/Province |
| postal_code | CharField(20) | NOT NULL | ZIP/Postal code |
| country | CharField(2) | NOT NULL | Country code (ISO 3166-1) |
| phone | CharField(17) | NULLABLE | Contact phone number |
| is_default | BooleanField | DEFAULT False | Default address flag |
| created_at | DateTimeField | AUTO_NOW_ADD | Address creation time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

**Indexes:**
- `idx_address_user` (user_id)
- `idx_address_type` (type)
- `idx_address_default` (user_id, is_default)

## 🛍️ Product Catalog Schema

### products_category
**Purpose**: Hierarchical product categorization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Category identifier |
| name | CharField(100) | UNIQUE, NOT NULL | Category name |
| slug | SlugField(120) | UNIQUE | URL-friendly identifier |
| description | TextField | | Category description |
| parent_id | BigIntegerField | FK(products_category), NULLABLE | Parent category |
| image | ImageField | NULLABLE | Category image |
| is_active | BooleanField | DEFAULT True | Active status |
| sort_order | PositiveIntegerField | DEFAULT 0 | Display order |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

**Indexes:**
- `idx_category_slug` (slug)
- `idx_category_parent` (parent_id)
- `idx_category_active` (is_active)

### products_brand
**Purpose**: Product brand information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Brand identifier |
| name | CharField(100) | UNIQUE, NOT NULL | Brand name |
| slug | SlugField(120) | UNIQUE | URL-friendly identifier |
| description | TextField | | Brand description |
| logo | ImageField | NULLABLE | Brand logo |
| website | URLField | | Brand website |
| is_active | BooleanField | DEFAULT True | Active status |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### products_product
**Purpose**: Main product information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Product identifier |
| title | CharField(200) | NOT NULL | Product title |
| slug | SlugField(220) | UNIQUE | URL-friendly identifier |
| description | TextField | | Full product description |
| short_description | CharField(500) | | Brief product summary |
| category_id | BigIntegerField | FK(products_category), NULLABLE | Product category |
| brand_id | BigIntegerField | FK(products_brand), NULLABLE | Product brand |
| price | DecimalField(10,2) | NOT NULL | Current price |
| compare_price | DecimalField(10,2) | NULLABLE | Original/compare price |
| sku | CharField(100) | UNIQUE, NULLABLE | Stock keeping unit |
| stock | PositiveIntegerField | DEFAULT 0 | Available quantity |
| weight | DecimalField(8,3) | NULLABLE | Product weight (kg) |
| dimensions_length | DecimalField(8,2) | NULLABLE | Length (cm) |
| dimensions_width | DecimalField(8,2) | NULLABLE | Width (cm) |
| dimensions_height | DecimalField(8,2) | NULLABLE | Height (cm) |
| is_digital | BooleanField | DEFAULT False | Digital product flag |
| requires_shipping | BooleanField | DEFAULT True | Shipping requirement |
| attributes | JSONField | DEFAULT {} | Custom attributes |
| care_instructions | JSONField | DEFAULT [] | Care instruction list |
| condition | CharField(100) | NULLABLE | Product condition |
| era | CharField(100) | NULLABLE | Historical era |
| material | CharField(200) | NULLABLE | Primary materials |
| authenticity_verified | BooleanField | DEFAULT False | Authenticity status |
| is_featured | BooleanField | DEFAULT False | Featured product flag |
| status | CharField(20) | DEFAULT 'draft' | Product status |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |
| published_at | DateTimeField | NULLABLE | Publication timestamp |

**Indexes:**
- `idx_product_slug` (slug)
- `idx_product_category` (category_id)
- `idx_product_brand` (brand_id)
- `idx_product_status` (status)
- `idx_product_featured` (is_featured)
- `idx_product_price` (price)

### products_productimage
**Purpose**: Product image management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Image identifier |
| product_id | BigIntegerField | FK(products_product) | Associated product |
| image | ImageField | NOT NULL | Image file |
| alt_text | CharField(200) | | Alternative text |
| position | PositiveIntegerField | DEFAULT 0 | Display order |
| is_primary | BooleanField | DEFAULT False | Primary image flag |
| created_at | DateTimeField | AUTO_NOW_ADD | Upload timestamp |

**Indexes:**
- `idx_productimage_product` (product_id)
- `idx_productimage_primary` (product_id, is_primary)

### products_productvariant
**Purpose**: Product variations (size, color, etc.)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Variant identifier |
| product_id | BigIntegerField | FK(products_product) | Parent product |
| name | CharField(100) | NOT NULL | Variant name |
| sku | CharField(100) | UNIQUE | Variant SKU |
| price | DecimalField(10,2) | NOT NULL | Variant price |
| stock | PositiveIntegerField | DEFAULT 0 | Variant stock |
| attributes | JSONField | DEFAULT {} | Variant attributes |
| is_active | BooleanField | DEFAULT True | Active status |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

## 🛒 Shopping Cart Schema

### cart_cart
**Purpose**: User shopping carts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Cart identifier |
| user_id | BigIntegerField | FK(accounts_user), UNIQUE | Cart owner |
| created_at | DateTimeField | AUTO_NOW_ADD | Cart creation time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### cart_cartitem
**Purpose**: Items in shopping carts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Cart item identifier |
| cart_id | BigIntegerField | FK(cart_cart) | Associated cart |
| product_id | BigIntegerField | FK(products_product) | Product reference |
| variant_id | BigIntegerField | FK(products_productvariant), NULLABLE | Product variant |
| quantity | PositiveIntegerField | DEFAULT 1 | Item quantity |
| price_at_add | DecimalField(10,2) | NOT NULL | Price when added |
| options | JSONField | DEFAULT {} | Custom options |
| created_at | DateTimeField | AUTO_NOW_ADD | Addition timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### cart_saveditem
**Purpose**: Wishlist/saved items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Saved item identifier |
| user_id | BigIntegerField | FK(accounts_user) | User reference |
| product_id | BigIntegerField | FK(products_product) | Product reference |
| variant_id | BigIntegerField | FK(products_productvariant), NULLABLE | Product variant |
| notes | TextField | | User notes |
| created_at | DateTimeField | AUTO_NOW_ADD | Save timestamp |

**Indexes:**
- `idx_saveditem_user` (user_id)
- `idx_saveditem_product` (product_id)

## 📦 Order Management Schema

### orders_order
**Purpose**: Customer orders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Order identifier |
| order_number | CharField(20) | UNIQUE | Human-readable order number |
| order_id | CharField(50) | UNIQUE | System order ID |
| user_id | BigIntegerField | FK(accounts_user) | Customer reference |
| status | CharField(20) | DEFAULT 'pending' | Order status |
| payment_status | CharField(20) | DEFAULT 'pending' | Payment status |
| payment_method | CharField(20) | | Payment method used |
| subtotal | DecimalField(10,2) | NOT NULL | Items subtotal |
| tax_amount | DecimalField(10,2) | DEFAULT 0 | Tax amount |
| shipping_cost | DecimalField(10,2) | DEFAULT 0 | Shipping cost |
| discount_amount | DecimalField(10,2) | DEFAULT 0 | Discount applied |
| total_amount | DecimalField(10,2) | NOT NULL | Final total |
| currency | CharField(3) | DEFAULT 'USD' | Currency code |
| shipping_address | JSONField | NOT NULL | Shipping address data |
| billing_address | JSONField | NOT NULL | Billing address data |
| notes | TextField | | Customer notes |
| tracking_number | CharField(100) | NULLABLE | Shipment tracking |
| carrier | CharField(50) | NULLABLE | Shipping carrier |
| estimated_delivery_date | DateTimeField | NULLABLE | Expected delivery |
| created_at | DateTimeField | AUTO_NOW_ADD | Order placement time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

**Indexes:**
- `idx_order_user` (user_id)
- `idx_order_status` (status)
- `idx_order_payment_status` (payment_status)
- `idx_order_number` (order_number)
- `idx_order_created` (created_at)

### orders_orderitem
**Purpose**: Items within orders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Order item identifier |
| order_id | BigIntegerField | FK(orders_order) | Parent order |
| product_id | BigIntegerField | FK(products_product) | Product reference |
| variant_id | BigIntegerField | FK(products_productvariant), NULLABLE | Product variant |
| product_title | CharField(200) | NOT NULL | Product title snapshot |
| product_sku | CharField(100) | | Product SKU snapshot |
| quantity | PositiveIntegerField | NOT NULL | Ordered quantity |
| price | DecimalField(10,2) | NOT NULL | Unit price |
| total_price | DecimalField(10,2) | NOT NULL | Line total |
| options | JSONField | DEFAULT {} | Item options |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |

### orders_orderstatushistory
**Purpose**: Order status change tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | History identifier |
| order_id | BigIntegerField | FK(orders_order) | Associated order |
| status | CharField(20) | NOT NULL | Status value |
| notes | TextField | | Status change notes |
| changed_by_id | BigIntegerField | FK(accounts_user), NULLABLE | User who made change |
| timestamp | DateTimeField | AUTO_NOW_ADD | Change timestamp |

## 💳 Payment Schema

### payments_payment
**Purpose**: Payment transaction records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Payment identifier |
| order_id | BigIntegerField | FK(orders_order) | Associated order |
| payment_method | CharField(20) | NOT NULL | Payment method |
| payment_intent_id | CharField(100) | UNIQUE, NULLABLE | Stripe payment intent |
| amount | DecimalField(10,2) | NOT NULL | Payment amount |
| currency | CharField(3) | DEFAULT 'USD' | Currency code |
| status | CharField(20) | DEFAULT 'pending' | Payment status |
| gateway_response | JSONField | DEFAULT {} | Gateway response data |
| failure_reason | TextField | | Failure description |
| processed_at | DateTimeField | NULLABLE | Processing timestamp |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### payments_refund
**Purpose**: Refund transaction records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Refund identifier |
| payment_id | BigIntegerField | FK(payments_payment) | Original payment |
| order_id | BigIntegerField | FK(orders_order) | Associated order |
| amount | DecimalField(10,2) | NOT NULL | Refund amount |
| reason | CharField(200) | | Refund reason |
| status | CharField(20) | DEFAULT 'pending' | Refund status |
| refund_id | CharField(100) | UNIQUE, NULLABLE | Gateway refund ID |
| processed_at | DateTimeField | NULLABLE | Processing timestamp |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |

## ⭐ Review System Schema

### reviews_review
**Purpose**: Product reviews and ratings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Review identifier |
| user_id | BigIntegerField | FK(accounts_user) | Reviewer |
| product_id | BigIntegerField | FK(products_product) | Reviewed product |
| order_item_id | BigIntegerField | FK(orders_orderitem), NULLABLE | Purchase reference |
| rating | PositiveSmallIntegerField | NOT NULL | Rating (1-5) |
| title | CharField(200) | | Review title |
| content | TextField | NOT NULL | Review content |
| is_verified_purchase | BooleanField | DEFAULT False | Purchase verification |
| is_approved | BooleanField | DEFAULT False | Moderation status |
| helpfulness_score | IntegerField | DEFAULT 0 | Helpfulness votes |
| created_at | DateTimeField | AUTO_NOW_ADD | Review timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

**Indexes:**
- `idx_review_product` (product_id)
- `idx_review_user` (user_id)
- `idx_review_approved` (is_approved)
- `idx_review_rating` (rating)

### reviews_reviewimage
**Purpose**: Review image attachments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Image identifier |
| review_id | BigIntegerField | FK(reviews_review) | Associated review |
| image | ImageField | NOT NULL | Image file |
| caption | CharField(200) | | Image caption |
| position | PositiveIntegerField | DEFAULT 0 | Display order |
| created_at | DateTimeField | AUTO_NOW_ADD | Upload timestamp |

### reviews_reviewhelpfulness
**Purpose**: Review helpfulness voting

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Vote identifier |
| review_id | BigIntegerField | FK(reviews_review) | Voted review |
| user_id | BigIntegerField | FK(accounts_user) | Voter |
| is_helpful | BooleanField | NOT NULL | Vote value |
| created_at | DateTimeField | AUTO_NOW_ADD | Vote timestamp |

**Constraints:**
- UNIQUE(review_id, user_id) - One vote per user per review

## 📧 Communication Schema

### contact_contactmessage
**Purpose**: Customer contact messages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Message identifier |
| name | CharField(100) | NOT NULL | Sender name |
| email | EmailField | NOT NULL | Sender email |
| subject | CharField(200) | NOT NULL | Message subject |
| message | TextField | NOT NULL | Message content |
| phone | CharField(17) | NULLABLE | Contact phone |
| status | CharField(20) | DEFAULT 'new' | Message status |
| assigned_to_id | BigIntegerField | FK(accounts_user), NULLABLE | Assigned staff |
| response | TextField | | Staff response |
| responded_at | DateTimeField | NULLABLE | Response timestamp |
| created_at | DateTimeField | AUTO_NOW_ADD | Message timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### newsletter_newslettersubscriber
**Purpose**: Newsletter subscriptions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Subscriber identifier |
| email | EmailField | UNIQUE, NOT NULL | Subscriber email |
| name | CharField(100) | | Subscriber name |
| status | CharField(20) | DEFAULT 'active' | Subscription status |
| subscribed_at | DateTimeField | AUTO_NOW_ADD | Subscription timestamp |
| unsubscribed_at | DateTimeField | NULLABLE | Unsubscription timestamp |
| created_at | DateTimeField | AUTO_NOW_ADD | Record creation time |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### newsletter_newsletter
**Purpose**: Newsletter campaigns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Newsletter identifier |
| subject | CharField(200) | NOT NULL | Email subject |
| content | TextField | NOT NULL | Email content |
| html_content | TextField | | HTML email content |
| status | CharField(20) | DEFAULT 'draft' | Campaign status |
| scheduled_at | DateTimeField | NULLABLE | Send schedule |
| sent_at | DateTimeField | NULLABLE | Actual send time |
| created_by_id | BigIntegerField | FK(accounts_user) | Creator |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### newsletter_newslettersendlog
**Purpose**: Newsletter delivery tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Log identifier |
| newsletter_id | BigIntegerField | FK(newsletter_newsletter) | Campaign reference |
| subscriber_id | BigIntegerField | FK(newsletter_newslettersubscriber) | Recipient |
| status | CharField(20) | DEFAULT 'pending' | Delivery status |
| sent_at | DateTimeField | NULLABLE | Send timestamp |
| error_message | TextField | | Error details |
| created_at | DateTimeField | AUTO_NOW_ADD | Log creation time |

## ⚙️ Settings Schema

### settings_sitesettings
**Purpose**: Global site configuration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Settings identifier |
| site_name | CharField(100) | DEFAULT 'Unique & Antique' | Site name |
| site_description | TextField | | Site description |
| contact_email | EmailField | | Contact email |
| contact_phone | CharField(17) | | Contact phone |
| address | TextField | | Business address |
| currency | CharField(3) | DEFAULT 'USD' | Default currency |
| tax_rate | DecimalField(5,4) | DEFAULT 0 | Default tax rate |
| shipping_cost | DecimalField(10,2) | DEFAULT 0 | Default shipping |
| free_shipping_threshold | DecimalField(10,2) | DEFAULT 100 | Free shipping minimum |
| maintenance_mode | BooleanField | DEFAULT False | Maintenance flag |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### settings_shippingzone
**Purpose**: Shipping zone configuration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Zone identifier |
| name | CharField(100) | NOT NULL | Zone name |
| countries | JSONField | DEFAULT [] | Country codes |
| is_active | BooleanField | DEFAULT True | Active status |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

### settings_shippingrate
**Purpose**: Shipping rate configuration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PRIMARY KEY | Rate identifier |
| zone_id | BigIntegerField | FK(settings_shippingzone) | Shipping zone |
| name | CharField(100) | NOT NULL | Rate name |
| min_weight | DecimalField(8,3) | DEFAULT 0 | Minimum weight |
| max_weight | DecimalField(8,3) | NULLABLE | Maximum weight |
| cost | DecimalField(10,2) | NOT NULL | Shipping cost |
| estimated_days | PositiveIntegerField | | Delivery estimate |
| is_active | BooleanField | DEFAULT True | Active status |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update time |

## 🔍 Database Relationships

### Key Relationships

1. **User → Profile**: One-to-One relationship
2. **User → Addresses**: One-to-Many relationship
3. **User → Orders**: One-to-Many relationship
4. **Category → Products**: One-to-Many with hierarchy support
5. **Product → Images**: One-to-Many relationship
6. **Product → Variants**: One-to-Many relationship
7. **Order → OrderItems**: One-to-Many relationship
8. **Product → Reviews**: One-to-Many relationship
9. **Review → Images**: One-to-Many relationship

### Foreign Key Constraints

All foreign key relationships include:
- **ON DELETE CASCADE**: For dependent records
- **ON DELETE SET NULL**: For optional references
- **ON DELETE PROTECT**: For critical business data

## 📊 Performance Considerations

### Indexing Strategy

1. **Primary Keys**: Automatic B-tree indexes
2. **Foreign Keys**: Indexed for join performance
3. **Search Fields**: Full-text search indexes
4. **Filter Fields**: Composite indexes for common filters
5. **Unique Constraints**: Automatic unique indexes

### Query Optimization

1. **Pagination**: Efficient LIMIT/OFFSET queries
2. **Prefetch Related**: Reduces N+1 query problems
3. **Select Related**: Optimizes foreign key joins
4. **Database Views**: For complex reporting queries
5. **Materialized Views**: For expensive aggregations

### Maintenance Tasks

1. **VACUUM**: Regular table maintenance
2. **ANALYZE**: Statistics updates for query planner
3. **REINDEX**: Index rebuilding when needed
4. **Backup Strategy**: Regular automated backups
5. **Archive Strategy**: Historical data management

---

*Last Updated: October 2025*
*Database Version: PostgreSQL 13+*
