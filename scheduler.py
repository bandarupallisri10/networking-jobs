"""
Scheduler daemon: runs daily job scrapes and sends morning/evening notifications.

Usage:
    python scheduler.py           # Runs in foreground (Ctrl+C to stop)
    python scheduler.py --once    # Scrape once and exit (for cron use)

Cron alternative (add to crontab with: crontab -e):
    0 7  * * * /usr/bin/python3 /path/to/scheduler.py --once >> /var/log/networkingjobs.log 2>&1
    0 8  * * * /usr/bin/python3 /path/to/notifier.py morning >> /var/log/networkingjobs.log 2>&1
    0 18 * * * /usr/bin/python3 /path/to/notifier.py evening >> /var/log/networkingjobs.log 2>&1
"""
import sys
import time
import logging
import argparse
import schedule
from datetime import datetime

import database as db
from notifier import send_morning_notification, send_evening_notification, send_new_jobs_alert
from config import (
    JOB_TITLES,
    US_COMPANIES,
    MORNING_NOTIFICATION_TIME,
    EVENING_NOTIFICATION_TIME,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("networkingjobs.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_full_scrape():
    """Scrape all portals and company career pages, save new jobs, alert."""
    from scrapers import PORTAL_SCRAPERS, scrape_company_careers

    logger.info("=" * 60)
    logger.info(f"Starting full job scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    total_new = 0

    # ── Scrape job portals ──────────────────────────────────────
    for title in JOB_TITLES:
        for portal_name, scraper_fn in PORTAL_SCRAPERS.items():
            try:
                logger.info(f"[Portal] {portal_name} | Searching: {title}")
                jobs = scraper_fn(title)
                new_count = sum(db.upsert_job(j) for j in jobs)
                total_new += new_count
                logger.info(f"[Portal] {portal_name} | {len(jobs)} found, {new_count} new")
            except Exception as e:
                logger.error(f"[Portal] {portal_name} | Error: {e}")

    # ── Scrape company career pages ─────────────────────────────
    for title in JOB_TITLES:
        for company_name, info in US_COMPANIES.items():
            try:
                logger.info(f"[Company] {company_name} | Searching: {title}")
                jobs = scrape_company_careers(company_name, info["careers_url"], title)
                new_count = sum(db.upsert_job(j) for j in jobs)
                total_new += new_count
                logger.info(f"[Company] {company_name} | {len(jobs)} found, {new_count} new")
            except Exception as e:
                logger.error(f"[Company] {company_name} | Error: {e}")

    logger.info(f"Scrape complete. Total new jobs this run: {total_new}")

    # Send real-time alert if new jobs found
    if total_new > 0:
        send_new_jobs_alert(total_new)

    return total_new


def setup_schedule():
    """Configure daily schedule."""
    # Morning scrape at 7:00 AM so data is ready for 8 AM notification
    schedule.every().day.at("07:00").do(run_full_scrape)

    # Morning notification at configured time (default 08:00)
    schedule.every().day.at(MORNING_NOTIFICATION_TIME).do(send_morning_notification)

    # Midday top-up scrape
    schedule.every().day.at("12:00").do(run_full_scrape)

    # Evening notification at configured time (default 18:00)
    schedule.every().day.at(EVENING_NOTIFICATION_TIME).do(send_evening_notification)

    # Late afternoon scrape to catch new postings
    schedule.every().day.at("17:30").do(run_full_scrape)

    logger.info(f"Schedule configured:")
    logger.info(f"  07:00 - Morning scrape")
    logger.info(f"  {MORNING_NOTIFICATION_TIME} - Morning notification")
    logger.info(f"  12:00 - Midday scrape")
    logger.info(f"  17:30 - Afternoon scrape")
    logger.info(f"  {EVENING_NOTIFICATION_TIME} - Evening notification")


def run_daemon():
    """Run as a long-running background daemon."""
    db.init_db()
    logger.info("Networking Jobs Scheduler started.")
    logger.info(f"Job titles: {', '.join(JOB_TITLES)}")
    logger.info(f"Monitoring {len(US_COMPANIES)} company career pages + 12 job portals")

    setup_schedule()

    # Run an immediate scrape on start
    logger.info("Running initial scrape on startup...")
    run_full_scrape()
    send_morning_notification()

    logger.info("Scheduler running. Press Ctrl+C to stop.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)


def run_once():
    """Single scrape run — for use with cron."""
    db.init_db()
    logger.info("Running single scrape (--once mode)...")
    total = run_full_scrape()
    logger.info(f"Done. {total} new jobs found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Networking Jobs Scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for cron)")
    parser.add_argument("action", nargs="?", choices=["morning", "evening"],
                        help="Send a specific notification immediately")
    args = parser.parse_args()

    if args.action == "morning":
        db.init_db()
        send_morning_notification()
    elif args.action == "evening":
        db.init_db()
        send_evening_notification()
    elif args.once:
        run_once()
    else:
        run_daemon()
