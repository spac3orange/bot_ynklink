import asyncio

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from pydantic import with_config

from app.crud import AsyncSessionLocal, funcs, prepare_jsonb_data
from app.keyboards import main_kb
from app.states import states
from app.filters import IsAdmin
from app.core import logger, aiogram_bot
import magic

router = Router()
router.message.filter(
    IsAdmin()
)

async def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type

async def is_video(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('video')


async def is_photo(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('image')


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
        sorted_tarifs = sorted(tarifs, key=lambda tarif: tarif.record_id)
    tarifs_text = ('Тарифы:'
                   f'\n1. Месячный: {sorted_tarifs[0].price} тг.'
                   f'\n2. Квартальный: {sorted_tarifs[1].price} тг.'
                   f'\n3. Годовой: {sorted_tarifs[2].price} тг.'
                   f'\n4. Акционный: {sorted_tarifs[3].price} тг.'
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
        sorted_tarifs = sorted(tarifs, key=lambda tarif: tarif.record_id)
    tarifs_text = ('Тарифы:'
                   f'\n1. Месячный: {sorted_tarifs[0].price} тг.'
                   f'\n2. Квартальный: {sorted_tarifs[1].price} тг.'
                   f'\n3. Годовой: {sorted_tarifs[2].price} тг.'
                   f'\n4. Акционный: {sorted_tarifs[3].price} тг.'
                   )
    await message.answer(tarifs_text, reply_markup=main_kb.admin_edit_tarifs())


@router.callback_query(F.data == 'adm_users_panel')
async def p_adm_users(call: CallbackQuery):
    await call.answer()
    async with AsyncSessionLocal() as session:
        all_users = await funcs.get_all_users(session)
    if all_users:
        for u in all_users:
            uid = u.id
            uname = u.name
            u_sub = u.subscription
            u_substart = u.sub_start_date
            u_subend = u.sub_end_date
            adm_message = (f'\nTG ID: {uid} '
                           f'\nUsername: {uname}'
                           f'\nПодписка: {u_sub}'
                           f'\nНачало подписки: {u_substart}'
                           f'\nКонец подписки: {u_subend}')
            await call.message.answer(adm_message, reply_markup=main_kb.adm_edit_user(uid))
    else:
        await call.message.answer('Пользователи не найдены.')


@router.callback_query(F.data.startswith('adm_get_data_'))
async def p_adm_get_user_data(call: CallbackQuery):
    await call.answer()
    uid = call.data.split('_')[-1]
    async with AsyncSessionLocal() as session:
        user_data = await funcs.get_user_data_by_user_id(session, int(uid))
    if user_data:
        for d in user_data:
            media = False
            adm_message = (f'\n\nНомер телефона: {d.number}'
                           f'\nГород: {d.city}'
                           f'\nНомер документа: {d.document}'
                           f'\nФамилия и/или имя: {d.name}'
                           f'\nКомментарий: {d.comment}')
            if isinstance(d.media, list) and d.media:
                media = True
                album_builder = MediaGroupBuilder()
                for m in d.media:
                    if await is_video(m):
                        album_builder.add_video(media=FSInputFile(m))
                    elif await is_photo(m):
                        album_builder.add_photo(media=FSInputFile(m))
            if media:
                await call.message.answer_media_group(album_builder.build())
                await call.message.answer(adm_message)
            else:
                await call.message.answer(adm_message)
            await asyncio.sleep(1)
    else:
        await call.message.answer('Данные не найдены.')
    pass

@router.callback_query(F.data.startswith('adm_block_'))
async def p_adm_blockuser(call: CallbackQuery):
    await call.answer()
    uid = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        await funcs.update_subscription(session, uid, 'blocked', None, None)
    await call.message.answer('Пользователь заблокирован.')

@router.callback_query(F.data.startswith('adm_unblock_'))
async def p_adm_unblockuser(call: CallbackQuery):
    await call.answer()
    uid = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        await funcs.update_subscription(session, uid, None, None, None)
    await call.message.answer('Пользователь разблокирован.')
