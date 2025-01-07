from aiogram.fsm.state import StatesGroup, State


class AddData(StatesGroup):
    number = State()
    city = State()
    document = State()
    name = State()
    comment = State()
    media = State()


class GetData(StatesGroup):
    input_phone = State()
    input_doc = State()