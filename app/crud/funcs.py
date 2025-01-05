from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.models import User
from sqlalchemy.future import select


async def add_user(session: AsyncSession,
                   user_id: int,
                   user_name: str) -> User:
    # Попробуем получить пользователя с таким id
    stmt = select(User).filter_by(id=user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        # Если пользователя нет, создаем нового
        user = User(id=user_id, name=user_name, subscription=None)
        session.add(user)
        await session.commit()  # Сохраняем в базу
        await session.refresh(user)  # Обновляем объект

    return user


async def get_user(session: AsyncSession,
                   user_id: int) -> User | None:
    """
    Получить пользователя по id.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Объект User или None, если пользователь не найден.
    """
    stmt = select(User).filter_by(id=user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()  # Получаем первого подходящего пользователя или None
    return user


async def update_subscription(
    session: AsyncSession,
    user_id: int,
    subscription: str,
    sub_start_date: str,
    sub_end_date: str
) -> User:

    stmt = select(User).filter_by(id=user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    user.subscription = subscription
    user.sub_start_date = sub_start_date
    user.sub_end_date = sub_end_date

    await session.commit()  # Сохраняем изменения в базе
    await session.refresh(user)  # Обновляем объект

    return user