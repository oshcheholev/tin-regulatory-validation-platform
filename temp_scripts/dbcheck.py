
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('PRAGMA index_list(tin_rules)')
for row in cursor.fetchall():
    idx_name = row[1]
    cursor.execute(f'PRAGMA index_info({idx_name})')
    print(f'Index {idx_name}: {cursor.fetchall()}')

