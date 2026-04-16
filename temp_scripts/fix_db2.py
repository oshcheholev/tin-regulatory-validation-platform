import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get the schema
tables = ['validation_results_failed_rules', 'validation_results_matched_rules']

for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t}")
    
cur.execute("""
CREATE TABLE "validation_results_failed_rules" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "validationresult_id" bigint NOT NULL REFERENCES "validation_results" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tinrule_id" bigint NOT NULL REFERENCES "tin_rules" ("id") DEFERRABLE INITIALLY DEFERRED
)
""")
cur.execute('CREATE UNIQUE INDEX "validation_results_failed_rules_validationresult_id_tinrule_id_idx" ON "validation_results_failed_rules" ("validationresult_id", "tinrule_id")')
cur.execute('CREATE INDEX "validation_results_failed_rules_validationresult_id_idx" ON "validation_results_failed_rules" ("validationresult_id")')
cur.execute('CREATE INDEX "validation_results_failed_rules_tinrule_id_idx" ON "validation_results_failed_rules" ("tinrule_id")')

cur.execute("""
CREATE TABLE "validation_results_matched_rules" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "validationresult_id" bigint NOT NULL REFERENCES "validation_results" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tinrule_id" bigint NOT NULL REFERENCES "tin_rules" ("id") DEFERRABLE INITIALLY DEFERRED
)
""")
cur.execute('CREATE UNIQUE INDEX "validation_results_matched_rules_validationresult_id_tinrule_id_idx" ON "validation_results_matched_rules" ("validationresult_id", "tinrule_id")')
cur.execute('CREATE INDEX "validation_results_matched_rules_validationresult_id_idx" ON "validation_results_matched_rules" ("validationresult_id")')
cur.execute('CREATE INDEX "validation_results_matched_rules_tinrule_id_idx" ON "validation_results_matched_rules" ("tinrule_id")')


conn.commit()
print("Fixed real tables schema!")
