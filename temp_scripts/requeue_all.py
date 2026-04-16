import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.tasks import process_document_task
for d in RuleSourceDocument.objects.all():
    process_document_task.delay(d.id)
    print(f'Queued {d.id}')
