from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.middlewares import album_middleware
from app.states import states
import os
router = Router()
router.message.middleware(album_middleware.AlbumMiddleware())
media_folder = 'app/media'

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
async def p_doc(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer('Введите комментарий: ')
    await state.set_state(states.AddData.comment)


@router.message(states.AddData.comment)
async def p_doc(message: Message, state: FSMContext):
    comment = message.text
    await state.update_data(comm=comment)
    await message.answer('Загрузите медиа-файлы (до 3-х файлов): ')
    await state.set_state(states.AddData.media)


@router.message(F.media_group_id, states.AddData.media)
async def p_doc(message: Message, state: FSMContext, album: list = None):
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
            elif media_message.document:
                file_id = media_message.document.file_id
                file_extension = f".{media_message.document.file_name.split('.')[-1]}"

            # Скачиваем файл, если ID найден
            if file_id and file_extension:
                file_path = os.path.join(media_folder, f"{file_id}{file_extension}")
                await media_message.bot.get_file(file_id).download(destination=file_path)
                saved_files.append(file_path)

        await message.answer(f'Спасибо за {len(album)} файла(ов)')
    else:
        await message.answer('Медиа-группа пуста')

    # Сохраняем данные о медиа
    await state.update_data(media=saved_files)

    # Выводим пути сохраненных файлов
    for file_path in saved_files:
        print(f"File saved: {file_path}")

    # Завершаем состояние
    await state.clear()
    await message.answer("Файлы сохранены. Спасибо!")

    # media = message.text
    # await state.update_data(media=media)
    # data = await state.get_data()
    # await state.clear()
    # await message.answer('Предпросмотр: ')
