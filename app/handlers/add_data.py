from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.crud import AsyncSessionLocal, funcs, prepare_jsonb_data
from app.keyboards import main_kb
from app.middlewares import album_middleware
from app.states import states
from app.core import aiogram_bot
from app.utils import inform_admins
from app.filters import IsSub
from random import randint
import magic
import os

router = Router()
router.message.filter(IsSub(F))
router.message.middleware(album_middleware.AlbumMiddleware())

media_folder = 'app/media'

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



async def send_data(state_data: dict, from_uid: int):
    uid = from_uid
    sdata = state_data

    adm_message = (f'\nНомер телефона: {sdata['number']}'
                   f'\nГород: {sdata['city']}'
                   f'\nНомер документа: {sdata['doc']}'
                   f'\nФамилия и/или имя: {sdata['name']}'
                   f'\nКомментарий: {sdata['comm']}')
    media_temp = None
    album_builder = None
    if isinstance(sdata['media'], list):
        media_temp = prepare_jsonb_data(sdata['media'])
        album_builder = MediaGroupBuilder()
        for m in sdata['media']:
            if await is_video(m):
                album_builder.add_video(media=FSInputFile(m))
            elif await is_photo(m):
                album_builder.add_photo(media=FSInputFile(m))
    async with AsyncSessionLocal() as session:
        record_id = await funcs.add_temp_user_data(
            session=session,
            user_id=uid,
            number=sdata.get("number"),
            city=sdata.get("city"),
            document=sdata.get("doc"),
            name=sdata.get("name"),
            comment=sdata.get("comm"),
            media=media_temp
        )
    await inform_admins(message=adm_message, from_id=uid, album_builder=album_builder, record_id=record_id)





@router.callback_query(F.data == 'add_data')
async def add_data(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер телефона: ')
    await state.set_state(states.AddData.number)


@router.message(states.AddData.number)
async def p_number(message: Message, state: FSMContext):
    number = message.text
    await state.update_data(number=number)
    await message.answer('Введите город:')
    await state.set_state(states.AddData.city)

@router.message(states.AddData.city)
async def p_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    await message.answer('Введите номер документа:')
    await state.set_state(states.AddData.document)

@router.message(states.AddData.document)
async def p_doc(message: Message, state: FSMContext):
    doc = message.text
    await state.update_data(doc=doc)
    await message.answer('Введите фамилию и/или имя:')
    await state.set_state(states.AddData.name)


@router.message(states.AddData.name)
async def p_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer('Введите комментарий: ')
    await state.set_state(states.AddData.comment)


@router.message(states.AddData.comment)
async def p_comm(message: Message, state: FSMContext):
    comment = message.text
    await state.update_data(comm=comment)
    await message.answer('Загрузите медиа-файлы (до 3-х файлов): '
                         '\n*Не обязательно, для продолжения введите "Нет"' )
    await state.set_state(states.AddData.media)


@router.message(F.media_group_id, states.AddData.media)
async def p_media(message: Message, state: FSMContext, album: list = None):
    saved_files = []
    if album:
        if len(album) > 3:
            await message.answer('Вы можете загрузить максимум 3 медиа файла! Попробуйте еще раз, или напишите "Нет"')
            return
        for media_message in album:
            file_id = None
            file_extension = None
            # Проверяем тип файла и извлекаем его ID
            if media_message.photo:
                file_id = media_message.photo[-1].file_id
            elif media_message.video:
                file_id = media_message.video.file_id
            else:
                await message.answer('Ошибка. Пожалуйста загрузите фото или видео файлы.')
                return
            # Скачиваем файл
            try:
                file_info = await media_message.bot.get_file(file_id)
                file_path = file_info.file_path
                file_extension = os.path.splitext(file_path)[-1]  # Извлекаем расширение из пути
                unique_name = f"{media_message.from_user.id}_{randint(1000, 9999)}{file_extension}"
                file_path = os.path.join(media_folder, unique_name)

                await media_message.bot.download_file(file_info.file_path, destination=file_path)
                saved_files.append(file_path)
                await state.update_data(media=saved_files)
            except Exception as e:
                print(f"Ошибка при скачивании файла: {e}")
    else:
        await message.answer('Медиа-группа пуста')

    sdata = await state.get_data()
    await message.answer('Предпросмотр: ')
    if isinstance(sdata['media'], str):
        await message.answer(f'\nНомер телефона: {sdata['number']}'
                             f'\nГород: {sdata['city']}'
                             f'\nНомер документа: {sdata['doc']}'
                             f'\nФамилия и/или имя: {sdata['name']}'
                             f'\nКомментарий: {sdata['comm']}', reply_markup=main_kb.confirm_data())
    else:
        album_builder = MediaGroupBuilder()
        for m in sdata['media']:
            if await is_video(m):
                album_builder.add_video(media=FSInputFile(m))
            elif await is_photo(m):
                album_builder.add_photo(media=FSInputFile(m))
        await message.answer_media_group(media=album_builder.build())
        await message.answer(f'\nНомер телефона: {sdata['number']}'
                             f'\nГород: {sdata['city']}'
                             f'\nНомер документа: {sdata['doc']}'
                             f'\nФамилия и/или имя: {sdata['name']}'
                             f'\nКомментарий: {sdata['comm']}', reply_markup=main_kb.confirm_data())


@router.message(states.AddData.media)
async def p_nomedia(message: Message, state: FSMContext):
    media = message.text
    await state.update_data(media=media)
    sdata = await state.get_data()
    if sdata['media'].lower() == 'нет':
        await message.answer('Предпросмотр: ')
        await message.answer(f'\nНомер телефона: {sdata['number']}'
                             f'\nГород: {sdata['city']}'
                             f'\nНомер документа: {sdata['doc']}'
                             f'\nФамилия и/или имя: {sdata['name']}'
                             f'\nКомментарий: {sdata['comm']}', reply_markup=main_kb.confirm_data())
    else:
        await message.answer('Ошибка. Введите "Нет", или загрузите медиа-файлы.\nОтменить /cancel')
        return


@router.callback_query(F.data == 'edit_data')
async def p_edit_data(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await add_data(call, state)


@router.callback_query(F.data == 'confirm_data')
async def p_conf_data(call: CallbackQuery, state: FSMContext):
    await call.answer()
    sdata = await state.get_data()
    uid = call.from_user.id
    await state.clear()
    await call.message.answer('Спасибо! Данные будут отправлены администратору на проверку.')
    await send_data(sdata, uid)




@router.callback_query(F.data.startswith('adm_confirm_data_'))
async def adm_confirm_data(call: CallbackQuery):
    from_uid = call.data.split('_')[-2]
    record_id = int(call.data.split('_')[-1])
    await call.answer()
    await aiogram_bot.send_message(from_uid, 'Спасибо! Данные обновлены.')
    await call.message.answer('Данные сохранены. Пользователь получит уведомление.')
    async with AsyncSessionLocal() as session:
        await funcs.transfer_temp_to_user_data(session, record_id)


@router.callback_query(F.data.startswith('adm_decline_data_'))
async def adm_decline_data(call: CallbackQuery):
    from_uid = call.data.split('_')[-2]
    record_id = int(call.data.split('_')[-1])
    await call.answer()
    await aiogram_bot.send_message(from_uid, 'Администратор отклонил ваши данные.')