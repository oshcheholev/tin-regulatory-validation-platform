import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.models import TinRule

docs_completed = RuleSourceDocument.objects.filter(status='completed').count()
docs_total = RuleSourceDocument.objects.count()
rules_extracted = TinRule.objects.count()

print(f"Documents Completed: {docs_completed} / {docs_total}")
print(f"TIN Rules Extracted: {rules_extracted}")
