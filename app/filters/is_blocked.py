from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.core import logger, config_aiogram
from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs


class IsBlocked(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = str(message.from_user.id)  # Получаем ID пользователя из сообщения

        # Получаем список активных пользователей с подпиской
        async with AsyncSessionLocal() as session:
            blocked_users = await funcs.get_blocked_users(session)

        # Список ID пользователей с активной подпиской
        block_list = [str(user.id) for user in blocked_users]

        # Логируем процесс
        logger.info(f"Checking if user {user_id} is blocked.")

        admin_list = config_aiogram.admin_id
        if str(message.from_user.id) in admin_list:
            return True

        # Проверяем, есть ли ID пользователя в списке активных подписчиков
        return user_id not in block_list