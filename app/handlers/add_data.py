from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
router = Router()

@router.callback_query(F.data == 'add_data')
async def add_data(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Введите данные: ')

