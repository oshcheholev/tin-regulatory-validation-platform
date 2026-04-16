
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.models import TinRule
from apps.rule_extraction.tasks import process_document_task
import time

print('Clearing old extracted rules...')
TinRule.objects.all().delete()

docs = RuleSourceDocument.objects.all()
print(f'Starting processing for {docs.count()} documents...')

for doc in docs:
    doc.status = 'pending'
    doc.save()

success = 0
failed = 0

with open('extraction_log.txt', 'w', encoding='utf-8') as f:
    for doc in docs:
        print(f'Processing Doc {doc.id} ({doc.file.name})...')
        f.write(f'--- Processing Doc {doc.id} ({doc.file.name}) ---\n')
        try:
            res = process_document_task(doc.id)
            print(f' -> Success: {res}')
            f.write(f'Success: {res}\n')
            success += 1
        except Exception as e:
            print(f' -> Failed: {e}')
            f.write(f'Failed: {e}\n')
            failed += 1

print(f'\nFinished. Successful: {success}, Failed: {failed}')

