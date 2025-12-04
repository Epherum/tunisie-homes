import os
import requests
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
import time

class ImageDownloader:
    """
    Downloads images from URLs and saves them locally.
    Generates unique filenames based on URL hash to avoid duplicates.
    """

    def __init__(self, output_dir: str = "downloaded_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def download_images(self, image_urls: List[str], property_id: str) -> List[str]:
        """
        Download images for a property and return local file paths.

        Args:
            image_urls: List of image URLs to download
            property_id: Unique property identifier (used for organizing files)

        Returns:
            List of local file paths (relative to output_dir)
        """
        if not image_urls:
            return []

        # Create property-specific subdirectory
        property_dir = self.output_dir / property_id
        property_dir.mkdir(exist_ok=True)

        local_paths = []

        for idx, url in enumerate(image_urls):
            try:
                local_path = self._download_single_image(url, property_dir, idx)
                if local_path:
                    # Store relative path from output_dir
                    relative_path = local_path.relative_to(self.output_dir)
                    local_paths.append(str(relative_path))

                # Be polite - small delay between downloads
                time.sleep(0.5)

            except Exception as e:
                print(f"Error downloading image {url}: {e}")
                continue

        return local_paths

    def _download_single_image(self, url: str, output_dir: Path, index: int) -> Optional[Path]:
        """
        Download a single image and return its local path.
        """
        try:
            # Generate unique filename based on URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]

            # Get file extension from URL
            ext = self._get_extension(url)

            # Construct filename: index_hash.ext
            filename = f"{index:02d}_{url_hash}{ext}"
            filepath = output_dir / filename

            # Skip if already downloaded
            if filepath.exists():
                print(f"Image already exists: {filepath}")
                return filepath

            # Download image
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Save to disk
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {filename}")
            return filepath

        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None

    def _get_extension(self, url: str) -> str:
        """
        Extract file extension from URL, default to .jpg
        """
        # Try to get extension from URL
        url_lower = url.lower()
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            if ext in url_lower:
                return ext

        # Default to .jpg
        return '.jpg'

    def get_image_info(self, local_path: str) -> Dict:
        """
        Get information about a downloaded image.
        """
        full_path = self.output_dir / local_path

        if not full_path.exists():
            return None

        stat = full_path.stat()

        return {
            'path': str(local_path),
            'size': stat.st_size,
            'exists': True
        }

    def cleanup_property_images(self, property_id: str):
        """
        Delete all images for a specific property.
        """
        property_dir = self.output_dir / property_id
        if property_dir.exists():
            import shutil
            shutil.rmtree(property_dir)
            print(f"Deleted images for property: {property_id}")
