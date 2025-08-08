from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'inventory.db'

# Database connection helper
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if not exist
def init_db():
    conn = get_db()
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

# Home page with inventory + trends
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()

    # Get all items
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # Alerts
    alerts = []
    for item in items:
        name = item['name']
        stock = item['stock']
        expiry = item['expiry_date']
        if stock < 10:
            alerts.append(f"Low stock: {name}")
        if datetime.strptime(expiry, "%Y-%m-%d") < datetime.now():
            alerts.append(f"Expired: {name}")

    # Usage trends (last 7 days)
    cur.execute("""
        SELECT items.name, SUM(usage_log.quantity_used) as used_count
        FROM usage_log
        JOIN items ON usage_log.item_id = items.id
        WHERE used_on >= date('now', '-7 days')
        GROUP BY usage_log.item_id
    """)
    usage_data = cur.fetchall()

    conn.close()
    return render_template('index.html', items=items, alerts=alerts, usage_data=usage_data)

# Add new item or update existing
@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['item_name'].strip()
    stock = int(request.form['stock'])
    expiry = request.form['expiry_date']

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, stock FROM items WHERE name = ?", (name,))
    existing = cur.fetchone()

    if existing:
        new_stock = existing['stock'] + stock
        cur.execute("UPDATE items SET stock = ?, expiry_date = ? WHERE id = ?", (new_stock, expiry, existing['id']))
    else:
        cur.execute("INSERT INTO items (name, stock, expiry_date) VALUES (?, ?, ?)", (name, stock, expiry))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Use 1 quantity
@app.route('/use_item/<int:item_id>', methods=['POST'])
def use_item(item_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT stock FROM items WHERE id=?", (item_id,))
    result = cur.fetchone()

    if result and result['stock'] > 0:
        cur.execute("UPDATE items SET stock = stock - 1 WHERE id=?", (item_id,))
        cur.execute("INSERT INTO usage_log (item_id, used_on, quantity_used) VALUES (?, ?, ?)",
                    (item_id, datetime.now().strftime("%Y-%m-%d"), 1))
        conn.commit()

    conn.close()
    return redirect(url_for('index'))

# Increase stock by 1
@app.route('/increase_stock/<int:item_id>', methods=['POST'])
def increase_stock(item_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT stock FROM items WHERE id=?", (item_id,))
    result = cur.fetchone()

    if result:
        new_stock = result['stock'] + 1
        cur.execute("UPDATE items SET stock = ? WHERE id=?", (new_stock, item_id))
        conn.commit()

    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Make sure DB is created
    app.run(debug=True)
