import sqlite3
import os
import threading

DB_FILE = os.path.join(os.path.dirname(__file__), "scraper.db")

def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE, timeout=10) # Added timeout for concurrent access

def create_table():
    """Creates the 'products' table if it doesn't already exist."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        "Product Name" TEXT,
        "Brand" TEXT,
        "Segment" TEXT,
        "Positioning" TEXT,
        "Animal Product Replicated" TEXT,
        "Consumption Format" TEXT,
        "Storage Condition" TEXT,
        "Availability" TEXT,
        "In Stock" BOOLEAN,
        "Status" TEXT,
        "Price (INR)" TEXT,
        "Weight" REAL,
        "Weight Unit" TEXT,
        "Pack Size" TEXT,
        "Distribution Channels" TEXT,
        "Channel" TEXT,
        "Product Page" TEXT PRIMARY KEY,
        "Website" TEXT,
        "Source Name" TEXT,
        "Source Links" TEXT,
        "Ingredients List" TEXT,
        "Ingredient Count" INTEGER,
        "Last Updated" TEXT,
        "Notes" TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("Database table 'products' is ready.")

def upsert_product(product_data, db_lock):
    """
    Inserts a new product or replaces an existing one in a thread-safe manner.
    """
    with db_lock:
        try:
            conn = db_connect()
            cursor = conn.cursor()

            columns = ', '.join([f'"{col}"' for col in product_data.keys()])
            placeholders = ', '.join(['?'] * len(product_data))

            sql = f"INSERT OR REPLACE INTO products ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, list(product_data.values()))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

def get_all_products():
    """Fetches all products from the database and returns them as a list of dictionaries."""
    conn = db_connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    products = [dict(row) for row in rows]

    conn.close()
    return products

if __name__ == '__main__':
    create_table()
