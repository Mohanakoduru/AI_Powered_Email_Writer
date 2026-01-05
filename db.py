import sqlite3

DB_NAME = "emails.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_email(recipient, subject, body, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO emails (recipient, subject, body, status) VALUES (?, ?, ?, ?)",
        (recipient, subject, body, status)
    )
    conn.commit()
    conn.close()

def get_emails(status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT id, recipient, subject, body, timestamp FROM emails WHERE status=? ORDER BY timestamp DESC",
        (status,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def delete_email(email_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM emails WHERE id=?", (email_id,))
    conn.commit()

    # FREE STORAGE
    c.execute("VACUUM")
    conn.close()
