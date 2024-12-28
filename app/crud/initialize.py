from app.crud.session import Base


async def initialize_database(engine):
    async with engine.begin() as conn:
        # Удаляем существующие таблицы и создаем заново (для разработки)
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized")