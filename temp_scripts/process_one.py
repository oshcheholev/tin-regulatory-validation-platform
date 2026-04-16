import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.tasks import process_document_task

doc = RuleSourceDocument.objects.filter(status='pending').first()
if doc:
    print(f"Processing doc {doc.id} - {doc.title}")
    res = process_document_task(doc.id)
    print("Result:", res)
else:
    print("No pending docs found.")
