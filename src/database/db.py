import sqlite3
from pathlib import Path

DB_PATH = Path("database/cloudcart.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_orders_by_customer(customer_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            customer_id,
            order_id,
            status,
            total,
            currency,
            ordered_at,
            delivered_at,
            estimated_delivery
        FROM orders
        WHERE customer_id = ?
    """, (customer_id,))

    rows = cursor.fetchall()

    orders = []

    for row in rows:
        orders.append({
            "customer_id": row[0],
            "order_id": row[1],
            "status": row[2],
            "total": row[3],
            "currency": row[4],
            "ordered_at": row[5],
            "delivered_at": row[6],
            "estimated_delivery": row[7],
        })

    conn.close()

    return orders


def get_order_items(order_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sku,
            item_name,
            quantity,
            price
        FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    rows = cursor.fetchall()

    items = []

    for row in rows:
        items.append({
            "sku": row[0],
            "name": row[1],
            "quantity": row[2],
            "price": row[3],
        })

    conn.close()

    return items