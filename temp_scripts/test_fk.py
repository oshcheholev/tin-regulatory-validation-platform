import sqlite3
c = sqlite3.connect('db.sqlite3')
cur = c.cursor()
cur.execute('PRAGMA foreign_key_check')
print('FK Check:', cur.fetchall())
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in cur.fetchall():
    print(row[0])
