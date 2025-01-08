from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.filters import IsSub
from datetime import datetime

router = Router()

@router.callback_query(F.data == 'subscription')
async def sub_menu(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    async with AsyncSessionLocal() as session:
        user = await funcs.get_user(session, uid)
        user_sub = user.subscription
    if user_sub:
        # Преобразование строки даты в объект datetime
        end_date = datetime.strptime(user.sub_end_date, "%d-%m-%Y %H:%M:%S")
        current_date = datetime.now()

        # Вычисляем оставшиеся дни
        days_left = (end_date - current_date).days
        answer_str = ('\n<b>Подписка:</b> Активна'
                      f'\n<b>Дата начала подписки:</b> {user.sub_start_date}'
                      f'\n<b>Дата окончания подписки:</b> {user.sub_end_date}'
                      f'\n<b>Осталось дней:</b> {days_left}')
    else:
        answer_str = ('\n<b>Подписка:</b> Не активна'
                      f'\n<b>Дата начала подписки:</b> Нет'
                      f'\n<b>Дата окончания подписки:</b> Нет')
    await call.message.answer(text=answer_str, parse_mode='HTML')
