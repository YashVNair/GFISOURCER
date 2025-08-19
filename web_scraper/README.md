# Smart Protein Web Scraper

This project is a powerful and extensible web scraping application designed to collect product information from various "smart protein" company websites. It features a graphical user interface (GUI) for easy management, a robust Scrapy backend for high-performance concurrent scraping, and a persistent SQLite database for storing data.

## Features

- **Graphical User Interface (GUI):** A user-friendly interface built with Tkinter to manage the scraping process.
- **Dynamic Company Management:** Add, remove, and configure the list of companies to scrape directly from the GUI.
- **Scrapy Backend:** Utilizes the powerful Scrapy framework for efficient and scalable web scraping.
- **Concurrent Scraping:** Scrapes multiple websites at the same time, significantly speeding up the data collection process.
- **Persistent Database:** All scraped data is saved to a local SQLite database (`scraper.db`), preventing data loss and handling de-duplication automatically.
- **Platform Detection:** Automatically detects the e-commerce platform (e.g., Shopify) of a new website to simplify configuration.
- **Anti-Bot Capabilities:** Includes basic anti-bot bypass techniques (e.g., User-Agent spoofing) and is built on a framework (Scrapy + Playwright) that allows for implementing more advanced techniques.
- **Data Export:** Export all collected data from the database to JSON or CSV files directly from the GUI.

## Project Structure

- `gui.py`: The main entry point for the application. Run this file to start the GUI.
- `database.py`: A module that handles all interactions with the SQLite database (`scraper.db`).
- `companies.csv`: A CSV file that stores the master list of companies to be scraped. This is managed by the GUI.
- `file_exporter.py`: A utility module for exporting data from the database to JSON and CSV formats.
- `platform_detector.py`: A utility module that detects the e-commerce platform of a given URL.
- `requirements.txt`: A list of all the Python libraries required for the project.
- `scraper.db`: The SQLite database file where all scraped data is stored.
- `product_scraper/`: This directory is a Scrapy project that contains the core scraping logic.
  - `product_scraper/spiders/`: This folder contains the scraper code.
    - `product_spider.py`: A single, generic spider that can scrape different types of sites based on arguments passed to it by the GUI.
  - `product_scraper/pipelines.py`: Contains the `DatabasePipeline` which processes the scraped data and saves it to the database.
  - `product_scraper/settings.py`: Configuration file for the Scrapy project, including settings for Playwright and User-Agent.
  - `product_scraper/items.py`: Defines the data structure (`ProductItem`) for the scraped data.

## Setup and Installation

Before running the application, you need to install its dependencies.

**1. Install Python Libraries:**
Open your terminal, navigate to this `web_scraper` directory, and run:
```bash
pip install -r requirements.txt
```

**2. Install Browser Binaries for Playwright:**
The scraper uses Playwright to handle JavaScript-heavy websites. Run the following command to download the necessary browser files:
```bash
playwright install --with-deps
```

## How to Run the Application

To run the program, execute the `gui.py` script from your terminal:
```bash
python3 gui.py
```
The main application window will appear.

## How to Use the GUI

The GUI is organized into two tabs: "Scraper Control" and "Data Viewer".

### Scraper Control Tab
- **Manage Companies:** The table on the left shows all the companies configured in your `companies.csv` file.
  - **To Add a Company:**
    1. Fill in the "Name", "URL", and "Type" fields in the "Add New Company" section.
    2. To automatically determine the type, enter the URL and click the "Detect" button.
    3. Click "Add Company".
  - **To Remove a Company:**
    1. Select a company in the table.
    2. Click "Remove Selected Company".
- **Run Scrapers:** Click the "Run All Scrapers" button to start the scraping process for all companies listed in the table. The progress and logs will be displayed in the black text box on the right.
- **Progress Bar:** The progress bar at the bottom will show the overall progress of the scraping run.

### Data Viewer Tab
- **View Data:** This tab contains a table that displays all the data currently stored in your `scraper.db` database.
- **Refresh Data:** Click the "Refresh Data" button to load the latest data from the database into the table. This is useful after a scraping run is complete.
- **Export Data:** Click the "Export Data" button to save a snapshot of your database. You will be prompted to choose a save location and filename for a JSON file and a CSV file.

## How to Extend the Scraper

The application is designed to be easily extended with new scrapers.

### Adding a New Shopify Site
1. Open the GUI.
2. In the "Add New Company" section, enter the company's name and its main URL.
3. Click "Detect". It should automatically fill the "Type" field with `shopify`.
4. Click "Add Company".
5. That's it! The generic spider will automatically handle this new site.

### Adding a New Non-Shopify Site (Custom Scraper)
This requires adding new parsing logic to the spider. Let's say you want to add a scraper for a site called "New Brand".

1.  **Analyze the Site:** Manually inspect the new site's product page HTML to find the CSS selectors for the data you want to extract (e.g., product name, price).
2.  **Add a New Scraper Type:**
    *   Open `web_scraper/product_scraper/spiders/product_spider.py`.
    *   Add a new `elif` condition to the `start_requests` method for your new scraper type (e.g., `elif self.scraper_type == 'new_brand_type':`).
    *   This block should `yield` a `scrapy.Request` pointing to a new parsing method (e.g., `self.parse_new_brand`).
3.  **Implement the New Parser:**
    *   Create the new parsing method (e.g., `def parse_new_brand(self, response):`).
    *   Inside this method, use `response.css('your-selector-here')` to extract the data.
    *   Populate a `ProductItem` with the data and `yield` it, just like in the existing parsers.
4.  **Add the Company to the GUI:**
    *   Run the GUI.
    *   Add the new company, making sure to enter the new `type` you just created (e.g., `new_brand_type`) in the "Type" field.
5.  **Run and Test:** Run the scrapers and check the "Data Viewer" to ensure your new scraper works correctly.
