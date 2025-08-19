import scrapy
import json
import re
from product_scraper.items import ProductItem

# Helper functions can remain here or be moved to a separate utils.py file
def extract_ingredients(body_html):
    if not body_html:
        return "", 0
    from bs4 import BeautifulSoup
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
    match = re.search(r'\((\d+)\s*g\)', title, re.IGNORECASE)
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
    elif "noodles" in title_lower or "halwa" in title_lower or "fries" in title_lower:
        animal_replicated = "n/a"
    elif "soya chaap" in title_lower:
        animal_replicated = "Meat"
    positioning = "Plant-based"
    if "high protein" in title_lower:
        positioning = "High protein vegetarian product"
    return segment, animal_replicated, positioning

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
            yield scrapy.Request(f"{self.start_url}/products.json", self.parse_shopify_json)
        else:
            self.logger.error(f"Scraper type '{self.scraper_type}' is not supported for company '{self.company_name}'.")

    def parse_shopify_json(self, response):
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
            return

        for product in data.get('products', []):
            product_url = f"{self.start_url}/products/{product['handle']}"

            if "(copy)" in product['title'].lower():
                continue

            segment, animal_replicated, positioning = infer_product_details(product['title'])
            if animal_replicated == "n/a":
                self.logger.info(f"Skipping product '{product['title']}' as it does not seem to be a meat analogue.")
                continue

            for variant in product.get('variants', []):
                ingredients, ingredient_count = extract_ingredients(product.get('body_html', ''))
                weight = variant.get('grams') or parse_weight_from_title(product['title'])
                pack_size = variant.get('title') if variant.get('title') != 'Default Title' else f"{weight}g" if weight else ""

                item = ProductItem()
                item['product_name'] = product['title']
                item['brand'] = self.company_name
                item['segment'] = segment
                item['positioning'] = positioning
                item['animal_product_replicated'] = animal_replicated
                item['consumption_format'] = "RTC"
                # Storage condition can be inferred or set based on brand if needed
                item['storage_condition'] = "Frozen" if self.company_name == "Blue Tribe" else "Ambient"
                item['availability'] = "Active" if variant.get('available') else "OOS"
                item['in_stock'] = 1 if variant.get('available') else 0
                item['status'] = "Launched"
                item['price_inr'] = variant.get('price')
                item['weight'] = weight
                item['weight_unit'] = "g"
                item['pack_size'] = pack_size
                item['distribution_channels'] = "Brand website"
                item['channel'] = "D2C"
                item['product_page'] = product_url
                item['website'] = self.start_url
                item['source_name'] = f"{self.company_name} Official Website"
                item['source_links'] = product_url
                item['ingredients_list'] = ingredients
                item['ingredient_count'] = ingredient_count
                item['last_updated'] = product.get('updated_at', '').split('T')[0]
                item['notes'] = ""
                yield item
