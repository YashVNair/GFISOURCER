import sys
import os
import threading

# Add the parent directory to the path to allow importing the database module
# This makes the project runnable from the root directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

class DatabasePipeline:
    def open_spider(self, spider):
        """
        This method is called when the spider is opened.
        """
        self.db_lock = threading.Lock()
        # The database table is now created and migrated by the runner script
        # before the spider starts, so we don't need to do it here.
        # database.create_table()
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
        # The `upsert_product` function in our database module is now smart enough
        # to handle the mapping from Scrapy item fields to the correct DB columns.
        database.upsert_product(dict(item), self.db_lock)

        # Use the new 'title' field for logging
        spider.logger.debug(f"Upserted item to DB: {item['title']}")

        return item
