from scrapers.tunisie_annonce import TunisieAnnonceScraper
import json

# URL from the scraped_data.json that had missing info
URL = "http://www.tunisie-annonce.com/Details_Annonces_Immobilier.asp?cod_ann=3351642"

if __name__ == "__main__":
    scraper = TunisieAnnonceScraper()
    print(f"Fetching {URL}...")
    html = scraper.fetch_page(URL)
    if html:
        details = scraper.extract_details(html, URL)
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        print("Failed to fetch page.")
