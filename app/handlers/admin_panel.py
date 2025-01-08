from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.crud import AsyncSessionLocal, funcs, prepare_jsonb_data
from app.keyboards import main_kb
from app.middlewares import album_middleware
from app.states import states
from app.core import aiogram_bot
from app.utils import inform_admins
from app.filters import IsAdmin
from random import randint
import magic
import os

router = Router()
router.message.filter(
    IsAdmin()
)

