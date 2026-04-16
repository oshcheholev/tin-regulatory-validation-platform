import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

countries_to_check = ['argentina', 'brunei', 'bulgaria', 'saint-lucia', 'st-lucia', 'cayman', 'cayman-islands', 'bulgaria', 'macau']
headers = {'User-Agent': 'Mozilla/5.0'}
for c in countries_to_check:
    url = f'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/{c}-tin.pdf'
    resp = requests.head(url, headers=headers, verify=False, allow_redirects=True, timeout=10)
    print(f"{c}: {resp.status_code}")
