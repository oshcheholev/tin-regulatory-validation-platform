import os

file_path = '/mnt/c/bank_austria/backend/apps/rule_extraction/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

prefix = text.split('# Known TIN patterns per country (simplified OECD rules)')[0]

new_code = prefix + """
def extract_rules_from_text(text: str, document_id: int) -> list[dict]:
    \"\"\"
    Rule extraction from PDF text using DeepSeek LLM.
    Returns a list of rule dictionaries.
    \"\"\"
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
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not found in environment.")
        return []

    # Limit text length to avoid token limits per chunk
    # Usually chunking is done before this function, but just in case
    text = text[:15000]

    prompt = f\"\"\"You are a data extraction assistant for Tax Identification Number (TIN) rules.
I will provide text extracted from an official OECD PDF.
Your task is to identify and extract rules for TIN validation.
Return the rules as a strictly formatted JSON array of dictionaries.
Each dictionary MUST have the following keys (use EXACTLY these keys):
- "country_code": The 2-letter ISO 3166-1 alpha-2 country code (e.g., "US", "DE")
- "country_name": The full English name of the country.
- "rule_type": One of "format", "length", "checksum", "character_set", "structure", or "other".
- "description": A concise explanation of the format rule.
- "regex_pattern": A valid PCRE/Python regular expression pattern that matches this TIN format (e.g., "^\\\\d{{9}}$").
- "min_length": Integer representing the minimum length, or null.
- "max_length": Integer representing the maximum length, or null.

Only output valid JSON, no markdown formatting (like ```json), and no extra text.
If no TIN formats or rules are found, output an empty array: []

Text to analyze:
{text}
\"\"\"

    extracted_rules = []
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
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
        
        if result_text and result_text != "[]" and result_text.startswith("[") and result_text.endswith("]"):
            rules_data = json.loads(result_text)
            for rule in rules_data:
                rule['source_document_id'] = document_id
                rule['confidence_score'] = 0.9
                rule['raw_extraction'] = {'source': 'deepseek_llm'}
                extracted_rules.append(rule)
                
    except Exception as e:
        logger.error(f"Error calling DeepSeek API or parsing result: {e}")

    return extracted_rules

def seed_default_rules():
    \"\"\"Deprecated. Hardcoded rules were removed. Use the pipeline logic instead.\"\"\"
    logger.info('seed_default_rules is deprecated')
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Updated pipeline.py")
