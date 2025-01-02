from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
router = Router()

@router.callback_query(F.data == 'subscription')
async def sub_menu(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    async with AsyncSessionLocal() as session:
        user = await funcs.get_user(session, uid)
        user_sub = user.subscription
    if user_sub:
        answer_str = ('\nПодписка: Активна'
                      f'\nДата начала подписки: {user_sub.sub_start_date}'
                      f'\nДата окончания подписки: {user_sub.sub_end_date}')
    else:
        answer_str = ('\nПодписка: Не активна'
                      f'\nДата начала подписки: Нет'
                      f'\nДата окончания подписки: Нет')
    await call.message.answer(text=answer_str)
