import os
import time
import argparse
from dotenv import load_dotenv
from scrapers.tunisie_annonce import TunisieAnnonceScraper
from db_client import DBClient
from normalizer import DataNormalizer
from image_downloader import ImageDownloader
from embeddings import EmbeddingGenerator, MockEmbeddingGenerator
from geocoding import Geocoder

# Load environment variables
load_dotenv()

def main():
    """
    Main data factory pipeline:
    1. Scrape properties from tunisie-annonce.com
    2. Normalize and clean data
    3. Geocode locations (lat/lng)
    4. Download images (optional)
    5. Generate embeddings (optional)
    6. Push to Supabase database
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TunisHome Data Factory")
    parser.add_argument("--max-listings", type=int, default=5, help="Maximum number of listings to scrape")
    parser.add_argument("--download-images", action="store_true", help="Download images locally")
    parser.add_argument("--upload-images", action="store_true", help="Upload images to Supabase Storage")
    parser.add_argument("--generate-embeddings", action="store_true", help="Generate embeddings for properties")
    parser.add_argument("--embedding-provider", choices=["gemini", "openai"], default="gemini", help="Embedding provider")
    parser.add_argument("--skip-geocoding", action="store_true", help="Skip geocoding step (faster for testing)")
    args = parser.parse_args()

    print("=" * 60)
    print("TunisHome Pro Data Factory")
    print("=" * 60)

    # Check if we have required credentials
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_KEY"):
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY are required.")
        print("Please add them to data-factory/.env")
        return

    # Initialize components
    print("\nInitializing components...")
    db = DBClient()
    scraper = TunisieAnnonceScraper()
    normalizer = DataNormalizer()

    # Geocoder (always initialized, but can be skipped)
    geocoder = Geocoder(user_agent="TunisHome/1.0 (contact@tunishome.com)")
    if args.skip_geocoding:
        print("Geocoding disabled (--skip-geocoding)")
    else:
        print("Geocoding enabled (Nominatim)")

    # Optional: Image downloader
    image_downloader = None
    if args.download_images:
        image_downloader = ImageDownloader(output_dir="downloaded_images")
        print("Image downloader enabled")
    elif args.upload_images:
        print("Image downloader disabled (uploading directly from source URLs)")

    if args.upload_images and not os.environ.get("STORAGE_BUCKET"):
        print("Warning: STORAGE_BUCKET is not set; Storage uploads will be skipped")

    # Optional: Embedding generator
    embedding_generator = None
    if args.generate_embeddings:
        try:
            embedding_generator = EmbeddingGenerator(provider=args.embedding_provider)
            print(f"Embedding generator enabled ({args.embedding_provider})")
        except Exception as e:
            print(f"Warning: Could not initialize embedding generator: {e}")
            print("Continuing without embeddings...")

    # Step 1: Scrape properties
    print(f"\nScraping properties (max: {args.max_listings})...")
    properties = scraper.run(max_pages=1, max_listings=args.max_listings)
    print(f"Found {len(properties)} properties")

    if not properties:
        print("No properties found. Exiting.")
        return

    # Step 2: Process each property
    print("\nProcessing properties...")
    processed_count = 0

    for i, property_data in enumerate(properties, 1):
        try:
            title_preview = property_data['title'][:50]
            print(f"\n[{i}/{len(properties)}] Processing: {title_preview}...")
        except UnicodeEncodeError:
            print(f"\n[{i}/{len(properties)}] Processing property...")

        try:
            image_urls = property_data.get('images', [])

            # Normalize and clean data
            property_data = normalizer.normalize(property_data)

            # Validate data
            if not normalizer.validate(property_data):
                print(f"  Skipping invalid property data")
                continue

            # Geocode location if enabled
            if not args.skip_geocoding and property_data.get('city'):
                city = property_data.get('city')
                region = property_data.get('region')

                print(f"  Geocoding: {city}, {region}...")
                coords = geocoder.geocode(city, region)

                if coords:
                    property_data['latitude'] = coords[0]
                    property_data['longitude'] = coords[1]
                    print(f"  Location: ({coords[0]:.4f}, {coords[1]:.4f})")
                else:
                    print(f"  Could not geocode location")

            # Generate embedding if enabled
            if embedding_generator:
                print(f"  Generating embedding...")
                embedding = embedding_generator.generate_property_embedding(property_data)
                if embedding:
                    property_data['descriptionEmbedding'] = embedding
                    print(f"  Generated {len(embedding)}-dimensional embedding")
                else:
                    print(f"  Could not generate embedding")

            # Push to database
            print(f"  Saving to database...")
            should_upload_images = bool(args.upload_images and image_urls)

            # When uploading, skip syncing images on the initial upsert so we can replace them with Storage URLs
            property_id = db.upsert_property(
                property_data,
                sync_images=not should_upload_images,
                image_urls=None if should_upload_images else image_urls
            )

            if property_id:
                if image_downloader and image_urls:
                    print(f"  Downloading {len(image_urls)} images...")
                    local_paths = image_downloader.download_images(
                        image_urls,
                        str(property_id)
                    )
                    print(f"  Downloaded {len(local_paths)} images")

                if should_upload_images:
                    print(f"  Uploading images to storage ({len(image_urls)})...")
                    uploaded_urls = db.upload_images_to_storage(property_id, image_urls)
                    if uploaded_urls:
                        db.sync_images(property_id, uploaded_urls)
                        print(f"  Synced {len(uploaded_urls)} images to database")
                    else:
                        print("  No images uploaded; skipping image sync")

                processed_count += 1

            # Be polite to the database
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error processing property: {e}")
            continue

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline completed!")
    print(f"Processed: {processed_count}/{len(properties)} properties")

    # Show database stats
    total_properties = db.get_property_count()
    print(f"Total in database: {total_properties} properties")
    print("=" * 60)

if __name__ == "__main__":
    main()
