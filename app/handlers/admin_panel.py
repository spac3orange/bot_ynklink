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

@router.callback_query(F.data == 'adm_tarifs')
async def p_get_tar(call: CallbackQuery):
    await call.answer()
    async with AsyncSessionLocal() as session:
        tarifs = await funcs.get_all_tarifs(session)
    tarifs_text = ('Тарифы:'
                   f'\n1. Месячный: {tarifs[0].price} тг.'
                   f'\n2. Квартальный: {tarifs[1].price} тг.'
                   f'\n3. Годовой: {tarifs[2].price} тг.'
                   f'\n4. Акционный: {tarifs[3].price} тг.'
                   )
    await call.message.answer(tarifs_text, reply_markup=main_kb.admin_edit_tarifs())


@router.callback_query(F.data == 'adm_edit_tarifs')
async def p_tar_num(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер тарифа и новую цену через пробел:\nПример: 1 5000')
    await state.set_state(states.AdmEditTar.tar_num)


@router.message(states.AdmEditTar.tar_num)
async def p_edit_tar(message: Message, state: FSMContext):
    tar_data = message.text.split(' ')
    tar_num, tar_price = int(tar_data[0]), int(tar_data[1])
    async with AsyncSessionLocal() as session:
        await funcs.update_tarif_price(tar_num, tar_price, session)
    await message.answer('Стоимость обновлена.')
    await state.clear()

    async with AsyncSessionLocal() as session:
        tarifs = await funcs.get_all_tarifs(session)
    tarifs_text = ('Тарифы:'
                   f'\n1. Месячный: {tarifs[0].price} тг.'
                   f'\n2. Квартальный: {tarifs[1].price} тг.'
                   f'\n3. Годовой: {tarifs[2].price} тг.'
                   f'\n4. Акционный: {tarifs[3].price} тг.'
                   )
    await message.answer(tarifs_text, reply_markup=main_kb.admin_edit_tarifs())
