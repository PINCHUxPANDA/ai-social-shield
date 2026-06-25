import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('security_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            threat_score REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_scan(username, threat_score):
    conn = sqlite3.connect('security_logs.db')
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO audit_logs (username, threat_score, timestamp)
        VALUES (?, ?, ?)
    ''', (username, threat_score, current_time))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = sqlite3.connect('security_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, threat_score, timestamp FROM audit_logs ORDER BY id DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs