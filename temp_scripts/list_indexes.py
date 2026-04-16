
import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
cur.execute('PRAGMA index_list(tin_rules)')
print(cur.fetchall())

