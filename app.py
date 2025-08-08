from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Homepage: Show items, alerts & trends
@app.route('/')
def index():
    conn = sqlite3.connect('inventory.db')
    cur = conn.cursor()

    # Get items
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # Alerts
    alerts = []
    for item in items:
        name = item[1]
        stock = item[2]
        expiry = item[3]

        if stock < 10:
            alerts.append(f"Low stock: {name}")
        if datetime.strptime(expiry, "%Y-%m-%d") < datetime.now():
            alerts.append(f"Expired: {name}")

    # Trends
    cur.execute("""
        SELECT items.name, COUNT(*) as used_count
        FROM usage_log
        JOIN items ON usage_log.item_id = items.id
        WHERE used_on >= date('now', '-7 days')
        GROUP BY usage_log.item_id
    """)
    usage_data = cur.fetchall()

    trends = []
    for row in usage_data:
        trends.append(f"{row[0]} used {row[1]} times in last 7 days")

    conn.close()
    return render_template("index.html", items=items, alerts=alerts, trends=trends)

# Add new item
@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['item_name']
    stock = int(request.form['stock'])
    expiry = request.form['expiry_date']

    conn = sqlite3.connect('inventory.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name, stock, expiry_date) VALUES (?, ?, ?)",
                (name, stock, expiry))
    conn.commit()
    conn.close()
    return redirect('/')

# Use item (stock -1 and log)
@app.route('/use_item/<int:item_id>', methods=['POST'])
def use_item(item_id):
    conn = sqlite3.connect('inventory.db')
    cur = conn.cursor()

    # Get current stock
    cur.execute("SELECT stock FROM items WHERE id=?", (item_id,))
    result = cur.fetchone()

    if result and result[0] > 0:
        # Reduce stock
        cur.execute("UPDATE items SET stock = stock - 1 WHERE id=?", (item_id,))
        # Log usage
        cur.execute("INSERT INTO usage_log (item_id, used_on, quantity_used) VALUES (?, ?, ?)",
                    (item_id, datetime.now().strftime("%Y-%m-%d"), 1))
        conn.commit()

    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
