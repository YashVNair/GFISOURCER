import sys
import os
import threading

# Add the parent directory to the path to allow importing the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

class DatabasePipeline:
    def open_spider(self, spider):
        """
        This method is called when the spider is opened.
        """
        self.db_lock = threading.Lock()
        # Ensure the table is created before any spider starts running
        database.create_table()
        spider.logger.info("Database pipeline opened.")

    def close_spider(self, spider):
        """
        This method is called when the spider is closed.
        """
        spider.logger.info("Database pipeline closed.")

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component.
        It saves the item to the database.
        """
        # The item is a scrapy.Item object, we need to convert it to a dict
        product_data = dict(item)

        # We need to map the item fields to the database column names
        # The item fields are already named correctly, but let's be explicit
        # and handle the fact that our DB columns have spaces.
        db_data = {
            "Product Name": product_data.get("product_name"),
            "Brand": product_data.get("brand"),
            "Segment": product_data.get("segment"),
            "Positioning": product_data.get("positioning"),
            "Animal Product Replicated": product_data.get("animal_product_replicated"),
            "Consumption Format": product_data.get("consumption_format"),
            "Storage Condition": product_data.get("storage_condition"),
            "Availability": product_data.get("availability"),
            "In Stock": product_data.get("in_stock"),
            "Status": product_data.get("status"),
            "Price (INR)": product_data.get("price_inr"),
            "Weight": product_data.get("weight"),
            "Weight Unit": product_data.get("weight_unit"),
            "Pack Size": product_data.get("pack_size"),
            "Distribution Channels": product_data.get("distribution_channels"),
            "Channel": product_data.get("channel"),
            "Product Page": product_data.get("product_page"),
            "Website": product_data.get("website"),
            "Source Name": product_data.get("source_name"),
            "Source Links": product_data.get("source_links"),
            "Ingredients List": product_data.get("ingredients_list"),
            "Ingredient Count": product_data.get("ingredient_count"),
            "Last Updated": product_data.get("last_updated"),
            "Notes": product_data.get("notes"),
        }

        database.upsert_product(db_data, self.db_lock)
        spider.logger.debug(f"Upserted item to DB: {item['product_name']}")

        return item
