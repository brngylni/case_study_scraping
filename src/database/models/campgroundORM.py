from sqlalchemy import Column, String, Float, Boolean, Integer, TIMESTAMP, JSON
from src.database.engine import Base


class CampgroundORM(Base):
    __tablename__ = "campgrounds"

    id = Column(String, primary_key=True)
    type = Column(String)
    link_self = Column(String)  # Flatten the nested `links.self`
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    region_name = Column(String)
    administrative_area = Column(String, nullable=True)
    nearest_city_name = Column(String, nullable=True)
    accommodation_type_names = Column(JSON, default=list)  # List[str]
    bookable = Column(Boolean, default=False)
    camper_types = Column(JSON, default=list)  # List[str]
    operator = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    photo_urls = Column(JSON, default=list)  # List[str]
    photos_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    reviews_count = Column(Integer, default=0)
    slug = Column(String, nullable=True)
    price_low = Column(Float, nullable=True)
    price_high = Column(Float, nullable=True)
    availability_updated_at = Column(
        TIMESTAMP(timezone=True),  # 👈 Add this
        nullable=True
    )
