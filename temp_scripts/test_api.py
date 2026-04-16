import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client
from users.models import User
c = Client()
u = User.objects.first()
c.force_login(u)
response = c.get('/api/v1/documents/')
import json
print(json.dumps(response.json(), indent=2)[:500])
