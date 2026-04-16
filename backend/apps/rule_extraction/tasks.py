import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    """
    Celery task for processing an uploaded OECD PDF document.
    Steps:
      1. Extract text from PDF
      2. Chunk text
      3. Extract TIN rules
      4. Store rules in database
    """
    from apps.documents.models import RuleSourceDocument
    from apps.rule_extraction.models import Country, TinRule
    from apps.rule_extraction.pipeline import (
        extract_text_from_pdf,
        chunk_text,
        extract_rules_from_text,
    )

    try:
        document = RuleSourceDocument.objects.get(id=document_id)
        document.status = 'processing'
        document.save(update_fields=['status'])

        # Step 1: Extract text
        logger.info(f'Extracting text from document {document_id}')
        text, page_count = extract_text_from_pdf(document.file.path)
        document.page_count = page_count
        document.extracted_text = text
        document.save(update_fields=['page_count', 'extracted_text'])

        # Step 2: Chunk text
        chunks = chunk_text(text)
        logger.info(f'Document {document_id} split into {len(chunks)} chunks')

        # Step 3: Extract rules from all chunks
        all_rules = []
        for chunk in chunks:
            rules = extract_rules_from_text(chunk, document_id)
            all_rules.extend(rules)

        # Step 4: Store unique rules
        created_count = 0
        for rule_data in all_rules:
            country_code = rule_data.pop('country_code')
            country_name = rule_data.pop('country_name')
            country, _ = Country.objects.get_or_create(
                code=country_code,
                defaults={'name': country_name},
            )
            extracted_regex = rule_data.get('regex_pattern')
            if extracted_regex == '':
                extracted_regex = None

            _, created = TinRule.objects.get_or_create(
                country=country,
                rule_type=rule_data['rule_type'],
                regex_pattern=extracted_regex,
                defaults={
                    'source_document': document,
                    'description': rule_data['description'],
                    'min_length': rule_data.get('min_length'),
                    'max_length': rule_data.get('max_length'),
                    'confidence_score': rule_data.get('confidence_score', 1.0),
                    'raw_extraction': rule_data.get('raw_extraction', {}),
                },
            )
            if created:
                created_count += 1

        document.status = 'completed'
        document.save(update_fields=['status'])
        logger.info(f'Document {document_id} processed: {created_count} new rules extracted')
        return {'document_id': document_id, 'rules_created': created_count}

    except RuleSourceDocument.DoesNotExist:
        logger.error(f'Document {document_id} not found')
        return {'error': 'Document not found'}
    except Exception as exc:
        logger.error(f'Error processing document {document_id}: {exc}')
        try:
            document = RuleSourceDocument.objects.get(id=document_id)
            document.status = 'failed'
            document.error_message = str(exc)
            document.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=60)
