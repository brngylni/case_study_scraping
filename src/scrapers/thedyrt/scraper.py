from sqlalchemy.ext.asyncio import AsyncSession
import os
import httpx
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

from src.scrapers.util import get_area_description_from_bbox
from src.setup_logging import setup_logger
from src.models.campground import Campground
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from src.database.util import upsert_campground
import asyncio
from datetime import datetime, timedelta

load_dotenv()
logger = setup_logger("scrapers.thedyrt")

longitude_1 = os.getenv("LONGITUDE_1")
longitude_2 = os.getenv("LONGITUDE_2")
latitude_1 = os.getenv("LATITUDE_1")
latitude_2 = os.getenv("LATITUDE_2")
url = os.getenv("DYRT_SEARCH_ENDPOINT")

headers = {
    "accept": "application/vnd.api+json",
    "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/vnd.api+json",
}

MAX_CONCURRENT_REQUESTS = 10


def __parse_campground_response(response_json: Dict[str, Any]) -> List[Campground]:
    campgrounds = []
    for item in response_json.get("data", []):
        try:
            attributes = item.get("attributes", {})
            campground_data = {
                "id": item.get("id"),
                "type": item.get("type"),
                "links": {"self": item["links"]["self"]},
                "name": attributes.get("name"),
                "latitude": attributes.get("latitude"),
                "longitude": attributes.get("longitude"),
                "region-name": attributes.get("region-name"),
                "administrative-area": attributes.get("administrative-area"),
                "nearest-city-name": attributes.get("nearest-city-name"),
                "accommodation-type-names": attributes.get("accommodation-type-names", []),
                "bookable": attributes.get("bookable", False),
                "camper-types": attributes.get("camper-types", []),
                "operator": attributes.get("operator"),
                "photo-url": attributes.get("photo-url"),
                "photo-urls": attributes.get("photo-urls", []),
                "photos-count": attributes.get("photos-count", 0),
                "rating": attributes.get("rating"),
                "reviews-count": attributes.get("reviews-count", 0),
                "slug": attributes.get("slug"),
                "price-low": float(attributes["price-low"]) if attributes.get("price-low") else None,
                "price-high": float(attributes["price-high"]) if attributes.get("price-high") else None,
                "availability-updated-at": attributes.get("availability-updated-at"),
            }
            campground = Campground(**campground_data)
            campgrounds.append(campground)
        except Exception as e:
            logger.error(f"⚠️ Skipping invalid entry: {e}")
    return campgrounds


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=20),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True
)
async def __get_page(page: int) -> Tuple[List[Campground], Optional[str], Optional[int]]:
    params = {
        "filter[search][drive_time]": "any",
        "filter[search][air_quality]": "any",
        "filter[search][electric_amperage]": "any",
        "filter[search][max_vehicle_length]": "any",
        "filter[search][price]": "any",
        "filter[search][rating]": "any",
        "filter[search][bbox]": f"{longitude_1},{latitude_1},{longitude_2},{latitude_2}",
        "sort": "recommended",
        "page[number]": str(page),
        "page[size]": "500"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            json_data = response.json()
            total_pages = json_data.get("meta", {}).get("page-count", None)
            return __parse_campground_response(json_data), json_data.get("links", {}).get("next", None), total_pages
        except httpx.HTTPError as e:
            logger.warning(f"❌ HTTP error on page {page}: {e}")
            return [], None, None
        except Exception as e:
            logger.warning(f"❌ General error on page {page}: {e}")
            return [], None, None


async def scrape(db: AsyncSession, start_page: int = 1):
    try:
        address = get_area_description_from_bbox()

        logger.info("Getting Campgrounds for the Address: \n")
        logger.info(address)
        logger.info("🚀 Fetching first page to determine page count...")
        first_results, _, page_count = await __get_page(start_page)
        logger.info("Number of Pages: %s" % page_count)

        if not first_results:
            logger.warning("❌ No results from page 1. Exiting.")
            return

        await asyncio.gather(*(upsert_campground(db, cg) for cg in first_results))
        await db.commit()
        logger.info(f"✅ Page {start_page} processed ({len(first_results)} entries)")

        if not page_count:
            logger.warning("⚠️ Could not determine total page count. Defaulting to 100.")
            page_count = 100

        start_time = datetime.now()
        for batch_start in range(start_page + 1, page_count + 1, MAX_CONCURRENT_REQUESTS):
            await asyncio.sleep(0)

            batch_pages = range(batch_start, min(batch_start + MAX_CONCURRENT_REQUESTS, page_count + 1))
            logger.info(f"⚙️ Fetching batch: pages {list(batch_pages)}")

            tasks = [__get_page(p) for p in batch_pages]
            results = await asyncio.gather(*tasks)

            for page_num, (campgrounds, _, _) in zip(batch_pages, results):
                for cg in campgrounds:
                    await upsert_campground(db, cg)
                logger.info(f"✅ Page {page_num} done ({len(campgrounds)} entries)")

            # Progress logging
            pages_done = batch_start + len(batch_pages) - 1
            percentage = int((pages_done / page_count) * 100)
            elapsed = datetime.now() - start_time
            est_total = (elapsed / percentage) * 100 if percentage else timedelta(seconds=0)
            remaining = est_total - elapsed
            logger.info(f"📊 Progress: {percentage}% — ⏱ ETA: {str(remaining).split('.')[0]}")

            await db.commit()

    except asyncio.CancelledError:
        logger.warning("❌ Scraper cancelled")
        raise
    except Exception as e:
        logger.error(f"❌ Scraper error: {e}")
    finally:
        await db.close()
