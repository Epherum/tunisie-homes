# Project Status & Implementation Plan

## Current Position
- Data factory scrapes Tunisie Annonce, normalizes data (enums/features/price-per-sqm), supports geocoding, optional image download/storage upload, optional embeddings.
- Frontend shows a Supabase-backed listings grid, detail page, and a simple admin editor; Lenis + view transitions integrated; `/admin` now protected via basic auth (`ADMIN_PASS`).
- Prisma schema added at `frontend/prisma/schema.prisma`; Supabase reset and in sync (extensions enabled for PostGIS/vector). Tables are currently empty—rerun the data factory to repopulate.

## High-Level Goal
Ship the PRD: “Bloomberg Terminal for Tunisian real estate” with map/heatmap, semantic search, price intelligence, AI-assisted uploads, and a polished UI.

## Immediate Fixes (Day 0)
- Done: `imageError` scoping fixed; params typing corrected; `/admin` behind basic auth.
- Done: Prisma schema committed and applied; `scrapedAt` preserved on updates.
- Pending: DB permissions/grants — run `fix_permissions.sql` or grant script so anon/authenticated can read `properties`/`images`.

## Data Factory Roadmap
1) **Stabilize ingestion**: run pipeline with geocoding on 10–20 listings; verify pricePerSqm, features, listingType enums are stored; ensure PostGIS coords present.  
2) **Neighborhood stats + deal rating**: implement `price_analyzer.py` to aggregate per-city/region stats and compute `dealRating`; backfill existing rows.  
3) **AI signals**: wire embeddings (Gemini/OpenAI) behind a flag; add renovation score + tags placeholder to schema; prep Ollama vision hook.  
4) **Storage**: default to uploading images to Supabase Storage and syncing URLs; set bucket in env.  
5) **Additional sources**: add Tayara/Mubawab scrapers once core is stable.  
6) **Scheduling**: add cron/PM2/GitHub Actions for nightly runs; include health logging.

## Frontend Roadmap
1) **Map & heatmap**: add Mapbox token env; build map view with markers, clustering, heatmap toggle, and split list/map layout.  
2) **Search & filters**: price range, property type, listing type, surface, city; wire to Supabase/PostGIS queries; add semantic search (pgvector) endpoint/action.  
3) **AI insights**: surface deal rating, renovation score, price-per-sqm, neighborhood averages on cards and detail view; add badges/legends.  
4) **User upload flow**: form + image upload; call Gemini Flash for auto-fill and description generation; store as `DataSource.USER_UPLOAD`.  
5) **Admin/auth**: protect `/admin` (basic password or Supabase auth); add inline image reorder/delete and status toggle.  
6) **UX polish**: loading skeletons, error states, mobile layout, motion tuning; add view-transition names for map/list.

## Database & Infra
- Confirm PostGIS + pgvector enabled; ensure indexes exist (dealRating, listingType, propertyType, status, lat/lng).  
- Add RLS policies if needed (read-only for anon, write via service role/actions).  
- Create Prisma schema reflecting enums, AI fields, neighborhood stats, price history; commit migrations; run `npx prisma db push` after verification.

## Testing & Quality
- Add lightweight tests: scraper unit (parser), normalizer enum/feature extraction, geocoder rate-limit stub, DB upsert smoke (with test project).  
- Frontend: add minimal Vitest/RTL for formatters/components; Supabase client mocked.  
- Add CI lint/test job; optional nightly ingest dry-run.

## Milestones
1) Fix blockers + DB grants + schema committed.  
2) Map/heatmap + filters on live data.  
3) Deal rating + neighborhood stats + embeddings/semantic search.  
4) User upload with Gemini auto-fill + secured admin.  
5) Additional scrapers + cron + polish/performance pass.
