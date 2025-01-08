from app.crud.session import Base
from app.core import logger
from app.crud.models import Tarifs
from sqlalchemy.future import select


async def initialize_database(engine):
    async with engine.begin() as conn:
        # Удаляем существующие таблицы и создаем заново (для разработки)
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Проверяем, пустая ли таблица
        result = await conn.execute(select(Tarifs).limit(1))  # Проверяем наличие хотя бы одной записи
        existing_records = result.scalar()

        # Если записей нет, вставляем новые
        if not existing_records:
            await conn.execute(
                Tarifs.__table__.insert(),
                [
                    {"price": 2500},
                    {"price": 7125},
                    {"price": 27000},
                    {"price": 50000},
                ]
            )
            logger.info("Default tarifs inserted into the database.")

        logger.info("Database initialized")