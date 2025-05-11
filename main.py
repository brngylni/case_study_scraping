"""
Main entrypoint for The Dyrt web scraper case study.

Usage:
    The scraper can be run directly (`python main.py`) or via Docker Compose (`docker compose up`).

If you have any questions in mind you can connect to me directly via info@smart-maple.com
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.endpoints import router
from src.database.engine import SessionLocal
from src.database.engine import engine, Base



@asynccontextmanager
async def lifespan(app: FastAPI):

    # Apply DB migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Init DB client
    app.state.__db = SessionLocal()

    yield

    # Close DB instance at application destruction
    await app.state.__db.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)



