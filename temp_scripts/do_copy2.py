import shutil
import sys

try:
    shutil.copyfile('/mnt/c/bank_austria/backend/apps/documents/scraper_temp.py', '/mnt/c/bank_austria/backend/apps/documents/scraper.py')
    print("SUCCESS_COPY")
except Exception as e:
    print("ERROR:", str(e))
