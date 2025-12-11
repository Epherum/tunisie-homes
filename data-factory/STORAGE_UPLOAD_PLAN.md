# Populate Supabase Storage for listing images

Current state:
- `image_downloader.py` saves files locally when `--download-images` is used, but nothing is pushed to Supabase Storage.
- `DBClient.upsert_property` inserts the original scraped URLs into the `images` table; it never uploads files or rewrites URLs.
- Local download paths are keyed by `hash(sourceUrl)` (before DB insert), so they don’t line up with the real `property_id`.

Result: the Storage bucket stays empty and the frontend shows “no photo” unless origin URLs still work and RLS permits them.

What to implement
-----------------
1) **Upload to Storage after you have the real property_id.**  
   Flow: scrape → normalize → upsert property → get `property_id` → upload images to `properties/{property_id}/{filename}`.

2) **Use the Supabase Python storage client with the service role key.**  
   Required env: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `STORAGE_BUCKET` (e.g., `property-images`).  
   Upload either the streamed response from the source URL or the locally downloaded file. Fetch the public URL via `storage.from(bucket).get_public_url(path)` (or use CDN if configured).

3) **Stop using `hash(sourceUrl)` for image folders.**  
   Use the actual `property_id` returned from `upsert_property` so paths are stable and idempotent.

4) **Add a flag to control uploads.**  
   Example: `--upload-images` (likely alongside `--download-images`). When set, perform the Storage uploads and store the resulting public URLs in the `images` table.

5) **Keep the `images` table in sync with Storage URLs.**  
   After uploading, delete existing rows for the property and insert rows with the Storage public URLs (and optionally keep original URLs as a separate column if needed).

6) **RLS sanity check.**  
   Ensure anon can `select` from `properties`/`images` or expose via a service role/edge function. Otherwise the frontend/admin will look empty even with populated data.

Optional backfill
-----------------
Write a one-off script to:
1) Read existing `images.url` rows (source URLs).  
2) Download or stream each image, upload to Storage under `properties/{propertyId}/`.  
3) Update `images.url` to the new Storage public URL (or add a new column if you want both).  
This backfills the bucket from current DB data.
