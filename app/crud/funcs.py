from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.models import User, UserData, TempData
from app.core import logger
from sqlalchemy.future import select
from typing import Optional, List, Union
from sqlalchemy.orm.exc import NoResultFound


async def add_user(session: AsyncSession, user_id: int, user_name: str) -> User:
    logger.info(f"Attempting to add or retrieve user with ID: {user_id}")
    try:
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
            logger.info(f"Created new user with ID: {user_id}")
        else:
            logger.info(f"User with ID: {user_id} already exists")

        return user
    except Exception as e:
        logger.error(f"Failed to add or retrieve user with ID: {user_id}. Error: {e}")
        raise


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    logger.info(f"Fetching user with ID: {user_id}")
    try:
        stmt = select(User).filter_by(id=user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()  # Получаем первого подходящего пользователя или None
        if user:
            logger.info(f"User with ID: {user_id} found")
        else:
            logger.warning(f"User with ID: {user_id} not found")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user with ID: {user_id}. Error: {e}")
        raise


async def update_subscription(
    session: AsyncSession,
    user_id: int,
    subscription: str,
    sub_start_date: str,
    sub_end_date: str
) -> User:
    logger.info(f"Updating subscription for user ID: {user_id}")
    try:
        stmt = select(User).filter_by(id=user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            logger.error(f"User with ID: {user_id} not found for subscription update")
            raise ValueError(f"User with ID: {user_id} not found.")

        user.subscription = subscription
        user.sub_start_date = sub_start_date
        user.sub_end_date = sub_end_date

        await session.commit()  # Сохраняем изменения в базе
        await session.refresh(user)  # Обновляем объект

        logger.info(f"Subscription updated for user ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Failed to update subscription for user ID: {user_id}. Error: {e}")
        await session.rollback()
        raise


async def add_user_data(
    session: AsyncSession,
    user_id: int,
    number: Optional[int] = None,
    city: Optional[str] = None,
    document: Optional[int] = None,
    name: Optional[str] = None,
    comment: Optional[str] = None,
    media: Optional[List[Union[str, dict]]] = None
):
    logger.info(f"Adding user data for user ID: {user_id}")
    try:
        # Создаём новую запись
        new_record = UserData(
            id=user_id,
            number=number,
            city=city,
            document=document,
            name=name,
            comment=comment,
            media=media if media else []  # Если media не передано, записываем пустой список
        )
        # Добавляем запись в сессию
        session.add(new_record)
        # Сохраняем изменения
        await session.commit()
        logger.info(f"User data added for user ID: {user_id}")
    except Exception as e:
        logger.error(f"Failed to add user data for user ID: {user_id}. Error: {e}")
        await session.rollback()
        raise


async def add_temp_user_data(
    session: AsyncSession,
    user_id: int,
    number: Optional[int] = None,
    city: Optional[str] = None,
    document: Optional[int] = None,
    name: Optional[str] = None,
    comment: Optional[str] = None,
    media: Optional[List[Union[str, dict]]] = None
):
    logger.info(f"Adding user data for user ID: {user_id}")
    try:
        # Создаём новую запись
        new_record = TempData(
            id=user_id,
            number=number,
            city=city,
            document=document,
            name=name,
            comment=comment,
            media=media if media else []  # Если media не передано, записываем пустой список
        )
        # Добавляем запись в сессию
        session.add(new_record)
        # Сохраняем изменения
        await session.commit()
        await session.refresh(new_record)
        logger.info(f"User data added for user ID: {user_id} with record_id: {new_record.record_id}")
        return new_record.record_id
    except Exception as e:
        logger.error(f"Failed to add user data for user ID: {user_id}. Error: {e}")
        await session.rollback()
        raise


async def transfer_temp_to_user_data(
    session: AsyncSession,
    record_id: int
) -> UserData:
    logger.info(f"Transferring record with record_id: {record_id} from TempData to UserData.")
    try:
        # Извлекаем запись из TempData
        stmt = select(TempData).filter_by(record_id=record_id)
        result = await session.execute(stmt)
        temp_record = result.scalars().first()

        if not temp_record:
            logger.error(f"Record with record_id: {record_id} not found in TempData.")
            raise NoResultFound(f"Record with record_id {record_id} not found in TempData.")

        # Создаём новую запись в UserData
        user_data = UserData(
            id=temp_record.id,
            number=temp_record.number,
            city=temp_record.city,
            document=temp_record.document,
            name=temp_record.name,
            comment=temp_record.comment,
            media=temp_record.media
        )
        session.add(user_data)

        # Удаляем запись из TempData
        await session.delete(temp_record)

        # Сохраняем изменения
        await session.commit()
        logger.info(f"Successfully transferred record_id: {record_id} to UserData.")
        await session.refresh(user_data)  # Обновляем объект user_data
        return user_data
    except Exception as e:
        logger.error(f"Failed to transfer record_id: {record_id} from TempData to UserData. Error: {e}")
        await session.rollback()
        raise