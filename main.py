import sqlite3

DATABASE = "database.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Attendance table
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        time TEXT,
        status TEXT,
        method TEXT
    )
    ''')

    # Activity Logs table (with date column for new DB)
    c.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll_number TEXT,
        class TEXT,
        action TEXT,
        status TEXT,
        time TEXT,
        date TEXT
    )
    ''')

    # 👇 SAFE: agar pehle se table hai aur date column nahi hai
    try:
        c.execute("ALTER TABLE activity_logs ADD COLUMN date TEXT")
    except:
        pass  # column already exists, ignore

    conn.commit()
    conn.close()


def main():
    init_db()
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    main()