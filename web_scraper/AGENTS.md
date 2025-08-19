# Agent Instructions for Smart Protein Web Scraper

This document provides instructions for developers on how to build and maintain this application, with a focus on keeping it simple for non-technical users.

## Project Goal

The primary goal of the recent changes was to simplify this application so that it can be used by individuals with little to no technical expertise. This involved removing technical jargon from the UI, simplifying the workflow, and packaging the application into a single, easy-to-run executable file.

## Key Simplification Changes

1.  **Packaged Executable:** The application is bundled into a single executable using PyInstaller. This removes the need for users to install Python, pip, or any other dependencies.
2.  **Simplified UI with Manual Override:**
    *   The workflow is centered around automatic platform detection.
    *   To handle edge cases or undetectable sites, a "Type" dropdown has been added. This allows a user to manually specify the platform (`Shopify`, `WooCommerce`), overriding the automatic detection.
3.  **User-Friendly Logging:** The technical Scrapy logs have been replaced with high-level status messages (e.g., "Scraping [Company]... Success").
4.  **Graceful Error Handling:** Technical error messages are caught and replaced with simple, user-friendly dialogs.

## How to Build the Executable

To create the single-file executable for distribution, you will need to have PyInstaller installed.

**1. Install Dependencies:**
Make sure all project dependencies, including `pyinstaller`, are installed. From the `web_scraper` directory, run:
```bash
pip install -r requirements.txt
```

**2. Run the Build Script:**
A `build.py` script is included in the `web_scraper` directory. This script runs PyInstaller with all the necessary arguments to correctly bundle the Scrapy project, data files, and other resources. To run it, execute the following command from the `web_scraper` directory:
```bash
python build.py
```

**3. Locate the Executable:**
After the build process is complete, you will find the executable file in the `dist` directory. The file will be named `Smart Protein Scraper.exe` (on Windows) or `Smart Protein Scraper` (on macOS/Linux). This is the file you should distribute to end-users.

## Maintaining the Simplified Application

*   **Keep it Simple:** When adding new features, always consider the non-technical user. Avoid adding features that require technical knowledge to use.
*   **Test the Build:** After making any significant changes to the code, always run the build script and test the resulting executable to ensure that everything is still working as expected.
*   **Adding a New Scraper:** The application now supports `Shopify` and `WooCommerce`. To add a new scraper for another platform (e.g., 'new_platform'):
    1.  **Implement the Parser:** Add `parse_new_platform_listing` and `parse_new_platform_product` methods to `product_spider.py`.
    2.  **Update the Router:** Add an `elif` condition for `'new_platform'` in the `start_requests` method of the spider.
    3.  **Update the Detector:** Add a new detection fingerprint for the platform in `platform_detector.py`.
    4.  **Update the GUI:** Add `'New Platform'` to the list of values in the `self.type_combo` Combobox in `gui.py`.
