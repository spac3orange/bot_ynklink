from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import with_config
from app.core import logger, aiogram_bot
from app.crud import AsyncSessionLocal, funcs
from app.keyboards import main_kb


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info('Scheduler started')


    async def schedule_subscription_check(self):
        self.scheduler.add_job(
            check_and_notify_subscriptions,
            CronTrigger(hour=9, minute=0)
        )

        self.scheduler.add_job(
            check_and_notify_subscriptions,
            CronTrigger(hour=21, minute=0)
        )



async def notify_users(users):
    for user in users:
        try:
            await aiogram_bot.send_message(chat_id=user.id, text=f"Ваша подписка истекает {user.sub_end_date}. Продлите её!",
                                           reply_markup=main_kb.prolong_sub())
            logger.info(f"Notification sent to {user.id}")
        except Exception as e:
            logger.error(f"Error while sending notification to {user.id}: {e}")

async def notify_expired(users):
    for user in users:
        try:
            await aiogram_bot.send_message(chat_id=user.id, text=f"Ваша подписка истекла. Для возобновления доступа, продлите её.",
                                           reply_markup=main_kb.tarifs())
            logger.info(f"Notification sent to {user.id}")
            async with AsyncSessionLocal() as session:
                await funcs.reset_subscription_for_user(session, user.id)
        except Exception as e:
            logger.error(f"Error while sending notification to {user.id}: {e}")


async def check_and_notify_subscriptions():
    async with AsyncSessionLocal() as session:
        expiring_users = await funcs.get_users_with_expiring_subscriptions(session)
        expired_users = await funcs.get_users_with_expired_subscriptions(session)
    if expiring_users:
        await notify_users(expiring_users)
    if expired_users:
        await notify_expired(expired_users)
    else:
        logger.info("No users with expiring subscription")



