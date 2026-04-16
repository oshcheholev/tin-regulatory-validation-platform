import re
with open('apps/documents/scraper.py', 'r') as f:
    text = f.read()

old_block = re.search(r'ALL_POSSIBLE_COUNTRIES = \[.*for country, pdf_url in found_pdfs.items():', text, flags=re.DOTALL)
if old_block:
    new_block = '''import io
import openpyxl

def parse_date(date_str):
    try:
        from datetime import datetime
        if isinstance(date_str, datetime):
            return date_str
        return datetime.strptime(str(date_str).strip(), " %d %b %y
