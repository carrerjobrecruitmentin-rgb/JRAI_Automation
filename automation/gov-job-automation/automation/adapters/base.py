from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAdapter(ABC):
    """
    Abstract Base Class for all Government Source Adapters.
    Every adapter (UPSC, SSC, DRDO) MUST implement these methods.
    """
    
    source_name: str = "Base"
    domain: str = ""
    requires_js: bool = False
    
    @abstractmethod
    def get_target_urls(self) -> List[str]:
        """
        Returns a list of URLs to crawl for this specific source.
        E.g., pagination links, specific category links.
        """
        pass
        
    @abstractmethod
    def extract_job_links(self, html_content: str) -> List[str]:
        """
        Extracts individual job notification links from a listing page.
        """
        pass

    @abstractmethod
    def parse_job_details(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extracts job details from a specific notification page and returns a standardized JSON structure.
        """
        pass

    def get_standardized_schema(self) -> Dict[str, Any]:
        """
        Returns the mandatory output format that LLM or Scraper must produce.
        """
        return {
            "title": "",
            "department": "",
            "organization": "",
            "vacancies": None,
            "salary_text": "",
            "qualification": "",
            "last_date": "",
            "apply_url": "",
            "notification_pdf": ""
        }
