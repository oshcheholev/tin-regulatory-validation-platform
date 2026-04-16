import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
cur.execute("UPDATE oecd_sync_logs SET status='failed' WHERE status='running';")
conn.commit()
conn.close()
print("Reset stuck logs to failed.")
