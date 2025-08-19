import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "scraper.db")

def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

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

def upsert_product(product_data):
    """Inserts a new product or replaces an existing one based on the primary key (Product Page)."""
    conn = db_connect()
    cursor = conn.cursor()

    columns = ', '.join([f'"{col}"' for col in product_data.keys()])
    placeholders = ', '.join(['?'] * len(product_data))

    sql = f"INSERT OR REPLACE INTO products ({columns}) VALUES ({placeholders})"

    cursor.execute(sql, list(product_data.values()))

    conn.commit()
    conn.close()

def get_all_products():
    """Fetches all products from the database and returns them as a list of dictionaries."""
    conn = db_connect()
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    products = [dict(row) for row in rows]

    conn.close()
    return products

if __name__ == '__main__':
    # Initialize the database and table when the script is run directly
    create_table()
