from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.campground import Campground
from src.database.models.campgroundORM import CampgroundORM
from src.models.util import pydantic_to_orm
from src.setup_logging import setup_logger

logger = setup_logger("database.util")


async def upsert_campground(db: AsyncSession, data: Campground):
    values = pydantic_to_orm(data).__dict__.copy()
    values.pop("_sa_instance_state", None)

    stmt = insert(CampgroundORM).values(**values).on_conflict_do_update(
        index_elements=["id"],
        set_={k: v for k, v in values.items() if k != "id"}
    )

    await db.execute(stmt)