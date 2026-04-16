from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.models import TinRule

completed = RuleSourceDocument.objects.filter(status="completed").count()
print(f"Completed docs: {completed}")
rules = TinRule.objects.all().count()
print(f"Total Rules extracted so far: {rules}")
