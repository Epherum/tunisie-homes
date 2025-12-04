import re
from typing import Dict, Optional, List

class DataNormalizer:
    """
    Normalizes and cleans scraped property data.
    - Maps to enum values for type safety
    - Extracts property types, listing types from titles
    - Cleans descriptions
    - Normalizes location data
    - Extracts room/bathroom counts and features
    """

    # Property type mapping to enum values
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

    # Feature keywords for extraction
    FEATURE_KEYWORDS = {
        'parking': ['parking', 'garage', 'stationnement', 'place de parking'],
        'elevator': ['ascenseur', 'lift'],
        'garden': ['jardin', 'green space', 'espace vert'],
        'pool': ['piscine', 'pool', 'swimming'],
        'balcony': ['balcon', 'terrasse', 'balcony'],
        'furnished': ['meublé', 'furnished', 'équipé'],
        'air_conditioning': ['climatisé', 'climatisation', 'clim', 'a/c', 'climatiseur'],
        'heating': ['chauffage', 'heating', 'chauffage central'],
        'security': ['gardé', 'sécurisé', 'security', 'concierge', 'gardien', 'résidence sécurisée'],
        'fiber': ['fibre', 'fiber', 'internet', 'wifi'],
    }

    def __init__(self):
        pass

    def normalize(self, property_data: Dict) -> Dict:
        """
        Main normalization function that cleans all fields and maps to new schema.
        """
        normalized = property_data.copy()

        # Map to enum values (NEW)
        normalized['propertyType'] = self._extract_property_type(property_data['title'])
        normalized['listingType'] = self._extract_listing_type(
            property_data.get('sourceUrl', ''),
            property_data['title'],
            property_data.get('description', '')
        )

        # Set source and status (NEW)
        normalized['source'] = normalized.get('source', 'TUNISIE_ANNONCE')
        normalized['status'] = 'ACTIVE'

        # Clean description
        if normalized.get('description'):
            normalized['description'] = self._clean_description(normalized['description'])

        # Normalize location data
        normalized['city'] = self._normalize_location(normalized.get('city'))
        normalized['region'] = self._normalize_location(normalized.get('region'))

        # Try to extract rooms/bathrooms from description if not set
        if not normalized.get('rooms') and normalized.get('description'):
            normalized['rooms'] = self._extract_rooms(normalized['description'], property_data['title'])

        if not normalized.get('bathrooms') and normalized.get('description'):
            normalized['bathrooms'] = self._extract_bathrooms(normalized['description'])

        # Extract features from description (NEW)
        normalized['features'] = self._extract_features(normalized.get('description', ''))

        # Calculate price per sqm if possible (NEW)
        if normalized.get('surfaceArea') and normalized.get('surfaceArea', 0) > 0:
            normalized['pricePerSqm'] = normalized['price'] / normalized['surfaceArea']

        # Detect if price is negotiable (NEW)
        if normalized.get('description'):
            normalized['isPriceNegotiable'] = self._is_price_negotiable(normalized['description'])

        # Ensure required fields have defaults
        normalized.setdefault('currency', 'TND')
        normalized.setdefault('price', 0.0)

        return normalized

    def _extract_property_type(self, title: str) -> Optional[str]:
        """
        Extract property type from title and return enum value.
        """
        title_lower = title.lower()

        for keyword, enum_value in self.PROPERTY_TYPE_MAP.items():
            if keyword.lower() in title_lower:
                return enum_value

        return None  # Will be stored as NULL

    def _extract_listing_type(self, url: str, title: str, description: str) -> str:
        """
        Determine if listing is for RENT or SALE.
        """
        text = f"{url} {title} {description}".lower()

        # Keywords for rent
        rent_keywords = ['louer', 'location', 'à louer', 'a louer', 'للكراء', 'للإيجار']
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

    def _extract_features(self, description: str) -> List[str]:
        """
        Extract features/amenities from description text.
        """
        if not description:
            return []

        features = []
        text_lower = description.lower()

        for feature, keywords in self.FEATURE_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                features.append(feature)

        return features

    def _is_price_negotiable(self, description: str) -> bool:
        """
        Detect if price is negotiable from description.
        """
        negotiable_keywords = ['négociable', 'negociable', 'à négocier', 'a negocier', 'قابل للتفاوض']
        text_lower = description.lower()

        return any(keyword in text_lower for keyword in negotiable_keywords)

    def _clean_description(self, description: str) -> str:
        """
        Clean and normalize description text.
        """
        # Remove excessive hashtags
        cleaned = re.sub(r'#(\w+)', r'\1', description)

        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Remove excessive punctuation
        cleaned = re.sub(r'([.!?])\1+', r'\1', cleaned)

        # Trim
        cleaned = cleaned.strip()

        return cleaned

    def _normalize_location(self, location: Optional[str]) -> Optional[str]:
        """
        Normalize location strings (capitalize properly, clean).
        """
        if not location:
            return None

        # Basic cleaning
        location = location.strip()

        # Capitalize first letter of each word
        location = location.title()

        return location

    def _extract_rooms(self, description: str, title: str) -> Optional[int]:
        """
        Try to extract number of rooms from description or title.
        Looks for patterns like:
        - "s+3", "s3", "s 3" (salon + 3 chambres)
        - "3 chambres"
        - "salon plus 3 chambres"
        """
        combined_text = f"{title} {description}".lower()

        # Pattern: s+3, s3, s 3 (Tunisian notation for apartments)
        match = re.search(r's\+?(\d+)', combined_text)
        if match:
            return int(match.group(1))

        # Pattern: "3 chambres" or "3 chambre"
        match = re.search(r'(\d+)\s*chambres?', combined_text)
        if match:
            return int(match.group(1))

        # Pattern: "salon plus 3 chambres"
        match = re.search(r'salon\s+plus\s+(\d+)', combined_text)
        if match:
            return int(match.group(1))

        return None

    def _extract_bathrooms(self, description: str) -> Optional[int]:
        """
        Try to extract number of bathrooms from description.
        """
        description_lower = description.lower()

        # Pattern: "2 salles de bain" or "2 sdb"
        match = re.search(r'(\d+)\s*salles?\s+de\s+bains?', description_lower)
        if match:
            return int(match.group(1))

        match = re.search(r'(\d+)\s*sdb', description_lower)
        if match:
            return int(match.group(1))

        # If "salle de bain" mentioned without number, assume 1
        if 'salle de bain' in description_lower or 'sdb' in description_lower:
            return 1

        return None

    def validate(self, property_data: Dict) -> bool:
        """
        Validate that required fields are present and valid for new schema.
        """
        # Required fields for new schema
        required_fields = ['sourceUrl', 'source', 'listingType', 'title']

        for field in required_fields:
            if not property_data.get(field):
                print(f"    Missing required field: {field}")
                return False

        # Validate price is non-negative
        if property_data.get('price', 0) < 0:
            print(f"    Invalid price: {property_data.get('price')}")
            return False

        return True
