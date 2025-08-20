import scrapy
import json
import re
from product_scraper.items import ProductItem

import scrapy
import json
import re
from product_scraper.items import ProductItem
import os
import importlib
from scrapers.base_scraper import BaseScraper

def load_scrapers():
    """
    Dynamically loads all scraper plugins from the 'scrapers' directory.
    """
    scrapers = {}
    scrapers_dir = os.path.join(os.path.dirname(__file__), "..", "..", "scrapers")
    for scraper_type in os.listdir(scrapers_dir):
        scraper_dir = os.path.join(scrapers_dir, scraper_type)
        if os.path.isdir(scraper_dir) and not scraper_type.startswith('__'):
            try:
                module_path = f"scrapers.{scraper_type}.spider"
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseScraper) and attr is not BaseScraper:
                        scrapers[scraper_type] = attr
                        break
            except ImportError as e:
                print(f"Could not import scraper '{scraper_type}': {e}")
    return scrapers

class ProductSpider(scrapy.Spider):
    name = "product_spider"
    scrapers = load_scrapers()

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.company_name = kwargs.get('name')
        self.scraper_type = kwargs.get('type')
        self.start_url = kwargs.get('url')

        if not all([self.company_name, self.scraper_type, self.start_url]):
            raise ValueError("Spider must be run with `name`, `type`, and `url` arguments.")

        scraper_class = self.scrapers.get(self.scraper_type)
        if not scraper_class:
            raise ValueError(f"Scraper type '{self.scraper_type}' is not supported.")

        self.scraper_instance = scraper_class(
            spider=self,
            company_name=self.company_name,
            start_url=self.start_url
        )

    def start_requests(self):
        yield from self.scraper_instance.start_requests()

    def parse(self, response, **kwargs):
        # This method is intentionally left empty.
        # The parsing logic is handled by the callbacks defined in the scraper plugins'
        # Request objects. Scrapy requires this method to be present, but it
        # will not be called if the requests have their own callbacks.
        pass
