import json
import csv

def write_to_json(data, filename):
    """Writes a list of dictionaries to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data successfully written to {filename}")
        return True
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return False

def write_to_csv(data, filename):
    """Writes a list of dictionaries to a CSV file."""
    if not data:
        print("No data provided to write to CSV.")
        # Still create an empty file with headers
        data = []

    # Define all possible headers based on the database schema
    headers = [
        "Product Name", "Brand", "Segment", "Positioning", "Animal Product Replicated",
        "Consumption Format", "Storage Condition", "Availability", "In Stock", "Status",
        "Price (INR)", "Weight", "Weight Unit", "Pack Size", "Distribution Channels",
        "Channel", "Product Page", "Website", "Source Name", "Source Links",
        "Ingredients List", "Ingredient Count", "Last Updated", "Notes"
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            if data:
                writer.writerows(data)
        print(f"Data successfully written to {filename}")
        return True
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return False
