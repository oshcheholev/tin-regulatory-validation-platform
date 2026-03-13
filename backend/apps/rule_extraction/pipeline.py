"""
PDF processing pipeline:
  1. Extract text from PDF
  2. Chunk text
  3. Extract TIN rules using pattern matching and heuristics
  4. Store rules in database
"""
import re
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """Extract text content from a PDF file. Returns (text, page_count)."""
    try:
        from pdfminer.high_level import extract_text
        from pdfminer.pdfpage import PDFPage

        text = extract_text(file_path)

        # Count pages
        with open(file_path, 'rb') as f:
            page_count = sum(1 for _ in PDFPage.get_pages(f))

        return text, page_count
    except Exception as e:
        logger.error(f'PDF extraction error: {e}')
        raise


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks for processing."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# Known TIN patterns per country (simplified OECD rules)
COUNTRY_TIN_RULES = {
    'US': {
        'name': 'United States',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'US EIN format: XX-XXXXXXX (9 digits)',
                'regex_pattern': r'^\d{2}-\d{7}$',
                'min_length': 10,
                'max_length': 10,
            },
            {
                'rule_type': 'format',
                'description': 'US SSN format: XXX-XX-XXXX (9 digits)',
                'regex_pattern': r'^\d{3}-\d{2}-\d{4}$',
                'min_length': 11,
                'max_length': 11,
            },
            {
                'rule_type': 'format',
                'description': 'US ITIN format: 9XX-XX-XXXX (starts with 9)',
                'regex_pattern': r'^9\d{2}-\d{2}-\d{4}$',
                'min_length': 11,
                'max_length': 11,
            },
        ],
    },
    'GB': {
        'name': 'United Kingdom',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'UK UTR (Unique Taxpayer Reference): 10 digits',
                'regex_pattern': r'^\d{10}$',
                'min_length': 10,
                'max_length': 10,
            },
            {
                'rule_type': 'format',
                'description': 'UK National Insurance Number: XX 99 99 99 X',
                'regex_pattern': r'^[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]$',
                'min_length': 9,
                'max_length': 9,
            },
        ],
    },
    'DE': {
        'name': 'Germany',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'German Tax ID (Steueridentifikationsnummer): 11 digits, first digit non-zero',
                'regex_pattern': r'^[1-9]\d{10}$',
                'min_length': 11,
                'max_length': 11,
            },
        ],
    },
    'FR': {
        'name': 'France',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'French Tax ID (Numéro fiscal): 13 digits',
                'regex_pattern': r'^\d{13}$',
                'min_length': 13,
                'max_length': 13,
            },
        ],
    },
    'CA': {
        'name': 'Canada',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Canadian SIN: XXX-XXX-XXX (9 digits)',
                'regex_pattern': r'^\d{3}-\d{3}-\d{3}$',
                'min_length': 11,
                'max_length': 11,
            },
        ],
    },
    'AU': {
        'name': 'Australia',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Australian TFN: 8 or 9 digits',
                'regex_pattern': r'^\d{8,9}$',
                'min_length': 8,
                'max_length': 9,
            },
        ],
    },
    'IN': {
        'name': 'India',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Indian PAN: 5 uppercase letters + 4 digits + 1 uppercase letter',
                'regex_pattern': r'^[A-Z]{5}\d{4}[A-Z]$',
                'min_length': 10,
                'max_length': 10,
            },
        ],
    },
    'CN': {
        'name': 'China',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Chinese TIN for individuals: 18-digit Resident Identity Card number',
                'regex_pattern': r'^\d{17}[\dX]$',
                'min_length': 18,
                'max_length': 18,
            },
        ],
    },
    'JP': {
        'name': 'Japan',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Japanese My Number (Individual Number): 12 digits',
                'regex_pattern': r'^\d{12}$',
                'min_length': 12,
                'max_length': 12,
            },
        ],
    },
    'NL': {
        'name': 'Netherlands',
        'rules': [
            {
                'rule_type': 'format',
                'description': 'Dutch BSN (Burgerservicenummer): 9 digits with 11-proof check',
                'regex_pattern': r'^\d{9}$',
                'min_length': 9,
                'max_length': 9,
            },
        ],
    },
}


def extract_rules_from_text(text: str, document_id: int) -> list[dict]:
    """
    Heuristic rule extraction from PDF text.
    In production, this would call an AI/LLM API.
    Returns a list of rule dictionaries.
    """
    extracted_rules = []

    # Look for country codes in text
    country_pattern = re.compile(
        r'\b(United States|USA|United Kingdom|UK|Germany|France|Canada|Australia|India|China|Japan|Netherlands)\b',
        re.IGNORECASE
    )
    country_map = {
        'united states': 'US', 'usa': 'US',
        'united kingdom': 'GB', 'uk': 'GB',
        'germany': 'DE',
        'france': 'FR',
        'canada': 'CA',
        'australia': 'AU',
        'india': 'IN',
        'china': 'CN',
        'japan': 'JP',
        'netherlands': 'NL',
    }

    found_countries = set()
    for match in country_pattern.finditer(text):
        country_name = match.group(0).lower()
        if country_name in country_map:
            found_countries.add(country_map[country_name])

    # Add rules for found countries
    for code in found_countries:
        if code in COUNTRY_TIN_RULES:
            for rule in COUNTRY_TIN_RULES[code]['rules']:
                extracted_rules.append({
                    'country_code': code,
                    'country_name': COUNTRY_TIN_RULES[code]['name'],
                    'source_document_id': document_id,
                    'confidence_score': 0.85,
                    'raw_extraction': {'source': 'text_extraction'},
                    **rule,
                })

    return extracted_rules


def seed_default_rules():
    """Seed database with default TIN rules for common countries."""
    from apps.rule_extraction.models import Country, TinRule

    rules_to_create = []
    for code, data in COUNTRY_TIN_RULES.items():
        country, _ = Country.objects.get_or_create(
            code=code,
            defaults={'name': data['name']},
        )
        for rule_data in data['rules']:
            exists = TinRule.objects.filter(
                country=country,
                rule_type=rule_data['rule_type'],
                regex_pattern=rule_data.get('regex_pattern', ''),
            ).exists()
            if not exists:
                rules_to_create.append(TinRule(
                    country=country,
                    rule_type=rule_data['rule_type'],
                    description=rule_data['description'],
                    regex_pattern=rule_data.get('regex_pattern', ''),
                    min_length=rule_data.get('min_length'),
                    max_length=rule_data.get('max_length'),
                    confidence_score=1.0,
                ))

    if rules_to_create:
        TinRule.objects.bulk_create(rules_to_create)
        logger.info(f'Seeded {len(rules_to_create)} TIN rules')
