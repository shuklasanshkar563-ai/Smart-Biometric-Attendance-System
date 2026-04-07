import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE activity_logs ADD COLUMN date TEXT")
    print("✅ date column added")
except Exception as e:
    print("⚠️", e)

conn.commit()
conn.close()