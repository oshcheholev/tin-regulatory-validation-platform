import sqlite3
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE sql LIKE '%tin_rules_old%'")
res=cur.fetchall()
for r in res:
    print(r[0])
    print(r[1])
    print('---')
