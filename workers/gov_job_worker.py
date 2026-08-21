import time
import schedule
from common.logger import log
from common.config import settings

def run_crawler_job():
    log.info("Executing scheduled Government Recruitment Crawler scan...")
    # Add autonomous crawler scraping tasks here
    time.sleep(2)
    log.info("Scheduled Crawler scan complete.")

def main():
    log.info("Starting JRAI Government Job Background Crawler Worker on Render...")
    # Schedule crawler to run every 6 hours
    schedule.every(6).hours.do(run_crawler_job)

    # Initial run upon worker startup
    run_crawler_job()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
