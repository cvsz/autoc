import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'autoc_enterprise.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

def get_helpdesk_messages():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM helpdesk_messages ORDER BY id DESC")
    return [dict(row) for row in c.fetchall()]

def get_automations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM automations")
    return [dict(row) for row in c.fetchall()]

def get_analytics():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM analytics ORDER BY id DESC LIMIT 30")
    return [dict(row) for row in c.fetchall()]

def get_broadcasts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM broadcasts")
    return [dict(row) for row in c.fetchall()]

# Initialize database on import
init_db()
