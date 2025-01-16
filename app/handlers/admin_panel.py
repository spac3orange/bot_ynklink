import asyncio

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

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


from datetime import datetime, timedelta

async def add_days_to_date(sub_end_date: str, days: int) -> str:
    try:
        end_date = datetime.strptime(sub_end_date, "%d-%m-%Y %H:%M:%S")
        new_end_date = end_date + timedelta(days=days)
        return new_end_date.strftime("%d-%m-%Y %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Неверный формат даты: {sub_end_date}. Ожидаемый формат: '%d-%m-%Y %H:%M:%S'. Ошибка: {e}")



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
                   f'\n4. Акционный: {sorted_tarifs[3].price} тг. Дней: {sorted_tarifs[3].days}'
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
    if tar_num == 4:
        await message.answer('Введите кол-во дней: ')
        await state.set_state(states.AdmEditTar.days)
        await state.update_data(tar_num=4, tar_price=tar_price)
    else:
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
                       f'\n4. Акционный: {sorted_tarifs[3].price} тг. Дней: {sorted_tarifs[3].days}'
                       )
        await message.answer(tarifs_text, reply_markup=main_kb.admin_edit_tarifs())


@router.message(states.AdmEditTar.days)
async def p_edit_tar_4(message: Message, state: FSMContext):
    days = message.text
    sdata = await state.get_data()
    tar_num = int(sdata['tar_num'])
    tar_price = int(sdata['tar_price'])
    tar_days = int(days)
    await state.clear()
    async with AsyncSessionLocal() as session:
        await funcs.update_tarif(session, record_id=tar_num, price=tar_price, days=tar_days)
    await message.answer('Стоимость обновлена.')

    async with AsyncSessionLocal() as session:
        tarifs = await funcs.get_all_tarifs(session)
        sorted_tarifs = sorted(tarifs, key=lambda tarif: tarif.record_id)
    tarifs_text = ('Тарифы:'
                   f'\n1. Месячный: {sorted_tarifs[0].price} тг.'
                   f'\n2. Квартальный: {sorted_tarifs[1].price} тг.'
                   f'\n3. Годовой: {sorted_tarifs[2].price} тг.'
                   f'\n4. Акционный: {sorted_tarifs[3].price} тг. Дней: {sorted_tarifs[3].days}'
                   )
    await message.answer(tarifs_text, reply_markup=main_kb.admin_edit_tarifs())


@router.callback_query(F.data == 'adm_users_panel')
async def p_adm_users(call: CallbackQuery, page: int = 1):
    await call.answer()
    async with AsyncSessionLocal() as session:
        # Пагинация: выбираем пользователей с учетом страницы
        offset = (page - 1) * 10  # Сдвиг для пагинации
        all_users = await funcs.get_users_with_pagination(session, offset=offset, limit=10)

    if all_users:
        # Отправляем информацию о пользователях
        for u in all_users:
            uid = u.id
            uname = u.name
            u_sub = u.subscription
            u_substart = u.sub_start_date
            u_subend = u.sub_end_date
            adm_message = (f'\n<b>TG ID:</b> {uid} '
                           f'\n<b>Username:</b> @{uname} '
                           f'\n<b>Подписка:</b> {u_sub} '
                           f'\n<b>Начало подписки:</b> {u_substart} '
                           f'\n<b>Конец подписки:</b> {u_subend}')
            await call.message.answer(adm_message, reply_markup=main_kb.adm_edit_user(uid), parse_mode='HTML')

        # Проверяем, есть ли ещё пользователи для отображения
        next_page = page + 1
        await call.message.answer(
            "Далее",
            reply_markup=main_kb.pagination(next_page)
        )
    else:
        await call.message.answer('Пользователи не найдены.')


@router.callback_query(F.data.startswith('adm_users_panel_'))
async def p_adm_users_next_page(call: CallbackQuery):
    page = int(call.data.split('_')[-1])
    await p_adm_users(call, page=page)


@router.callback_query(F.data.startswith('adm_get_data_'))
async def p_adm_get_user_data(call: CallbackQuery):
    await call.answer()
    uid = call.data.split('_')[-1]
    async with AsyncSessionLocal() as session:
        user_data = await funcs.get_user_data_by_user_id(session, int(uid))
    if user_data:
        for d in user_data:
            media = False
            adm_message = (f'\n\n<b>Номер телефона:</b> {d.number}'
                           f'\n<b>Город:</b> {d.city}'
                           f'\n<b>Номер документа:</b> {d.document}'
                           f'\n<b>Фамилия и/или имя:</b> {d.name}'
                           f'\n<b>Комментарий:</b> {d.comment}')
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
                await call.message.answer(adm_message, parse_mode='HTML')
            else:
                await call.message.answer(adm_message, parse_mode='HTML')
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


@router.callback_query(F.data.startswith('adm_edit_sub_'))
async def p_edit_sub(call: CallbackQuery):
    await call.answer()
    uid = int(call.data.split('_')[-1])
    await call.message.answer('Выберите действие:', reply_markup=main_kb.adm_sub_menu(uid))


@router.callback_query(F.data.startswith('adm_prolong_sub_'))
async def p_adm_prol_sub(call: CallbackQuery, state: FSMContext):
    await call.answer()
    uid = int(call.data.split('_')[-1])
    await call.message.answer('Введите кол-во дней, которые будут прибавлены: ')
    await state.set_state(states.AdmProlSub.days)
    await state.update_data(target_uid=uid)

@router.message(states.AdmProlSub.days)
async def p_add_days(message: Message, state: FSMContext):
    days = int(message.text)
    sdata = await state.get_data()
    target_uid = int(sdata['target_uid'])
    async with AsyncSessionLocal() as session:
        user_data = await funcs.get_user(session, target_uid)
        cur_sub_end = user_data.sub_end_date
        cur_sub_start = user_data.sub_start_date
        if cur_sub_end:
            new_sub_end = await add_days_to_date(cur_sub_end, days)
            await funcs.update_subscription(session, target_uid, 'special', cur_sub_start, new_sub_end )
        else:
            current_time = datetime.utcnow()
            new_sub_end = await add_days_to_date(current_time.strftime("%d-%m-%Y %H:%M:%S"), days)
            await funcs.update_subscription(session, target_uid, 'special', current_time.strftime("%d-%m-%Y %H:%M:%S"), new_sub_end)
    await message.answer(f'Подписка для пользователя {target_uid} продлена на {days} дней.')
    await state.clear()



@router.callback_query(F.data.startswith('adm_delete_sub_'))
async def p_adm_del_sub(call: CallbackQuery):
    await call.answer()
    uid = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        await funcs.update_subscription(session, uid, None, None, None)
    await call.message.answer(f'Подписка пользователя {uid} аннулирована.')


@router.callback_query(F.data == 'adm_search_user')
async def p_search_user(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Выберите способ поиска:', reply_markup=main_kb.adm_search_menu())


@router.callback_query(F.data == 'adm_search_byid')
async def search_byid(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите id пользователя: ')
    await state.set_state(states.AdmSearchuser.input_id)


@router.message(states.AdmSearchuser.input_id)
async def p_search_byid(message: Message, state: FSMContext):
    target_id = message.text
    if target_id.isdigit():
        async with AsyncSessionLocal() as session:
            udata = await funcs.get_user(session, int(target_id))
            if udata:
                uid = udata.id
                uname = udata.name
                u_sub = udata.subscription
                u_substart = udata.sub_start_date
                u_subend = udata.sub_end_date
                adm_message = (f'\n<b>TG ID:</b> {uid} '
                               f'\n<b>Username:</b> @{uname}'
                               f'\n<b>Подписка:</b> {u_sub}'
                               f'\n<b>Начало подписки:</b> {u_substart}'
                               f'\n<b>Конец подписки:</b> {u_subend}')
                await message.answer(adm_message, reply_markup=main_kb.adm_edit_user(uid), parse_mode='HTML')
            else:
                await message.answer('Пользователь не найден.')
    else:
        await message.answer('Ошибка. ID должен состоять из цифр.')
    await state.clear()


@router.callback_query(F.data == 'adm_search_byuname')
async def search_byuname(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите username пользователя: ')
    await state.set_state(states.AdmSearchuser.input_uname)


@router.message(states.AdmSearchuser.input_uname)
async def p_search_byuname(message: Message, state: FSMContext):
    target_uname = message.text
    async with AsyncSessionLocal() as session:
        if target_uname.startswith('@'):
            target_uname = target_uname.lstrip('@')
        udata = await funcs.get_user_by_name(session, target_uname)
        if udata:
            uid = udata.id
            uname = udata.name
            u_sub = udata.subscription
            u_substart = udata.sub_start_date
            u_subend = udata.sub_end_date
            adm_message = (f'\n<b>TG ID:</b> {uid} '
                           f'\n<b>Username:</b> @{uname}'
                           f'\n<b>Подписка:</b> {u_sub}'
                           f'\n<b>Начало подписки:</b> {u_substart}'
                           f'\n<b>Конец подписки:</b> {u_subend}')
            await message.answer(adm_message, reply_markup=main_kb.adm_edit_user(uid), parse_mode='HTML')
        else:
            await message.answer('Пользователь не найден.')
    await state.clear()
