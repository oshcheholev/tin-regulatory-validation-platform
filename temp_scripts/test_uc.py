import undetected_chromedriver as uc
import time
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
try:
    driver = uc.Chrome(options=options, version_main=145)
    driver.get('https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html')
    time.sleep(5)
    print('TITLE:', driver.title)
    html = driver.page_source
    print('HTML LEN:', len(html))
    print('HAS TIN.PDF:', 'tin.pdf' in html.lower())
    driver.quit()
except Exception as e:
    print('ERROR:', e)
