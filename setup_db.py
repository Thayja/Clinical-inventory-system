import sqlite3

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()

# Items table
cur.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL,
    expiry_date TEXT NOT NULL
)
''')

# Usage log table
cur.execute('''
CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    used_on TEXT,
    quantity_used INTEGER
)
''')

conn.commit()
conn.close()
