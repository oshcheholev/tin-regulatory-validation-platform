import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_batch_validation_task(self, batch_id: int):
    """
    Celery task for processing a batch TIN validation CSV.
    """
    import csv
    import io
    from django.utils import timezone
    from apps.validation.models import ValidationBatch, ValidationResult
    from apps.rule_extraction.models import Country, TinRule
    from apps.validation.engine import validate_tin

    try:
        batch = ValidationBatch.objects.get(id=batch_id)
        batch.status = 'processing'
        batch.save(update_fields=['status'])

        results = []
        valid_count = 0
        invalid_count = 0
        unknown_count = 0

        with batch.csv_file.open('r') as f:
            text = f.read()
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            reader = csv.DictReader(io.StringIO(text))

            for row in reader:
                country_code = row.get('country', '').strip()
                tin = row.get('tin', '').strip()

                if not country_code or not tin:
                    continue

                validation = validate_tin(country_code, tin)

                result = ValidationResult(
                    tin=tin,
                    is_valid=validation['is_valid'],
                    status=validation['status'],
                    explanation=validation['explanation'],
                    batch_id=str(batch_id),
                    validated_by=batch.created_by,
                )

                try:
                    country = Country.objects.get(code=country_code.upper())
                    result.country = country
                except Country.DoesNotExist:
                    pass

                result.save()

                if validation['matched_rule_ids']:
                    result.matched_rules.set(validation['matched_rule_ids'])
                if validation['failed_rule_ids']:
                    result.failed_rules.set(validation['failed_rule_ids'])

                if validation['status'] == 'valid':
                    valid_count += 1
                elif validation['status'] == 'invalid':
                    invalid_count += 1
                else:
                    unknown_count += 1

        total = valid_count + invalid_count + unknown_count
        batch.total_count = total
        batch.valid_count = valid_count
        batch.invalid_count = invalid_count
        batch.unknown_count = unknown_count
        batch.status = 'completed'
        batch.completed_at = timezone.now()
        batch.save()

        logger.info(f'Batch {batch_id} completed: {total} TINs validated')
        return {'batch_id': batch_id, 'total': total}

    except ValidationBatch.DoesNotExist:
        logger.error(f'Batch {batch_id} not found')
        return {'error': 'Batch not found'}
    except Exception as exc:
        logger.error(f'Error processing batch {batch_id}: {exc}')
        try:
            batch = ValidationBatch.objects.get(id=batch_id)
            batch.status = 'failed'
            batch.error_message = str(exc)
            batch.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=60)
