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
    if formatted_number.startswith('8'):
        formatted_number = '+7' + formatted_number[1:]

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
            response_parts = ['Найдена запись в QTizim:']
            if d.number and d.number not in ("-", "нет"):
                response_parts.append(f'<b>Номер телефона:</b> {d.number}')
            if d.city and d.city not in ("-", "нет"):
                response_parts.append(f'<b>Город:</b> {d.city}')
            if d.document and d.document not in ("-", "нет"):
                response_parts.append(f'<b>Номер документа:</b> {d.document}')
            if d.name and d.name not in ("-", "нет"):
                response_parts.append(f'<b>Фамилия и/или имя:</b> {d.name}')
            if d.comment and d.comment not in ("-", "нет"):
                response_parts.append(f'<b>Комментарий:</b> {d.comment}')

            if response_parts:
                response_text = '\n'.join(response_parts)
                await message.answer(response_text, parse_mode='HTML')
                await asyncio.sleep(1)
            else:
                await message.answer("Данные по вашему запросу в QTizim не найдены", parse_mode='HTML')


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
    if len(formated_phone) < 10:
        await message.answer("Номер телефона некорректен. Пожалуйста, введите корректный номер.")
        return
    await state.clear()
    if formated_phone[1:].isdigit():
        if not formated_phone.startswith('+'):
            formated_phone = f"+{formated_phone}"
        async with AsyncSessionLocal() as session:
            extracted_data = await funcs.get_user_data_by_number_or_document(session, number=formated_phone)
        if extracted_data:
            await send_data_message(message, extracted_data)
            await asyncio.sleep(1)
            await message.answer('Выберите способ поиска:', reply_markup=main_kb.data_type())
        else:
            await message.answer('Данные по вашему запросу в QTizim не найдены')

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
                await asyncio.sleep(1)
                await message.answer('Выберите способ поиска:', reply_markup=main_kb.data_type())
            else:
                await message.answer('Данные по вашему запросу в QTizim не найдены')
        else:
            await message.answer('Ошибка. Номер документа должен состоять из цифр.')
    else:
        await message.answer("Номер документа должен содержать только цифры. Пожалуйста, введите корректный номер.")
        return