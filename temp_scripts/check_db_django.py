from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.models import TINRule
from django.db.models import Count

print("Docs state:")
for state in RuleSourceDocument.objects.values('status').annotate(total=Count('id')):
    print(f"  {state['status']}: {state['total']}")

print(f"Rules count: {TINRule.objects.count()}")
