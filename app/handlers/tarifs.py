from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.utils import create_payment_page
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
        await call.message.answer('\n<b>Стоимость:</b> 2.500 тг.', reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'quart':
        await call.message.answer('\n<b>Стоимость:</b> 7.125 тг.', reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'year':
        await call.message.answer('\n<b>Стоимость:</b> 27.000 тг.', reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'sale':
        await call.message.answer('\n<b>Стоимость:</b> Не указана', reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')


@router.callback_query(F.data.startswith('buy_tar_'))
async def process_buy(call: CallbackQuery):
    await call.answer()
    tar_name = call.data.split('_')[-1]
    print(tar_name)
    price_dict = {'month': 2500, 'quart': 7125, 'year': 27000, 'sale': 100000}
    ppage = await create_payment_page()
    print(ppage)
    price = price_dict[tar_name]
    print(price)
    await call.message.answer('В разработке.')
