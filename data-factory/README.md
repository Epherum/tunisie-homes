# TunisHome Data Factory

Automated data pipeline for scraping, processing, and storing property listings from Tunisian real estate websites.

## Features

- **Web Scraping**: Scrapes property listings from tunisie-annonce.com
- **Data Normalization**: Cleans and standardizes property data
- **Image Downloading**: Downloads property images locally (optional)
- **AI Embeddings**: Generates vector embeddings for semantic search (optional)
- **Database Storage**: Stores data in Supabase with PostgreSQL + pgvector

## Architecture

```
┌─────────────────┐
│  Web Scraping   │ → tunisie_annonce.py
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Normalization  │ → normalizer.py
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Image Download  │ → image_downloader.py (optional)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Embeddings    │ → embeddings.py (optional)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    Database     │ → db_client.py → Supabase
└─────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
cd data-factory
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `data-factory` directory:

```env
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Optional (for embeddings)
GEMINI_API_KEY=your_gemini_api_key
# or
OPENAI_API_KEY=your_openai_api_key

# Optional (for storage uploads)
STORAGE_BUCKET=property-images
```

## Usage

### Basic Usage (5 listings, no images, no embeddings)

```bash
python main.py
```

### Advanced Usage

```bash
# Scrape 10 listings
python main.py --max-listings 10

# Download images locally
python main.py --download-images

# Upload images to Supabase Storage (requires STORAGE_BUCKET)
python main.py --upload-images

# Generate embeddings with Gemini
python main.py --generate-embeddings --embedding-provider gemini

# Generate embeddings with OpenAI
python main.py --generate-embeddings --embedding-provider openai

# Full pipeline
python main.py --max-listings 20 --download-images --generate-embeddings
```

### Command Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--max-listings` | int | 5 | Maximum number of listings to scrape |
| `--download-images` | flag | False | Download images locally |
| `--upload-images` | flag | False | Upload images to Supabase Storage and sync DB URLs |
| `--generate-embeddings` | flag | False | Generate AI embeddings |
| `--embedding-provider` | string | gemini | Provider for embeddings (gemini/openai) |

## Modules

### scrapers/tunisie_annonce.py

Scraper for tunisie-annonce.com:
- Handles Windows-1252 encoding
- Extracts property details (title, description, price, location, images)
- Polite scraping with delays

### normalizer.py

Data cleaning and normalization:
- Extracts property type from title
- Cleans descriptions (removes hashtags, excess whitespace)
- Normalizes location data
- Attempts to extract room/bathroom counts
- Validates data quality

### image_downloader.py

Image downloading and storage:
- Downloads images from URLs
- Generates unique filenames (hash-based)
- Organizes by property ID
- Handles duplicates

### embeddings.py

AI embedding generation:
- Supports Google Gemini (768-dim)
- Supports OpenAI (768-dim)
- Combines title, description, and metadata
- Falls back gracefully if API unavailable

### db_client.py

Database operations:
- Upserts properties to Supabase
- Handles images relation
- Stores vector embeddings
- Provides utility methods (exists, count)

## Data Flow

1. **Scrape**: Fetch HTML from tunisie-annonce.com
2. **Extract**: Parse property details using BeautifulSoup
3. **Normalize**: Clean and standardize data
4. **Download**: Save images locally (if enabled)
5. **Embed**: Generate vector embeddings (if enabled)
6. **Store**: Upsert to Supabase database

## Database Schema

See `frontend/prisma/schema.prisma` for the complete schema.

Key tables:
- `Property`: Main property data with vector embeddings
- `Image`: Property images (one-to-many)
- `PriceHistory`: Historical price tracking

## Notes

### Image Storage

Images are stored by URL in the database. When `--download-images` is used, images are also saved locally in `downloaded_images/`. Use `--upload-images` to push them to Supabase Storage (bucket set by `STORAGE_BUCKET`) and replace DB URLs with public Storage links.

### Embeddings

- Gemini: Free tier available, 768 dimensions
- OpenAI: Paid, 768 dimensions (configured)
- Both use `retrieval_document` task type for optimal search

### Error Handling

The pipeline continues on errors:
- Invalid properties are skipped
- Failed image downloads are logged but don't stop processing
- Embedding failures fall back to no embedding

## Testing

Test the scraper only:
```bash
python scrapers/tunisie_annonce.py
```

This creates `scraped_data.json` with sample data.

## Maintenance

### Cleaning Up Images

```python
from image_downloader import ImageDownloader
downloader = ImageDownloader()
downloader.cleanup_property_images("property_id")
```

### Database Stats

The pipeline shows database stats after completion:
- Properties processed
- Total properties in database

## Future Enhancements

- [ ] Support for additional scrapers (tayara.tn, etc.)
- [ ] Supabase Storage integration for images
- [ ] Price history tracking
- [ ] AI-powered property analysis (renovation score, deal rating)
- [ ] Scheduled runs (cron/celery)
- [ ] Duplicate detection
- [ ] Change tracking

## Backup & Restore (resetting your PC)
Back up before wiping:
- `data-factory/.env`
- Local artifacts you want to keep: `downloaded_images/` and `scraped_data.json`

Supabase data lives in the cloud, so your listings persist there.

Restore steps:
1. Recreate `data-factory/.env`.
2. `pip install -r requirements.txt` and run the CLI as needed.
