import scrapy
import json
import re
from product_scraper.items import ProductItem
from bs4 import BeautifulSoup

# Helper functions
def extract_from_html(pattern, html, group=1, default=""):
    """Extracts a value from HTML using a regex pattern."""
    if not html:
        return default
    # Use BeautifulSoup to get clean text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(group).strip() if match else default

def calculate_price_per_kg_l(price, weight_g):
    """Calculates the price per kg/l from price and weight in grams."""
    if not price or not weight_g or weight_g == 0:
        return ""
    try:
        price_float = float(price)
        weight_kg = float(weight_g) / 1000
        return round(price_float / weight_kg, 2)
    except (ValueError, TypeError):
        return ""

def extract_ingredients(body_html):
    if not body_html:
        return "", 0, ""

    text = BeautifulSoup(body_html, 'html.parser').get_text(separator=' ', strip=True)

    ingredients_str = extract_from_html(r'(Ingredients|Made from|Made with)\s*[:-]?\s*([\w\s,()\[\]\.-]+)', text, group=2)
    allergen_info = extract_from_html(r'Allergen Information\s*[:-]?\s*(.*?)(?:\.|$)', text)

    if ingredients_str:
        # Clean up the ingredients string
        ingredients_str = re.sub(r'\.?\s*Contains.*', '', ingredients_str, flags=re.IGNORECASE)
        ingredients_list = [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]
        return ", ".join(ingredients_list), len(ingredients_list), allergen_info

    return "", 0, allergen_info

def parse_weight_from_title(title):
    match = re.search(r'\((\d+)\s*g\)', title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)\s*g', title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

def infer_product_details(title):
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
    elif any(x in title_lower for x in ["milk", "mylk", "creamer"]):
        segment = "PBD"
        animal_replicated = "Dairy"
    else:
        # If no specific meat/egg/dairy keyword, maybe it's not a replication
        animal_replicated = "n/a"

    # Basic positioning and format inference
    positioning = "Plant-based"
    consumption_format = "RTC" # Ready to Cook
    if any(x in title_lower for x in ["drink", "shake", "smoothie"]):
        consumption_format = "RTD" # Ready to Drink

    return segment, positioning, animal_replicated, consumption_format

class ProductSpider(scrapy.Spider):
    name = "product_spider"

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.company_name = kwargs.get('name')
        self.scraper_type = kwargs.get('type')
        self.start_url = kwargs.get('url')
        if not all([self.company_name, self.scraper_type, self.start_url]):
            raise ValueError("Spider must be run with `name`, `type`, and `url` arguments.")

    def start_requests(self):
        if self.scraper_type == 'shopify':
            # Append .json to the products URL if it's not already there
            url = self.start_url if self.start_url.endswith('.json') else f"{self.start_url.rstrip('/')}/products.json"
            yield scrapy.Request(url, self.parse_shopify_json)
        else:
            # For simplicity, we are focusing on Shopify. Other types are placeholders.
            self.logger.error(f"Scraper type '{self.scraper_type}' is not currently supported for deep scraping.")

    def parse_shopify_json(self, response):
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
            return

        for product in data.get('products', []):
            product_url = f"{self.start_url.split('/products.json')[0]}/products/{product['handle']}"

            if "(copy)" in product['title'].lower():
                self.logger.info(f"Skipping product with '(copy)' in title: {product['title']}")
                continue

            segment, positioning, animal_replicated, consumption_format = infer_product_details(product['title'])

            if animal_replicated == "n/a":
                self.logger.info(f"Skipping product '{product['title']}' as it does not seem to be a meat/dairy/egg analogue.")
                continue

            for variant in product.get('variants', []):
                item = ProductItem()

                # --- Basic Info ---
                item['title'] = product['title']
                item['brand'] = self.company_name
                item['category'] = product.get('product_type', '')
                item['animal_product_replicated'] = animal_replicated
                item['segment'] = segment
                item['positioning'] = positioning
                item['consumption_format'] = consumption_format

                # --- Status & Availability ---
                item['status'] = "Launched"
                item['availability'] = "Active" if variant.get('available') else "Out of Stock"
                item['in_stock'] = 1 if variant.get('available') else 0
                item['launch_date'] = product.get('created_at', '').split('T')[0]
                item['last_updated'] = product.get('updated_at', '').split('T')[0]

                # --- Pricing & Physical Details ---
                weight = variant.get('grams') or parse_weight_from_title(variant['title']) or parse_weight_from_title(product['title'])
                price = variant.get('price')
                item['price_inr'] = price
                item['weight'] = weight
                item['weight_unit'] = "g" if weight else ""
                item['pack_size'] = variant.get('title') if variant.get('title') != 'Default Title' else f"{weight}g" if weight else ""
                item['price_per_kg_l'] = calculate_price_per_kg_l(price, weight)

                # --- Ingredients & Nutrition from HTML body ---
                body_html = product.get('body_html', '')
                ingredients, ingredient_count, allergen_info = extract_ingredients(body_html)
                item['ingredients_list'] = ingredients
                item['ingredient_count'] = ingredient_count
                item['allergen_info'] = allergen_info

                # --- Other Details from HTML Body ---
                item['shelf_life'] = extract_from_html(r'Shelf Life\s*[:-]?\s*(\d+\s*\w+)', body_html)
                item['storage_condition'] = extract_from_html(r'Storage Condition\s*[:-]?\s*([\w\s]+)', body_html, default="Ambient")
                item['manufactured_by'] = extract_from_html(r'Manufactured by\s*[:-]?\s*([^,]+)', body_html)

                # --- Distribution & Sales ---
                item['channel'] = "D2C"
                item['distribution_channels'] = "Brand website"

                # --- Digital & Reference ---
                item['product_page'] = product_url
                item['website'] = self.start_url.split('/products.json')[0]
                item['images'] = product.get('images', [{}])[0].get('src', '') if product.get('images') else ""
                item['sku_code'] = variant.get('sku', '')
                item['source_name'] = f"{self.company_name} Official Website"
                item['source_links'] = product_url
                item['notes'] = "" # Clearer to have an empty string than n/a

                # --- Administrative ---
                item['added_by'] = self.name # Spider name

                yield item
