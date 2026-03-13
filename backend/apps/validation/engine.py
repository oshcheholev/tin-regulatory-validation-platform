"""
TIN validation engine.
Validates a TIN against extracted rules for a given country.
"""
import re
import logging

logger = logging.getLogger(__name__)


def validate_tin(country_code: str, tin: str) -> dict:
    """
    Validate a TIN against all active rules for a given country.
    Returns a dict with: is_valid, status, explanation, matched_rule_ids, failed_rule_ids
    """
    from apps.rule_extraction.models import Country, TinRule

    result = {
        'is_valid': False,
        'status': 'unknown',
        'explanation': '',
        'matched_rule_ids': [],
        'failed_rule_ids': [],
    }

    try:
        country = Country.objects.get(code=country_code.upper())
    except Country.DoesNotExist:
        result['explanation'] = f'No rules found for country code: {country_code}'
        return result

    rules = TinRule.objects.filter(country=country, is_active=True)

    if not rules.exists():
        result['explanation'] = f'No active validation rules found for {country.name}'
        return result

    # Normalize TIN (strip whitespace)
    tin_normalized = tin.strip()

    matched_rules = []
    failed_rules = []
    explanations = []

    for rule in rules:
        rule_passed = True
        rule_explanation = []

        # Check regex pattern
        if rule.regex_pattern:
            try:
                if re.fullmatch(rule.regex_pattern, tin_normalized):
                    rule_explanation.append(f'Matches pattern: {rule.regex_pattern}')
                else:
                    rule_passed = False
                    rule_explanation.append(f'Does not match pattern: {rule.regex_pattern}')
            except re.error as e:
                logger.warning(f'Invalid regex pattern in rule {rule.id}: {e}')

        # Check length constraints
        tin_len = len(tin_normalized)
        if rule.min_length is not None and tin_len < rule.min_length:
            rule_passed = False
            rule_explanation.append(f'Too short: {tin_len} < {rule.min_length}')
        if rule.max_length is not None and tin_len > rule.max_length:
            rule_passed = False
            rule_explanation.append(f'Too long: {tin_len} > {rule.max_length}')

        if rule_passed:
            matched_rules.append(rule.id)
            explanations.append(f'✓ Rule [{rule.rule_type}]: {rule.description}')
        else:
            failed_rules.append(rule.id)
            explanations.append(f'✗ Rule [{rule.rule_type}]: {"; ".join(rule_explanation)}')

    result['matched_rule_ids'] = matched_rules
    result['failed_rule_ids'] = failed_rules

    if matched_rules:
        result['is_valid'] = True
        result['status'] = 'valid'
        result['explanation'] = (
            f'TIN "{tin}" is valid for {country.name}.\n' + '\n'.join(explanations)
        )
    else:
        result['is_valid'] = False
        result['status'] = 'invalid'
        result['explanation'] = (
            f'TIN "{tin}" is invalid for {country.name}.\n' + '\n'.join(explanations)
        )

    return result
