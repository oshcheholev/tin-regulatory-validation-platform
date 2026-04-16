import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.models import TinRule
from django.db.models import Count

print("Docs state:")
for state in RuleSourceDocument.objects.values('status').annotate(total=Count('id')):
    print(f"  {state['status']}: {state['total']}")

print(f"Rules count: {TinRule.objects.count()}")

