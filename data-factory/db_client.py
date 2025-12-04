import os
from typing import Optional, List
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DBClient:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")

        self.supabase: Client = create_client(url, key)
        print("Database client initialized")

    def upsert_property(self, property_data):
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

            if existing.data and len(existing.data) > 0:
                # Update existing property
                property_id = existing.data[0]['id']
                response = self.supabase.table("properties").update(payload).eq("id", property_id).execute()
            else:
                # Insert new property (let DB generate ID)
                response = self.supabase.table("properties").insert(payload).execute()

            if response.data:
                property_id = response.data[0]['id']

                # Handle Images
                # Delete existing images for this property first
                self.supabase.table("images").delete().eq("propertyId", property_id).execute()

                # Insert new images
                if property_data.get('images'):
                    image_payloads = [
                        {"url": img_url, "propertyId": property_id}
                        for img_url in property_data['images']
                    ]
                    self.supabase.table("images").insert(image_payloads).execute()

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

    def _format_vector(self, vector: List[float]) -> str:
        """
        Format a vector list as a PostgreSQL vector string.
        Example: [0.1, 0.2, 0.3] -> '[0.1,0.2,0.3]'
        """
        return '[' + ','.join(str(v) for v in vector) + ']'

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
