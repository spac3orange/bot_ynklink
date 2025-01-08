from app.crud.session import Base
from app.core import logger


async def initialize_database(engine):
    async with engine.begin() as conn:
        # Удаляем существующие таблицы и создаем заново (для разработки)
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")