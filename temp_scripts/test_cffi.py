from curl_cffi import requests
url = 'https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html'
try:
    r = requests.get(url, impersonate='chrome110')
    print('STATUS:', r.status_code)
    print('TIN PDF IN TEXT:', 'tin.pdf' in r.text.lower())
    if 'Just a moment...' in r.text:
       print('BLOCKED by CF')
except Exception as e:
    print('ERR:', e)
