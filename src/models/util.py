from src.database.models.campgroundORM import CampgroundORM
from src.models.campground import Campground, CampgroundLinks


def pydantic_to_orm(data: Campground) -> CampgroundORM:
    return CampgroundORM(
        id=data.id,
        type=data.type,
        link_self=str(data.links.self),  # Important: convert HttpUrl to str
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        region_name=data.region_name,
        administrative_area=data.administrative_area,
        nearest_city_name=data.nearest_city_name,
        accommodation_type_names=data.accommodation_type_names,
        bookable=data.bookable,
        camper_types=data.camper_types,
        operator=data.operator,
        photo_url=str(data.photo_url) if data.photo_url else None,
        photo_urls=[str(url) for url in data.photo_urls],
        photos_count=data.photos_count,
        rating=data.rating,
        reviews_count=data.reviews_count,
        slug=data.slug,
        price_low=data.price_low,
        price_high=data.price_high,
        availability_updated_at=data.availability_updated_at
    )


def orm_to_pydantic(orm_obj: CampgroundORM) -> Campground:
    return Campground(
        id=orm_obj.id,
        type=orm_obj.type,
        links=CampgroundLinks(self=orm_obj.link_self),
        name=orm_obj.name,
        latitude=orm_obj.latitude,
        longitude=orm_obj.longitude,
        region_name=orm_obj.region_name,
        administrative_area=orm_obj.administrative_area,
        nearest_city_name=orm_obj.nearest_city_name,
        accommodation_type_names=orm_obj.accommodation_type_names,
        bookable=orm_obj.bookable,
        camper_types=orm_obj.camper_types,
        operator=orm_obj.operator,
        photo_url=orm_obj.photo_url,
        photo_urls=orm_obj.photo_urls,
        photos_count=orm_obj.photos_count,
        rating=orm_obj.rating,
        reviews_count=orm_obj.reviews_count,
        slug=orm_obj.slug,
        price_low=orm_obj.price_low,
        price_high=orm_obj.price_high,
        availability_updated_at=orm_obj.availability_updated_at
    )


