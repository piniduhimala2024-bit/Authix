# Ceylon Secure Network SaaS

Production-ready starter SaaS web app for VPN + VPS + Hosting + Digital Services.

## Stack
- Next.js 14 App Router + TypeScript + Tailwind
- NextAuth (Credentials + Google optional)
- PostgreSQL + Prisma ORM
- Stripe checkout + webhook
- Nodemailer transactional email
- Zod validation + rate limiting + sanitization
- Vitest tests

## Setup
1. Install dependencies:
   ```bash
   npm install
   ```
2. Configure env:
   ```bash
   cp .env.example .env
   ```
3. Run database:
   ```bash
   docker compose up -d db
   ```
4. Generate and migrate Prisma:
   ```bash
   npx prisma generate
   npx prisma migrate dev --name init
   ```
5. Seed data (admin + sample products):
   ```bash
   npx prisma db seed
   ```
6. Start app:
   ```bash
   npm run dev
   ```

Admin login:
- Email: `admin@ceylonsecurenetwork.lk`
- Password: `ChangeMe123!`

## Docker full app
```bash
docker compose up --build
```

## Testing
```bash
npm test
```

## Feature checklist
- [x] Public marketing pages (home, pricing, store, about, contact, blog scaffold, terms, privacy, status)
- [x] Auth with NextAuth credentials and role-based middleware
- [x] User dashboard pages (orders, subscriptions, services, tickets, wallet, profile, notifications)
- [x] Admin dashboard pages (analytics, users, products, orders, tickets, settings, audit)
- [x] Product and support APIs with validation and security helpers
- [x] Stripe checkout + webhook integration scaffolding
- [x] Prisma schema for required models + seed script
- [x] Docker, env example, API docs, and tests
