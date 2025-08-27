OLX Car Cover Scraper
Overview
olx_car_cover_scraper.py is a Python script that scrapes OLX India’s search results for "car cover" (https://www.olx.in/items/q-car-cover?isSearchCall=true). It extracts up to 309 ads, collecting title, price, and url, and saves them to a single CSV file. It uses Selenium for dynamic content and BeautifulSoup for HTML parsing, handling OLX’s "Load More" button to fetch all ads.
Features

Extracts title, price, and url for all ads, including related listings (e.g., houses with "covered car parking").
Handles dynamic content with Selenium and clicks "Load More" to collect all ads.
Outputs a single timestamped CSV (e.g., olx_car_cover_results_20250827_170500.csv).
Logs progress and errors to olx_scraper.log.

Prerequisites

Python 3.8+
Chrome browser
Dependencies: selenium, beautifulsoup4, webdriver-manager, pandas
Stable internet connection

Install dependencies:
pip install selenium beautifulsoup4 webdriver-manager pandas

Installation

Download olx_car_cover_scraper.py.
Ensure Chrome is installed.
Install dependencies:pip install selenium beautifulsoup4 webdriver-manager pandas



Usage

Run the script:python olx_car_cover_scraper.py


Output:
CSV: olx_car_cover_results_YYYYMMDD_HHMMSS.csv with title, price, and url.
Log: olx_scraper.log with progress and errors.


Behavior: Extracts up to 309 ads, clicking "Load More" as needed, and saves to CSV.