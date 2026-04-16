import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.documents.models import RuleSourceDocument
c = RuleSourceDocument.objects.filter(status='failed').update(status='pending', error_message=None)
print('Re-queued', c, 'documents.')
