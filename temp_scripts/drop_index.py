
import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
try:
    cur.execute('DROP INDEX tin_rules_country_id_rule_type_regex_p_da3edcbf_uniq')
    con.commit()
    print('Dropped index!')
except Exception as e:
    print('Error dropping index:', e)

