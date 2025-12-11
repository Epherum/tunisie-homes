# Tunisie Homes

End-to-end real estate platform for Tunisian listings. A Python data factory scrapes and normalizes properties into Supabase, while a Next.js frontend showcases the live feed with map-ready metadata and AI-friendly fields.

## Repository structure
- `frontend/` Next.js 14 app that reads `properties` and `images` from Supabase and renders animated listing cards.
- `data-factory/` Python scraper + ETL that ingests tunisie-annonce.com, normalizes records, downloads images (optional), and can generate embeddings before upserting to Supabase.
- `docs/` Project documentation (schema upgrade notes, Gemini analysis, Mapbox setup, requirements, status, etc.).
- `scraped_data.json` Sample output generated when running the scraper directly.

## Quick start
### Frontend
```bash
cd frontend
npm install
# Configure env vars
export NEXT_PUBLIC_SUPABASE_URL=...
export NEXT_PUBLIC_SUPABASE_ANON_KEY=...
npm run dev
```
Open http://localhost:3000 to view the listing grid. Data comes straight from your Supabase `properties` and `images` tables.

### Data factory
```bash
cd data-factory
pip install -r requirements.txt
# Configure env vars
export SUPABASE_URL=...
export SUPABASE_SERVICE_KEY=...
python main.py --max-listings 10 --download-images --generate-embeddings
```
Flags let you control scrape volume, image downloading/uploading, and embedding provider (Gemini or OpenAI). See `data-factory/README.md` for CLI options and architecture.

## Additional docs
- Browse `docs/` for schema upgrade notes, API analysis, Mapbox setup, and requirements.
- Prisma schema lives in `frontend/prisma/schema.prisma`.
- Storage and upload plans are documented in `data-factory/STORAGE_UPLOAD_PLAN.md`.
