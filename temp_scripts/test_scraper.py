import cloudscraper
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
r = scraper.get('https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html', timeout=30)
if 'Just a moment...' in r.text or r.status_code == 403:
    print('Failed with status:', r.status_code)
else:
    print('Scraping worked:', len(r.text))
