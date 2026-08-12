import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager
from threading import Lock

DB_PATH = os.path.join(os.path.dirname(__file__), 'autoc_enterprise.db')
_db_lock = Lock()
_db_connection = None

@contextmanager
def _get_db_connection():
    """Thread-safe database connection manager with connection pooling."""
    global _db_connection
    with _db_lock:
        if _db_connection is None:
            _db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            _db_connection.row_factory = sqlite3.Row
        yield _db_connection

def init_db():
    with _get_db_connection() as conn:
        c = conn.cursor()
        # Helpdesk
        c.execute('''CREATE TABLE IF NOT EXISTS helpdesk_messages
                     (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp TEXT, status TEXT)''')
        # Automations
        c.execute('''CREATE TABLE IF NOT EXISTS automations
                     (id INTEGER PRIMARY KEY, name TEXT, trigger TEXT, actions TEXT)''')
        # Analytics
        c.execute('''CREATE TABLE IF NOT EXISTS analytics
                     (id INTEGER PRIMARY KEY, date TEXT, visitors INTEGER, csat REAL)''')
        # Broadcast
        c.execute('''CREATE TABLE IF NOT EXISTS broadcasts
                     (id INTEGER PRIMARY KEY, campaign_name TEXT, target_segment TEXT, status TEXT)''')
        
        # Seed data if empty
        c.execute("SELECT COUNT(*) FROM helpdesk_messages")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO helpdesk_messages (sender, message, timestamp, status) VALUES (?, ?, ?, ?)",
                      ("Customer", "Hello, I need help with my order.", datetime.now().isoformat(), "unread"))
            c.execute("INSERT INTO automations (name, trigger, actions) VALUES (?, ?, ?)",
                      ("Welcome Flow", "new_user", json.dumps(["send_welcome", "tag_lead"])))
            c.execute("INSERT INTO analytics (date, visitors, csat) VALUES (?, ?, ?)",
                      (datetime.now().strftime("%Y-%m-%d"), 1500, 4.8))
            c.execute("INSERT INTO broadcasts (campaign_name, target_segment, status) VALUES (?, ?, ?)",
                      ("Summer Sale 2026", "VIP Customers", "scheduled"))
        conn.commit()

def get_helpdesk_messages():
    with _get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM helpdesk_messages ORDER BY id DESC")
        return [dict(row) for row in c.fetchall()]

def get_automations():
    with _get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM automations")
        return [dict(row) for row in c.fetchall()]

def get_analytics():
    with _get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM analytics ORDER BY id DESC LIMIT 30")
        return [dict(row) for row in c.fetchall()]

def get_broadcasts():
    with _get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM broadcasts")
        return [dict(row) for row in c.fetchall()]

# Initialize database on import
init_db()
