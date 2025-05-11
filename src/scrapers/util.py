import os

import httpx
from typing import Optional
from src.setup_logging import setup_logger

logger = setup_logger("scrapers.util")

def get_area_description_from_bbox() -> Optional[str]:
    """
    Reverse geocodes the center of a bounding box (defined by two longitude/latitude pairs)
    into a human-readable location description using OpenStreetMap Nominatim API.
    """
    lat1 = float(os.getenv("LATITUDE_1"))
    lat2 = float(os.getenv("LATITUDE_2"))
    lon1 = float(os.getenv("LONGITUDE_1"))
    lon2 = float(os.getenv("LONGITUDE_2"))


    # Calculate center point
    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2

    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": center_lat,
                "lon": center_lon,
                "format": "jsonv2"
            },
            headers={"User-Agent": "campground-scraper/1.0"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("display_name")
    except Exception as e:
        logger.error(f"❌ Reverse geocoding error: {e}")
        return None

