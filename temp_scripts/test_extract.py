import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.documents.models import RuleSourceDocument
from apps.rule_extraction.pipeline import extract_rules_from_text

# Get a random completed doc
docs = RuleSourceDocument.objects.all()
docs_with_text = RuleSourceDocument.objects.filter(extracted_text__isnull=False).exclude(extracted_text="")
print("Total docs:", docs.count())
print("Docs with text:", docs_with_text.count())

doc = docs_with_text.first()
if doc:
    print(f"Reading {doc.title} - Text length: {len(doc.extracted_text)}")    
    rules = extract_rules_from_text(doc.extracted_text[:4000], doc.id)
    print("RULES EXTRACTED:")
    print(rules)
else:
    print("No docs with text.")
