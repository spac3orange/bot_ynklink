import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.core import aiogram_bot
from app.core.logger import logger
from app.keyboards import set_commands_menu
from app.handlers import start, tarifs, add_data, get_data, subscription, admin_panel
from app.crud import initialize_database, engine
from app.utils import Scheduler

async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(tarifs.router)
    dp.include_router(add_data.router)
    dp.include_router(get_data.router)
    dp.include_router(subscription.router)
    dp.include_router(admin_panel.router)

    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД
    await initialize_database(engine)

    # инициализация планировщика
    scheduler = Scheduler()
    await scheduler.schedule_subscription_check()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    await asyncio.gather(task1)


if __name__ == '__main__':
    asyncio.run(main())
