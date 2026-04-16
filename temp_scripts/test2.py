
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.rule_extraction.models import Country, TinRule
from apps.documents.models import RuleSourceDocument
print(f'Countries: {Country.objects.count()}')
print(f'Rules: {TinRule.objects.count()}')
print(f'Docs: {RuleSourceDocument.objects.count()}')
for doc in RuleSourceDocument.objects.all()[:5]:
    print(f'Doc ID {doc.id}: {doc.filename}, status={doc.status}, error={doc.error_message}, pc={doc.page_count}')

