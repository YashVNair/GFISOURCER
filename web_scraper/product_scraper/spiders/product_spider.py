import scrapy
import json
import re
from product_scraper.items import ProductItem

# Helper functions
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

def extract_claims(body_html):
    if not body_html:
        return ""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body_html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True).lower()

    possible_claims = [
        'vegan', 'plant-based', 'gluten-free', 'non-gmo', 'gmo-free',
        'organic', 'natural', 'no preservatives', 'high protein',
        'dairy-free', 'soy-free', 'no added sugar'
    ]

    found_claims = [claim for claim in possible_claims if claim in text]

    return ", ".join(list(set(found_claims)))

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
        elif self.scraper_type == 'trekky':
            trekky_url = f"{self.start_url}/cities?city=paris&page=1"
            yield scrapy.Request(trekky_url, self.parse_trekky_listing)
        elif self.scraper_type == 'playwright':
            # For this type, we tell Scrapy to use Playwright via the meta flag
            yield scrapy.Request(
                self.start_url,
                callback=self.parse_playwright_page,
                meta={"playwright": True}
            )
        else:
            self.logger.error(f"Scraper type '{self.scraper_type}' is not supported for company '{self.company_name}'.")

    def parse_playwright_page(self, response):
        """
        This parser is used for pages that require JavaScript rendering.
        The response object here has been processed by Playwright.
        The structure of the trekky-reviews site is the same across levels,
        so we can reuse the same parsing logic as the simple 'trekky' type.
        """
        self.logger.info(f"Successfully rendered and fetched page with Playwright: {response.url}")
        # The page structure is the same as level2, so we can reuse the listing parser
        yield from self.parse_trekky_listing(response)

    def parse_trekky_listing(self, response):
        self.logger.info(f"Parsing hotel listing on {response.url}")
        for hotel_link in response.css('.hotel-link'):
            # When following links from a Playwright response, we don't need to add the meta flag again
            # unless the linked page also requires special Playwright actions. Here it doesn't.
            yield response.follow(url=hotel_link, callback=self.parse_trekky_hotel)

    def parse_trekky_hotel(self, response):
        self.logger.info(f"Parsing hotel details on {response.url}")
        item = ProductItem()
        item['brand'] = self.company_name
        item['product_name'] = response.css('.hotel-name::text').get(default='').strip()
        email = response.css('.hotel-email::text').get(default='').strip()
        reviews = response.css('.hotel-review .review-rating::text').getall()
        review_ratings = [r.strip() for r in reviews]
        item['notes'] = f"Email: {email}, Reviews: {', '.join(review_ratings)}"
        item['product_page'] = response.url
        item['website'] = self.start_url
        item['last_updated'] = 'n/a'
        yield item

    def parse_shopify_json(self, response):
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
            return
        for product in data.get('products', []):
            product_url = f"{self.start_url}/products/{product['handle']}"
            if "(copy)" in product['title'].lower(): continue
            _, animal_replicated, _ = infer_product_details(product['title'])
            if animal_replicated == "n/a":
                self.logger.info(f"Skipping product '{product['title']}' as it does not seem to be a meat analogue.")
                continue
            for variant in product.get('variants', []):
                body_html = product.get('body_html', '')
                ingredients, ingredient_count = extract_ingredients(body_html)
                claims = extract_claims(body_html)
                weight = variant.get('grams') or parse_weight_from_title(product['title'])
                pack_size = variant.get('title') if variant.get('title') != 'Default Title' else f"{weight}g" if weight else ""
                item = ProductItem()
                item['product_name'] = product['title']
                item['brand'] = self.company_name
                # ... (rest of the shopify item population logic is the same)
                item['segment'], item['positioning'], item['animal_product_replicated'] = "PBM", "Plant-based", "Meat"
                item['consumption_format'] = "RTC"
                item['storage_condition'] = "Frozen" if self.company_name == "Blue Tribe" else "Ambient"
                item['availability'] = "Active" if variant.get('available') else "OOS"
                item['in_stock'] = 1 if variant.get('available') else 0
                item['status'] = "Launched"
                item['price_inr'] = variant.get('price')
                item['weight'] = weight
                item['weight_unit'] = "g"
                item['pack_size'] = pack_size
                item['sku'] = variant.get('sku')
                item['claims'] = claims
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
