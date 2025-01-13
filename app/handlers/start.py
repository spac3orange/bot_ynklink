from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core import logger, config_aiogram
from app.crud import funcs
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.utils import pp, oferta, payment_info

router = Router()

@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f'user {message.from_user.username} connected')
    uid = message.from_user.id
    uname = message.from_user.username
    async with AsyncSessionLocal() as session:
        user = await funcs.add_user(session, uid, uname)
        user_sub = user.subscription if user.subscription != 'blocked' else None
    if user_sub and not str(uid) in config_aiogram.admin_id:
        await message.answer('Добро пожаловать', reply_markup=main_kb.start_btns(True))
    elif str(uid) in config_aiogram.admin_id:
        await message.answer('Добро пожаловать', reply_markup=main_kb.start_btns(False, admin=True))
    else:
        await message.answer('Вы не подписаны.', reply_markup=main_kb.start_btns(False))


@router.message(Command(commands='privacy_policy'))
async def process_pp(message: Message, state: FSMContext):
    await state.clear()
    pp_text = pp
    for p in pp_text:
        await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)

@router.message(Command(commands='oferta'))
async def process_oferta(message: Message, state: FSMContext):
    await state.clear()
    oferta_text = oferta
    for p in oferta_text:
        await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)

@router.message(Command(commands='payment'))
async def process_paymentinfo(message: Message, state: FSMContext):
    await state.clear()
    pinfo = payment_info
    for p in pinfo:
        if p == pinfo[0]:
            caption = 'Оплата банковскими картами осуществляется через Международный сервис платежей Freedom Pay. К оплате принимаются карты VISA и MasterCard.'
            photo = FSInputFile('app/utils/visa_mc.png')
            await message.answer_photo(photo, caption=caption, parse_mode='HTML')
            await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)


@router.message(Command(commands='support'))
async def process_support(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('<b>Тех. Поддержка:</b> @None', parse_mode='HTML')
