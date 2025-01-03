from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.utils import create_payment_page, get_payment_status
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
    pid, ppage = await create_payment_page(price_dict[tar_name])
    if ppage:
        link = f'<a href="{ppage}">Freedom Pay</a>'
        await call.message.answer(f'Ссылка для оплаты: {link}'
                                  f'\n\nПосле оплаты, пожалуйста нажмите кнопку ниже для првоерки статуса платежа.'
                                  f' Когда платеж будет обработан, вы будете перенаправлены на главную страницу.',
                                  reply_markup=main_kb.check_payment(pid, tar_name))
    else:
        await call.message.answer('Ошибка при создании ссылки на оплату. Пожалуйста, обратитесь в Тех. Поддержку.')


@router.callback_query(F.data.startswith('get_pstatus'))
async def get_pstatus(call: CallbackQuery):
    await call.answer()
    pid = call.data.split('_')[-1]
    tarif = call.data.split('_')[-2]
    pstatus, tarif = await get_payment_status(pid, tarif)
    if pstatus in ['new', 'process', 'waiting']:
        await call.message.answer('Платеж еще обрабатывается')
    else:
        pass
    print('Статус платежа:', pstatus)

