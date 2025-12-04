import requests
from bs4 import BeautifulSoup
import re

# URL from the scraped_data.json that had missing info
URL = "http://www.tunisie-annonce.com/Details_Annonces_Immobilier.asp?cod_ann=3433868"

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        # Force Windows-1252 encoding as per the scraper
        response.encoding = 'windows-1252'
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def debug_extraction(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Helper to find field by label
    def get_field_text(label):
        # Try exact match first
        print(f"Searching for label: {label}")
        # We use re.compile to match case-insensitive and partial
        label_tag = soup.find('td', class_='da_label_field', string=re.compile(re.escape(label), re.I))
        
        if label_tag:
            print(f"Found label tag for '{label}': {label_tag}")
            # Try da_field_text first
            value_tag = label_tag.find_next_sibling('td', class_='da_field_text')
            if not value_tag:
                # Try da_contact_value (User hint)
                print("da_field_text not found, trying da_contact_value...")
                value_tag = label_tag.find_next_sibling('td', class_='da_contact_value')
            
            if value_tag:
                print(f"Found value tag: {value_tag.get_text(strip=True)}")
                return value_tag.get_text(strip=True)
            else:
                print("No value tag found (checked da_field_text and da_contact_value)")
        else:
            print(f"Label tag for '{label}' NOT FOUND")
            
            # Debug: print all da_label_field to see what's there
            print("Dumping all 'da_label_field' tags found:")
            for tag in soup.find_all('td', class_='da_label_field'):
                print(f" - {tag.get_text(strip=True)}")
                
        return None

    print("-" * 20)
    print("Searching for 'da_contact_value' class...")
    contact_values = soup.find_all(class_='da_contact_value')
    for i, tag in enumerate(contact_values):
        print(f"Match {i+1}:")
        print(tag.prettify())
        print("-" * 10)

    print("-" * 20)
    print("Searching for Email (@ symbol)...")
    # Find text nodes containing "@"
    emails = soup.find_all(string=re.compile("@"))
    for e in emails:
        print(f"Found '@' in: {e.parent.name} (Classes: {e.parent.get('class')})")
        print(e.parent.prettify())
        print("-" * 10)

    print("-" * 20)
    print("Searching for mailto links...")
    mailtos = soup.select('a[href^="mailto:"]')
    for m in mailtos:
        print(f"Found mailto: {m['href']}")
        print(m.prettify())
        print("-" * 10)

if __name__ == "__main__":
    print(f"Fetching {URL}...")
    html = fetch_page(URL)
    if html:
        debug_extraction(html)
    else:
        print("Failed to fetch page.")
