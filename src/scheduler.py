from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.scrapers.thedyrt.scraper import scrape
from src.database.engine import SessionLocal
from src.setup_logging import setup_logger
import asyncio
from datetime import datetime, timedelta

logger = setup_logger("scheduler")
scheduler = AsyncIOScheduler()

def schedule_scraper(start_in_minutes: int = 0, interval_hours: int = 24):
    """Schedules scraper to repeat every X hours, starting at custom time."""
    start_time = datetime.now() + timedelta(minutes=start_in_minutes)

    scheduler.add_job(
        scheduled_scrape_job,
        trigger=IntervalTrigger(hours=interval_hours, start_date=start_time),
        id="dynamic_scraper",
        name="Dynamic scraper interval job",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
        logger.info("📆 Scheduler started")
    logger.info(f"✅ Scraper scheduled every {interval_hours}h starting at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

async def scheduled_scrape_job():
    db = SessionLocal()
    try:
        logger.info("🔁 Running scheduled scrape")
        await scrape(db)
        logger.info("✅ Scheduled scrape finished")
    except asyncio.CancelledError:
        logger.warning("❌ Scheduled job cancelled")
    except Exception as e:
        logger.error(f"❌ Scheduled scrape error: {e}")
    finally:
        await db.close()
