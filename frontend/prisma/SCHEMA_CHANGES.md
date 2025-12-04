# Schema Changes & PRD Alignment

## Major Additions

### 1. Enums for Type Safety
**Why**: Prevents invalid data, improves type safety, better performance

- `PropertyType`: APARTMENT, HOUSE, VILLA, DUPLEX, STUDIO, PENTHOUSE, LAND, COMMERCIAL, OFFICE, FARM
- `ListingType`: RENT, SALE (critical for filtering)
- `PropertyStatus`: ACTIVE, SOLD, RENTED, INACTIVE (FR requirement)
- `DataSource`: TUNISIE_ANNONCE, USER_UPLOAD, TAYARA, MUBAWAB (track origin)

### 2. Enhanced Property Model

#### Pricing Intelligence (FR-05)
```prisma
pricePerSqm        Float?  // Auto-calculated for comparisons
estimatedFairValue Float?  // AI-predicted market value
isPriceNegotiable  Boolean // Scraped from "Prix négociable"
```

#### Location (PostGIS Support)
```prisma
location Unsupported("geometry(Point, 4326)")? // PostGIS point for spatial queries
```
- Enables distance queries: "Properties within 5km of downtown"
- Supports heatmap generation (FR-09)
- Indexed for fast geo-lookups

#### Property Details
```prisma
floor        Int?  // "3ème étage"
totalFloors  Int?  // "sur 5 étages"
features     String[] // ["parking", "elevator", "garden"]
```

#### Source Tracking (PRD Section 4.1)
```prisma
source       DataSource         // TUNISIE_ANNONCE vs USER_UPLOAD
status       PropertyStatus     // ACTIVE/SOLD/RENTED
scrapedAt    DateTime          // When data was collected
analyzedAt   DateTime?         // When AI analysis completed
```

#### AI Intelligence (FR-04, FR-05, FR-06)
```prisma
aiDescription        String? // Gemini-enhanced description
descriptionEmbedding vector(768) // For semantic search
```

#### User Uploads (FR-07)
```prisma
contactPhone   String?
contactEmail   String?
contactName    String?
```

#### Analytics
```prisma
views          Int      @default(0)
isFeatured     Boolean  @default(false)
```

### 3. Enhanced Image Model

```prisma
localPath        String?  // Path to downloaded image
caption          String?  // AI-generated or user-provided
order            Int      // Display order
width/height     Int?     // For responsive loading

// Per-Image AI Analysis (Ollama)
analyzedAt       DateTime?
aiTags           String[] // ["modern_kitchen", "marble_floors"]
renovationScore  Float?   // 0-10 per image
```

**Why**: Each room can have different renovation levels. Kitchen might be 9/10, bathroom 4/10.

### 4. AIAnalysis Model (NEW)

**Purpose**: Track all AI operations for debugging and improvement

```prisma
modelUsed     String   // "ollama-llama3.2-vision" or "gemini-1.5-flash"
analysisType  String   // "renovation_score", "price_prediction"
result        Json     // Flexible storage
confidence    Float?   // Model confidence
```

**Use Cases**:
- Audit trail: "Why did we rate this 8/10?"
- A/B testing: Compare Ollama vs Gemini results
- Cost tracking: Count Gemini API calls
- Debug: "Model thought this was modern but it's clearly old"

### 5. NeighborhoodStats Model (NEW)

**Purpose**: Power the price prediction (FR-05)

```prisma
city            String
region          String?
avgPricePerSqm  Float    // Key metric for deal rating
medianPrice     Float
totalListings   Int
activeListings  Int
avgRentPrice    Float?   // Separate rent/sale markets
avgSalePrice    Float?
```

**How It Works**:
1. Scraper collects 100 listings in "L'Aouina"
2. Calculate: avgPricePerSqm = 2,500 TND/m²
3. New listing: 100m² for 200,000 TND = 2,000 TND/m²
4. **Deal Rating**: ((2500 - 2000) / 2500) * 100 = 20% below market → Green Deal!

### 6. Performance Indexes

Added 10+ indexes for common queries:
- `@@index([dealRating])` - Sort by best deals
- `@@index([listingType])` - Filter rent vs sale
- `@@index([propertyType])` - Filter apartments vs houses
- `@@index([status])` - Show only active listings
- `@@index([source])` - Filter scraped vs user uploads
- `@@index([latitude, longitude])` - Map viewport queries
- `@@index([rooms, bathrooms])` - Bedroom/bath filters

### 7. PostGIS Extension

```prisma
extensions = [postgis, ...]
```

**Enables**:
- Distance queries: `ST_DWithin(location, ST_MakePoint(lat, lng), 5000)`
- Heatmaps: `ST_HexagonGrid()` for density visualization
- Neighborhood boundaries: Polygon containment checks

## Breaking Changes

### Required Fields Now
- `listingType` (RENT or SALE) - **must be set**
- `source` (DataSource enum) - **must be set**

### Renamed/Removed
- `sourceName` → now `source` (enum instead of string)
- `type` → now `propertyType` (enum instead of string)

## Migration Strategy

### For Existing Data (10 properties)
```sql
-- Set required fields with defaults
UPDATE properties SET
  listing_type = 'SALE',  -- Default to SALE
  source = 'TUNISIE_ANNONCE';

-- Map old type strings to enums
UPDATE properties SET property_type =
  CASE
    WHEN type ILIKE '%appartement%' THEN 'APARTMENT'
    WHEN type ILIKE '%maison%' THEN 'HOUSE'
    WHEN type ILIKE '%villa%' THEN 'VILLA'
    WHEN type ILIKE '%terrain%' THEN 'LAND'
    WHEN type ILIKE '%duplex%' THEN 'DUPLEX'
    ELSE NULL
  END;
```

### For Data Factory Scripts

Update `db_client.py` to use new fields:
```python
payload = {
    "listingType": "SALE",  # or "RENT" based on URL
    "source": "TUNISIE_ANNONCE",
    "status": "ACTIVE",
    "propertyType": map_to_enum(extracted_type),
    # ... rest of fields
}
```

## SQL Scripts to Run

### 1. Enable PostGIS
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. Create Spatial Index (after migration)
```sql
CREATE INDEX idx_properties_location ON properties USING GIST(location);
```

### 3. Update Stats Function (for price predictions)
```sql
CREATE OR REPLACE FUNCTION update_neighborhood_stats()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO neighborhood_stats (city, region, avg_price_per_sqm, median_price, total_listings, active_listings)
  SELECT
    city,
    region,
    AVG(price / NULLIF(surface_area, 0)) as avg_price_per_sqm,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price,
    COUNT(*) as total_listings,
    COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_listings
  FROM properties
  WHERE city IS NOT NULL AND surface_area > 0
  GROUP BY city, region
  ON CONFLICT (city, region)
  DO UPDATE SET
    avg_price_per_sqm = EXCLUDED.avg_price_per_sqm,
    median_price = EXCLUDED.median_price,
    total_listings = EXCLUDED.total_listings,
    active_listings = EXCLUDED.active_listings,
    updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_stats
AFTER INSERT OR UPDATE ON properties
FOR EACH ROW
EXECUTE FUNCTION update_neighborhood_stats();
```

## PRD Compliance Checklist

- ✅ **FR-01**: Scraper support (already working)
- ✅ **FR-02**: Encoding handled (already working)
- ✅ **FR-03**: Normalization (schema ready, needs geocoding implementation)
- ✅ **FR-04**: Computer Vision (schema ready: `renovationScore`, `aiTags`)
- ✅ **FR-05**: Price Prediction (schema ready: `dealRating`, `NeighborhoodStats`)
- ✅ **FR-06**: Semantic Search (schema ready: `descriptionEmbedding`)
- ✅ **FR-07**: Smart Auto-Fill (schema ready: contact fields, user upload tracking)
- ✅ **FR-08**: Map Interface (PostGIS support added)
- ✅ **FR-09**: Heatmap Mode (PostGIS + spatial indexes)
- ✅ **Status Tracking**: `PropertyStatus` enum
- ✅ **Source Tracking**: `DataSource` enum

## Performance Estimates (200 Listings)

### Database Size
- Properties: ~200 rows × 2KB = 400KB
- Images: ~800 images × 500 bytes = 400KB
- Embeddings: 200 × 768 floats × 4 bytes = 600KB
- **Total**: ~2MB (negligible)

### Query Performance
With proper indexes:
- Map viewport (50 properties): <50ms
- Full-text search: <100ms
- Vector similarity (semantic search): <200ms
- Price range filter: <10ms

### Recommended Indexes Created
All critical queries will use indexes, no full table scans.
