import sqlite3
from pathlib import Path
from random import choice, randint, uniform
from datetime import datetime, timedelta

DB_PATH = Path("database/cloudcart.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# CREATE TABLES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    order_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    total REAL NOT NULL,
    currency TEXT NOT NULL,
    ordered_at TEXT NOT NULL,
    delivered_at TEXT,
    estimated_delivery TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    sku TEXT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
""")

# =========================
# CLEAR OLD DATA
# =========================

cursor.execute("DELETE FROM orders")
cursor.execute("DELETE FROM order_items")

# =========================
# SAMPLE DATA
# =========================

statuses = [
    "Delivered",
    "Preparing",
    "Shipped",
    "Cancelled"
]

products = [
    ("CC-SHIRT-01", "CloudCart T-shirt"),
    ("CC-MUG-02", "CloudCart Coffee Mug"),
    ("CC-BAG-03", "CloudCart Backpack"),
    ("CC-SOCK-05", "CloudCart Socks Pack"),
    ("CC-CAP-07", "CloudCart Cap"),
]

customer_ids = [
    "user-001",
    "user-002",
    "user-003",
]

# =========================
# INSERT 30 ORDERS
# =========================

for i in range(1, 31):

    order_id = f"CART-{1000 + i}"

    customer_id = choice(customer_ids)

    status = choice(statuses)

    total = round(uniform(20, 300), 2)

    ordered_date = datetime.now() - timedelta(days=randint(1, 60))

    ordered_at = ordered_date.strftime("%Y-%m-%d")

    delivered_at = None
    estimated_delivery = None

    if status == "Delivered":
        delivered_at = (
            ordered_date + timedelta(days=randint(2, 7))
        ).strftime("%Y-%m-%d")

    elif status in ["Preparing", "Shipped"]:
        estimated_delivery = (
            ordered_date + timedelta(days=randint(3, 10))
        ).strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO orders (
        customer_id,
        order_id,
        status,
        total,
        currency,
        ordered_at,
        delivered_at,
        estimated_delivery
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        order_id,
        status,
        total,
        "USD",
        ordered_at,
        delivered_at,
        estimated_delivery
    ))

    # Add 1-3 items per order
    for _ in range(randint(1, 3)):

        sku, item_name = choice(products)

        quantity = randint(1, 4)

        price = round(uniform(10, 80), 2)

        cursor.execute("""
        INSERT INTO order_items (
            order_id,
            sku,
            item_name,
            quantity,
            price
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            order_id,
            sku,
            item_name,
            quantity,
            price
        ))

conn.commit()
conn.close()

print("CloudCart database initialized with 30 sample orders.")