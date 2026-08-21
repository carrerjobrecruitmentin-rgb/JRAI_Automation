import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from automation.engine.orchestrator import CrawlOrchestrator

logger = logging.getLogger(__name__)

class JobScheduler:
    """
    Enterprise cron job scheduler to trigger the scraping queues at defined intervals.
    For horizontal scaling, this would just push tasks to a Redis Queue.
    """
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        # self.orchestrator = CrawlOrchestrator()
        
    def start(self):
        logger.info("Starting Automation Scheduler...")
        
        # High Priority sources (SSC, UPSC) every 30 minutes
        self.scheduler.add_job(
            self._dispatch_high_priority,
            trigger=IntervalTrigger(minutes=30),
            id='high_priority_crawler',
            name='Crawl High Priority Sources',
            replace_existing=True
        )
        
        # Medium Priority sources (PSUs, Defense) every 4 hours
        self.scheduler.add_job(
            self._dispatch_medium_priority,
            trigger=IntervalTrigger(hours=4),
            id='medium_priority_crawler',
            name='Crawl Medium Priority Sources',
            replace_existing=True
        )

        # Cleanup Task Daily
        self.scheduler.add_job(
            self._cleanup_task,
            trigger=IntervalTrigger(days=1),
            id='daily_cleanup',
            name='Clean Temp PDFs and old logs',
            replace_existing=True
        )
        
        self.scheduler.start()
        
    def _dispatch_high_priority(self):
        logger.info("[CRON] Dispatching High Priority Crawl Queue (SSC, UPSC, RRB)...")
        try:
            import subprocess
            import sys
            import os
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            orchestrator_path = os.path.join(root_dir, "automation", "engine", "orchestrator.py")
            subprocess.Popen([sys.executable, orchestrator_path], cwd=root_dir)
            logger.info("[CRON] Orchestrator process launched successfully.")
        except Exception as e:
            logger.error(f"[CRON] Error launching high priority crawl: {e}")

    def _dispatch_medium_priority(self):
        logger.info("[CRON] Dispatching Medium Priority Crawl Queue (PSUs, State PSCs)...")
        try:
            import subprocess
            import sys
            import os
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            orchestrator_path = os.path.join(root_dir, "automation", "engine", "orchestrator.py")
            subprocess.Popen([sys.executable, orchestrator_path], cwd=root_dir)
        except Exception as e:
            logger.error(f"[CRON] Error launching medium priority crawl: {e}")
        
    def _cleanup_task(self):
        logger.info("[CRON] Running daily maintenance tasks...")
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = JobScheduler()
    scheduler.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.scheduler.shutdown()
