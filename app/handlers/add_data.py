from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.middlewares import album_middleware
from app.states import states
from app.core import aiogram_bot
from random import randint
import magic

import os
router = Router()
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
        for media_message in album:
            file_id = None
            file_extension = None
            # Проверяем тип файла и извлекаем его ID
            if media_message.photo:
                file_id = media_message.photo[-1].file_id
                file_extension = ".jpg"
            elif media_message.video:
                file_id = media_message.video.file_id
                file_extension = ".mp4"
            else:
                await message.answer('Ошибка')
            # Скачиваем файл
            try:
                file_info = await media_message.bot.get_file(file_id)
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
    await state.clear()
    await message.answer('Предпросмотр: ')
    if sdata['media'].lower() == 'нет':
        await message.answer(f'\nНомер телефона: {sdata['number']}'
                             f'\nГород: {sdata['city']}'
                             f'\nНомер документа: {sdata['doc']}'
                             f'\nФамилия и/или имя: {sdata['name']}'
                             f'\nКомментарий: {sdata['comm']}')
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
                             f'\nКомментарий: {sdata['comm']}')

@router.message(states.AddData.media)
async def p_nomedia(message: Message, state: FSMContext):
    media = message.text
    await state.update_data(media=media)
    sdata = await state.get_data()
    await state.clear()
    await message.answer('Предпросмотр: ')
    if sdata['media'].lower() == 'нет':
        await message.answer(f'\nНомер телефона: {sdata['number']}'
                             f'\nГород: {sdata['city']}'
                             f'\nНомер документа: {sdata['doc']}'
                             f'\nФамилия и/или имя: {sdata['name']}'
                             f'\nКомментарий: {sdata['comm']}')
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
                             f'\nКомментарий: {sdata['comm']}')
