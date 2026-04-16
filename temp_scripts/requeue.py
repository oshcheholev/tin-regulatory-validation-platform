
import sqlite3
import os
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE documents_rulesourcedocument SET status='pending', error_message=NULL WHERE status='failed'")
print('Re-queued', cur.rowcount, 'failed documents.')
conn.commit()
conn.close()

