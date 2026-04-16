import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
for row in cur.fetchall():
    print(row[0])
