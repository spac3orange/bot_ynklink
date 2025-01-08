from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.crud import AsyncSessionLocal, funcs, prepare_jsonb_data
from app.keyboards import main_kb
from app.states import states
from app.filters import IsAdmin
from app.core import logger, aiogram_bot
router = Router()
router.message.filter(
    IsAdmin()
)

async def users_mailing(mailing_text: str):
    async with AsyncSessionLocal() as session:
        users_list = await funcs.get_all_users(session)
    for u in users_list:
        try:
            uid = u.id
            await aiogram_bot.send_message(uid, mailing_text)
        except Exception as e:
            logger.error(e)
            continue


@router.callback_query(F.data == 'admin_panel')
async def p_admp(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Панель администратора', reply_markup=main_kb.admin_panel())


@router.callback_query(F.data == 'adm_send_msg')
async def adm_input_text(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите текст рассылки: ')
    await state.set_state(states.AdmSend.text)


@router.message(states.AdmSend.text)
async def adm_send_text(message: Message, state: FSMContext):
    text = message.text
    await users_mailing(text)
    await message.answer('Рассылка завершена.')
    await state.clear()
