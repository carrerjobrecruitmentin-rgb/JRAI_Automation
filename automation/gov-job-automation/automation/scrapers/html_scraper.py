import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HTMLScraper:
    """
    Static web scraper using requests. 
    Handles basic anti-bot headers and timeouts.
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
    def fetch_page(self, url: str, timeout: int = 15) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None
