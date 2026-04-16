import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls = [
    'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/tin_argentina.pdf',
    'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/bulgaria%20-%20tin.pdf',
    'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/brunei-darussalam-tin%20.pdf',
    'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/cayman_islands_tin.pdf',
    'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/saintlucia-tin.pdf'
]
headers = {'User-Agent': 'Mozilla/5.0'}
for url in urls:
    resp = requests.head(url, headers=headers, verify=False, allow_redirects=True, timeout=10)
    print(f"{url}: {resp.status_code}")
