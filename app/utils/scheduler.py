from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import with_config
from app.core import logger, aiogram_bot
from app.crud import AsyncSessionLocal, funcs


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        print('scheduler started')


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
            await aiogram_bot.send_message(chat_id=user.id, text=f"Ваша подписка истекает {user.sub_end_date}. Продлите её!")
            logger.info(f"Notification sent to {user.id}")
        except Exception as e:
            logger.error(f"Error while sending notification to {user.id}: {e}")


async def check_and_notify_subscriptions():
    async with AsyncSessionLocal() as session:
        expiring_users = await funcs.get_users_with_expiring_subscriptions(session)
    if expiring_users:
        await notify_users(expiring_users)
    else:
        logger.info("No users with expiring subscription")



