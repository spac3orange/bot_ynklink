from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.models import User, UserData, TempData, Tarifs
from app.core import logger
from typing import Optional, List, Union
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import os
from sqlalchemy import update


async def delete_media_files(media_list: list[str]) -> None:
    for media_path in media_list:
        try:
            if os.path.exists(media_path):
                os.remove(media_path)
                logger.info(f"Deleted media file: {media_path}")
            else:
                logger.warning(f"Media file not found: {media_path}")
        except Exception as e:
            logger.error(f"Failed to delete media file: {media_path}. Error: {e}")



async def get_all_users(session: AsyncSession):
    try:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()

        return users

    except Exception as e:
        # Логирование ошибки
        logger.error(f"Failed to retrieve users: {e}")
        raise


async def get_all_user_data(session: AsyncSession):
    try:
        result = await session.execute(select(UserData))
        user_data_records = result.scalars().all()
        return user_data_records
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all_user_data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_all_user_data: {e}")
    return []


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


async def get_user_data_by_number_or_document(
    session: AsyncSession,
    number: Optional[str] = None,
    document: Optional[str] = None
) -> List[UserData]:
    if not number and not document:
        logger.error("Either number or document must be provided.")
        raise ValueError("Either number or document must be provided.")

    try:
        stmt = select(UserData)
        if number:
            stmt = stmt.filter_by(number=number)
        elif document:
            stmt = stmt.filter_by(document=document)

        result = await session.execute(stmt)
        user_data = list(result.scalars().all())

        if user_data:
            logger.info(f"Found {len(user_data)} records matching the given criteria.")
        else:
            logger.info("No records found matching the given criteria.")

        return user_data

    except Exception as e:
        logger.error(f"Error retrieving data from users_data table: {e}")
        raise



async def get_users_with_expiring_subscriptions(session: AsyncSession):
    """
    Получить пользователей, у которых подписка истекает в ближайшие 3 дня.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список пользователей с истекающей подпиской.
    """
    try:
        # Определяем текущую дату и дату через 3 дня
        now = datetime.now()
        three_days_later = now + timedelta(days=3)

        # Выполняем запрос к таблице пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        # Отбираем пользователей с подпиской, истекающей в ближайшие 3 дня
        expiring_users = []
        for user in users:
            if user.sub_end_date:  # Проверяем, указана ли дата окончания подписки
                sub_end_date = datetime.strptime(user.sub_end_date, "%d-%m-%Y %H:%M:%S")
                if now <= sub_end_date <= three_days_later:
                    expiring_users.append(user)

        return expiring_users

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_users_with_expiring_subscriptions: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_users_with_expiring_subscriptions: {e}")
    return []


async def get_users_with_expired_subscriptions(session: AsyncSession):
    """
    Получить пользователей с истекшей подпиской.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список пользователей с истекшей подпиской.
    """
    try:
        # Определяем текущую дату
        now = datetime.now()

        # Выполняем запрос к таблице пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        # Отбираем пользователей с истекшей подпиской
        expired_users = []
        for user in users:
            if user.sub_end_date:  # Проверяем, указана ли дата окончания подписки
                sub_end_date = datetime.strptime(user.sub_end_date, "%d-%m-%Y %H:%M:%S")
                if sub_end_date < now:  # Если дата окончания подписки раньше текущей даты
                    expired_users.append(user)

        return expired_users

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_users_with_expired_subscriptions: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_users_with_expired_subscriptions: {e}")
    return []


async def reset_subscription_for_user(session: AsyncSession, user_id: int):
    logger.info(f"Resetting subscription for user ID: {user_id}")

    try:
        # Fetch the user from the database
        stmt = select(User).filter_by(id=user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            logger.error(f"User with ID: {user_id} not found for subscription reset")
            raise ValueError(f"User with ID: {user_id} not found.")

        # Reset subscription fields
        user.subscription = None
        user.sub_start_date = None
        user.sub_end_date = None

        await session.commit()  # Save changes to the database
        await session.refresh(user)  # Refresh the object

        logger.info(f"Subscription reset for user ID: {user_id}")
        return user

    except Exception as e:
        logger.error(f"Failed to reset subscription for user ID: {user_id}. Error: {e}")
        await session.rollback()  # Rollback in case of error
        raise


async def get_active_users(session: AsyncSession):
    try:
        stmt = (
            select(User)
            .filter(User.subscription.isnot(None))  # Subscription is not None
            .filter(User.subscription != 'blocked')  # Subscription is not 'blocked'
        )

        result = await session.execute(stmt)
        users = result.scalars().all()

        return users

    except Exception as e:
        logger.error(f"Failed to retrieve active users: {e}")
        raise


async def get_blocked_users(session: AsyncSession) -> List[User]:
    try:
        stmt = (
            select(User)
            .filter(User.subscription == 'blocked')  # Subscription is 'blocked'
        )

        result = await session.execute(stmt)
        users = result.scalars().all()

        logger.info(f"Found {len(users)} blocked users.")
        return users

    except Exception as e:
        logger.error(f"Failed to retrieve blocked users: {e}")
        raise


async def get_all_tarifs(session: AsyncSession):
    """
    Получает все записи из таблицы 'tarifs'.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список объектов Tarifs.
    """
    try:
        # Формируем запрос для получения всех записей
        stmt = select(Tarifs)
        result = await session.execute(stmt)  # Выполняем запрос
        tarifs = result.scalars().all()  # Получаем все строки как объекты Tarifs

        return tarifs

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Failed to retrieve tarifs: {e}")
        raise


async def update_tarif_price(record_id: int,
                             new_price: int,
                             session: AsyncSession):
    try:
        # Получаем запись по record_id
        stmt = select(Tarifs).filter(Tarifs.record_id == record_id)
        result = await session.execute(stmt)
        tarif = result.scalar_one_or_none()  # Получаем одну запись или None

        if tarif is None:
            logger.info(f"No record found with ID {record_id}.")
            return None

        # Обновляем значение price
        tarif.price = new_price
        await session.commit()  # Сохраняем изменения
        await session.refresh(tarif)  # Обновляем объект в сессии

        logger.info(f"Updated record ID {record_id} with new price {new_price}.")
        return tarif

    except Exception as e:
        logger.error(f"Failed to update price for record ID {record_id}: {e}")
        await session.rollback()  # Откатываем изменения в случае ошибки
        raise


async def get_temp_data_by_recid(session: AsyncSession,
                                 record_id: int) -> TempData | None:
    try:
        # Формируем запрос для выбора записи
        stmt = select(TempData).where(TempData.record_id == record_id)
        result = await session.execute(stmt)
        temp_data = result.scalar_one_or_none()

        return temp_data
    except Exception as e:
        logger.error(f"Error while retrieving TempData by record_id {record_id}: {e}")
        raise


async def update_temp_data_by_id(session: AsyncSession,
                                 record_id: int,
                                 fields_to_update: dict) -> bool:
    try:
        # Получаем запись по record_id
        stmt = select(TempData).where(TempData.record_id == record_id)
        result = await session.execute(stmt)
        temp_data = result.scalar_one_or_none()

        if temp_data is None:
            logger.warning(f"No record found with record_id {record_id}")
            return False

        # Обновляем переданные поля
        for field, value in fields_to_update.items():
            if hasattr(temp_data, field):  # Проверяем, существует ли поле в модели
                setattr(temp_data, field, value)
            else:
                logger.warning(f"Field '{field}' does not exist in TempData model.")

        # Сохраняем изменения
        await session.commit()
        logger.info(f"Record with record_id {record_id} updated successfully.")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error while updating TempData record_id {record_id}: {e}")
        raise


async def get_user_data_by_user_id(
    session: AsyncSession,
    user_id: int
) -> List[UserData]:
    if not user_id:
        logger.error("User ID must be provided.")
        raise ValueError("User ID must be provided.")

    try:
        stmt = select(UserData).filter_by(id=user_id)
        result = await session.execute(stmt)
        user_data = list(result.scalars().all())

        if user_data:
            logger.info(f"Found {len(user_data)} records matching user_id {user_id}.")
        else:
            logger.info(f"No records found for user_id {user_id}.")

        return user_data

    except Exception as e:
        logger.error(f"Error retrieving data from UserData table for user_id {user_id}: {e}")
        raise


async def get_user_by_name(session: AsyncSession, name: str) -> User | None:
    logger.info(f"Fetching user with name: {name}")
    try:
        stmt = select(User).filter_by(name=name)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info(f"User with name: {name} found")
        else:
            logger.warning(f"User with name: {name} not found")
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user with name: {name}. Error: {e}")
        raise


async def delete_temp_data(
    session: AsyncSession,
    record_id: int
) -> None:
    logger.info(f"Deleting record with record_id: {record_id} from TempData.")
    try:
        stmt = select(TempData).filter_by(record_id=record_id)
        result = await session.execute(stmt)
        temp_record = result.scalars().first()

        if not temp_record:
            logger.error(f"Record with record_id: {record_id} not found in TempData.")
            raise NoResultFound(f"Record with record_id {record_id} not found in TempData.")

        if temp_record.media:
            media_list = temp_record.media if isinstance(temp_record.media, list) else []
            await delete_media_files(media_list)

        await session.delete(temp_record)

        await session.commit()
        logger.info(f"Successfully deleted record_id: {record_id} from TempData.")
    except Exception as e:
        logger.error(f"Failed to delete record_id: {record_id} from TempData. Error: {e}")
        await session.rollback()
        raise


async def update_tarif(session: AsyncSession,
                       record_id: int,
                       price: int,
                       days: int) -> None:
    try:
        stmt = (
            update(Tarifs)
            .where(Tarifs.record_id == record_id)
            .values(price=price, days=days)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise NoResultFound(f"Tarif with record_id {record_id} not found.")

        await session.commit()
        print(f"Tarif with record_id {record_id} updated successfully.")
    except Exception as e:
        await session.rollback()
        print(f"Failed to update tarif with record_id {record_id}. Error: {e}")
        raise

async def get_users_with_pagination(session: AsyncSession, offset: int, limit: int):
    stmt = select(User).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()