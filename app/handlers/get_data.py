from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
router = Router()

@router.callback_query(F.data == 'get_data')
async def get_data(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите способ поиска:', reply_markup=main_kb.data_type())


@router.callback_query(F.data == 'get_data_by_num')
async def get_data_byphone(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Введите номер телефона:')


@router.callback_query(F.data == 'get_data_by_doc')
async def get_data_bydoc(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Введите номер документа:')