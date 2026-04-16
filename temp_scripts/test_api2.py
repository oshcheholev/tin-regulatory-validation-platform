import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

u = User.objects.first()
token = RefreshToken.for_user(u).access_token
c = Client(HTTP_AUTHORIZATION=f'Bearer {token}')
response = c.get('/api/v1/documents/')

import json
print("STATUS:", response.status_code)
d = response.json()
print("KEYS:", list(d.keys()))
if 'count' in d: print("COUNT:", d['count'])
if 'results' in d: print("RESULTS_LEN:", len(d['results']))
