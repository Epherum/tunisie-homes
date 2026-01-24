# Tunisie Homes Frontend

Next.js frontend that reads listings from Supabase and renders the public site and admin views.

## Setup
```bash
npm install
```

## Environment Variables
Create `frontend/.env.local` or export variables in your shell.

Required:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `ADMIN_PASS` (required to access `/admin`)

Optional:
- `ADMIN_USER` (defaults to `admin`)
- `DATABASE_URL` / `DIRECT_URL` (only if running Prisma locally)

## Run
```bash
npm run dev
# open http://localhost:3000
```

## Backup & Restore (resetting your PC)
Back up before wiping:
- `frontend/.env.local`

Supabase data lives in the cloud, so listings/images persist there.

Restore steps:
1. Recreate `frontend/.env.local`.
2. `npm install` then `npm run dev`.
