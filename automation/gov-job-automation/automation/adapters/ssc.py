from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseAdapter

class SSCAdapter(BaseAdapter):
    source_name = "SSC"
    domain = "ssc.gov.in"
    requires_js = False # SSC notices are generally static HTML tables
    
    def get_target_urls(self) -> List[str]:
        return [
            "https://ssc.gov.in/notices",
            "https://ssc.gov.in/latest-news"
        ]
        
    def extract_job_links(self, html_content: str) -> List[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        # Example SSC DOM parsing: look for table rows in the notices section
        for a_tag in soup.select("table.notice-list tr td a"):
            href = a_tag.get("href")
            if href and ("notice" in href or "pdf" in href):
                links.append(href)
        return links

    def parse_job_details(self, html_content: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # SSC usually provides raw PDFs, so HTML parsing might just extract the title.
        # Deep extraction will be handled by the OCR/PDF and LLM services.
        title = soup.title.string if soup.title else "SSC Notification"
        
        data = self.get_standardized_schema()
        data["title"] = title.strip()
        data["organization"] = "Staff Selection Commission (SSC)"
        data["apply_url"] = "https://ssc.gov.in"
        
        if url.endswith(".pdf"):
            data["notification_pdf"] = url
            
        return data
