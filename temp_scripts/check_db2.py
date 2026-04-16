import sqlite3

def check():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    docs = cursor.execute("SELECT status, COUNT(id) FROM documents_rulesourcedocument GROUP BY status;").fetchall()
    rules = cursor.execute("SELECT COUNT(id) FROM rule_extraction_tinrule;").fetchall()
    print("Documents:", docs)
    print("Rules:", rules)

if __name__ == "__main__":
    check()
