from app.core import config_aiogram, aiogram_bot
from app.keyboards import main_kb
from app.core import logger


async def inform_admins(message, from_id, album_builder=None, record_id=None):
    if isinstance(config_aiogram.admin_id, list):
        for a in config_aiogram.admin_id:
            try:
                if album_builder:
                    await aiogram_bot.send_media_group(chat_id=a, media=album_builder.build())
                    await aiogram_bot.send_message(chat_id=a, text=message, reply_markup=main_kb.admin_confirmation(from_id, record_id))
                else:
                    await aiogram_bot.send_message(chat_id=a, text=message, reply_markup=main_kb.admin_confirmation(from_id, record_id))
            except Exception as e:
                logger.error(e)
    else:
        try:
            if album_builder:
                await aiogram_bot.send_media_group(chat_id=config_aiogram.admin_id, media=album_builder.build())
                await aiogram_bot.send_message(chat_id=config_aiogram.admin_id, text=message,
                                               reply_markup=main_kb.admin_confirmation(from_id, record_id))
            else:
                await aiogram_bot.send_message(chat_id=config_aiogram.admin_id, text=message,
                                               reply_markup=main_kb.admin_confirmation(from_id, record_id))
        except Exception as e:
            logger.error(e)
