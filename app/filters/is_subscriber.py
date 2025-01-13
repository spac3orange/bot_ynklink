from app.crud import AsyncSessionLocal
from app.core import logger, config_aiogram
from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.crud import funcs


class IsSub(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = str(message.from_user.id)

        async with AsyncSessionLocal() as session:
            active_users = await funcs.get_active_users(session)

        sub_list = [str(user.id) for user in active_users]

        logger.info(f"Checking if user {user_id} has an active subscription.")
        logger.info(f"Active subscribers: {sub_list}")

        admin_list = config_aiogram.admin_id
        if str(message.from_user.id) in admin_list:
            return True

        return user_id in sub_list