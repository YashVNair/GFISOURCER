import sqlite3
import os
import threading

DB_FILE = os.path.join(os.path.dirname(__file__), "scraper.db")

# This schema defines the columns in the database.
schema = {
    "Title": "TEXT", "Brand": "TEXT", "Category": "TEXT", "Subcategory": "TEXT",
    "Product Format": "TEXT", "Animal Product Replicated": "TEXT", "Status": "TEXT",
    "Availability": "TEXT", "In Stock": "BOOLEAN", "Launch Date": "TEXT",
    "Last Updated": "TEXT", "Price INR": "TEXT", "Unit Price": "TEXT",
    "Price per Kg/L": "TEXT", "Weight": "REAL", "Weight Unit": "TEXT",
    "Pack Size": "TEXT", "Positioning": "TEXT", "Segment": "TEXT",
    "Storage Condition": "TEXT", "Consumption Format": "TEXT", "Shelf Life": "TEXT",
    "Type of Manufacturing": "TEXT", "Ingredients List": "TEXT",
    "Ingredients Summary": "TEXT", "Ingredient Count": "INTEGER",
    "Protein Sources": "TEXT", "Complete Protein": "TEXT", "Nutritional Data": "TEXT",
    "Nutritional Claims": "TEXT", "Health Claims": "TEXT", "Allergen Info": "TEXT",
    "Marketing Claims": "TEXT", "Certifications": "TEXT", "Channel": "TEXT",
    "Distribution Channels": "TEXT", "Manufactured By": "TEXT",
    "Distributed By": "TEXT", "Packaged By": "TEXT", "Marketed By": "TEXT",
    "Product Page": "TEXT PRIMARY KEY", "Website": "TEXT", "Images": "TEXT",
    "SKU Code": "TEXT", "Source Name": "TEXT", "Source Links": "TEXT",
    "Notes": "TEXT", "Added By": "TEXT", "Update Type": "TEXT",
}

# This mapping defines how to convert Scrapy Item field names to Database column names.
ITEM_TO_DB_MAPPING = {
    'title': 'Title', 'brand': 'Brand', 'category': 'Category', 'subcategory': 'Subcategory',
    'product_format': 'Product Format', 'animal_product_replicated': 'Animal Product Replicated',
    'status': 'Status', 'availability': 'Availability', 'in_stock': 'In Stock',
    'launch_date': 'Launch Date', 'last_updated': 'Last Updated', 'price_inr': 'Price INR',
    'unit_price': 'Unit Price', 'price_per_kg_l': 'Price per Kg/L', 'weight': 'Weight',
    'weight_unit': 'Weight Unit', 'pack_size': 'Pack Size', 'positioning': 'Positioning',
    'segment': 'Segment', 'storage_condition': 'Storage Condition',
    'consumption_format': 'Consumption Format', 'shelf_life': 'Shelf Life',
    'type_of_manufacturing': 'Type of Manufacturing', 'ingredients_list': 'Ingredients List',
    'ingredients_summary': 'Ingredients Summary', 'ingredient_count': 'Ingredient Count',
    'protein_sources': 'Protein Sources', 'complete_protein': 'Complete Protein',
    'nutritional_data': 'Nutritional Data', 'nutritional_claims': 'Nutritional Claims',
    'health_claims': 'Health Claims', 'allergen_info': 'Allergen Info',
    'marketing_claims': 'Marketing Claims', 'certifications': 'Certifications',
    'channel': 'Channel', 'distribution_channels': 'Distribution Channels',
    'manufactured_by': 'Manufactured By', 'distributed_by': 'Distributed By',
    'packaged_by': 'Packaged By', 'marketed_by': 'Marketed By', 'product_page': 'Product Page',
    'website': 'Website', 'images': 'Images', 'sku_code': 'SKU Code',
    'source_name': 'Source Name', 'source_links': 'Source Links', 'notes': 'Notes',
    'added_by': 'Added By', 'update_type': 'Update Type',
}


def db_connect():
    return sqlite3.connect(DB_FILE, timeout=10)

def create_table():
    conn = db_connect()
    cursor = conn.cursor()

    # Check if table exists to decide on migration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Get current columns
        cursor.execute("PRAGMA table_info(products)")
        current_columns = {row[1] for row in cursor.fetchall()}
        expected_columns = set(schema.keys())
        missing_columns = expected_columns - current_columns

        for col_name in missing_columns:
            col_type = schema[col_name]
            if "PRIMARY KEY" not in col_type:
                cursor.execute(f'ALTER TABLE products ADD COLUMN "{col_name}" {col_type}')
    else:
        # Create table from scratch
        columns_sql = ",\n".join([f'"{name}" {typ}' for name, typ in schema.items()])
        create_sql = f"CREATE TABLE IF NOT EXISTS products (\n{columns_sql}\n)"
        cursor.execute(create_sql)

    conn.commit()
    conn.close()

def upsert_product(product_data, db_lock):
    # Map item keys to DB column names
    db_data = {ITEM_TO_DB_MAPPING.get(k, k): v for k, v in product_data.items()}

    with db_lock:
        try:
            conn = db_connect()
            cursor = conn.cursor()

            # Filter out any keys that are not in our DB schema
            valid_columns = {k: v for k, v in db_data.items() if k in schema}

            if not valid_columns:
                print(f"Warning: No valid columns found for item: {product_data.get('title')}")
                return

            columns = ', '.join([f'"{col}"' for col in valid_columns.keys()])
            placeholders = ', '.join(['?'] * len(valid_columns))

            sql = f"INSERT OR REPLACE INTO products ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, list(valid_columns.values()))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e} for item {product_data.get('title')}")
        finally:
            if conn:
                conn.close()

def get_all_products():
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
    print("Database table 'products' is ready.")
