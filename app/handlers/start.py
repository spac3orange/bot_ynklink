from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.core.logger import logger
from app.crud.funcs import add_user
from app.crud import AsyncSessionLocal
from app.keyboards import main_kb
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

