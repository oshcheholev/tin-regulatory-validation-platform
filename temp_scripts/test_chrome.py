import undetected_chromedriver as uc
import time

try:
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options, version_main=145)
    driver.get('https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html')
    time.sleep(10)
    print('TITLE_IS:', driver.title)
    print('HTML_LEN:', len(driver.page_source))
    driver.quit()
except Exception as e:
    print('ERROR_IS:', e)
