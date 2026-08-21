import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PublisherAPI:
    """
    Connects the Python Automation Pipeline to the main JobRecruitmentAI Backend API.
    Pushes scraped government jobs directly to both Live Server and Local instances.
    """
    
    def __init__(self, live_url: str = "https://jobrecruitment.ai/php-backend/api/public/sync_govt_jobs.php", api_key: str = "jrk_90d4f60aa1433d47b0a6e802aa4248b7b7bb71bd16901e4c"):
        self.live_url = live_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
    def sync_bulk_jobs(self, jobs_list: List[Dict[str, Any]]) -> bool:
        """
        Sends the batch of scraped government jobs to the Live backend to sync to the live database.
        """
        try:
            response = requests.post(self.live_url, json={"jobs": jobs_list}, headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"🌐 [LIVE SYNC SUCCESS] {data.get('message')}")
                return True
            else:
                logger.warning(f"⚠️ [LIVE SYNC FAILED] HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ [LIVE SYNC ERROR] Could not reach live backend: {e}")
            return False
