from app.crud.session import Base
from app.core import logger
from app.crud.models import Tarifs


async def initialize_database(engine):
    async with engine.begin() as conn:
        # Удаляем существующие таблицы и создаем заново (для разработки)
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Вставляем записи после создания таблицы
        await conn.execute(
            Tarifs.__table__.insert(),
            [
                {"price": 2500},
                {"price": 7125},
                {"price": 27000},
                {"price": 50000},
            ]
        )

        logger.info("Database initialized")