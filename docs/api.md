# API Documentation

## Public
- `POST /api/contact` - Submit contact form.
- `GET /api/products` - List active products.
- `GET /api/stripe/checkout?productId=` - Start Stripe checkout.
- `POST /api/stripe/webhook` - Stripe webhook endpoint.

## User (authenticated)
- `GET /api/orders`
- `GET/POST /api/tickets`
- `GET /api/user/subscriptions`
- `PATCH /api/user/notifications`

## Admin (ADMIN role)
- `GET/PATCH /api/admin/users`
- `GET/POST /api/admin/products`
- `GET/PATCH /api/admin/orders`
- `GET/POST /api/admin/tickets`
- `GET/PATCH /api/admin/settings`
- `GET /api/admin/audit`
- `GET /api/admin/analytics`
