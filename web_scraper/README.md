# Smart Protein Web Scraper

Welcome to the Smart Protein Web Scraper! This application helps you easily collect product information from the websites of various "smart protein" companies.

It's designed to be simple: you add a company's website, and the app does the rest. All the data is saved automatically, and you can view it right in the app or export it to a file.

## Features

- **Easy to Use:** A simple, graphical interface for managing the entire process.
- **Add Companies Easily:** Just enter a company's name and website address. The app automatically figures out if it can be scraped.
- **Automatic Scraping:** The app can check multiple websites at once, saving you time.
- **Your Data is Saved:** All collected information is stored in a local database, so you never lose your data.
- **Export Your Data:** You can easily save all the collected product information to a JSON or CSV file on your computer.

## How to Install and Run the Application

1.  **Download the Application:** Get the latest version of the `Smart Protein Scraper` application file from the provided link.
2.  **Run the App:** Double-click the downloaded file to start the application. There's no other installation needed!

## How to Use the Application

The application has two main tabs: "Scraper Control" and "Data Viewer".

### Scraper Control Tab

This is where you manage the list of companies you want to get data from.

- **To Add a Company:**
    1.  In the "Add New Company" section, type the name of the company and the full URL of its website (e.g., `https://www.example.com`).
    2.  Click the **"Add Company"** button.
    3.  The application will check the website. If it's a compatible Shopify store, it will be added to the list. If not, a message will appear to let you know.

- **To Remove a Company:**
    1.  Click on a company in the list to select it.
    2.  Click the **"Remove Selected Company"** button.

- **To Start Scraping:**
    1.  Click the **"Run All Scrapers"** button.
    2.  The application will start visiting each website in your list to find product information.
    3.  You can see the progress in the "Scraper Log" window. It will tell you which companies it's scraping and whether it was successful.

### Data Viewer Tab

This is where you can see all the product information that has been collected.

- **View Your Data:** The table in this tab shows all the products found by the scraper.
- **Refresh the View:** After running the scrapers, click the **"Refresh Data"** button to see the newly collected information.
- **Export to a File:**
    1.  Click the **"Export Data"** button.
    2.  You will be asked where you want to save the file and what to name it.
    3.  The data will be saved in both JSON and CSV formats, which can be opened in a spreadsheet program like Excel.
