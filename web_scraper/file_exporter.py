import json
import csv
import database # Use absolute import

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
        data = []

    # Use the schema keys from the imported database module
    headers = list(database.schema.keys())

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
