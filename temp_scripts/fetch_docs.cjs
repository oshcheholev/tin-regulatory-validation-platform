const http = require('http');
const { execSync } = require('child_process');

let token = '';
try {
  token = execSync('wsl -d Ubuntu -e bash -c "cd /mnt/c/bank_austria/backend && source venv/bin/activate && python -c \\"import django, os; os.environ.setdefault(\\\\"DJANGO_SETTINGS_MODULE\\\\", \\\\"config.settings\\\\"); django.setup(); from users.models import User; from rest_framework_simplejwt.tokens import RefreshToken; print(RefreshToken.for_user(User.objects.first()).access_token)\\""').toString().trim();
} catch(e) { console.error('fetch token failed', e); process.exit(1); }

const req = http.request({
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/documents/?page=1',
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token
  }
}, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    try {
      const json = JSON.parse(data);
      console.log('Keys:', Object.keys(json));
      console.log('Count:', json.count);
      console.log('Results length:', json.results ? json.results.length : 0);
    } catch(e) {
      console.log(data);
    }
  });
});
req.on('error', console.error);
req.end();
