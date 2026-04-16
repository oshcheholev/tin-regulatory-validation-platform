import requests
import urllib3
urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
# Using the old download format
r = requests.head('https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/austria-tin.pdf', headers=headers, verify=False, allow_redirects=True)
print('STATUS HEAD:', r.status_code)
r = requests.get('https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/austria-tin.pdf', headers=headers, verify=False)
print('STATUS GET:', r.status_code)
