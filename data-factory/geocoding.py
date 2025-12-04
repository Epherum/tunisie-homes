import requests
import time
from typing import Optional, Tuple, Dict
from datetime import datetime

class Geocoder:
    """
    Geocode Tunisian addresses using Nominatim (OpenStreetMap).

    Rate Limits: 1 request per second (strict)
    Documentation: https://nominatim.org/release-docs/develop/api/Search/
    """

    def __init__(self, user_agent: str = "TunisHome/1.0"):
        """
        Initialize geocoder.

        Args:
            user_agent: User agent string (required by Nominatim)
        """
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': user_agent
        }
        self.last_request_time = 0
        self.cache = {}  # Simple in-memory cache

    def geocode(self, city: str, region: str = None, country: str = "Tunisia") -> Optional[Tuple[float, float]]:
        """
        Convert city/region to latitude/longitude coordinates.

        Args:
            city: City name (e.g., "L'Aouina", "Tunis")
            region: Region/governorate (e.g., "Ariana", "Tunis")
            country: Country name (default: "Tunisia")

        Returns:
            (latitude, longitude) tuple or None if geocoding fails
        """
        if not city:
            return None

        # Check cache first
        cache_key = self._make_cache_key(city, region, country)
        if cache_key in self.cache:
            print(f"Geocoding cache hit: {cache_key}")
            return self.cache[cache_key]

        # Build query
        query = self._build_query(city, region, country)

        try:
            # Respect rate limit (1 req/sec)
            self._respect_rate_limit()

            # Make request
            response = requests.get(
                self.base_url,
                params={
                    'q': query,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'tn',  # Restrict to Tunisia
                    'addressdetails': 1
                },
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            results = response.json()

            if results and len(results) > 0:
                result = results[0]
                lat = float(result['lat'])
                lon = float(result['lon'])

                # Cache the result
                self.cache[cache_key] = (lat, lon)

                print(f"Geocoded: {query} -> ({lat}, {lon})")
                return (lat, lon)
            else:
                print(f"No results for: {query}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Geocoding error for {query}: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error parsing geocoding response for {query}: {e}")
            return None

    def geocode_batch(self, locations: list[Dict[str, str]]) -> Dict[str, Tuple[float, float]]:
        """
        Geocode multiple locations with rate limiting.

        Args:
            locations: List of dicts with 'city' and optional 'region' keys

        Returns:
            Dict mapping cache_key to (lat, lon) tuples
        """
        results = {}
        total = len(locations)

        for i, location in enumerate(locations, 1):
            city = location.get('city')
            region = location.get('region')

            if not city:
                continue

            print(f"[{i}/{total}] Geocoding: {city}, {region}")

            coords = self.geocode(city, region)
            if coords:
                cache_key = self._make_cache_key(city, region)
                results[cache_key] = coords

        return results

    def _build_query(self, city: str, region: str = None, country: str = "Tunisia") -> str:
        """
        Build search query for Nominatim.
        """
        parts = [city]

        if region:
            parts.append(region)

        parts.append(country)

        return ", ".join(parts)

    def _make_cache_key(self, city: str, region: str = None, country: str = "Tunisia") -> str:
        """
        Create cache key from location components.
        """
        key = city.lower().strip()

        if region:
            key += f"_{region.lower().strip()}"

        return key

    def _respect_rate_limit(self):
        """
        Ensure we don't exceed 1 request per second (Nominatim requirement).
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        # If less than 1 second has passed, wait
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.
        """
        return {
            'cached_locations': len(self.cache),
            'locations': list(self.cache.keys())
        }


# Tunisia-specific location normalization
class TunisiaLocationNormalizer:
    """
    Normalize Tunisian location names for better geocoding results.
    """

    # Common variations and their standardized forms
    LOCATION_ALIASES = {
        # Cities
        'l\'aouina': 'La Marsa',
        'aouina': 'La Marsa',
        'menzah': 'El Menzah',
        'manar': 'El Manar',
        'soukra': 'La Soukra',
        'ariana': 'Ariana',
        'mnihla': 'Mnihla',
        'bizerte nord': 'Bizerte',
        'bizerte': 'Bizerte',

        # Regions (Governorates)
        'tunis': 'Tunis',
        'ariana': 'Ariana',
        'ben arous': 'Ben Arous',
        'manouba': 'Manouba',
        'bizerte': 'Bizerte',
        'nabeul': 'Nabeul',
        'sousse': 'Sousse',
    }

    @staticmethod
    def normalize(location: str) -> str:
        """
        Normalize location name.
        """
        if not location:
            return location

        location_lower = location.lower().strip()

        # Check if we have a known alias
        if location_lower in TunisiaLocationNormalizer.LOCATION_ALIASES:
            return TunisiaLocationNormalizer.LOCATION_ALIASES[location_lower]

        # Return title-cased version
        return location.title()
