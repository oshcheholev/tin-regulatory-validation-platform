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


def chunk_text(text: str, chunk_size: int = 15000, overlap: int = 500) -> list[str]:
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



def extract_rules_from_text(text: str, document_id: int) -> list[dict]:
    """
    Rule extraction from PDF text using DeepSeek LLM.
    Returns a list of rule dictionaries.
    """
    import os
    import json
    import requests
    from dotenv import load_dotenv
    
    # Load .env into os.environ
    # Walk up to find the .env file in the backend root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(env_path)
    # also try the root one for good measure
    load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'))
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment.")
        return []

    # Limit text length to avoid token limits per chunk
    # Usually chunking is done before this function, but just in case
    text = text[:15000]

    prompt = f"""You are a data extraction assistant for Tax Identification Number (TIN) rules.
I will provide text extracted from an official OECD PDF.
Your task is to identify and extract rules for TIN validation.
Return the rules as a strictly formatted JSON array of dictionaries.
Each dictionary MUST have the following keys (use EXACTLY these keys):
- "country_code": The 2-letter ISO 3166-1 alpha-2 country code (e.g., "US", "DE")
- "country_name": The full English name of the country.
- "rule_type": One of "format", "length", "checksum", "character_set", "structure", or "other".
- "description": A concise explanation of the format rule.
- "regex_pattern": A valid PCRE/Python regular expression pattern that matches this TIN format (e.g., "^\\d{{9}}$").
- "min_length": Integer representing the minimum length, or null.
- "max_length": Integer representing the maximum length, or null.

Only output valid JSON, no markdown formatting (like ```json), and no extra text.
If no TIN formats or rules are found, output an empty array: []

Text to analyze:
{text}
"""

    extracted_rules = []
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [
                    {"role": "system", "content": "You output only valid JSON arrays representing the requested data. No preamble or postamble."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
            },
            timeout=90
        )
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"].strip()
        
        # Cleanup potential markdown wrapper
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        result_text = result_text.strip()
        print("RAW OpenRouter Response:", result_text)
        
        # Sometime LLMs escape backslashes poorly for regexes. Remove single backslashes that shouldn't be there, or properly double them
        result_text = result_text.replace('\\\\', '\\')
        
        # Or better yet we can use strict to false in json or just raw string replacement if python fails.
        # But let's see what the actual response looks like first by printing it above.

        if result_text and result_text != "[]" and result_text.startswith("[") and result_text.endswith("]"):
            try:
                # The issue is typically unescaped backslashes in regexes
                # e.g. "^\d{9}$" instead of "^\\d{9}$"
                rules_data = json.loads(result_text)
            except json.JSONDecodeError as de:
                logger.error(f"JSON decode failed on: {result_text}")
                # Naive fallback cleanup for backslashes
                safe_text = result_text.replace("\\", "\\\\").replace("\\\\\\\\", "\\\\") 
                rules_data = json.loads(safe_text)

            for rule in rules_data:
                rule['source_document_id'] = document_id
                rule['confidence_score'] = 0.9
                rule['raw_extraction'] = {'source': 'openrouter_llm'}
                extracted_rules.append(rule)

    except Exception as e:
        logger.error(f"Error calling OpenRouter API or parsing result: {e}")
    return extracted_rules

def seed_default_rules():
    """Deprecated. Hardcoded rules were removed. Use the pipeline logic instead."""
    logger.info('seed_default_rules is deprecated')
