import scrapy

class BaseScraper:
    """
    Base class for all scraper plugins.
    """
    def __init__(self, spider, company_name, start_url, **kwargs):
        """
        Initializes the scraper.

        Args:
            spider (scrapy.Spider): The main spider instance.
            company_name (str): The name of the company being scraped.
            start_url (str): The starting URL for the scraper.
        """
        self.spider = spider
        self.company_name = company_name
        self.start_url = start_url
        self.logger = spider.logger

    def start_requests(self):
        """
        This method should be implemented by each plugin to return the
        initial scraping requests.
        """
        raise NotImplementedError("Each scraper plugin must implement the 'start_requests' method.")

    def get_product_item(self):
        """
        Helper method to create a new ProductItem and populate it with
        common data.
        """
        from product_scraper.items import ProductItem
        item = ProductItem()
        item['brand'] = self.company_name
        item['website'] = self.start_url
        item['distribution_channels'] = "Brand website"
        item['channel'] = "D2C"
        item['source_name'] = f"{self.company_name} Official Website"
        return item
