"""
Crawler for finding Kickstarter projects natively.
"""
import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger(__name__)

def crawl_discover_page(limit: int = 1) -> list:
    """
    Crawls the Kickstarter discover page and handles pagination.
    Returns a list of project URLs.
    """
    base_url = "https://www.kickstarter.com/discover/advanced?sort=magic"
    urls = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        for page in range(1, limit + 1):
            logger.info(f"Crawling discover page {page}...")
            url = f"{base_url}&page={page}"
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"HTTP Request failed for discover page {page}: {e}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_urls = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('/projects/') and '?' in href:
                    clean_url = "https://www.kickstarter.com" + href.split('?')[0]
                    if clean_url not in urls:
                        urls.append(clean_url)
                        page_urls.append(clean_url)
                        
            logger.info(f"Found {len(page_urls)} projects on page {page}.")
            time.sleep(2) # Respectful delay
            
    except Exception as e:
        logger.error(f"Error crawling discover page: {e}")
        
    return urls
