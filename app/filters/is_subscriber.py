from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs
from app.crud import AsyncSessionLocal


class IsSub(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        user_id = str(message.from_user.id)  # Получаем ID пользователя из сообщения

        # Получаем список пользователей с активной подпиской из базы данных
        async with AsyncSessionLocal() as session:
            active_users = await funcs.get_active_users(session)

        # Извлекаем список ID пользователей, у которых активная подписка
        sub_list = [str(user.id) for user in active_users]

        # Проверяем, есть ли ID пользователя в списке активных подписчиков
        return user_id in sub_list
