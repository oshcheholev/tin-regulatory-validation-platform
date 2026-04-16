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
        has_criteria = False

        # Check regex pattern
        if rule.regex_pattern:
            has_criteria = True
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
        if rule.min_length is not None:
            has_criteria = True
            if tin_len < rule.min_length:
                rule_passed = False
                rule_explanation.append(f'Too short: {tin_len} < {rule.min_length}')
        if rule.max_length is not None:
            has_criteria = True
            if tin_len > rule.max_length:
                rule_passed = False
                rule_explanation.append(f'Too long: {tin_len} > {rule.max_length}')

        if not has_criteria:
            continue

        if rule_passed:
            matched_rules.append(rule)
            explanations.append(f'✓ Rule [{rule.rule_type}]: {rule.description}')
        else:
            failed_rules.append(rule)
            explanations.append(f'✗ Rule [{rule.rule_type}]: {"; ".join(rule_explanation)}')

    matched_rule_ids = [r.id for r in matched_rules]
    failed_rule_ids = [r.id for r in failed_rules]
    result['matched_rule_ids'] = matched_rule_ids
    result['failed_rule_ids'] = failed_rule_ids

    # Group rules by type
    rules_by_type = {}
    for rule in matched_rules + failed_rules:
        if rule.rule_type not in rules_by_type:
            rules_by_type[rule.rule_type] = {'matched': [], 'failed': []}
    for rule in matched_rules:
        rules_by_type[rule.rule_type]['matched'].append(rule)
    for rule in failed_rules:
        rules_by_type[rule.rule_type]['failed'].append(rule)

    is_valid = True
    if not rules_by_type:
        is_valid = False
        result['status'] = 'unknown'
        result['explanation'] = f'No programmatic validation criteria (regex or length) found in the active rules for {country.name}'
    else:
        # A TIN is valid only if, for every rule type present, it passes AL LEAST ONE rule of that type
        for rule_type, lists in rules_by_type.items():
            if not lists['matched']:
                is_valid = False
                break
        
        if is_valid:
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
