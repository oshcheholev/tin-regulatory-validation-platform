from apps.documents.models import RuleSourceDocument; print(RuleSourceDocument.objects.count()); print(RuleSourceDocument.objects.filter(is_processed=True).count())
