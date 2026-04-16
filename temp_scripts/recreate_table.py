import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
cur.execute('SELECT sql FROM sqlite_master WHERE name=" tin_rules\')
schema
