import requests
import hashlib
import os
import sys
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from config import get_pdf_url, get_pdf_path


def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def scan_oecd_for_countries():
    """
    Scan OECD website for all available TIN PDFs and return discovered countries and URLs.
    Returns: dict with country keys and {'url': ..., 'filename': ...} values
    """
    print("Scanning OECD website for available TIN PDFs...")
    
    # Official OECD page with all TIN documents
    base_url = "https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html"
    tin_pattern = re.compile(r'([a-z\-]+)-tin\.pdf', re.IGNORECASE)
    found_pdfs = {}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Scan the main OECD TIN resources page with retries
        print(f"  Checking OECD TIN resources page...")
        for attempt in range(3):
            try:
                response = requests.get(base_url, headers=headers, timeout=20, verify=False)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        # Look for TIN PDF links
                        if 'tin.pdf' in href.lower() and 'oecd.org' in href.lower():
                            # Make full URL if relative
                            if href.startswith('http'):
                                full_url = href
                            else:
                                full_url = urljoin(base_url, href)
                            
                            # Extract country name from URL
                            match = tin_pattern.search(href.lower())
                            if match:
                                country = match.group(1).replace('_', '-')
                                if country not in found_pdfs:
                                    found_pdfs[country] = {
                                        'url': full_url,
                                        'filename': f'{country}_tin.pdf'
                                    }
                                    print(f"    [OK] Found: {country}")
                    
                    if len(found_pdfs) > 0:
                        print(f"\nDiscovered {len(found_pdfs)} countries with TIN PDFs\n")
                        return found_pdfs
                    break
            except Exception as e:
                if attempt < 2:
                    print(f"    Attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    print(f"  Warning: Could not scan page: {e}\n")
                    break
            
    except Exception as e:
        print(f"  Warning: Error during page scanning: {e}\n")
    
    # Fallback: Comprehensive list of all known countries with TIN documents
    print("  Using fallback: Testing direct URL pattern for all OECD member countries...")
    all_countries = [
        'albania', 'andorra', 'anguilla', 'antigua-and-barbuda', 'argentina', 'armenia',
        'aruba', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'barbados',
        'belgium', 'belize', 'bermuda', 'brazil', 'british-virgin-islands', 'brunei-darussalam',
        'bulgaria', 'cameroon', 'canada', 'cayman-islands', 'chile', 'china', 'colombia',
        'cook-islands', 'costa-rica', 'croatia', 'curacao', 'cyprus', 'czechia', 'czech-republic',
        'denmark', 'dominica', 'dominican-republic', 'ecuador', 'egypt', 'estonia', 'faroe-islands',
        'finland', 'france', 'georgia', 'germany', 'ghana', 'gibraltar', 'greece', 'greenland',
        'grenada', 'guadeloupe', 'guam', 'guatemala', 'guernsey', 'guyana', 'haiti', 'honduras',
        'hong-kong', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'isle-of-man',
        'israel', 'italy', 'jamaica', 'japan', 'jersey', 'jordan', 'kazakhstan', 'kenya', 'korea',
        'kuwait', 'latvia', 'lebanon', 'liechtenstein', 'lithuania', 'luxembourg', 'macau',
        'malaysia', 'maldives', 'malta', 'marshall-islands', 'mauritius', 'mexico', 'moldova',
        'monaco', 'montserrat', 'nauru', 'netherlands', 'new-zealand', 'nigeria', 'norway',
        'oman', 'pakistan', 'panama', 'peru', 'poland', 'portugal', 'qatar', 'romania',
        'russia', 'russian-federation', 'saint-kitts-and-nevis', 'saint-lucia', 'saint-vincent-and-the-grenadines',
        'samoa', 'san-marino', 'saudi-arabia', 'seychelles', 'singapore', 'sint-maarten',
        'slovak-republic', 'slovakia', 'slovenia', 'south-africa', 'spain', 'sweden', 'switzerland',
        'thailand', 'trinidad-and-tobago', 'turkey', 'turkiye', 'turks-and-caicos-islands',
        'turks-caicosislands', 'ukraine', 'united-arab-emirates', 'uae', 'united-kingdom', 'uk',
        'united-states', 'usa', 'uruguay', 'vanuatu'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        for country in all_countries:
            if country in found_pdfs:
                continue
            
            url = f"https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/{country}-tin.pdf"
            
            try:
                response = requests.head(url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                if response.status_code == 200:
                    found_pdfs[country] = {
                        'url': url,
                        'filename': f'{country}_tin.pdf'
                    }
                    print(f"    ✓ Found: {country}")
            except KeyboardInterrupt:
                # Re-raise to let outer handler catch it
                raise
            except (requests.RequestException, Exception):
                # Silently skip if URL doesn't exist or times out
                pass
    except KeyboardInterrupt:
        print("\n\n  ⚠ Scan interrupted by user")
        return found_pdfs
    
    print(f"\nDiscovered {len(found_pdfs)} countries with TIN PDFs\n")
    return found_pdfs


def update_config_with_discovered_countries(found_pdfs):
    """Update the config module with discovered countries and their URLs."""
    if not found_pdfs:
        print("No new countries discovered.")
        return
    
    # Update COUNTRIES list
    config.COUNTRIES = sorted(list(found_pdfs.keys()))
    
    # Update COUNTRY_CONFIG
    for country, pdf_info in found_pdfs.items():
        config.COUNTRY_CONFIG[country] = {
            'pdf_url': pdf_info['url'],
            'pdf_name': pdf_info['filename'],
        }
    
    print(f"Updated config with {len(config.COUNTRIES)} countries:")
    print(f"  {', '.join(sorted(config.COUNTRIES))}\n")


def download_pdf(country):
    pdf_url = get_pdf_url(country)
    pdf_path = get_pdf_path(country)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    if os.path.exists(pdf_path):
        print(f"File already exists: {pdf_path}")
        print("hash:", file_hash(pdf_path))
        return pdf_path

    if not pdf_url:
        print(f"No PDF URL configured for {country}")
        return None

    print(f"Downloading PDF for {country} from: {pdf_url}")

    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        r = requests.get(pdf_url, headers=headers, allow_redirects=True, timeout=30)

        # Check if request was successful
        if r.status_code != 200:
            print(f"Error: HTTP Status Code {r.status_code}")
            print("The URL might be incorrect or the file has moved.")
            return None

        # Check content type to verify it's a PDF
        content_type = r.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type and not r.content[:4] == b'%PDF':
            print("Warning: The downloaded content doesn't appear to be a PDF.")
            print(f"Content-Type: {content_type}")
            print("First 100 bytes of content:", r.content[:100])
            return None

        # Save the file
        with open(pdf_path, "wb") as f:
            f.write(r.content)

        print(f"Downloaded: {pdf_path}")
        print(f"Size: {len(r.content)} bytes")
        print("hash:", file_hash(pdf_path))
        return pdf_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None


if __name__ == "__main__":
    download_pdf("austria")