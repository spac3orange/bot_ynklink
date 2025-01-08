from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.models import User, UserData, TempData, Tarifs
from app.core import logger
from typing import Optional, List, Union
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

async def get_all_users(session: AsyncSession):
    try:
        # Формируем запрос для получения всех пользователей
        stmt = select(User)  # Запрос для выборки всех пользователей
        result = await session.execute(stmt)  # Выполняем запрос
        users = result.scalars().all()  # Получаем все результаты (список объектов User)

        return users

    except Exception as e:
        # Логирование ошибки
        logger.error(f"Failed to retrieve users: {e}")
        raise


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


async def get_users_with_expired_subscriptions(session: AsyncSession):
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