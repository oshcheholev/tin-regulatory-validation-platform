import urllib.request
headers = {'User-Agent': 'Mozilla/5.0'}

def direct_scan(country):
    url = f'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/{country}-tin.pdf'
    req = urllib.request.Request(url, headers=headers, method='HEAD')
    try:
        urllib.request.urlopen(req)
        return True
    except:
        return False
        
print('testing austria:', direct_scan('austria'))
print('testing fake:', direct_scan('fakecountry123'))
