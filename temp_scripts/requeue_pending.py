import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.tasks import process_document_task

pending = RuleSourceDocument.objects.exclude(status='completed')
count = pending.count()
print(f"Re-queuing {count} documents...")

for d in pending:
    process_document_task.delay(d.id)
    print(f"Queued {d.id} - title: {getattr(d, 'title', 'none')}")
