import os
import mimetypes
from io import BytesIO
from typing import Optional, List
from urllib.parse import urlparse
from datetime import datetime
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DBClient:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")
        self.storage_bucket = os.environ.get("STORAGE_BUCKET")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")

        self.supabase: Client = create_client(url, key)
        self.supabase_url = url.rstrip("/")
        print("Database client initialized")

    def upsert_property(self, property_data, sync_images: bool = True, image_urls: Optional[List[str]] = None):
        """
        Upsert a property to the database.
        Handles property data, images, and embeddings with new schema.
        """
        try:
            # Prepare Property payload matching NEW Prisma schema
            now = datetime.utcnow().isoformat()
            payload = {
                # Core (REQUIRED fields)
                "sourceUrl": property_data['sourceUrl'],
                "source": property_data.get('source', 'TUNISIE_ANNONCE'),
                "listingType": property_data['listingType'],  # REQUIRED!
                "status": property_data.get('status', 'ACTIVE'),
                "title": property_data['title'],
                "price": property_data['price'],

                # Basic info
                "description": property_data.get('description'),
                "currency": property_data.get('currency', 'TND'),
                "contactPhone": property_data.get('phone'),
                "contactEmail": property_data.get('email'),

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

                # Pricing (NEW)
                "pricePerSqm": property_data.get('pricePerSqm'),
                "isPriceNegotiable": property_data.get('isPriceNegotiable', False),

                # Features (NEW)
                "features": property_data.get('features', []),

                # AI fields (populated later by AI modules)
                "renovationScore": property_data.get('renovationScore'),
                "dealRating": property_data.get('dealRating'),
                "aiTags": property_data.get('aiTags', []),
                "aiDescription": property_data.get('aiDescription'),

                # Timestamps
                "updatedAt": now,
                "scrapedAt": now,
            }

            # Add embedding if available
            if property_data.get('descriptionEmbedding'):
                # Convert list to PostgreSQL vector format
                embedding_str = self._format_vector(property_data['descriptionEmbedding'])
                payload['descriptionEmbedding'] = embedding_str

            # Remove None values to let DB defaults handle them
            payload = {k: v for k, v in payload.items() if v is not None}

            # Check if property exists first
            existing = self.supabase.table("properties").select("id").eq("sourceUrl", payload["sourceUrl"]).execute()
            is_update = bool(existing.data and len(existing.data) > 0)

            # Preserve original scrapedAt on updates
            if is_update and "scrapedAt" in payload:
                payload.pop("scrapedAt", None)

            if existing.data and len(existing.data) > 0:
                # Update existing property
                property_id = existing.data[0]['id']
                response = self.supabase.table("properties").update(payload).eq("id", property_id).execute()
            else:
                # Insert new property (let DB generate ID)
                response = self.supabase.table("properties").insert(payload).execute()

            if response.data:
                property_id = response.data[0]['id']

                if sync_images:
                    images_to_sync = image_urls if image_urls is not None else property_data.get('images', [])
                    self.sync_images(property_id, images_to_sync)

                # Safe print with encoding handling
                try:
                    title_preview = property_data['title'][:50]
                    print(f"Upserted property: {title_preview}... (ID: {property_id})")
                except UnicodeEncodeError:
                    print(f"Upserted property (ID: {property_id})")
                return property_id

        except Exception as e:
            try:
                print(f"Error upserting {property_data.get('sourceUrl', 'unknown')}: {e}")
            except UnicodeEncodeError:
                print(f"Error upserting property: {e}")
            return None

    def sync_images(self, property_id: str, image_urls: List[str]):
        """
        Replace image rows for a property.
        """
        # Delete existing images for this property first
        self.supabase.table("images").delete().eq("propertyId", property_id).execute()

        if image_urls:
            image_payloads = [
                {"url": img_url, "propertyId": property_id}
                for img_url in image_urls
            ]
            self.supabase.table("images").insert(image_payloads).execute()

    def upload_images_to_storage(self, property_id: str, image_urls: List[str]) -> List[str]:
        """
        Upload images to Supabase Storage and return their public URLs.
        """
        if not image_urls:
            return []

        if not self.storage_bucket:
            print("STORAGE_BUCKET is not set; skipping Storage upload")
            return []

        storage_client = self.supabase.storage.from_(self.storage_bucket)
        uploaded_urls: List[str] = []

        for idx, url in enumerate(image_urls):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip()
                content_type = content_type or "image/jpeg"

                extension = self._get_extension(url, content_type)
                storage_path = f"properties/{property_id}/{idx:02d}{extension}"

                storage_client.upload(
                    storage_path,
                    response.content,
                    {
                        "content-type": content_type,
                        "upsert": "true",
                    },
                )

                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.storage_bucket}/{storage_path}"
                uploaded_urls.append(public_url)
                print(f"  Uploaded image {idx + 1}/{len(image_urls)}")

            except Exception as e:
                print(f"  Failed to upload image {url}: {e}")
                continue

        return uploaded_urls

    def _format_vector(self, vector: List[float]) -> str:
        """
        Format a vector list as a PostgreSQL vector string.
        Example: [0.1, 0.2, 0.3] -> '[0.1,0.2,0.3]'
        """
        return '[' + ','.join(str(v) for v in vector) + ']'

    def _get_extension(self, url: str, content_type: Optional[str] = None) -> str:
        """
        Extract file extension from URL or content type, default to .jpg
        """
        path = urlparse(url).path.lower()
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            if path.endswith(ext):
                return ext

        if content_type:
            guessed = mimetypes.guess_extension(content_type)
            if guessed:
                return guessed

        return '.jpg'

    def property_exists(self, source_url: str) -> bool:
        """
        Check if a property already exists in the database.
        """
        try:
            response = self.supabase.table("properties").select("id").eq("sourceUrl", source_url).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking property existence: {e}")
            return False

    def get_property_count(self) -> int:
        """
        Get total count of properties in database.
        """
        try:
            response = self.supabase.table("properties").select("id", count="exact").execute()
            return response.count
        except Exception as e:
            print(f"Error getting property count: {e}")
            return 0
