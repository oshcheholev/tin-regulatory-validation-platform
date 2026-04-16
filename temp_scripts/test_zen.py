import urllib.request
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request('https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html', headers=headers)
try:
    with urllib.request.urlopen(req) as r:
        html = r.read().decode()
    print('TIN in HTML:', 'tin.pdf' in html)
except Exception as e:
    print('ERR:', e)
