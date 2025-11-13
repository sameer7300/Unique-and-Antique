You are an expert full-stack architect and developer. I want you to **generate a complete production-ready full-stack e-commerce web application** with the following requirements. 

---

## 🔹 Project Name
**Unique and antique** — a multi-category universal product store (garments, electronics, antiques, etc.)

---

## 🔹 Tech Stack
- **Backend**: Django + Django REST Framework (DRF)  
- **Frontend**: Next.js (React) with Tailwind CSS  
- **Database**: PostgreSQL  
- **Caching / Queues**: Redis  
- **Payment**: Stripe + Cash on Delivery (COD)  
- **Deployment**: Docker-based setup, backend can run on AWS/GCP/Azure/Heroku, frontend on Vercel.  
- **Storage**: S3-compatible for product images (AWS S3, DigitalOcean Spaces, etc.)  

---

## 🔹 Architecture
- Django REST API serves JSON responses, handles business logic, database, payments, order processing, reviews, authentication.
- Next.js frontend consumes API endpoints for all pages (client-side + SSR for SEO).  
- JWT or cookie-based auth.  
- Webhooks from Stripe to confirm payments.  
- Redis used for caching products, session management, and background jobs (emails, recommendations).  
- Background worker for async tasks (Celery + Redis).  

---

## 🔹 Core Features
1. **User Accounts**
   - Register, login, logout, password reset
   - Profile (name, phone, addresses, order history)
   - Role: Customer / Admin

2. **Product Catalog**
   - Categories, subcategories, tags
   - Product listing with filters (category, price, rating)
   - Product details page with gallery, specs, stock status
   - Related/recommended products

3. **Cart & Checkout**
   - Add to cart (guest + logged-in)
   - Persistent cart in DB for users, localStorage for guests
   - Update qty, remove items
   - Checkout flow: select address + payment method (Stripe or COD)

4. **Orders & Payments**
   - Create order after successful Stripe payment or COD selection
   - Order statuses: Pending → Confirmed → Packed → Shipped → Delivered → Returned
   - Stripe webhook updates payment status
   - COD orders flagged for admin confirmation

5. **Ratings & Reviews**
   - Users can post reviews with star rating + text
   - Only verified purchasers can leave reviews
   - Admin can moderate (approve/flag/remove)
   - Display average rating on product page

6. **Order Tracking**
   - Timeline view with status updates
   - Estimated delivery date shown

7. **Admin Dashboard**
   - Manage products (CRUD, upload images, stock updates)
   - Manage orders (change status, refund, confirm COD)
   - Manage users
   - Manage reviews (moderation)
   - View analytics (sales, orders, revenue trends)

8. **Search**
   - Full-text search across products (Postgres trigram / ElasticSearch optional later)
   - Typo tolerance and suggestions

---

## 🔹 Smart Features (Phase 2)
- Personalized recommendations (recently viewed, related items, collaborative filtering)
- Inventory alerts (low stock → notify admin)
- Smart promotions engine (discounts, bundles)
- Fraud detection heuristics (for Stripe & COD orders)
- AI chatbot for product discovery + FAQs

---

## 🔹 Workflows
### User Flow
- Register/login → browse categories → view product → add to cart → checkout → payment (Stripe or COD) → order placed → track order → leave review.  

### Admin Flow
- Login as admin → dashboard → add/edit products → manage orders → confirm COD → track revenue → moderate reviews.  

### Payment Flow
- User checks out with Stripe → backend creates PaymentIntent → frontend collects card info via Stripe Elements → Stripe webhook confirms → backend marks order as paid.  
- If COD → backend creates order with status `Pending (COD)` → admin confirms manually.

---

## 🔹 Django Models
Define Django models for:
- **User** (id, email, password, name, phone, role, created_at, updated_at)  
- **Category** (id, name, slug, parent)  
- **Product** (id, title, slug, description, price, stock, category, attributes JSON, created_at, updated_at)  
- **ProductImage** (id, product, url, alt_text, position)  
- **CartItem** (id, user/guest_token, product, qty, price_at_add, created_at)  
- **Order** (id, user, total_amount, currency, status, payment_method, placed_at)  
- **OrderItem** (id, order, product, qty, unit_price, total_price)  
- **Payment** (id, order, provider, provider_payment_id, amount, status, created_at)  
- **Review** (id, product, user, rating, title, body, status, created_at)  
- **TrackingHistory** (id, order, status, note, timestamp)  

Use Django REST Framework serializers & viewsets for API endpoints.

---

## 🔹 API Endpoints (REST)
- **Auth**:  
  - POST `/api/auth/register`  
  - POST `/api/auth/login`  
  - POST `/api/auth/logout`  
  - POST `/api/auth/refresh`  

- **Products**:  
  - GET `/api/products` (filters, search, pagination)  
  - GET `/api/products/{id}`  
  - POST `/api/products` (admin)  
  - PUT `/api/products/{id}` (admin)  

- **Cart**:  
  - GET `/api/cart`  
  - POST `/api/cart` (add item)  
  - PATCH `/api/cart/{id}` (update qty)  
  - DELETE `/api/cart/{id}`  

- **Orders**:  
  - POST `/api/orders` (checkout)  
  - GET `/api/orders/{id}`  
  - GET `/api/orders/my`  

- **Payments**:  
  - POST `/api/payments/create-intent` (Stripe)  
  - POST `/api/payments/webhook/stripe` (webhook handler)  

- **Reviews**:  
  - GET `/api/products/{id}/reviews`  
  - POST `/api/products/{id}/reviews`  

- **Admin**:  
  - GET `/api/admin/orders`  
  - GET `/api/admin/dashboard/stats`  

---

## 🔹 Frontend (Next.js Pages)
- `/` → Homepage (categories, featured products, recommendations)  
- `/products` → All products listing + filters  
- `/products/[slug]` → Product detail page + reviews + add to cart  
- `/cart` → Shopping cart  
- `/checkout` → Checkout page (address, payment)  
- `/orders/[id]` → Order details + tracking timeline  
- `/account` → Profile, orders, addresses  
- `/login` → Login page  
- `/register` → Register page  
- `/admin` → Admin dashboard (products, orders, reviews, stats)  

Use Tailwind CSS + shadcn/ui for modern styling.  

---

## 🔹 Deployment
- Use Docker Compose for dev environment (Django, Postgres, Redis, Next.js)  
- Deploy frontend on Vercel, backend on AWS/GCP/Heroku  
- Use S3 for product images + CloudFront CDN  
- Setup Stripe webhook endpoint in production  

---

## 🔹 Deliverables
- Django project with DRF API endpoints & Celery worker  
- Next.js frontend with all pages and components  
- Database migrations for Postgres  
- Docker Compose setup for local dev  
- Stripe integration (PaymentIntent + webhook)  
- Admin dashboard with product/order management  
- Unit tests + integration tests for critical flows  

---

Build this entire application step by step, starting with **backend models + serializers + API endpoints**, then move to **frontend Next.js pages + components**, then **integrate Stripe payments and order tracking**, and finally add **admin dashboard + smart features**.
