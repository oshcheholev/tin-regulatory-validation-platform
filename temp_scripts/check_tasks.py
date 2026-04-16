from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.tasks import process_document_task

d = RuleSourceDocument.objects.exclude(status="completed")
print(f"Total incomplete: {d.count()}")
for x in d[:5]:
    print(f"ID {x.id}: {x.title} - Status: {x.status} - User: {x.uploaded_by} | Err: {x.error_message}")
