from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
from app.utils import pp, oferta, payment

router = Router()

@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f'user {message.from_user.username} connected')
    uid = message.from_user.id
    uname = message.from_user.username
    async with AsyncSessionLocal() as session:
        user = await add_user(session, uid, uname)
        user_sub = user.subscription
    if user_sub:
        await message.answer('Добро пожаловать', reply_markup=main_kb.start_btns(True))
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
    pinfo = payment
    for p in pinfo:
        if p == pinfo[0]:
            caption = 'Оплата банковскими картами осуществляется через Международный сервис платежей Freedom Pay. К оплате принимаются карты VISA и MasterCard.'
            await message.answer_photo(photo='utils/visa_mc.png', caption=caption, parse_mode='HTML')
            await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.answer(p, parse_mode='HTML', disable_web_page_preview=True)


