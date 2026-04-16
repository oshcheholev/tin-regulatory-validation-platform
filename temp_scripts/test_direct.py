import subprocess
print('Attempting direct curl...')
result = subprocess.run(['curl', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '-L', 'https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html'], capture_output=True, text=True)
if 'Just a moment...' in result.stdout:
    print('Curl blocked by CF')
else:
    print('Curl bypass worked!', len(result.stdout))
