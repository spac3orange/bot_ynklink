from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
router = Router()

@router.callback_query(F.data == 'tarif_info')
async def tar_menu(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите тариф:', reply_markup=main_kb.tarif_menu())



@router.callback_query(F.data.startswith('tar_'))
async def tar_choose(call: CallbackQuery):
    await call.answer()
    tarif = call.data.split('_')[-1]
    if tarif == 'month':
        await call.message.answer('Месячный тариф:', reply_markup=main_kb.buy_tarif(tarif))
        pass
    if tarif == 'quart':
        await call.message.answer('Квартальный тариф:', reply_markup=main_kb.buy_tarif(tarif))
        pass
    if tarif == 'year':
        await call.message.answer('Годовой тариф:', reply_markup=main_kb.buy_tarif(tarif))
        pass
    if tarif == 'sale':
        await call.message.answer('Акционный тариф:', reply_markup=main_kb.buy_tarif(tarif))
        pass
