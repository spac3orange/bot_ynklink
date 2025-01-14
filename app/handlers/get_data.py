import asyncio

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.states import states
from app.keyboards import main_kb
from app.filters import IsSub, IsBlocked
import magic
import re

router = Router()

def format_phone_number(number: str) -> str:
    formatted_number = re.sub(r"[^\d+]", "", number)
    if formatted_number.startswith('+'):
        formatted_number = '+' + re.sub(r"[^\d]", "", formatted_number[1:])
    else:
        formatted_number = '+' + re.sub(r"[^\d]", "", formatted_number)

    return formatted_number

def is_valid_document(doc: str) -> bool:
    return bool(re.match(r'^\d+$', doc))


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
            # media = None
            # if isinstance(d.media, list) and d.media:
            #     media = MediaGroupBuilder()
            #     for m in d.media:
            #         if await is_video(m):
            #             media.add_video(media=FSInputFile(m))
            #         elif await is_photo(m):
            #             media.add_photo(media=FSInputFile(m))
            # if media:
            #     await message.answer_media_group(media.build())
            await message.answer(f'\nНомер телефона: {d.number}'
                                 f'\nГород: {d.city}'
                                 f'\nНомер документа: {d.document}'
                                 f'\nФамилия и/или имя: {d.name}'
                                 f'\nКомментарий: {d.comment}')
            await asyncio.sleep(1)
        print(extracted_data)


@router.callback_query(F.data == 'get_data', IsSub(), IsBlocked())
async def get_data(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите способ поиска:', reply_markup=main_kb.data_type())


@router.callback_query(F.data == 'get_data_by_num', IsBlocked())
async def get_data_byphone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер телефона:')
    await state.set_state(states.GetData.input_phone)


@router.message(states.GetData.input_phone)
async def p_input_phone(message: Message, state: FSMContext):
    number = message.text
    formated_phone = format_phone_number(number)
    if len(formated_phone) < 12:
        await message.answer("Номер телефона некорректен. Пожалуйста, введите корректный номер.")
        return
    await state.clear()
    print(number)
    print(number.isdigit())
    if number.isdigit():
        async with AsyncSessionLocal() as session:
            extracted_data = await funcs.get_user_data_by_number_or_document(session, number=number)
        if extracted_data:
            await send_data_message(message, extracted_data)
        else:
            await message.answer('Данные не найдены.')

    else:
        await message.answer('Ошибка. Номер телефона должен состоять из цифр.')



@router.callback_query(F.data == 'get_data_by_doc', IsBlocked())
async def get_data_bydoc(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер документа:')
    await state.set_state(states.GetData.input_doc)


@router.message(states.GetData.input_doc)
async def p_input_doc(message: Message, state: FSMContext):
    number = message.text
    if is_valid_document(number):
        await state.clear()
        if number.isdigit():
            async with AsyncSessionLocal() as session:
                extracted_data = await funcs.get_user_data_by_number_or_document(session, document=number)
            if extracted_data:
                await send_data_message(message, extracted_data)
            else:
                await message.answer('Данные не найдены.')
        else:
            await message.answer('Ошибка. Номер документа должен состоять из цифр.')
    else:
        await message.answer("Номер документа должен содержать только цифры. Пожалуйста, введите корректный номер.")
        return