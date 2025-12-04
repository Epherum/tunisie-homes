import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

class TunisieAnnonceScraper:
    BASE_URL = "http://www.tunisie-annonce.com"
    SEARCH_URL = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp"

    def __init__(self):
        self.session = requests.Session()
        # Mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            # CRITICAL: Force Windows-1252 encoding
            response.encoding = 'windows-1252'
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        # Correct selector based on inspection
        for a in soup.find_all('a', href=True):
            if 'Details_Annonces_Immobilier.asp' in a['href']:
                # The href might be relative or absolute, usually relative in this case
                href = a['href']
                if not href.startswith('http'):
                    full_url = f"{self.BASE_URL}/{href}"
                else:
                    full_url = href
                
                if full_url not in links:
                    links.append(full_url)
        return links

    def extract_details(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'sourceUrl': url,
            'source': 'TUNISIE_ANNONCE',  # Enum value (updated for new schema)
            'title': '',
            'description': '',
            'price': 0.0,
            'currency': 'TND',
            'city': '',
            'region': '',
            'surfaceArea': None,
            'rooms': None,
            'bathrooms': None,
            'phone': None,
            'email': None,
            'images': []
        }

        # Helper to find field by label
        def get_field_text(label):
            label_tag = soup.find('td', class_='da_label_field', string=re.compile(label, re.I))
            if label_tag:
                # The value is usually in the next sibling td with class da_field_text
                # But sometimes it's next sibling, or next next sibling if there are empty tds
                value_tag = label_tag.find_next_sibling('td', class_='da_field_text')
                if value_tag:
                    return value_tag.get_text(strip=True)
            return None

        # Extract Title
        # Try da_entete first
        title_tag = soup.find('tr', class_='da_entete')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)
        else:
            # Fallback to title tag
            if soup.title:
                data['title'] = soup.title.string.strip()

        # Extract Description
        desc = get_field_text('Texte')
        if desc:
            data['description'] = desc

        # Extract Price
        price_text = get_field_text('Prix')
        if price_text:
            # Clean price string (remove TND, spaces, commas, non-breaking spaces)
            clean_price = re.sub(r'[^\d]', '', price_text)
            if clean_price:
                data['price'] = float(clean_price)

        # Extract Surface
        surface_text = get_field_text('Surface')
        if surface_text:
            clean_surface = re.sub(r'[^\d]', '', surface_text)
            if clean_surface:
                data['surfaceArea'] = float(clean_surface)

        # Extract Phone
        phone_text = get_field_text('Téléphone')
        if not phone_text:
            # Fallback to da_contact_value (User hint)
            contact_val = soup.find(class_='da_contact_value')
            if contact_val:
                phone_text = contact_val.get_text(strip=True)

        if phone_text:
            # Clean phone (keep digits, maybe +)
            # Usually it's just digits in Tunisia, maybe spaces
            clean_phone = re.sub(r'[^\d+]', '', phone_text)
            if clean_phone:
                data['phone'] = clean_phone

        # Extract Email
        email_text = get_field_text('Email')
        if email_text:
            data['email'] = email_text.strip()

        # Extract Location (City/Region)
        # "Tunisie > Bizerte > Bizerte Nord > Bizerte"
        loc_text = get_field_text('Localisation')
        if loc_text:
            parts = [p.strip() for p in loc_text.split('>')]
            if len(parts) >= 2:
                data['region'] = parts[1] # e.g. Bizerte
            if len(parts) >= 3:
                data['city'] = parts[2] # e.g. Bizerte Nord

        # Extract Images
        # Look for large photos in div_photo_X
        for i in range(10): # Check up to 10 photos
            img_id = f"PhotoMax_{i}"
            img = soup.find('img', id=img_id)
            if img:
                src = img.get('src')
                if src:
                    if not src.startswith('http'):
                        src = f"{self.BASE_URL}/{src.lstrip('/')}"
                    if src not in data['images']:
                        data['images'].append(src)
        
        # Fallback: find all PhotoView1 if no PhotoMax found
        if not data['images']:
             for img in soup.find_all('img', class_='PhotoView1'):
                src = img.get('src')
                if src:
                    if not src.startswith('http'):
                        src = f"{self.BASE_URL}/{src.lstrip('/')}"
                    if src not in data['images']:
                        data['images'].append(src)

        return data

    def run(self, max_pages=1, max_listings=5):
        print(f"Starting scrape of {self.SEARCH_URL}")
        # For now, just fetch the main search page
        html = self.fetch_page(self.SEARCH_URL)
        if not html:
            return []

        links = self.parse_search_results(html)
        print(f"Found {len(links)} potential ads.")

        results = []
        for link in links[:max_listings]:
            print(f"Scraping {link}...")
            detail_html = self.fetch_page(link)
            if detail_html:
                details = self.extract_details(detail_html, link)
                results.append(details)
                time.sleep(1) # Be polite

        return results

if __name__ == "__main__":
    import json
    scraper = TunisieAnnonceScraper()
    data = scraper.run()

    # Save to JSON file
    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSuccessfully scraped {len(data)} listings!")
    print("Data saved to scraped_data.json")
