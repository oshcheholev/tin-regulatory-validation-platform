import os
import django
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.tasks import process_document_task

def run_extraction_loop():
    pending_docs = RuleSourceDocument.objects.filter(status='pending')
    total = pending_docs.count()
    print(f"Found {total} pending documents to process.")

    for i, doc in enumerate(pending_docs, 1):
        print(f"\n=======================================================")
        print(f"[{i}/{total}] Processing {doc.title} (ID: {doc.id})...")
        try:
            result = process_document_task(doc.id)
            print(f"  -> Success: Extracted {result.get('rules_created', 0)} rules!")
        except Exception as e:
            print(f"  -> Error: {e}")
        print(f"=======================================================\n")
        
        # small sleep to not hammer the API too hard immediately
        time.sleep(2)

if __name__ == "__main__":
    run_extraction_loop()
