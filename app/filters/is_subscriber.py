from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.core import logger
from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs  # Импортируем ваши функции для работы с базой данных


class IsSub(BaseFilter):
    """
    Фильтр для проверки, есть ли у пользователя активная подписка.

    Этот фильтр будет использовать F для извлечения ID пользователя из сообщения и будет проверять наличие ID в списке активных подписчиков.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, есть ли у пользователя активная подписка.

        :param message: Сообщение от пользователя.
        :return: True, если у пользователя активная подписка, иначе False.
        """
        user_id = str(message.from_user.id)  # Получаем ID пользователя из сообщения

        # Получаем список активных пользователей с подпиской
        async with AsyncSessionLocal() as session:
            active_users = await funcs.get_active_users(session)

        # Список ID пользователей с активной подпиской
        sub_list = [str(user.id) for user in active_users]

        # Логируем процесс
        logger.info(f"Checking if user {user_id} has an active subscription.")
        logger.info(f"Active subscribers: {sub_list}")

        # Проверяем, есть ли ID пользователя в списке активных подписчиков
        return user_id in sub_list