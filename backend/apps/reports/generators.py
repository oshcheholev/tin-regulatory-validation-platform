"""
Report generation utilities.
"""
import csv
import json
import io
import logging

logger = logging.getLogger(__name__)


def generate_csv_report(validation_results) -> bytes:
    """Generate CSV report from ValidationResult queryset."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Country', 'TIN', 'Status', 'Is Valid', 'Explanation', 'Validated At'])

    for result in validation_results:
        writer.writerow([
            result.id,
            result.country.code if result.country else '',
            result.tin,
            result.status,
            result.is_valid,
            result.explanation[:500] if result.explanation else '',
            result.created_at.isoformat(),
        ])

    return output.getvalue().encode('utf-8')


def generate_json_report(validation_results) -> bytes:
    """Generate JSON report from ValidationResult queryset."""
    data = []
    for result in validation_results:
        data.append({
            'id': result.id,
            'country': result.country.code if result.country else None,
            'tin': result.tin,
            'status': result.status,
            'is_valid': result.is_valid,
            'explanation': result.explanation,
            'validated_at': result.created_at.isoformat(),
        })
    return json.dumps({'results': data, 'total': len(data)}, indent=2).encode('utf-8')
