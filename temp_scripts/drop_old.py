
import sqlite3
c = sqlite3.connect('db.sqlite3')
cur = c.cursor()
try:
    cur.execute('DROP TABLE IF EXISTS tin_rules_old')
    c.commit()
    print('Dropped tin_rules_old')
except Exception as e:
    print(e)

