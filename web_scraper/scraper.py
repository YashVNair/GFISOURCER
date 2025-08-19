import json
import csv
import datetime
import time
import os
import requests
from bs4 import BeautifulSoup
import re

def load_companies_from_file():
    """Loads a list of companies from companies.txt, located in the same directory as the script."""
    try:
        # Build a path to companies.txt relative to the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, "companies.txt")
        with open(filepath, 'r', encoding='utf-8') as f:
            companies = [line.strip() for line in f if line.strip()]
        return companies
    except FileNotFoundError:
        print(f"Error: The file companies.txt was not found in the same directory as the scraper script.")
        return []

def get_today_date():
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def extract_ingredients(body_html):
    """Extracts ingredients from the product's body_html."""
    if not body_html:
        return "", 0

    soup = BeautifulSoup(body_html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)

    match = re.search(r'(Ingredients|Made from|Made with)\s*[:-]?\s*([\w\s,()\[\]\.-]+)', text, re.IGNORECASE)
    if match:
        ingredients_str = match.group(2).strip()
        ingredients_str = re.sub(r'\.?\s*Contains.*', '', ingredients_str, flags=re.IGNORECASE)
        ingredients_list = [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]
        return ", ".join(ingredients_list), len(ingredients_list)

    return "", 0

def parse_weight_from_title(title):
    """Parses weight from product title, e.g., (500g)"""
    match = re.search(r'\((\d+)\s*g\)', title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

def infer_product_details(title):
    """Infers Segment and Animal Product Replicated from the product title."""
    title_lower = title.lower()
    segment = "PBM"
    animal_replicated = "Meat"

    if "egg" in title_lower or "bhurji" in title_lower:
        segment = "PBE"
        animal_replicated = "Egg"
    elif "unmutton" in title_lower or "mutton" in title_lower:
        animal_replicated = "Mutton"
    elif "vegicken" in title_lower or "chicken" in title_lower:
        animal_replicated = "Chicken"
    elif "tikka" in title_lower:
        animal_replicated = "Chicken"
    elif "sausage" in title_lower:
        animal_replicated = "Pork"
    elif "kebab" in title_lower:
        animal_replicated = "Mutton"
    elif "momo" in title_lower:
        animal_replicated = "Chicken"
    elif "biryani" in title_lower:
        if "unmutton" in title_lower or "vegicken" in title_lower:
             animal_replicated = "Meat"
        else:
             animal_replicated = "n/a"
    elif "noodles" in title_lower:
        segment = "Other"
        animal_replicated = "n/a"
    elif "halwa" in title_lower:
        segment = "Other"
        animal_replicated = "n/a"
    elif "soya chaap" in title_lower:
        animal_replicated = "Meat"
    elif "fries" in title_lower:
        animal_replicated = "n/a"


    positioning = "Plant-based"
    if "high protein" in title_lower:
        positioning = "High protein vegetarian product"

    return segment, animal_replicated, positioning

def scrape_shopify_store(company_name, store_url):
    """Generic scraper for a Shopify store."""
    print(f"Scraping {company_name} (Shopify)...")
    products = []
    processed_urls = set()

    try:
        response = requests.get(f"{store_url}/collections/all/products.json", timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {company_name}: {e}")
        return products

    for product in data.get('products', []):
        product_url = f"{store_url}/products/{product['handle']}"
        if product_url in processed_urls:
            continue

        if "(copy)" in product['title'].lower():
            continue

        processed_urls.add(product_url)

        segment, animal_replicated, positioning = infer_product_details(product['title'])
        if animal_replicated == "n/a":
            print(f"Skipping product '{product['title']}' as it does not seem to be a meat analogue.")
            continue

        for variant in product.get('variants', []):
            ingredients, ingredient_count = extract_ingredients(product.get('body_html', ''))

            weight = variant.get('grams') or parse_weight_from_title(product['title'])
            pack_size = variant.get('title') if variant.get('title') != 'Default Title' else f"{weight}g" if weight else ""

            product_data = {
                "Product Name": product['title'],
                "Brand": company_name,
                "Segment": segment,
                "Positioning": positioning,
                "Animal Product Replicated": animal_replicated,
                "Consumption Format": "RTC",
                "Storage Condition": "Frozen",
                "Availability": "Active" if variant.get('available') else "OOS",
                "In Stock": variant.get('available', False),
                "Status": "Launched",
                "Price (INR)": variant.get('price'),
                "Weight": weight,
                "Weight Unit": "g",
                "Pack Size": pack_size,
                "Distribution Channels": "Brand website",
                "Channel": "D2C",
                "Product Page": product_url,
                "Website": store_url,
                "Source Name": f"{company_name} Official Website",
                "Source Links": product_url,
                "Ingredients List": ingredients,
                "Ingredient Count": ingredient_count,
                "Last Updated": product.get('updated_at', '').split('T')[0],
                "Notes": ""
            }
            products.append(product_data)

    print(f"Scraped {len(products)} products from {company_name}.")
    return products

def scrape_good_dot():
    """Scraper for Good Dot products."""
    products = scrape_shopify_store("Good Dot", "https://gooddot.in")
    for p in products:
        p["Storage Condition"] = "Ambient"
    return products

def scrape_blue_tribe():
    """Scraper for Blue Tribe products."""
    products = scrape_shopify_store("Blue Tribe", "https://www.bluetribefoods.com")
    for p in products:
        p["Storage Condition"] = "Frozen"
    return products

def scrape_company(company_name):
    """Generic scraper function that calls the specific scraper."""
    print(f"Scraping {company_name}...")
    products = []
    sanitized_name = company_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').replace("'", "")
    scraper_function_name = f"scrape_{sanitized_name}"

    scraper_function = globals().get(scraper_function_name)
    if scraper_function:
        products = scraper_function()
    else:
        print(f"No scraper implemented for {company_name} yet (expected function: {scraper_function_name}).")
    return products

def write_to_json(data, filename="products.json"):
    """Writes the scraped data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data written to {filename}")

def write_to_csv(data, filename="products.csv"):
    """Writes the scraped data to a CSV file."""
    if not data:
        print("No data to write to CSV. Creating an empty file with headers.")
        data = []

    headers = [
        "Product Name", "Brand", "Segment", "Positioning", "Animal Product Replicated",
        "Consumption Format", "Storage Condition", "Availability", "In Stock", "Status",
        "Price (INR)", "Weight", "Weight Unit", "Pack Size", "Distribution Channels",
        "Channel", "Product Page", "Website", "Source Name", "Source Links",
        "Ingredients List", "Ingredient Count", "Last Updated", "Notes"
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        if data:
            writer.writerows(data)
    print(f"Data written to {filename}")

def main():
    """Main function to orchestrate the scraping process."""
    companies = load_companies_from_file()
    if not companies:
        print("No companies to scrape. Please check companies.txt.")
        return

    all_products = []
    for company in companies:
        products = scrape_company(company)
        all_products.extend(products)
        time.sleep(1)

    # Build a path to the output directory relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = script_dir # Save in the same directory as the script

    write_to_json(all_products, os.path.join(output_dir, "products.json"))
    write_to_csv(all_products, os.path.join(output_dir, "products.csv"))

    if not all_products:
        print("No products were scraped.")

if __name__ == "__main__":
    main()
