import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
cur.execute('SELECT sql FROM sqlite_master WHERE name="tin_rules"')
row = cur.fetchone()
if row:
    schema = row[0]
    schema = schema.replace(', UNIQUE ("country_id", "rule_type", "regex_pattern")', '')
    cur.execute('PRAGMA foreign_keys = OFF;')
    cur.execute('ALTER TABLE tin_rules RENAME TO tin_rules_old;')
    print('New Schema:', schema)
    cur.execute(schema)
    cur.execute('INSERT INTO tin_rules SELECT * FROM tin_rules_old;')
    cur.execute('DROP TABLE tin_rules_old;')
    cur.execute('PRAGMA foreign_keys = ON;')
    con.commit()
    print('Table recreated without uniqueness constraint.')
else:
    print('Table not found.')
