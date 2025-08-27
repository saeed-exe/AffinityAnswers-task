import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('olx_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Set up Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def get_page_content(driver, url, is_first_page=True):
    """Load page and return parsed HTML content."""
    try:
        if is_first_page:
            driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._2CyHG > div > div:nth-child(2) > ul"))
        )
        time.sleep(3) 
        return BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        logger.error(f"Error loading page {url}: {e}")
        return None

def extract_ads(soup):
    """Extract ad details from a single page."""
    ads = []
    if not soup:
        logger.warning("No soup object to parse.")
        return ads
    
    ad_elements = soup.select('div._2CyHG > div > div:nth-child(2) > ul > li:not(.TA_b7)')
    logger.info(f"Found {len(ad_elements)} ad elements on page.")
    
    for i, ad in enumerate(ad_elements, 1):
        try:
            # Extract title
            title_elem = ad.find('span', class_='_2poNJ')
            title = title_elem.text.strip() if title_elem else 'N/A'
            
            # Extract price
            price_elem = ad.find('span', class_='_2Ks63')
            price = price_elem.text.strip() if price_elem else 'N/A'
            
            # Extract URL
            link_elem = ad.find('a', href=True)
            url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'N/A'
            if url != 'N/A' and not url.startswith('http'):
                url = f"https://www.olx.in{url}"
            
            ads.append({
                'title': title,
                'price': price,
                'url': url
            })
            logger.debug(f"Extracted ad {i}: {title[:50]}... | Price: {price} | URL: {url}")
        except Exception as e:
            logger.warning(f"Error parsing ad {i}: {e}")
            continue
    
    return ads

def save_to_csv(ads, filename='olx_car_cover_results.csv'):
    """Save ads to a CSV file."""
    if not ads:
        logger.warning("No ads to save.")
        return
    
    df = pd.DataFrame(ads)
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Saved {len(ads)} ads to {filename}")

def main():
    base_url = "https://www.olx.in/items/q-car-cover?isSearchCall=true"
    driver = setup_driver()
    all_ads = []
    max_ads = 309
    
    try:
        soup = get_page_content(driver, base_url, is_first_page=True)
        if not soup:
            logger.error("Failed to retrieve first page content. Stopping.")
            return
        
        ads = extract_ads(soup)
        all_ads.extend(ads)
        logger.info(f"Collected {len(ads)} ads from initial page. Total: {len(all_ads)}")
        
        while len(all_ads) < max_ads:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.TA_b7 > div > button[data-aut-id='btnLoadMore']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
                time.sleep(1)  
                driver.execute_script("arguments[0].click();", load_more_button)
                logger.info("Clicked 'Load More' button via JavaScript.")
                time.sleep(5)  
                
                soup = get_page_content(driver, base_url, is_first_page=False)
                if not soup:
                    logger.error("Failed to retrieve page content after clicking 'Load More'. Stopping.")
                    break
                
                ads = extract_ads(soup)
                if not ads:
                    logger.info("No new ads found after clicking 'Load More'. Stopping.")
                    break
                
                all_ads.extend(ads)
                logger.info(f"Collected {len(ads)} new ads. Total: {len(all_ads)}")
            
            except Exception as e:
                logger.info(f"No more 'Load More' button or error: {e}")
                break
        
        all_ads = all_ads[:max_ads]
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"olx_car_cover_results_{timestamp}.csv"
        save_to_csv(all_ads, output_file)
        
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        driver.quit()
        logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()