from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def pagination(page: int):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text="Далее", callback_data=f"adm_users_panel_{page}")
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)

def start_btns(sub: bool = False, admin = False):
    kb_builder = InlineKeyboardBuilder()
    if sub:
        kb_builder.button(text='Проверить данные', callback_data='get_data')
        kb_builder.button(text='Внести данные', callback_data='add_data')
        kb_builder.button(text='Подписка', callback_data='subscription')
    elif admin:
        kb_builder.button(text='Проверить данные', callback_data='get_data')
        kb_builder.button(text='Внести данные', callback_data='add_data')
        kb_builder.button(text='Подписка', callback_data='subscription')
        kb_builder.button(text='Панель администратора', callback_data='admin_panel')
    else:
        kb_builder.button(text='Тарифы', callback_data='tarif_info')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def tarif_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Месячный', callback_data='tar_month')
    kb_builder.button(text='Квартальный', callback_data='tar_quart')
    kb_builder.button(text='Годовой', callback_data='tar_year')
    kb_builder.button(text='Акционный', callback_data='tar_sale')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def buy_tarif(tarif_name: str):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Оплатить', callback_data=f'buy_tar_{tarif_name}')
    kb_builder.button(text='Назад', callback_data='tarif_info')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def data_type():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Номер телефона', callback_data=f'get_data_by_num')
    # kb_builder.button(text='Номер документа', callback_data='get_data_by_doc')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def check_payment(pid, tarif):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Проверить статус', callback_data=f'get_pstatus_{tarif}_{pid}')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def confirm_data():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data=f'confirm_data')
    kb_builder.button(text='Изменить', callback_data=f'edit_data')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def admin_confirmation(from_id, record_id):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data=f'adm_confirm_data_{from_id}_{record_id}')
    kb_builder.button(text='Редактировать', callback_data=f'adm_edit_data_{from_id}_{record_id}')
    kb_builder.button(text='Отказать', callback_data=f'adm_decline_data_{from_id}_{record_id}')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def admin_panel():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Рассылка', callback_data=f'adm_send_msg')
    kb_builder.button(text='Пользователи', callback_data=f'adm_users_panel')
    kb_builder.button(text='Тарифы', callback_data=f'adm_tarifs')
    kb_builder.button(text='Поиск пользователя', callback_data=f'adm_search_user')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def admin_edit_tarifs():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Редактировать', callback_data=f'adm_edit_tarifs')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)

def tarifs():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Тарифы', callback_data='tarif_info')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)

def adm_edit_data(rec_id):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Сохранить', callback_data=f'adm_save_new_data_{rec_id}')
    kb_builder.button(text='Редактировать', callback_data=f'adm_edit_new_data_{rec_id}')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def adm_edit_user(user_id):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Данные', callback_data=f'adm_get_data_{user_id}')
    kb_builder.button(text='Подписка', callback_data=f'adm_edit_sub_{user_id}')
    kb_builder.button(text='Заблокировать', callback_data=f'adm_block_{user_id}')
    kb_builder.button(text='Разблокировать', callback_data=f'adm_unblock_{user_id}')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def prolong_sub():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Продлить подписку', callback_data=f'prolong_sub_')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def adm_sub_menu(target_uid):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Продлить подписку', callback_data=f'adm_prolong_sub_{target_uid}')
    kb_builder.button(text='Аннулировать подписку', callback_data=f'adm_delete_sub_{target_uid}')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def adm_search_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Поиск по id', callback_data=f'adm_search_byid')
    kb_builder.button(text='Поиск по username', callback_data=f'adm_search_byuname')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)