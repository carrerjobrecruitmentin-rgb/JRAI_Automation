import logging
import json
# import redis

logger = logging.getLogger(__name__)

class QueueWorker:
    """
    Enterprise Redis-backed worker. 
    Listens to a specific queue (e.g. 'crawl_queue', 'llm_queue') and processes jobs.
    """
    
    def __init__(self, queue_name: str, redis_url: str = "redis://localhost:6379/0"):
        self.queue_name = queue_name
        self.redis_url = redis_url
        # self.redis_conn = redis.from_url(self.redis_url)
        
    def start_listening(self):
        logger.info(f"Worker started listening to {self.queue_name}...")
        # while True:
        #     # Blocking pop from redis list
        #     _, message = self.redis_conn.brpop(self.queue_name)
        #     job_data = json.loads(message)
        #     self.process_job(job_data)
        
    def process_job(self, job_data: dict):
        """
        To be implemented by specific worker subclasses (CrawlWorker, OCRWorker, LLMWorker)
        """
        logger.info(f"Processing job: {job_data}")
        pass
