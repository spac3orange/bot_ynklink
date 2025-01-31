from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router, F
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.filters import IsSub, IsBlocked
from datetime import datetime

router = Router()

@router.callback_query(F.data == 'subscription', IsBlocked())
async def sub_menu(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    async with AsyncSessionLocal() as session:
        user = await funcs.get_user(session, uid)
        user_sub = user.subscription
    if user_sub:
        end_date = datetime.strptime(user.sub_end_date, "%d-%m-%Y %H:%M:%S")
        current_date = datetime.now()

        days_left = (end_date - current_date).days
        answer_str = ('\n<b>Подписка:</b> Активна'
                      f'\n<b>Дата начала подписки:</b> {user.sub_start_date}'
                      f'\n<b>Дата окончания подписки:</b> {user.sub_end_date}'
                      f'\n<b>Осталось дней:</b> {days_left}')
    else:
        answer_str = ('\n<b>Подписка:</b> Не активна'
                      f'\n<b>Дата начала подписки:</b> Нет'
                      f'\n<b>Дата окончания подписки:</b> Нет')
    await call.message.answer(text=answer_str, parse_mode='HTML', reply_markup=main_kb.prolong_sub())


@router.callback_query(F.data.startswith('prolong_sub_'))
async def p_prol_sub(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите тариф:', reply_markup=main_kb.tarif_menu())
