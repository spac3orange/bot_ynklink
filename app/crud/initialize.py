from app.crud.session import Base
from app.core import logger
from app.crud.models import Tarifs
from sqlalchemy.future import select


async def initialize_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(select(Tarifs).limit(1))
        existing_records = result.scalar()

        if not existing_records:
            await conn.execute(
                Tarifs.__table__.insert(),
                [
                    {"price": 2500, "days": 30},
                    {"price": 7125, "days": 90},
                    {"price": 27000, "days": 365},
                    {"price": 50000, "days": 0},
                ]
            )
            logger.info("Default tarifs inserted into the database.")

        logger.info("Database initialized")