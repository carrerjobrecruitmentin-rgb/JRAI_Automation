import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DynamicScraper:
    """
    Dynamic web scraper using Playwright.
    Handles JavaScript rendering, infinite scroll, and SPA navigation.
    """
    
    def __init__(self):
        # We will import playwright locally to avoid blocking non-playwright tasks
        pass
        
    async def fetch_page_async(self, url: str, wait_for_selector: Optional[str] = None) -> Optional[str]:
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Setup anti-bot measures
                await page.set_extra_http_headers({
                    "Accept-Language": "en-US,en;q=0.9"
                })
                
                await page.goto(url, wait_until="domcontentloaded")
                
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                else:
                    # Give it a small buffer for JS frameworks to hydrate
                    await page.wait_for_timeout(2000)
                    
                content = await page.content()
                await browser.close()
                return content
                
        except Exception as e:
            logger.error(f"Playwright failed for {url}: {str(e)}")
            return None
