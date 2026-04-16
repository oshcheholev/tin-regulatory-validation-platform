import sqlite3
import pprint

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
cur.execute("SELECT status, start_time, end_time, total_found, error_details FROM oecd_sync_logs ORDER BY start_time DESC LIMIT 5;")
logs = cur.fetchall()
print("---- SYNC LOGS ----")
pprint.pprint(logs)
conn.close()
