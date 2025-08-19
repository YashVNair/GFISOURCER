# Agent Instructions for Smart Protein Web Scraper

This document provides instructions for developers on how to build and maintain this application, with a focus on keeping it simple for non-technical users.

## Project Goal

The primary goal of the recent changes was to simplify this application so that it can be used by individuals with little to no technical expertise. This involved removing technical jargon from the UI, simplifying the workflow, and packaging the application into a single, easy-to-run executable file.

## Key Simplification Changes

1.  **Packaged Executable:** The application is bundled into a single executable using PyInstaller. This removes the need for users to install Python, pip, or any other dependencies.
2.  **Simplified UI:**
    *   The "Type" field for companies has been removed. The application now automatically detects if a website is built on Shopify.
    *   Only Shopify websites are supported. If a user tries to add a non-Shopify site, the application will inform them that it's not supported.
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
*   **Scraper Logic:** The core scraper logic in `product_spider.py` is currently limited to Shopify sites. If you need to add support for other platforms, you will need to do so in a way that does not complicate the user experience. For example, you could add more automatic platform detectors. Do not re-introduce the manual "Type" field.
