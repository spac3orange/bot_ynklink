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
router = Router()
router.message.middleware(album_middleware.AlbumMiddleware())


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
    if album:
        count_media = len(album)
        await message.answer(f'Спасибо за {count_media} фото')
    else:
        await message.answer('Спасибо за фото')

    media = message.text
    await state.update_data(media=media)
    data = await state.get_data()
    await state.clear()
    await message.answer('Предпросмотр: ')
