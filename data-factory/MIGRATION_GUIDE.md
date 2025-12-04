# Data Factory Migration Guide

This guide shows what needs to be updated in the data factory to work with the new robust schema.

## Breaking Changes

### 1. Required Fields

**Old Schema**:
```python
payload = {
    "sourceUrl": url,
    "sourceName": "Tunisie Annonce",  # String
    "type": "Appartement"  # String (optional)
}
```

**New Schema**:
```python
payload = {
    "sourceUrl": url,
    "source": "TUNISIE_ANNONCE",  # Enum (required)
    "listingType": "RENT",  # Enum (required)
    "propertyType": "APARTMENT",  # Enum (optional)
    "status": "ACTIVE"  # Enum (required)
}
```

---

## Required Updates

### 1. Update `normalizer.py`

**Add Enum Mapping**:

```python
class DataNormalizer:

    # Mapping for property types
    PROPERTY_TYPE_MAP = {
        'appartement': 'APARTMENT',
        'appart': 'APARTMENT',
        'studio': 'STUDIO',
        's1': 'STUDIO',
        's2': 'APARTMENT',
        's3': 'APARTMENT',
        's4': 'APARTMENT',
        's+': 'APARTMENT',
        'maison': 'HOUSE',
        'villa': 'VILLA',
        'duplex': 'DUPLEX',
        'penthouse': 'PENTHOUSE',
        'terrain': 'LAND',
        'ارض': 'LAND',
        'أرض': 'LAND',
        'bureau': 'OFFICE',
        'local commercial': 'COMMERCIAL',
        'commercial': 'COMMERCIAL',
        'ferme': 'FARM',
        'مزرعة': 'FARM'
    }

    def _extract_property_type(self, title: str) -> Optional[str]:
        """Extract property type and return enum value."""
        title_lower = title.lower()

        for keyword, enum_value in self.PROPERTY_TYPE_MAP.items():
            if keyword.lower() in title_lower:
                return enum_value

        return None  # Will be stored as NULL

    def _extract_listing_type(self, url: str, title: str, description: str) -> str:
        """Determine if listing is for RENT or SALE."""
        text = f"{url} {title} {description}".lower()

        # Keywords for rent
        rent_keywords = ['louer', 'location', 'à louer', 'a louer', 'للكراء']
        # Keywords for sale
        sale_keywords = ['vendre', 'vente', 'à vendre', 'a vendre', 'للبيع']

        rent_score = sum(1 for kw in rent_keywords if kw in text)
        sale_score = sum(1 for kw in sale_keywords if kw in text)

        if rent_score > sale_score:
            return 'RENT'
        elif sale_score > rent_score:
            return 'SALE'
        else:
            # Default to SALE if ambiguous
            return 'SALE'

    def normalize(self, property_data: Dict) -> Dict:
        normalized = property_data.copy()

        # Map to enum values
        normalized['propertyType'] = self._extract_property_type(property_data['title'])
        normalized['listingType'] = self._extract_listing_type(
            property_data['sourceUrl'],
            property_data['title'],
            property_data.get('description', '')
        )

        # Set source and status
        normalized['source'] = 'TUNISIE_ANNONCE'  # Hardcode for this scraper
        normalized['status'] = 'ACTIVE'

        # Calculate price per sqm if possible
        if normalized.get('surfaceArea') and normalized.get('surfaceArea') > 0:
            normalized['pricePerSqm'] = normalized['price'] / normalized['surfaceArea']

        # ... rest of normalization
        return normalized
```

---

### 2. Update `db_client.py`

**Add New Required Fields**:

```python
def upsert_property(self, property_data):
    try:
        now = datetime.utcnow().isoformat()
        payload = {
            # Core (NEW: required fields)
            "sourceUrl": property_data['sourceUrl'],
            "source": property_data.get('source', 'TUNISIE_ANNONCE'),
            "listingType": property_data['listingType'],  # Required!
            "status": property_data.get('status', 'ACTIVE'),

            # Basic info
            "title": property_data['title'],
            "description": property_data.get('description'),
            "price": property_data['price'],
            "currency": property_data.get('currency', 'TND'),

            # Location
            "city": property_data.get('city'),
            "region": property_data.get('region'),
            "latitude": property_data.get('latitude'),
            "longitude": property_data.get('longitude'),

            # Property details
            "propertyType": property_data.get('propertyType'),
            "surfaceArea": property_data.get('surfaceArea'),
            "rooms": property_data.get('rooms'),
            "bathrooms": property_data.get('bathrooms'),
            "pricePerSqm": property_data.get('pricePerSqm'),

            # Features
            "features": property_data.get('features', []),

            # AI fields (populated later)
            "renovationScore": property_data.get('renovationScore'),
            "dealRating": property_data.get('dealRating'),
            "aiTags": property_data.get('aiTags', []),

            # Timestamps
            "updatedAt": now,
            "scrapedAt": now,
        }

        # Handle embeddings
        if property_data.get('descriptionEmbedding'):
            embedding_str = self._format_vector(property_data['descriptionEmbedding'])
            payload['descriptionEmbedding'] = embedding_str

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        # Upsert logic...
        # ... rest of code
```

---

### 3. Update `scrapers/tunisie_annonce.py`

**Add Listing Type Detection**:

```python
def extract_details(self, html, url):
    soup = BeautifulSoup(html, 'html.parser')
    data = {
        'sourceUrl': url,
        'source': 'TUNISIE_ANNONCE',  # NEW
        'title': '',
        'description': '',
        'price': 0.0,
        'currency': 'TND',
        # ... rest of fields
    }

    # Extract title
    title_tag = soup.find('tr', class_='da_entete')
    if title_tag:
        data['title'] = title_tag.get_text(strip=True)

    # Extract description
    desc = get_field_text('Texte')
    if desc:
        data['description'] = desc

    # Determine listing type from URL or description
    if 'location' in url.lower() or 'louer' in data['title'].lower():
        data['listingType'] = 'RENT'
    else:
        data['listingType'] = 'SALE'

    # ... rest of extraction

    return data
```

---

### 4. Add Features Extraction

**Extract amenities from description**:

```python
def _extract_features(self, description: str) -> list[str]:
    """Extract features from description text."""
    if not description:
        return []

    features = []
    text_lower = description.lower()

    feature_keywords = {
        'parking': ['parking', 'garage', 'stationnement'],
        'elevator': ['ascenseur', 'lift'],
        'garden': ['jardin', 'green space'],
        'pool': ['piscine', 'pool', 'swimming'],
        'balcony': ['balcon', 'terrasse', 'balcony'],
        'furnished': ['meublé', 'furnished', 'équipé'],
        'air_conditioning': ['climatisé', 'climatisation', 'clim', 'a/c'],
        'heating': ['chauffage', 'heating'],
        'security': ['gardé', 'sécurisé', 'security', 'concierge'],
        'fiber': ['fibre', 'fiber', 'internet'],
    }

    for feature, keywords in feature_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            features.append(feature)

    return features

# In normalize():
normalized['features'] = self._extract_features(property_data.get('description', ''))
```

---

## New Modules to Create

### 1. `geocoding.py` (For lat/lng)

```python
import requests
from typing import Optional, Tuple

class Geocoder:
    """Geocode Tunisian addresses using Nominatim."""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'TunisHome/1.0 (contact@example.com)'
        }

    def geocode(self, city: str, region: str = None) -> Optional[Tuple[float, float]]:
        """
        Convert city/region to lat/lng.
        Returns (latitude, longitude) or None.
        """
        if not city:
            return None

        # Build query
        query = f"{city}"
        if region:
            query += f", {region}"
        query += ", Tunisia"

        try:
            response = requests.get(
                self.base_url,
                params={
                    'q': query,
                    'format': 'json',
                    'limit': 1
                },
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 200 and response.json():
                result = response.json()[0]
                return (float(result['lat']), float(result['lon']))

        except Exception as e:
            print(f"Geocoding error for {query}: {e}")

        return None

# Usage in main.py or normalizer.py:
geocoder = Geocoder()
lat, lng = geocoder.geocode(property_data['city'], property_data['region'])
if lat and lng:
    property_data['latitude'] = lat
    property_data['longitude'] = lng
```

**Note**: Nominatim has rate limits (1 req/sec). Add `time.sleep(1)` between requests.

---

### 2. `price_analyzer.py` (For deal rating)

```python
from db_client import DBClient

class PriceAnalyzer:
    """Calculate deal ratings based on neighborhood stats."""

    def __init__(self, db_client: DBClient):
        self.db = db_client

    def calculate_deal_rating(self, property_data: dict) -> Optional[float]:
        """
        Calculate deal rating (0-100).
        Higher = better deal (underpriced).
        """
        city = property_data.get('city')
        surface = property_data.get('surfaceArea')
        price = property_data.get('price')

        if not all([city, surface, price]) or surface == 0:
            return None

        price_per_sqm = price / surface

        # Get neighborhood average
        avg_price_per_sqm = self._get_neighborhood_avg(city)
        if not avg_price_per_sqm:
            return None

        # Calculate discount percentage
        discount = ((avg_price_per_sqm - price_per_sqm) / avg_price_per_sqm) * 100

        # Convert to 0-100 scale
        # +20% discount = 100 rating (great deal)
        # 0% discount = 50 rating (fair price)
        # -20% overpriced = 0 rating (bad deal)
        deal_rating = 50 + (discount * 2.5)
        deal_rating = max(0, min(100, deal_rating))

        return round(deal_rating, 1)

    def _get_neighborhood_avg(self, city: str) -> Optional[float]:
        """Get average price/sqm for a city."""
        try:
            result = self.db.supabase.table("NeighborhoodStats") \
                .select("avgPricePerSqm") \
                .eq("city", city) \
                .execute()

            if result.data:
                return result.data[0]['avgPricePerSqm']

        except Exception as e:
            print(f"Error getting neighborhood stats: {e}")

        return None

    def update_neighborhood_stats(self):
        """Recalculate stats for all neighborhoods."""
        # Query all properties grouped by city
        # Calculate averages
        # Upsert to NeighborhoodStats table
        # ... implementation
```

---

## Testing the Migration

### 1. Test Data Transformation

```python
# test_migration.py
from normalizer import DataNormalizer

normalizer = DataNormalizer()

# Old format data
old_data = {
    'sourceUrl': 'http://test.com/1',
    'sourceName': 'Tunisie Annonce',
    'title': 'Appartement S+2 à louer',
    'type': 'Appartement',
    'price': 1000,
    'surfaceArea': 100
}

# Normalize to new format
new_data = normalizer.normalize(old_data)

# Check required fields
assert new_data['source'] == 'TUNISIE_ANNONCE'
assert new_data['listingType'] == 'RENT'  # Detected from title
assert new_data['propertyType'] == 'APARTMENT'
assert new_data['status'] == 'ACTIVE'
assert new_data['pricePerSqm'] == 10.0

print("✓ Migration test passed!")
```

### 2. Run Test Migration

```bash
# Backup existing data first!
pg_dump -h your-host -U postgres -d postgres -t properties > backup.sql

# Run migration
cd data-factory
python main.py --max-listings 2  # Test with 2 listings

# Check database
# Should see new fields populated
```

---

## Rollback Plan

If migration fails:

```bash
# Restore from backup
psql -h your-host -U postgres -d postgres < backup.sql

# Revert schema
cd frontend
git checkout HEAD~1 prisma/schema.prisma
npx prisma db push --force-reset
```

---

## Summary of Changes

| File | Changes Required |
|------|------------------|
| `normalizer.py` | ✅ Add enum mapping, listing type detection, features extraction |
| `db_client.py` | ✅ Add new required fields to payload |
| `scrapers/tunisie_annonce.py` | ✅ Add listing type detection |
| `main.py` | ✅ Add geocoding step (optional for now) |
| **NEW**: `geocoding.py` | 🆕 Create for lat/lng population |
| **NEW**: `price_analyzer.py` | 🆕 Create for deal rating calculation |

**Priority**:
1. **High**: Update normalizer & db_client (required for schema compatibility)
2. **Medium**: Add geocoding (needed for map)
3. **Low**: Add price analyzer (can be done after initial data load)
