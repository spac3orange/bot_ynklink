from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router, F
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.utils import create_payment_page, get_payment_status
from datetime import datetime, timedelta
from app.filters import IsSub, IsBlocked
from typing import Optional, Tuple
router = Router()



async def process_subscription(current_sub_end_date: Optional[str], tarif: str) -> Tuple[str, str]:
    now = datetime.utcnow()

    if current_sub_end_date:
        sub_start_date = datetime.strptime(current_sub_end_date, '%d-%m-%Y %H:%M:%S')
        if sub_start_date < now:
            sub_start_date = now
    else:
        sub_start_date = now

    if tarif == "month":  # 1 месяц
        sub_end_date = sub_start_date + timedelta(days=30)
    elif tarif == "quart":  # 3 месяца
        sub_end_date = sub_start_date + timedelta(days=90)
    elif tarif == "year":  # 1 год
        sub_end_date = sub_start_date + timedelta(days=365)
    elif tarif == "sale":  # Тариф без изменения срока
        sub_end_date = sub_start_date
    else:
        raise ValueError(f"Неизвестный тариф: {tarif}")

    sub_start_date_str = sub_start_date.strftime('%d-%m-%Y %H:%M:%S')
    sub_end_date_str = sub_end_date.strftime('%d-%m-%Y %H:%M:%S')

    return sub_start_date_str, sub_end_date_str

@router.callback_query(F.data == 'tarif_info')
async def tar_menu(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите тариф:', reply_markup=main_kb.tarif_menu())



@router.callback_query(F.data.startswith('tar_'), IsBlocked())
async def tar_choose(call: CallbackQuery):
    await call.answer()
    tarif = call.data.split('_')[-1]
    async with AsyncSessionLocal() as session:
        tarif_list = await funcs.get_all_tarifs(session)
        sorted_tarifs = sorted(tarif_list, key=lambda tar: tar.record_id)
    tarif_dict = {'month': sorted_tarifs[0].price,
                  'quart': sorted_tarifs[1].price,
                  'year': sorted_tarifs[2].price,
                  'sale': sorted_tarifs[3].price}
    if tarif == 'month':
        await call.message.answer(f'\n<b>Стоимость:</b> {tarif_dict['month']} тг.',
                                  reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'quart':
        await call.message.answer(f'\n<b>Стоимость:</b> {tarif_dict['quart']} тг.',
                                  reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'year':
        await call.message.answer(f'\n<b>Стоимость:</b> {tarif_dict['year']} тг.',
                                  reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')
    if tarif == 'sale':
        await call.message.answer(f'\n<b>Стоимость:</b> {tarif_dict['sale']} тг.',
                                  reply_markup=main_kb.buy_tarif(tarif), parse_mode='HTML')


@router.callback_query(F.data.startswith('buy_tar_'), IsBlocked())
async def process_buy(call: CallbackQuery):
    await call.answer()
    tar_name = call.data.split('_')[-1]
    async with AsyncSessionLocal() as session:
        tarif_list = await funcs.get_all_tarifs(session)
        sorted_tarifs = sorted(tarif_list, key=lambda tar: tar.record_id)
    tarif_dict = {'month': sorted_tarifs[0].price,
                  'quart': sorted_tarifs[1].price,
                  'year': sorted_tarifs[2].price,
                  'sale': sorted_tarifs[3].price}
    pid, ppage = await create_payment_page(tarif_dict[tar_name])
    if ppage:
        link = f'<a href="{ppage}">Freedom Pay</a>'
        await call.message.answer(f'Ссылка для оплаты: {link}'
                                  f'\n\nПосле оплаты, пожалуйста нажмите кнопку ниже для првоерки статуса платежа.'
                                  f' Когда платеж будет обработан, вы будете перенаправлены на главную страницу.',
                                  reply_markup=main_kb.check_payment(pid, tar_name), parse_mode='HTML')
    else:
        await call.message.answer('Ошибка при создании ссылки на оплату. Пожалуйста, обратитесь в Тех. Поддержку.')


@router.callback_query(F.data.startswith('get_pstatus'), IsBlocked())
async def get_pstatus(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    pid = call.data.split('_')[-1]
    tarif = call.data.split('_')[-2]
    pstatus = await get_payment_status(pid)
    print(pstatus)
    if pstatus in ['new', 'process', 'waiting']:
        await call.message.answer('Платеж еще обрабатывается')
    elif pstatus == 'error':
        await call.message.answer('Ошибка при проведении платежа. Пожалуйста, попробуйте позднее.')
    elif pstatus == 'success':
        await call.message.answer('Оплата прошла успешно.')
        async with AsyncSessionLocal() as session:
            user_data = await funcs.get_user(session, int(uid))
            sub_end_date = user_data.sub_end_date
            sub_start, sub_end = await process_subscription(sub_end_date, tarif)
            subscription = await funcs.update_subscription(session, uid, tarif, sub_start, sub_end)
        if subscription:
            await call.message.answer('Добро пожаловать', reply_markup=main_kb.start_btns(True))
        else:
            await call.message.answer('Ошибка при обновлении данных. Пожалуйста, обратитесь в Тех. Поддержку.')
    else:
        await call.message.answer('Ошибка при обновлении данных. Пожалуйста, обратитесь в Тех. Поддержку.')




