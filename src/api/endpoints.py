from typing import Optional
import asyncio
from src.setup_logging import setup_logger
from src.database.engine import SessionLocal
from src.scrapers.thedyrt.scraper import scrape
from src.scheduler import schedule_scraper
from fastapi import APIRouter
from src.scheduler import scheduler


logger = setup_logger("api.endpoints")

running_task: Optional[asyncio.Task] = None
router = APIRouter(
    prefix="/bot",
    tags=["Bot", "Operations", "Triggers"]
)



@router.post("/start")
async def start_bot():
    global running_task

    if running_task and not running_task.done():
        return {"status": "already running"}

    async def runner():
        db = SessionLocal()
        try:
            await scrape(db)
        finally:
            await db.close()

    # Create the first scraping task
    running_task = asyncio.create_task(runner())

    # Schedule repeat task to start AFTER this one finishes (e.g. 24h interval)
    schedule_scraper(start_in_minutes=5, interval_hours=24)  # start 5 minutes after first run
    return {"status": "started"}


@router.post("/stop")
async def stop_bot():
    global running_task

    if running_task and not running_task.done():
        running_task.cancel()

    try:
        scheduler.remove_job("dynamic_scraper")
        logger.info("📛 Scheduled job removed")
    except Exception as e:
        logger.warning(f"No active scheduled job to remove: {e}")

    return {"status": "stopping"}

