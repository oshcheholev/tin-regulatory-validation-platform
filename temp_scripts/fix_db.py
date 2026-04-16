import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get the schema
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='validation_validationresult_failed_rules'")
res = cur.fetchone()
if res:
    print(res[0])
    
# Let's fix it by recreating the table
cur.execute("DROP TABLE IF EXISTS validation_validationresult_failed_rules")
cur.execute("""
CREATE TABLE "validation_validationresult_failed_rules" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "validationresult_id" bigint NOT NULL REFERENCES "validation_validationresult" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tinrule_id" bigint NOT NULL REFERENCES "rule_extraction_tinrule" ("id") DEFERRABLE INITIALLY DEFERRED
)
""")
cur.execute('CREATE UNIQUE INDEX "validation_validationresult_failed_rules_validationresult_id_tinrule_id_b4b" ON "validation_validationresult_failed_rules" ("validationresult_id", "tinrule_id")')
cur.execute('CREATE INDEX "validation_validationresult_failed_rules_validationresult_id_1" ON "validation_validationresult_failed_rules" ("validationresult_id")')
cur.execute('CREATE INDEX "validation_validationresult_failed_rules_tinrule_id_2" ON "validation_validationresult_failed_rules" ("tinrule_id")')
conn.commit()
print("Fixed table schema!")
