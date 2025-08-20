import scrapy
import json
import re
from scrapers.base_scraper import BaseScraper

# Helper functions (to be moved to a shared utility module later)
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
    # ... (rest of the function is the same)
    return segment, "n/a", "n/a"

class ShopifyScraper(BaseScraper):
    """
    A scraper for Shopify websites.
    """
    def start_requests(self):
        """
        Starts the scraping process by requesting the /products.json endpoint.
        """
        yield scrapy.Request(
            f"{self.start_url}/products.json",
            callback=self.parse_shopify_json
        )

    def parse_shopify_json(self, response):
        """
        Parses the JSON response from the /products.json endpoint.
        """
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
            return

        for product in data.get('products', []):
            product_url = f"{self.start_url}/products/{product['handle']}"
            if "(copy)" in product['title'].lower():
                continue

            _, animal_replicated, _ = infer_product_details(product['title'])
            if animal_replicated == "n/a":
                self.logger.info(f"Skipping product '{product['title']}' as it does not seem to be a meat analogue.")
                continue

            for variant in product.get('variants', []):
                item = self.get_product_item()
                ingredients, ingredient_count = extract_ingredients(product.get('body_html', ''))
                weight = variant.get('grams') or parse_weight_from_title(product['title'])
                pack_size = variant.get('title') if variant.get('title') != 'Default Title' else f"{weight}g" if weight else ""

                item['product_name'] = product['title']
                item['segment'] = "PBM"
                item['positioning'] = "Plant-based"
                item['animal_product_replicated'] = "Meat"
                item['consumption_format'] = "RTC"
                item['storage_condition'] = "Frozen" if self.company_name == "Blue Tribe" else "Ambient"
                item['availability'] = "Active" if variant.get('available') else "OOS"
                item['in_stock'] = 1 if variant.get('available') else 0
                item['status'] = "Launched"
                item['price_inr'] = variant.get('price')
                item['weight'] = weight
                item['weight_unit'] = "g"
                item['pack_size'] = pack_size
                item['product_page'] = product_url
                item['source_links'] = product_url
                item['ingredients_list'] = ingredients
                item['ingredient_count'] = ingredient_count
                item['last_updated'] = product.get('updated_at', '').split('T')[0]
                item['notes'] = ""
                yield item
