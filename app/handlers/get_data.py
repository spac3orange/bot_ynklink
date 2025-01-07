from curses.ascii import isdigit

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.util import await_only
from aiogram.utils.media_group import MediaGroupBuilder
from app.core.logger import logger
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.states import states
from app.keyboards import main_kb
import magic

router = Router()

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

async def send_data_message(message, extracted_data):
    if extracted_data:
        for d in extracted_data:
            media = None
            if isinstance(d.media, list):
                album_builder = MediaGroupBuilder()
                for m in d.media:
                    if await is_video(m):
                        album_builder.add_video(media=FSInputFile(m))
                    elif await is_photo(m):
                        album_builder.add_photo(media=FSInputFile(m))
                media = album_builder
            if media:
                await message.answer_media_group(media.build())
            await message.answer(f'\nНомер телефона: {d.number}'
                                 f'\nГород: {d.city}'
                                 f'\nНомер документа: {d.document}'
                                 f'\nФамилия и/или имя: {d.name}'
                                 f'\nКомментарий: {d.comment}')
        print(extracted_data)


@router.callback_query(F.data == 'get_data')
async def get_data(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите способ поиска:', reply_markup=main_kb.data_type())


@router.callback_query(F.data == 'get_data_by_num')
async def get_data_byphone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер телефона:')
    await state.set_state(states.GetData.input_phone)


@router.message(states.GetData.input_phone)
async def p_input_phone(message: Message, state: FSMContext):
    number = message.text
    await state.clear()
    if isdigit(number):
        async with AsyncSessionLocal() as session:
            extracted_data = await funcs.get_user_data_by_number_or_document(session, number=number)
        if extracted_data:
            await send_data_message(message, extracted_data)
        else:
            await message.answer('Данные не найдены.')

    else:
        await message.answer('Ошибка. Номер телефона должен состоять из цифр.')



@router.callback_query(F.data == 'get_data_by_doc')
async def get_data_bydoc(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер документа:')
    await state.set_state(states.GetData.input_doc)


@router.message(states.GetData.input_doc)
async def p_input_doc(message: Message, state: FSMContext):
    number = message.text
    await state.clear()
    if isdigit(number):
        async with AsyncSessionLocal() as session:
            extracted_data = await funcs.get_user_data_by_number_or_document(session, number=number)
        if extracted_data:
            await send_data_message(message, extracted_data)
        else:
            await message.answer('Данные не найдены.')
    else:
        await message.answer('Ошибка. Номер документа должен состоять из цифр.')