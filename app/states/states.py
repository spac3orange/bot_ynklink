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

class AdmSend(StatesGroup):
    text = State()

class AdmEditTar(StatesGroup):
    tar_num = State()
    days = State()

class AdmEditData(StatesGroup):
    field_num = State()
    new_data = State()

class AdmProlSub(StatesGroup):
    days = State()

class AdmSearchuser(StatesGroup):
    input_id = State()
    input_uname = State()