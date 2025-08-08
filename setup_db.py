import sqlite3

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    stock INTEGER NOT NULL,
    expiry_date TEXT NOT NULL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    used_on TEXT,
    quantity_used INTEGER,
    FOREIGN KEY(item_id) REFERENCES items(id)
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully.")
