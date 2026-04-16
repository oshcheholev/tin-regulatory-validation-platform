
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.rule_extraction.models import TinRule
from collections import defaultdict
d = defaultdict(set)
for r in TinRule.objects.filter(is_active=True):
    d[r.country.code].add(r.rule_type)
print(dict(d))

