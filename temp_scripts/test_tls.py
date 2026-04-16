import tls_client
url = 'https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html'
session = tls_client.Session(client_identifier='chrome_120', random_tls_extension_order=True)
res = session.get(url)
print('STATUS:', res.status_code)
if 'Just a moment...' in res.text:
    print('BLOCKED BY CF')
else:
    print('SUCCESS, HAS TIN:', 'tin.pdf' in res.text.lower())
